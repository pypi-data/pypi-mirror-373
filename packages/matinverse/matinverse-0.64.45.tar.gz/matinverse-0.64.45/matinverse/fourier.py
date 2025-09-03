import numpy as np
from typing import Callable
from jax import numpy as jnp
from functools import partial
import jax
from matinverse import Geometry2D,Geometry3D
from matinverse.boundary_conditions import BoundaryConditions
import lineax as lx
from typing import Union
import equinox as eqx
import optimistix as optx
import time
from matinverse import sparse
import diffrax
from matinverse.cracknicolson import CrankNicolson


@eqx.filter_jit
def Fourier( geo:                           Union[Geometry2D,Geometry3D],\
             boundary_conditions:           BoundaryConditions,\
             thermal_conductivity:          Callable|None = None,\
             heat_capacity:                 Callable|None = None,\
             conductance:                   Callable|None = None,\
             heat_source:                   Callable|None = None,\
             mode:                          str           = 'linear',\
             linear_solver:                 str           = 'iterative',\
             collapse_direct:               bool          = False,\
             compute_side_flux:             jnp.array     = None,\
             batch_size:                    int           = 1,\
             tol:                           float         = 1e-9,\
             maxiter:                       int           = 5000,\
             maxiter_nonlinear:             int           = 100,\
             scale_nonlinear:               float         = None,\
             maxiter_transient:             int           = 10000,\
             saveat:                        jnp.array     = None,
             DT:                            float         = 1.0,\
             NT:                            int           = 1,\
             X0:                            jnp.array     = None
             )->(dict,dict):
        r"""Differentiable Fourier solver based on the Finite-volume method.

         :param geo: The geometry object containing the mesh information.

         :param boundary_conditions: The boundary conditions object

         :param thermal_conductivity: A function that takes batch, space (as a function of volume index), temperature and time and returns the thermal conductivity tensor :math:`[\mathrm{W\,m^{-1}\,K^{-1}}]`

            Example::

               thermal_conductivity = lambda batch, space, temp, t: 100.*jnp.eye(geo.dim)
         :param heat_capacity: A function that takes batch, space (as a function of volume index), temperature and time and returns the heat capacity :math:`[\mathrm{J\,m^{-3}\,K^{-1}}]`.
            Example::

               heat_capacity = lambda batch, space, temp, t: 1e3 

         :param conductance: A function that takes the indices of the volumes adjacent to a given side and returns the batched conductance :math:`[\mathrm{W\,m^{-2}\,K^{-1}}]`. If not provided, it is assumed to be large number so it won't affect calculation.      


            Example::
               conductance = lambda s1,s2: 1e3*jnp.ones(1) #assuming a single batch and uniform conductance

         :param heat_source: A function that takes batch, space (as a function of volume index) and time and returns the heat source :math:`[\mathrm{W\,m^{-3}}]`. If not provided, it is assumed to be zero.

            Example::
               heat_source = lambda b,s,t: 1e5 
         
         :param mode: The mode of the solver. Can be 'linear', 'nonlinear' or 'transient'.

         :param linear_solver: The linear solver to use. Can be 'iterative' or 'direct'. If 'iterative', it uses the GMRES method. If 'direct', it uses sparse LU factorization.

         :param collapse_direct: If ``True``, it uses the same assembly matrix for all the batches in the direct solver. It can be used only for direct solvers and if no Robin BCs are used.

         :param compute_side_flux: A jnp.array containing the indices of the sides for which the flux will be computed. If not provided, no internal interfacial flux will be computed.

         :param batch_size: The number of batches to use. If > 1, the solver will be vectorized over the batches.

         :param tol: The tolerance for the linear solver.

         :param maxiter: The maximum number of iterations for the solver.

         :param maxiter_nonlinear: The maximum number of iterations for the nonlinear solver (default is 100). It is used only if ``mode='nonlinear'``. 

         :param scale_nonlinear: A scaling factor for the nonlinear solver. If not provided, it is set to :math:`10^{-4} dx^2` It is used only if ``mode='nonlinear'``.

         :param maxiter_transient: The maximum number of iterations for the transient solver (default is 10000). It is used only if ``mode='transient'``.

         :param saveat: A jnp.array containing the time steps at which the solution will be saved. If not provided, it saves all time steps.

         :param DT: The time step for the transient solver.

         :param NT: The number of time steps for the transient solver.

         :param X0: The initial guess for the temperature. It is expected to be of shape ``(batch_size, geo.nDOFs)``. If ``batch_size = 1`` then it can be a 1D array. If not provided, it is assumed to be zero.

       
         :return: A tuple containing the output dictionary and the statistics dictionary. The output dictionary contains the following fields:

         - 'T': The temperature field of shape ``(NT, batch_size, geo.nDOFs)``. 
         - 'J': The heat flux field of shape ``(NT, batch_size, geo.nDOFs, geo.dim)``. 
         - 'kappa': The thermal conductivity tensor field of shape ``(NT, batch_size, geo.nDOFs, geo.dim, geo.dim)``.
         - 'kappa_effective': The effective thermal conductivity field of shape ``(NT, batch_size, geo.nDOFs)``.
         - 'P_boundary': The boundary flux field of shape ``(NT, batch_size, geo.nBoundarySides)``.
         - 'P_internal': The internal flux field of shape ``(NT, batch_size, geo.nSides)``.
         - 'T_boundary': The temperature field at the boundaries of shape ``(NT, batch_size, geo.nBoundarySides)``.
        
         The statistics dictionary contains the following fields:
         
          - 'num_steps': The number of steps taken by the nonlinear solver.

        """
        if saveat is None:
         saveat = jnp.arange(0, DT*NT, DT)

        NT_save = len(saveat)

        if compute_side_flux is None:
         compute_side_flux = jnp.array([], dtype=jnp.int32)

        if X0 is None:
         X0 = jnp.zeros((batch_size, geo.nDOFs))

        if thermal_conductivity is None:
          thermal_conductivity = lambda batch, space, temp, t: jnp.eye(geo.dim)

        if heat_capacity is None:
           heat_capacity = lambda batch, space, temp, t: 1 

        if heat_source is None:
          heat_source =lambda b,s,t:0

        N          = geo.nDOFs
       
        #Prepare the output structure
        stats = {}

        if compute_side_flux is None:
         compute_side_flux = jnp.array([], dtype=jnp.int32)
    
        bcs = boundary_conditions
    
        if not scale_nonlinear:
         scale = 1e-4*(geo.size[0]/geo.grid[0])**2
        else:
          scale = scale_nonlinear 

        #This assumes that h_ij = h_ji
        if not conductance:
          conductance = lambda x,t:1e10*jnp.ones((batch_size,geo.smap.shape[0]))
        else:
          conductance = geo.cell2side(conductance) 

 
        #if not X0: X0    = jnp.zeros((batch_size,N))
        if X0.ndim == 1: X0 = jnp.tile(X0,(batch_size,1))

       
        rows       = jnp.hstack((geo.smap[:,0],geo.smap[:,1],np.arange(N)))
        cols       = jnp.hstack((geo.smap[:,1],geo.smap[:,0],np.arange(N)))  

        #Non linearity Create TB0 from X0 [assuming 0 flux]]------------------------------------
        
        flux_sides   = bcs.get_flux_sides()
        flux_elems   = geo.boundary_sides[flux_sides]
        N_flux_sides = len(flux_elems)
        TB0          = X0[:,flux_elems]
        rows         = jnp.hstack((rows,jnp.arange(N_flux_sides)+N,jnp.arange(N_flux_sides)+N))
        cols         = jnp.hstack((cols,jnp.arange(N_flux_sides)+N,flux_elems))  
        #rows         = jnp.hstack((rows,flux_elems,flux_elems,                jnp.arange(N_flux_sides)+N,jnp.arange(N_flux_sides)+N))
        #cols         = jnp.hstack((cols,flux_elems,jnp.arange(N_flux_sides)+N,flux_elems,                jnp.arange(N_flux_sides)+N))  
        T0 = jnp.concatenate([X0,TB0], axis=1) 

       
        #------------------------------------------------------------------------

      
        def Laplacian(X,t):
         
         T  = X[:,:N]
         Tb = X[:,N:]

         B          = jnp.zeros((batch_size,N+N_flux_sides))
        
         #This vectorizes over batches and space. This needs to be simplified by vectorizing directly the Laplacian.
         kappa = jax.vmap(
                lambda b: jax.vmap(
                    thermal_conductivity, 
                    in_axes=(None, 0, 0, None), 
                   out_axes=0
                  )(b, jnp.arange(N), T[b], t)
         )(jnp.arange(batch_size))


         cond = partial(conductance,t=t)(T)
        
         kappa_i  =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,0]],geo.normals)
         kappa_j  =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,1]],geo.normals)

         cf       = 2*jnp.einsum('...s,s->...s',kappa_i*kappa_j/cond,1/geo.dists)
         
         kappa_ij = 2*kappa_i * kappa_j/(kappa_i + kappa_j + cf)
         factor =  geo.areas/geo.dists/geo.V

         #jax.debug.print("🤯 {x} 🤯", x=factor)


         d = jnp.zeros((batch_size,N)).at[:,geo.smap[:,0]].add(jnp.einsum('...s,s->...s',kappa_ij,factor)).at[:,geo.smap[:,1]].add(jnp.einsum('...s,s->...s',kappa_ij,factor))
         
         bulk_d  = jnp.einsum('...s,s->...s',kappa_ij,factor)

       
 
         #Thermalizing Boundaries        
         thermo_sides = bcs.get_temperature_sides()
         thermo_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_temperature_values(b,s,t))(jnp.arange(len(thermo_sides))))(jnp.arange(batch_size))

        
    
         side_normals  = jnp.array(geo.boundary_normals)[thermo_sides]
         thermo_elems  = jnp.array(geo.boundary_sides)[thermo_sides]

         kappa_b = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,thermo_elems],side_normals)
         
         factor =  geo.boundary_areas[thermo_sides]/geo.boundary_dists[thermo_sides]/geo.V
         d =  d.at[:,thermo_elems].add(jnp.einsum('...s,s->...s',kappa_b,factor))
         tmp = jnp.einsum('...s,...s->...s',thermo_values,kappa_b)
         B =  B.at[:,thermo_elems].add(jnp.einsum('...s,s->...s',tmp,factor))

         #Flux Boundaries 
         flux_sides  = bcs.get_flux_sides()
         flux_elems  = geo.boundary_sides[flux_sides]  
         kappa_b     = jnp.einsum('si,...sij,sj->...s',geo.boundary_normals[flux_sides],kappa[:,flux_elems],geo.boundary_normals[flux_sides])

         
         if len(flux_sides) > 0:
          flux_values = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(b,s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(jnp.arange(batch_size))
         else:
          flux_values = jnp.zeros((batch_size,len(flux_sides)))

      
         factor      = geo.boundary_areas[flux_sides]/geo.V
         B           = B.at[:,flux_elems].add(-jnp.einsum('...s,s->s',flux_values,factor))     

         #Nonlinear component
         B           = B.at[:,N:].add(-geo.boundary_dists[flux_sides][jnp.newaxis,:] * flux_values/kappa_b)

         #B           = B.at[:,N:].add(-jnp.einsum('...s,s->s',flux_values,factor))
         #factor      = geo.boundary_areas[flux_sides]/geo.boundary_dists[flux_sides]/geo.V
         #tmp         = jnp.einsum('...s,s->...s',kappa_b,factor)
         #data_flux   = jnp.concatenate([-tmp,tmp,tmp,-tmp], axis=1)
         #print(data_flux.shape)
         #quit()


         #----------------------------
        
         #Robin boundary
         robin_sides = bcs.get_robin_sides()
         robin_h,robin_T = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(jnp.arange(batch_size))
         robin_elems = geo.boundary_sides[robin_sides]
         side_normals = geo.boundary_normals[robin_sides]
         
         #print(geo.boundary_centroids[robin_sides])
         #print(robin_h)
         #quit()

         kappa_b = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,robin_elems],side_normals)

         gamma  = jnp.einsum('...s,s,...s->...s',robin_h,geo.boundary_dists[robin_sides],1/kappa_b)
         h_star = robin_h/(gamma+1)
         factor = geo.boundary_areas[robin_sides]/geo.V
         tmp = jnp.einsum('...s,...s,s->...s',h_star,robin_T,factor)
         B  = B.at[:,robin_elems].add(tmp)
         d  = d.at[:,robin_elems].add(jnp.einsum('...s,s->...s',h_star,factor))
         #---------------------------------------

         #Periodic 
         p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(jnp.arange(batch_size)))(t)
        
         p_elems  = geo.smap[p_sides]
   
         P        = jnp.zeros_like(B)
         tmp      = jnp.einsum('...s,...s->...s',bulk_d[:,p_sides],p_values)
         P        = P.at[:,p_elems[:,0]].add( tmp)
         P        = P.at[:,p_elems[:,1]].add(-tmp) 
         B       += P

         
         data   = jnp.hstack((-bulk_d,-bulk_d,d))

        

         #{reserves symmetry}        
         #data   = jnp.hstack((data,-data_flux))

         
         #Add nonlinear boundary conditions
  
         nonlinear_data = jnp.ones(N_flux_sides)
         repeated_data = jnp.tile(nonlinear_data[None, :], (batch_size, 1))         
         data = jnp.hstack((data,repeated_data,-repeated_data))
         #----------------------------------

         return data,B

        
        #Solve
        if mode =='nonlinear':

         H = jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,0))(jnp.arange(N))) (jnp.arange(batch_size))
         H = jnp.concatenate([H, jnp.zeros((batch_size,N_flux_sides))], axis=1) 
         
         def fn(x,args):
           
           data,B = Laplacian(x,0) 


           L = jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))

           RES = L - B - H
           
           return RES*scale

           #return L - B - H
           #return jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))  - B

         #linaer_solver = lx.AutoLinearSolver(well_posed=False)
         #linear_solver = lx.BiCGStab(atol=1e-12,rtol=1e-12)
         #linear_solver = lx.GMRES(atol=1e-12,rtol=1e-12)
         linear_solver =lx.LU()#AutoLinearSolver(well_posed=False)

         solve  = optx.Newton(rtol=1e-12,atol=1e-12,linear_solver=linear_solver)
         
         #print(solve.linear_solver)
         #quit()

         
         X0 = jnp.concatenate([X0,TB0], axis=1) #Concatenate the initial guess with the boundary conditions``

         out    = optx.root_find(fn, solve, X0,max_steps=maxiter_nonlinear)

         stats.update(out.stats)

         #stats['num_steps'] = out.stats['num_steps']
         #print(out.stats['num_steps'])

         X = out.value

      
         T  = X[:,:N]
         TB = X[:,N:] 
        
        elif mode == 'linear':
          

         data,B = Laplacian(T0,0) 

         L = lambda x: jnp.zeros_like(x).at[:,rows].add(jnp.einsum('ks,ks->ks',data,x[:,cols]))

         H = jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,0))(jnp.arange(N))) (jnp.arange(batch_size))

         H = jnp.concatenate([H, jnp.zeros((batch_size,N_flux_sides))], axis=1) 

         if linear_solver == 'iterative':  
        
          X,info = jax.scipy.sparse.linalg.cg(L,B+H,tol=tol,x0=T0,maxiter=maxiter)
          
         elif linear_solver == 'direct': 
          
          if collapse_direct: 
                        
           X = sparse.sparse_solve(data[0],rows,cols,(B+H).T).T

          else:
           
           X = jnp.array([sparse.sparse_solve(d,rows,cols,(B+H)[i])  for i,d in enumerate(data)])

         
        
         T = X[:,:N] #Get only the temperature values, not the boundary ones
         TB = X[:,N:]
         #operator = lx.FunctionLinearOperator(fn=L,tags=lx.positive_semidefinite_tag,input_structure=jax.eval_shape(lambda: jnp.zeros((batch_size,N))))
         #out = lx.linear_solve(operator, B + H,options={'y0':jax.lax.stop_gradient(X0)})  
         #T = out.value
         #T = jnp.ones_like(X0)
         
         
        elif mode == 'transient':
 
          #DT = kwargs['DT']

          H = lambda t: jax.vmap(lambda b: jax.vmap(lambda s:heat_source(b,s,t))(jnp.arange(N))) (jnp.arange(batch_size))

          # #Add nonlinearity
         
          # def update(y, t):

          #   data,B = Laplacian(y[t-1],t)           
          #   L = jnp.zeros((batch_size,N+N_flux_sides)).at[:,rows].add(jnp.einsum('ks,ks->ks',data,y[:,:,cols][t-1]))
          #   LAPLACIAN = L[:,:N]
            
          
          #   #Heat capacity [batch,space]       
          #   C = jax.vmap(lambda b: jax.vmap(lambda s: heat_capacity(b,s,y[t,b,s],t))(jnp.arange(N)))(jnp.arange(batch_size))      
            
          #   T = y[t-1,:,:N] + DT/C*(B[:,:N] + H(t) - LAPLACIAN)

          #   TB = T[:,flux_elems] + L[:,N:]

          #   y_new = jnp.concatenate([T,TB], axis=1)

          #   y = y.at[t].set(y_new)
          #   return y,None

          # y_init = jnp.zeros((NT,batch_size,N+N_flux_sides)).at[0].set(T0)

          # X, _ = jax.lax.scan(update, y_init,jnp.arange(NT))

          # T  = X[:,:,:N] #Get only the temperature values, not the boundary ones
          # TB = X[:,:,N:]
        
          # #DIFFRAX
          def vector_field(t, y, args):
           
            y = jnp.concatenate([y,TB0], axis=1)

            data,B = Laplacian(y,t)   

              
            L = jnp.zeros((batch_size,N+N_flux_sides)).at[:,rows].add(jnp.einsum('ks,ks->ks',data,y[:,cols]))
            LAPLACIAN = L[:,:N]
            B_tot     = B[:,:N] + H(t)


            C = jax.vmap(lambda b: jax.vmap(lambda s: heat_capacity(b,s,y,t))(jnp.arange(N)))(jnp.arange(batch_size))       

            return (B_tot - LAPLACIAN)/C

            #TB =  EQ_RES[:,flux_elems]*0 #TO DO

            #return  jnp.concatenate([EQ_RES,TB], axis=1)[0]
          
          
          # Tolerances
          rtol = 1e-10
          atol = 1e-10
          stepsize_controller = diffrax.PIDController(
          pcoeff=0.3, icoeff=0.4, rtol=rtol, atol=atol, dtmax=0.001
          )
       
      
          #solver = CrankNicolson(rtol=rtol,atol=atol)
          solver = diffrax.Tsit5()

          term = diffrax.ODETerm(vector_field)

          #X0 = jnp.concatenate([X0,TB0], axis=1)
          out = diffrax.diffeqsolve(
               term,
               solver,
               0,
               DT*NT,
               DT,
               X0,
               saveat=diffrax.SaveAt(ts=saveat),
               stepsize_controller=stepsize_controller,
               max_steps=maxiter_transient
          )

          X = out.ys
          #print(out.stats)

          #T = X[:,:,:N] #Get only the temperature values, not the boundary ones
          #TB = X[:,:,N:]
          T = X
     
          TB = jnp.zeros((NT_save,batch_size,N_flux_sides)) #TO DO: Add the boundary conditions for the transient case
          
       
       
        def get_flux(X,Tb,kappa,conductance,t):
        
         
        
         #Flux calculations (using Gauss)
         J                = jnp.zeros((batch_size,N,geo.dim))

         P_boundary       = jnp.zeros((batch_size,len(geo.boundary_sides)))       

         kappa_i          =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,0]],geo.normals)
         kappa_j          =  jnp.einsum('si,...sij,sj->...s',geo.normals,kappa[:,geo.smap[:,1]],geo.normals)

         cf               = 2*jnp.einsum('...s,s->...s',kappa_i*kappa_j/conductance,1/geo.dists)

         kappa_ij         = 2*kappa_i * kappa_j/(kappa_i + kappa_j + cf)

         #Bulk
         T_boundary_i     = (X[:,geo.smap[:,0]]*kappa_i+X[:,geo.smap[:,1]]*kappa_j + X[:,geo.smap[:,0]]*cf)/(kappa_i + kappa_j + cf)
         T_boundary_j     = (X[:,geo.smap[:,0]]*kappa_i+X[:,geo.smap[:,1]]*kappa_j + X[:,geo.smap[:,1]]*cf)/(kappa_i + kappa_j + cf)         

         contribution_i   = jnp.einsum('...s,sd,s->...sd',T_boundary_i*kappa_i,geo.normals,geo.areas)
         contribution_j   = jnp.einsum('...s,sd,s->...sd',T_boundary_j*kappa_j,geo.normals,geo.areas)
         J                = J.at[:,geo.smap[:,0],:].add(-contribution_i).at[:,geo.smap[:,1],:].add(contribution_j)

         #Compute side fluxes (internal)
         P_internal = -jnp.einsum('b...,b...,...,...->b...',kappa_ij[:,compute_side_flux],X[:,geo.smap[compute_side_flux,1]] - X[:,geo.smap[compute_side_flux,0]],\
                              geo.areas[compute_side_flux],1/geo.dists[compute_side_flux])
         
         T_boundary = jnp.zeros((batch_size,geo.boundary_sides.shape[0]))
         #Periodic
         p_sides,p_values = (lambda t: jax.vmap(lambda b: bcs.get_periodic(b, t),0,(None,0))(jnp.arange(batch_size)))(t)
       
         contribution     = jnp.einsum('...s,...s,s,sd->...sd',0.5*kappa_ij[:,p_sides],p_values,geo.areas[p_sides],geo.normals[p_sides]) 
         J                = J.at[:,geo.smap[p_sides,0],:].add(-contribution)
         J                = J.at[:,geo.smap[p_sides,1],:].add(-contribution) 
         P                = jnp.zeros((batch_size,N))
         factor           =  geo.areas/geo.dists/geo.V
         bulk_d           = jnp.einsum('...s,s->...s',kappa_ij,factor)
         tmp              = jnp.einsum('...s,...s->...s',bulk_d[:,p_sides],p_values)
         p_elems          = geo.smap[p_sides]
         P                = P.at[:,p_elems[:,0]].add( tmp)
         P                = P.at[:,p_elems[:,1]].add(-tmp)
         kappa_effective  = jnp.einsum('...s,...s,s->...',kappa_ij[:,p_sides],p_values**2,geo.areas[p_sides]/geo.dists[p_sides]) - jnp.einsum('...c,...c->...',X,P)*geo.V
         
         #Thermalizing boundaries
         thermo_sides     = bcs.get_temperature_sides()
         thermo_values    = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_temperature_values(b,s,t))(jnp.arange(len(thermo_sides))))(jnp.arange(batch_size))
         side_normals     = geo.boundary_normals[thermo_sides]
         thermo_elems     = geo.boundary_sides[thermo_sides]
         kappa_b          = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,thermo_elems],side_normals)
         #T_boundary       = thermo_values
         contribution     = jnp.einsum('...s,...s,sd,s->...sd',thermo_values,kappa_b,side_normals,geo.boundary_areas[thermo_sides])
         J                = J.at[:,thermo_elems,:].add(-contribution)
         factor           = geo.boundary_areas[thermo_sides]/geo.boundary_dists[thermo_sides]
         J_boundary       = jnp.einsum('...s,...s,s->...s',thermo_values-X[:,thermo_elems],kappa_b,factor)
         kappa_effective += jnp.absolute(J_boundary).sum(axis=1)/2
         P_boundary       = P_boundary.at[:,thermo_sides].set(-J_boundary)
         T_boundary       = T_boundary.at[:,thermo_sides].set(thermo_values)

         #Flux boundaries
         flux_sides       = bcs.get_flux_sides()
         flux_elems       = geo.boundary_sides[flux_sides]  
         kappa_b          = jnp.einsum('si,...sij,sj->...s',geo.boundary_normals[flux_sides],kappa[:,flux_elems],geo.boundary_normals[flux_sides])
         if len(flux_sides) > 0:
          flux_values      = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_flux_values(b,s,t,Tb[b,s]))(jnp.arange(len(flux_sides))))(jnp.arange(batch_size))
         else:
          flux_values      = jnp.zeros((batch_size,len(flux_sides)))
         
         #T_boundary       = X[:,flux_elems] - geo.boundary_dists[flux_sides][jnp.newaxis,:] * flux_values/kappa_b

        
         T_boundary       = T_boundary.at[:,flux_sides].set(Tb)


         contribution     = jnp.einsum('...s,sd,s...->...sd',Tb*kappa_b,geo.boundary_normals[flux_sides],geo.boundary_areas[flux_sides])
         J                = J.at[:,flux_elems,:].add(-contribution)
         P_boundary       = P_boundary.at[:,flux_sides].set(flux_values*geo.boundary_areas[flux_sides])

         
         #Robin boundary conditions---
         robin_sides      = bcs.get_robin_sides()
         robin_h,robin_T  = jax.vmap(lambda b:jax.vmap(lambda s:bcs.get_robin_values(b,s,t))(jnp.arange(len(robin_sides))))(jnp.arange(batch_size))
         robin_elems      = geo.boundary_sides[robin_sides]
         side_normals     = geo.boundary_normals[robin_sides]
         kappa_b          = jnp.einsum('si,...sij,sj->...s',side_normals,kappa[:,robin_elems],side_normals)  
         gamma            = jnp.einsum('...s,s,...s->...s',robin_h,geo.boundary_dists[robin_sides],1/kappa_b)

     
         T_boundary_robin       =(X[:,robin_elems] + gamma*robin_T)/(1+gamma)
         contribution     = jnp.einsum('...s,...s,sd,s->...sd',T_boundary_robin,kappa_b,side_normals,geo.boundary_areas[robin_sides])
         J                = J.at[:,robin_elems,:].add(-contribution)
         flux_values      = robin_h*(T_boundary_robin-robin_T)
         P_boundary       = P_boundary.at[:,robin_sides].set(flux_values*geo.boundary_areas[robin_sides])
         T_boundary       = T_boundary.at[:,robin_sides].set(T_boundary_robin)


         return J/geo.V,kappa_effective,P_boundary,P_internal,T_boundary
        
        
        T = T.reshape((NT_save,batch_size,-1))
        TB = TB.reshape((NT_save,batch_size,-1))

        #Vectorize kappa in batch, time and space
        kappa = jax.vmap(
         lambda t:
         jax.vmap(
            lambda b:
                jax.vmap(
                    lambda i:
                        thermal_conductivity(b,i,T[t, b, i],t)
                )(jnp.arange(N))
         )(jnp.arange(batch_size))
        )(jnp.arange(NT_save))

     
        cond = jax.vmap(conductance, in_axes=(0, 0))(T, jnp.arange(NT_save)) 

        J,kappa_effective,P_boundary,P_internal,T_boundary = jax.vmap(get_flux)(T,TB,kappa,cond,jnp.arange(NT_save))

        output = {'T':T,'J':J,'kappa':kappa,'kappa_effective':kappa_effective,'P_boundary':P_boundary,'P_internal':P_internal,'T_boundary':T_boundary}

        if batch_size > 1 and NT_save == 1: 
          output = jax.tree.map(lambda x:x[0],output)

        if batch_size == 1 and NT_save > 1:
           output = jax.tree.map(lambda x:x[:,0,...],output)

        if batch_size == 1 and NT_save == 1:
           output = jax.tree.map(lambda x:x[0,0],output)   

        
        return output,stats
    
   
