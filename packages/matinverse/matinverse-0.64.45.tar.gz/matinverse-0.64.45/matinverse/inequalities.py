from jax import numpy as jnp
from functools import partial,update_wrapper
import jax
from dataclasses import dataclass,field
from typing import Callable
from matinverse.filtering import Conic2D
from matinverse.projection import projection
from matinverse.utils import compute_gradient
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class ZeroDerivative:

     NT                 : int
     t0                 : int
     I_spatial_dof      : np.ndarray
     needs_filtered     : bool = field(default=False, init=False)
     #n_constraints      : int  = field(default=1, init=False)
     epsilon            : Callable[[int], float] = field(default=lambda x: 0.0)

     def __call__(self,x):
         
      @jax.jit
      def zeroderivative(x):
          x = x.reshape((self.NT,-1))
          g = jnp.mean(jnp.power(jnp.diff(x[self.t0:,self.I_spatial_dof],axis=0),2))
          #g = jnp.diff(x[self.t0:,:],axis=0).sum()
          value = jnp.array([g])

          return value,(value,None)

      return zeroderivative(x)

def volume_fraction(minp,maxp):
     
      @jax.jit
      def func(x):

       V = jnp.sum(x)
       N  = len(x)
       p  = V/N

       values = []

       values.append(minp/p-1)
       values.append(1-maxp/p)

       return jnp.array(values),({'Volume':[p]},None)

      return func

    

def get_conic_radius_from_eta_e(L,eta_e):

 if (eta_e >= 0.5) and (eta_e < 0.75):
        return L / (2 * jnp.sqrt(eta_e - 0.5))
 elif (eta_e >= 0.75) and (eta_e <= 1):
        return L / (2 - 2 * jnp.sqrt(1 - eta_e))
 else:
        raise ValueError(
            "The erosion threshold point (eta_e) must be between 0.5 and 1."
        )
 



def lengthscale(geo,Ls,SSP2=False,gradient_order_lengthscale='linear',gradient_order_projection='linear',hessian_order='cubic2',padding=True):
      """
      param: Ls is the lenghscale in physical units
      """
     
      #We follow this approach:
      #https://opg.optica.org/oe/fulltext.cfm?uri=oe-29-15-23916&id=453270
      #https://github.com/NanoComp/meep/blob/master/python/adjoint/filters.py
      #Zhou, M., Lazarov, B. S., Wang, F., & Sigmund, O. (2015). Minimum length scale in topology optimization by
      #geometric constraints. Computer Methods in Applied Mechanics and Engineering, 293, 266-282.

      eta_e = 0.75

      dx = geo.size[0]/geo.grid[0]
      dy = geo.size[1]/geo.grid[1]

      resolution = 1/dx

      c0    = 64 * Ls**2

      R = get_conic_radius_from_eta_e(Ls,eta_e)

      filtering = Conic2D(geo,R)
    
      # if gradient_order == 'linear':
      #   compute_gradient = compute_gradient_linear
      # elif gradient_order == 'cubic':
      #   compute_gradient = compute_gradient_cubic
      # else:   
      #   raise ValueError("gradient_order must be 'linear' or 'cubic'.")


      #@jax.jit
      def func(x,beta,epsilon=1e-8):

       
        #Compute gradient
        filtered_field  = filtering(x)
        #gradient_filtered_field = jnp.gradient(filtered_field)
        #grad_mag = ((gradient_filtered_field[0]/dx) ** 2 + (gradient_filtered_field[1]/dy)**2) #1/m^2

        gradient_filtered_field = compute_gradient(filtered_field,geo.periodic,(dx,dy),order=gradient_order_lengthscale,padding=padding)

        grad_mag = ((gradient_filtered_field[0]) ** 2 + (gradient_filtered_field[1])**2) #1/m^2

       
        common = jnp.exp(-c0*grad_mag)#.flatten()

 
        #This is flatten (TO CHANGE)
        projected_field = projection(filtered_field,beta=beta,resolution=resolution,SSP2=SSP2,gradient_order=gradient_order_projection,hessian_order=hessian_order,periodic=geo.periodic,padding=padding)
       
       
        #solid
        Is  = projected_field*common

        
        Is2 = jnp.minimum(filtered_field - eta_e, 0)**2

        Is3 = Is*Is2



        Ls  = jnp.mean(Is3)

        #void
        Iv    = (1-projected_field)*common
        eta_d = 1-eta_e
        Iv2   = jnp.minimum(eta_d - filtered_field, 0)**2
        Iv3   = Iv*Iv2
        Lv    = jnp.mean(Iv3)

       
        constraint = jnp.array([Ls,Lv])/epsilon-1

        #return constraint,({'Ls':constraint},{'Violation_S':Is3,'gradient':Is,'Is2':Is2})
        return constraint,({'Ls':constraint},{})
      
      return func

