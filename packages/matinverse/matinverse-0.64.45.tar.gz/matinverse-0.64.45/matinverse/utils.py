from jax import numpy as jnp
from jax import custom_vjp,custom_jvp
from typing import Generic, TypeVar,Callable
from dataclasses import dataclass,field
import jax
from functools import wraps
from interpax import Interpolator2D,interp2d



def compute_gradient_old(x,periodic,d):
    
    Nx,Ny = x.shape

    if periodic[0] and not periodic[1]:
        x = jnp.pad(x, ((Nx, Nx), (0, 0)), mode='wrap')
        tmp = jnp.gradient(x)
        return  jnp.array([tmp[0][Nx:2*Nx, :]/d[0],tmp[1][Nx:2*Nx, :]/d[1]])

    elif periodic[1] and not periodic[0]:    
        x = jnp.pad(x, ((0, 0), (Ny, Ny)), mode='wrap')      
        tmp = jnp.gradient(x)
        return  jnp.array([tmp[0][:, Ny:2*Ny]/d[0],tmp[1][:, Ny:2*Ny]/d[1]])
    
    elif not periodic[1] and not periodic[0]:
        tmp = jnp.gradient(x)
        return  jnp.array([tmp[0]/d[0],tmp[1]/d[1]])
    
    elif periodic[1] and periodic[0]:        
         x =  jnp.pad(x, ((Nx,Nx), (Ny,Ny)), mode='wrap')
         tmp = jnp.gradient(x)
         return  jnp.array([tmp[0][Nx:2*Nx, Ny:2*Ny]/d[0],tmp[1][Nx:2*Nx, Ny:2*Ny]/d[1]])

    else:
        raise ValueError("Invalid periodicity configuration.")      






def compute_gradient(x,periodic,d,order,padding=True):

     if order == 'old':
         return compute_gradient_old(x,periodic,d)

     x = x.T

     Nx,Ny = x.shape
     Lx = Nx * d[0]
     Ly = Ny * d[1]
  
     #For now, we don't treat periodicity only along one axis
     if periodic[0]:
      
      if padding:
       x_padded   = jnp.pad(x, ((Nx, Nx), (Ny, Ny)), mode='wrap')
       xc         = jnp.linspace(-3*Lx / 2 + d[0] / 2, 3*Lx / 2  - d[0] / 2, 3*Nx)
       yc         = jnp.linspace(-3*Ly / 2 + d[1] / 2, 3*Ly / 2  - d[1] / 2, 3*Ny) 
       centroids  = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
       interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x_padded, method=order)
       grad       = jax.vmap(jax.grad(interp2D))(centroids).T.reshape(2,3*Nx,3*Ny).transpose(0, 2, 1)[:,Nx:2*Nx,Ny:2*Ny]

      else: 
       
       xc         = jnp.linspace(-Lx / 2 + d[0] / 2, Lx / 2  - d[0] / 2, Nx)
       yc         = jnp.linspace(-Ly / 2 + d[1] / 2, Ly / 2  - d[1] / 2, Ny) 
       centroids  = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
       interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x, method=order,period=[Lx,Ly])
       grad       = jax.vmap(jax.grad(interp2D))(centroids).T.reshape(2,Nx,Ny).transpose(0, 2, 1)

     else: 

       xc = jnp.linspace(-Lx / 2 + d[0] / 2, Lx / 2  - d[0] / 2, Nx)
       yc = jnp.linspace(-Ly / 2 + d[1] / 2, Ly / 2  - d[1] / 2, Ny) 
       centroids = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
     
       interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x, method=order)
       grad = jax.vmap(jax.grad(interp2D))(centroids).T.reshape(2,Nx,Ny).transpose(0, 2, 1)

     return grad


def compute_hessian(x,periodic,d,order,padding=True):

     x = x.T

     Nx,Ny = x.shape
     Lx    = Nx * d[0]
     Ly    = Ny * d[1]
  
     if periodic[0]:
         
        if padding: 
         
         x_padded   = jnp.pad(x, ((Nx, Nx), (Ny, Ny)), mode='wrap')
         xc         = jnp.linspace(-3*Lx / 2 + d[0] / 2, 3*Lx / 2  - d[0] / 2, 3*Nx)
         yc         = jnp.linspace(-3*Ly / 2 + d[1] / 2, 3*Ly / 2  - d[1] / 2, 3*Ny) 
         centroids  = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
         interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x_padded, method=order)
         hessian    = jax.vmap(jax.hessian(interp2D))(centroids).reshape(3*Nx,3*Ny,2,2).transpose(2,3,0,1)[:,:,Nx:2*Nx,Ny:2*Ny]

        else:
           
         xc         = jnp.linspace(-Lx / 2 + d[0] / 2, Lx / 2  - d[0] / 2, Nx)
         yc         = jnp.linspace(-Ly / 2 + d[1] / 2, Ly / 2  - d[1] / 2, Ny) 
         centroids  = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
         interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x, method=order)
         hessian    = jax.vmap(jax.hessian(interp2D))(centroids).reshape(Nx,Ny,2,2).transpose(2,3,0,1)

     else:    

        xc = jnp.linspace(-Lx / 2 + d[0] / 2, Lx / 2  - d[0] / 2, Nx)
        yc = jnp.linspace(-Ly / 2 + d[1] / 2, Ly / 2  - d[1] / 2, Ny) 
        centroids = jnp.stack(jnp.meshgrid(xc, yc, indexing='ij'), axis=-1).reshape(-1, 2)
       
        interp2D =   lambda xq: interp2d(xq[0],xq[1],xc,yc, x, method=order)

        hessian = jax.vmap(jax.hessian(interp2D))(centroids).reshape(Nx, Ny, 2, 2).transpose(2, 3, 1, 0)

     return hessian

    

     


# def constraint(needs_filtered: bool = False, epsilon: Callable[[int], float] = lambda x: 0.0):
#     """Utilities for constraint"""

#     def decorator(func):

#         @wraps(func)
#         def wrapper(x):

#             return func(x)

#         wrapper.epsilon = epsilon
#         wrapper.needs_filtered = needs_filtered
#         return wrapper
    
#     return decorator


# def compose_bwd(func):
#     """It adds a custom vjp to func"""
#     #fdiff = custom_vjp(cachable(func))
#     fdiff = custom_vjp(func)

#     def f_fwd(pt,*args):
#      output = fdiff(pt,*args)

#      return output[0],output[1]

#     #@jax.jit
#     def f_bwd(jac, v):
       
#      output = jnp.zeros(jac[list(v[0].keys())[0]].shape[-1])
#      for k,(key,v1) in enumerate(v[0].items()):
#            output  += jnp.einsum('...,...i->i',v1,jac[key])

#      return (output,None)  

#     fdiff.defvjp(f_fwd, f_bwd)

#     return fdiff

# def apply_g_to_f(f, g):
#          """Helper function"""
#          def new_func(a,b):
#           return f(g(a),b)
#          return new_func
    
