from typing import Callable
from jax import numpy as jnp
import jax
from matinverse import Geometry2D
from matinverse.material import Gray2D
import time
from matinverse.solver import source_iteration


def BTE(geo     :Geometry2D ,\
        mat     :Gray2D   ,\
        tol     :float=1e-8,\
        solver  :str = 'GMRES',\
        maxiter :int = 500)->Callable:

 
  #Import material
  S = mat.S #W/m/K

  
  M = S.shape[0]

  W = jnp.diag(mat.W_RTA) + mat.W_od
  scale = mat.W_RTA.sum()
  #-----------------

  #Import geometry 
  i_mat        = jnp.hstack((geo.smap[:,0],geo.smap[:,1]))
  j_mat        = jnp.hstack((geo.smap[:,1],geo.smap[:,0]))
  normals      = jnp.vstack((geo.normals,-geo.normals))
  N            = geo.N
  factor = geo.areas/geo.V

  factor = jnp.concatenate((factor,factor))

  #Build transport matrices
  G        = jnp.einsum('qj,nj,n->qn',S,normals,factor,optimize=True) #W/m^2/K
  gp       = G.clip(min=0)
  gm       = G.clip(max=0)
  GG       = jnp.einsum('qn,n->qn',gp,1/gm.sum(axis=0))

  im = jnp.concatenate((i_mat,jnp.arange(N)))
  jm = jnp.concatenate((j_mat,jnp.arange(N)))
  
  k0       = 1e-12;k1 = 1 
 
  #@jax.jit
  def func(rho,bcs,**kwargs):  

    n_batches = kwargs.setdefault('n_batches',1)
    
    #First guess
    X0     = kwargs.setdefault('x0',jnp.zeros((n_batches,M,N)))

    if X0.shape[0] != n_batches: 
       X0 = jnp.repeat(X0[jnp.newaxis,:,:], n_batches, axis=0)
 
   
    #Heating
    H     = kwargs.setdefault('H',jnp.zeros((n_batches,N)))
    if H.ndim == 1: H  = jnp.tile(H,(n_batches,1))

    rho = k0 + rho*(k1-k0)
    t = 2*rho[i_mat] * rho[j_mat]/(rho[i_mat] + rho[j_mat])
    
    #t = jnp.concatenate((t,t)) #This is needed when a function for t is passed instead
    gm_direct = jnp.einsum('un,n->un',gm,t)
    gp_direct = jnp.einsum('un,n->un',gp,t)
    gm_reflected = gm_direct-gm
    #R_reflected  = jnp.einsum('un,qn->uqn',gm_reflected,GG)
    
    B        = jnp.zeros((n_batches,M,N))
    D        = jnp.zeros((N,M)).at[i_mat].add(gp.T).T

    #PERIODIC-------------------------------------
    p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(jnp.arange(n_batches)))(0)
    #p_sides  = bcs.periodic_indices
    #p_values   = bcs.periodic
    p_sides_b  = p_sides+geo.smap.shape[0] #We do this because we have (normals,-normals)
    p_elems    = geo.smap[p_sides]
    tmp        = jnp.einsum('qs,...s->...qs',gm_direct[:,p_sides],p_values)
    B          = B.at[...,p_elems[:,0]].add(  -tmp)
    tmp        = jnp.einsum('qs,...s->...qs',gm_direct[:,p_sides_b],p_values)
    B          = B.at[...,p_elems[:,1]].add(   tmp)
    #--------------------------------------------

    #---Thermalizing boundary----------------------
    #thermo_sides,thermo_values = bcs.get_temperature(0)
    #thermo_sides,thermo_values = (lambda t: jax.vmap(lambda b: bcs.get_temperature(b, t),0,(None,0))(jnp.arange(n_batches)))(0)
    thermo_sides = bcs.get_temperature_sides()
    thermo_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_temperature_values(b,s,t))(jnp.arange(len(thermo_sides))))(jnp.arange(n_batches))
    thermo_elems   = geo.boundary_sides[thermo_sides]
    factor         = geo.boundary_areas[thermo_sides]/geo.V
    thermo_normals = jnp.array(geo.boundary_normals)[thermo_sides]
    G_thermo       = jnp.einsum('qj,nj,n->qn',S,thermo_normals,factor,optimize=True)
    gp_thermo      = G_thermo.clip(min=0)
    gm_thermo      = G_thermo.clip(max=0)
    D              = D.at[:,thermo_elems].add(gp_thermo)
    B              = B.at[:,:,thermo_elems].add(-jnp.einsum('qn,...n->...qn',gm_thermo,thermo_values))


    #---Permanent Adiabatic Boundary-------
    flux_sides   = bcs.get_flux_sides()
    flux_elems   = geo.boundary_sides[flux_sides]
  
    flux_normals = jnp.array(geo.boundary_normals)[flux_sides]
    factor       = geo.boundary_areas[flux_sides]/geo.V
    G_flux       = jnp.einsum('qj,nj,n->qn',S,flux_normals,factor,optimize=True)
    gp_flux      = G_flux.clip(min=0)
    gm_flux      = G_flux.clip(max=0)
    D            = D.at[:,flux_elems].add(gp_flux)
    R_flux       = -jnp.einsum('un,qn,n->uqn',gm_flux,gp_flux,1/gm_flux.sum(axis=0),optimize=True)
    #-----------------------------------------
    
    #DIAG    = (D+mat.W_RTA[:,jnp.newaxis])
    #data   = jnp.concatenate((gm_direct,DIAG),axis=1)
    
  
    @jax.jit
    def L(X):
    
      #Partial reflection due to TopOpt
      tmp     = jnp.einsum('un,qn,kqn->kun',gm_reflected,GG,X[:,:,i_mat],optimize=True) 

      #Straight component
      tmp    += jnp.einsum('un,kun->kun',gm_direct,X[:,:,j_mat])
      output  = jnp.zeros_like(X).at[:,:,i_mat].add(tmp)

      #permanent adiabatic--------------------------------------
      tmp     = jnp.einsum('uqn,kqn->kun',R_flux,X[:,:,flux_elems])
      output  = output.at[:,:,flux_elems].add(tmp)
      #---------------------------------------------------------

      output += jnp.einsum('uc,kuc->kuc',D,X) 
      output += jnp.einsum('uv,kvc->kuc',W,X)  
      
      return output
   
    #Add heat source
    B += jnp.einsum('dc,q->dqc',H,mat.Q_weigths)

    #print(jnp.einsum('dc,q->dqc',H,mat.Q_weigths).sum())
    #print(H.sum()*geo.V)
    #quit()

     
    if solver == 'GMRES':   
     X = jax.scipy.sparse.linalg.gmres(lambda x:L(x)/scale, B/scale,solve_method ='batched',tol=tol,x0=jax.lax.stop_gradient(X0),maxiter=maxiter)[0]
    elif solver =='source_iteration':
     X = source_iteration(B,D,gm_reflected,gm_direct,jax.lax.stop_gradient(X0),i_mat,j_mat,tol,maxiter,GG,mat.W_od,im,jm,flux_elems,R_flux,mat.W_RTA)
    else:
      raise 'Solver not recognized:'


    #control error
    error = jnp.linalg.norm(L(X)-B)/jnp.linalg.norm(B)

    #jax.debug.print("🤯 {x} 🤯", x=error)
    
    #Temperature 
    T = jnp.einsum('u,kuc->kc',mat.T_weigths,X)

    #Flux
    J = jnp.einsum('ui,kuc->kci',S,X) #W/m/m

    #If periodic boundary conditions
    P_adj   = jnp.zeros((n_batches,M,N))
 
    tmp     = jnp.einsum('qs,...s->...qs',gp_direct[:,p_sides],p_values)
    P_adj   =  P_adj.at[:,:,p_elems[:,0]].add(  -tmp)
    tmp     = jnp.einsum('qs,...s->...qs',gp_direct[:,p_sides_b],p_values)
    P_adj   =  P_adj.at[:,:,p_elems[:,1]].add(   tmp)

    kappa   = -jnp.einsum('s,us,...s ->...',t[p_sides],gm[:,p_sides],p_values**2)
    kappa  +=  jnp.einsum('...uc,...uc->...',P_adj,X)

    kappa  *=  geo.V #This assume square domain
    #------------------------
    output = {'T':T,'kappa':kappa,'J':J}
    #If there is only 1 BC, then just delete the first dimension 
    if n_batches == 1: output = jax.tree.map(lambda x:x[0],output)

    
    return output
  
  return func
  
