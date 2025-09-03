"""
NOTE: Adapted from: https://github.com/arpastrana/jax_fdm/blob/main/src/jax_fdm/equilibrium/sparse.py
       Waiting for the CPU backend to be added in https://jax.readthedocs.io/en/latest/_autosummary/jax.experimental.sparse.linalg.spsolve.html#jax.experimental.sparse.linalg.spsolve
NOTE: Sparse solver does not support forward mode auto-differentiation yet.
"""
import jax
import jax.numpy as jnp

from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve as spsolve_scipy
from functools import partial
from jax.experimental.sparse.linalg import spsolve as spsolve_jax


def spsolve_GPU(data,indices,indptr,B):

    x = jnp.zeros_like(B)
    for i in range(B.shape[1]):
        x = x.at[:,i].set(spsolve_jax(data,indices, indptr, B[:, i],tol=1e-9))

    return x


# ==========================================================================
# Sparse linear solver on CPU
# ==========================================================================

def _spsolve(data,rows,cols, b):

    """
    A wrapper around scipy sparse linear solver that acts as a JAX pure callback.
    """
    def callback(data, rows, cols, _b):
       
        _A = csc_matrix((data, (rows, cols)),shape=(b.shape[0], b.shape[0]))


        return spsolve_scipy(_A, _b)

    return_type = b
    if b.ndim == 2:
     if b.shape[1] == 1:
       return_type = b[:,0]
     
    xk = jax.pure_callback(callback,  # callback function
                           return_type,  # return type is b
                           data,  # callback function arguments from here on
                           rows,
                           cols,
                           b)
    
   
    return xk.reshape((len(xk),-1))



# ==========================================================================
# Define sparse linear solver
# ==========================================================================
@jax.custom_vjp
def sparse_solve(data,rows,cols, b):
    """
    The sparse linear solver.
    """

  
    return _spsolve(data,rows,cols, b)

        #return b - jnp.zeros_like(xk).at[rows].add(data[...,jnp.newaxis] * xk[cols])

# ==========================================================================
# Forward and backward passes
# ==========================================================================

def sparse_solve_fwd(data,rows,cols, b):
    """
    Forward pass of the sparse linear solver.

    Call the linear solve and save parameters and solution for the backward pass.
    """
    xk = sparse_solve(data,rows,cols,b)

    return xk,(xk,data,rows,cols,b)


def sparse_solve_bwd(res, g):
    """
    Backward pass of the sparse linear solver.
    """

    xk,data,rows,cols,b = res

    # Solve adjoint system
    lam = sparse_solve(data,cols,rows,g)

    # the implicit constraint function for implicit differentiation
    def residual_fn(params):
        data, b = params
 
        return b - jnp.zeros_like(xk).at[rows].add(jnp.einsum('i,i...->i...',data,xk[cols]))

    params = (data, b)

    # Call vjp of residual_fn to compute gradient wrt params
    params_bar = jax.vjp(residual_fn, params)[1](lam)[0]

    return (params_bar[0],None,None,params_bar[1]) 


sparse_solve.defvjp(sparse_solve_fwd, sparse_solve_bwd)



