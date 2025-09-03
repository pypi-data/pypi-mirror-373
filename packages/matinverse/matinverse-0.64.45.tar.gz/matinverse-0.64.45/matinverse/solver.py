import numpy as np
from cachetools import cached,LRUCache
import scipy.sparse as sp
from jax import numpy as jnp
import jax
from jax import debug

def solve_adjoint(B,D,gm_reflected,gm_direct,*options) :
     
     X0,i_mat,j_mat,rtol,maxiter,GG,W_od,im,jm,flux_elems,R,W_RTA  = options

     X     = np.zeros_like(B)
     #W = jnp.diag(W_RTA) + W_od
     
     (K,M,N) = np.shape(B)

     cache_compute_lu = LRUCache(maxsize=1e3)

     DIAG    = (D+W_RTA[:,jnp.newaxis])
     data   = jnp.concatenate((gm_direct,DIAG),axis=1)

     @cached(cache=cache_compute_lu)
     def compute_lu(q):
        return  sp.linalg.splu(sp.csc_matrix((data[q],(jm,im)),shape=(N,N),dtype=np.float64)) #Transposed

     #This needs to be vectorized
     #@jax.jit
     #def L(X):
    
      #Partial reflection due to TopOpt
     # tmp     = jnp.einsum('un,qn,kqn->kun',gm_reflected,GG,X[:,:,i_mat],optimize=True) 

      #Straight component
     # tmp    += jnp.einsum('un,kun->kun',gm_direct,X[:,:,j_mat])
     # output  = jnp.zeros_like(X).at[:,:,i_mat].add(tmp)

      #permanent adiabatic--------------------------------------
     # tmp     = jnp.einsum('uqn,kqn->kun',R,X[:,:,flux_elems])
     # output  = output.at[:,:,flux_elems].add(tmp)
      #---------------------------------------------------------

     # output += jnp.einsum('uc,kuc->kuc',D,X) 
     # output += jnp.einsum('uv,kvc->kuc',W,X)  
      
     # return output


     r_old =   0
     error = 1
     n_iter = 0
     #indices = np.ix_(range(M),i_mat)

     while error > rtol  and n_iter < maxiter:
        #-------
        
        B_tot  = np.array(B) - np.einsum('qu,kqc->kuc',W_od,X) 
            
        #TopOpt
        np.add.at(B_tot.transpose(2,0,1),i_mat,-np.einsum('us,qs,kqs->sku',gm_reflected,GG,X[:,:,i_mat]))
 
        #Permanent boundaries
        np.add.at(B_tot.transpose(2,0,1),flux_elems,-np.einsum('qus,kqs->sku',R,X[:,:,flux_elems]))
        

        for n in range(M):
            X[:,n, :]  = compute_lu(n).solve(B_tot[:,n,:].T).T

        r = np.linalg.norm(X)
        error   = abs(r-r_old)/r
        #error = np.linalg.norm(L(X)-B)/np.linalg.norm(B)
        r_old = r
        n_iter += 1
        print('Adjoint',n_iter,error)
     #print(' ' + str(n_iter))

     return X

def solve_forward(B,D,gm_reflected,gm_direct,*options) :
     
     X0,i_mat,j_mat,tol,maxiter,GG,W_od,im,jm,flux_elems,R,W_RTA  = options
    
     W = jnp.diag(W_RTA) + W_od

     X = np.array(X0) 
     
     (K,M,N) = np.shape(X)
    
     cache_compute_lu = LRUCache(maxsize=1e3)

     DIAG    = (D+W_RTA[:,jnp.newaxis])
     data   = jnp.concatenate((gm_direct,DIAG),axis=1)

     @cached(cache=cache_compute_lu)
     def compute_lu(q):
        return  sp.linalg.splu(sp.csc_matrix((data[q],(im,jm)),shape=(N,N),dtype=np.float64))

     r_old  = 0
     error  = 1
     n_iter = 0

     #This needs to be vectorized
     @jax.jit
     def L(X):
    
      #Partial reflection due to TopOpt
      tmp     = jnp.einsum('un,qn,kqn->kun',gm_reflected,GG,X[:,:,i_mat],optimize=True) 

      #Straight component
      tmp    += jnp.einsum('un,kun->kun',gm_direct,X[:,:,j_mat])
      output  = jnp.zeros_like(X).at[:,:,i_mat].add(tmp)

      #permanent adiabatic--------------------------------------
      tmp     = jnp.einsum('uqn,kqn->kun',R,X[:,:,flux_elems])
      output  = output.at[:,:,flux_elems].add(tmp)
      #---------------------------------------------------------

      output += jnp.einsum('uc,kuc->kuc',D,X) 
      output += jnp.einsum('uv,kvc->kuc',W,X)  
      
      return output

     while error > tol  and n_iter < maxiter:
        #-------

        B_tot  = np.array(B) - np.einsum('uv,kvc->kuc',W_od,X)

        #From TopOpt
        np.add.at(B_tot.transpose(2,0,1),i_mat,-np.einsum('us,qs,kqs->sku',gm_reflected,GG,X[:,:,i_mat]))
 
        #Permanent boundaries
        np.add.at(B_tot.transpose(2,0,1),flux_elems,-np.einsum('uqs,kqs->sku',R,X[:,:,flux_elems]))

        for n in range(M):
            X[:,n, :]  = compute_lu(n).solve(B_tot[:,n,:].T).T

        #error = np.linalg.norm(L(X)-B)/np.linalg.norm(B)

        r = np.linalg.norm(X)
        error   = abs(r-r_old)/r
        #jax.debug.print("🤯 {x} 🤯", x=(X.min(),X.max()))
        r_old = r
        n_iter += 1
        #print('Forward',n_iter,error)
        jax.debug.print("🤯 {x} 🤯", x=error)
       
        #print(' ' + str(error))
     #quit()

     return X

def spsolve(B,*options):
  
   
    return jax.pure_callback(solve_forward,B,B,*options)

def spsolve_adjoint(B,*options):

    #debug.callbacl(solve_adjoint,*options) 
    return jax.pure_callback(solve_adjoint,B,B,*options)


# ==========================================================================
# Define sparse linear solver
# ==========================================================================
@jax.custom_vjp
def source_iteration(B,*options):
    
    """Forward call"""
  
    return spsolve(B,*options)


# ==========================================================================
# Forward and backward passes
# ==========================================================================

def solve_fwd(B,*options):
    """
    Forward pass of the sparse linear solver.

    Call the linear solve and save parameters and solution for the backward pass.
    """
    X_fwd = source_iteration(B,*options)

    return X_fwd,(X_fwd,B,*options)

def solve_bwd(res, g):
    """
    Backward pass of the sparse linear solver.
    """

    X_fwd,B,*options = res


    # Solve adjoint system
    lam = spsolve_adjoint(g,*options)

    #lam = -X_fwd[options[-1]]
    #jax.debug.print("🤯 {x} 🤯", x=jnp.allclose(lam,-X_fwd[options[-1]]))

    # the implicit constraint function for implicit differentiation
    def residual_fn(params):
        B,D,gm_reflected,gm_direct,X0,i_mat,j_mat,rtol,max_iter,GG,W_od,im,jm,flux_elems,R,W_RTA = params

        W = jnp.diag(W_RTA) + W_od

        @jax.jit
        def L(X):
    
         #Partial reflection due to TopOpt
         tmp     = jnp.einsum('un,qn,kqn->kun',gm_reflected,GG,X[:,:,i_mat],optimize=True) 

         #Straight component
         tmp    += jnp.einsum('us,kus->kus',gm_direct,X[:,:,j_mat])
         output  = jnp.zeros_like(X).at[:,:,i_mat].add(tmp)

         #permanent adiabatic--------------------------------------
         tmp     = jnp.einsum('uqs,kqs->kus',R,X[:,:,flux_elems])
         output  = output.at[:,:,flux_elems].add(tmp)
         #---------------------------------------------------------

         output += jnp.einsum('uc,kuc->kuc',D,X) 
         output += jnp.einsum('uq,kqc->kuc',W,X)  
      
         return output


        return B  - L(X_fwd)

    # Call vjp of residual_fn to compute gradient wrt params
    params = (B,) + tuple(options)

    params_bar = jax.vjp(residual_fn,params)[1](lam)[0]

    return tuple(params_bar[:4]) + (None,) * 12
 

source_iteration.defvjp(solve_fwd, solve_bwd)


