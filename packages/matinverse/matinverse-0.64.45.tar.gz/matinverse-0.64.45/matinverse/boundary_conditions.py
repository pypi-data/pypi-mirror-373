import equinox as eqx
import jax
from jax import numpy as jnp
from matinverse import Geometry2D,Geometry3D
import numpy as np
from functools import partial
from dataclasses import dataclass,field
from typing import Callable
#from jaxopt import FixedPointIteration




@partial(jax.tree_util.register_dataclass,
          data_fields=['default_flux','temp_funcs','flux_funcs','flux_corr','temp_corr','robin_corr','remaining','temp_robin_funcs','robin_funcs','periodic_funcs','temp_indices','flux_indices','robin_indices','periodic_indices','geo'],
          meta_fields=['n_bcs'])
@dataclass
class BoundaryConditions:
    """Class to handle boundary conditions for a heat conduction solver.

    :param default_flux: A callable function that returns the default flux value.
      

    """


    geo:                       Geometry2D | Geometry3D
    n_bcs:                     int = 1
    default_flux:              Callable = lambda batch, x, t, Tb: 0.0
    temp_funcs:                list = field(default_factory=lambda :[])
    flux_funcs:                list = field(default_factory=lambda :[]) 
    temp_robin_funcs:          list = field(default_factory=lambda :[])
    robin_funcs:               list = field(default_factory=lambda :[])
    periodic_funcs:            list = field(default_factory=lambda :[])
    robin_indices:             np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    temp_indices:              np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    flux_indices:              np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    flux_corr:                 np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    robin_corr:                np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    temp_corr:                 np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    remaining:                 np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    periodic_indices:          np.ndarray = field(default_factory=lambda :jnp.empty((0,), jnp.int32))
    

    def periodic(self,direction,periodic_func):
       
        if direction == 'x':
            func = lambda p  : jnp.isclose(p[0],self.geo.size[0]/2)
        elif  direction == 'y' :    
            func = lambda p  : jnp.isclose(p[1],-self.geo.size[1]/2)
        elif  direction == 'z' :
            func = lambda p  : jnp.isclose(p[2],self.geo.size[2]/2)    
        else:
            raise ValueError("Direction must be 'x', 'y', or 'z'.")    
        
        inds = self.geo.select_internal_boundary(func)
        

        test_func = lambda batch,t:jax.vmap(lambda s:periodic_func(batch,s, t))(inds)
        self.periodic_funcs.append(test_func)

      
        self.periodic_indices = jnp.concatenate((self.periodic_indices,inds))

    def get_periodic(self,b,t):
        
      
        values = jnp.empty((0,), jnp.float32)  # Initialize as a 1D array with 0 elements
        for func in self.periodic_funcs:
            values = jnp.concatenate((values,func(b,t)),axis=0)

        return self.periodic_indices,values
    
        
    def temperature(self,geometry_func,temp_func):
        
        inds = self.geo.select_boundary(geometry_func)

        self.temp_corr = jnp.concatenate((self.temp_corr,len(self.temp_funcs)*jnp.ones(len(inds),dtype=int)))        
    
        self.temp_funcs.append(temp_func)

        self.temp_indices = np.concatenate((self.temp_indices,inds))
        if len(self.remaining) == 0:
            self.remaining = np.arange(len(self.geo.boundary_sides))
        self.remaining = np.setdiff1d(self.remaining, self.temp_indices) 

        return inds

        
       


    def robin(self,geometry_func,robin_func):
    
        inds = self.geo.select_boundary(geometry_func)

        self.robin_corr = jnp.concatenate((self.robin_corr,len(self.robin_funcs)*jnp.ones(len(inds),dtype=int)))
        
        self.robin_funcs.append(robin_func)

        self.robin_indices = np.concatenate((self.robin_indices,inds))
        if len(self.remaining) == 0:
            self.remaining = np.arange(len(self.geo.boundary_sides))
        self.remaining = np.setdiff1d(self.remaining, self.robin_indices)  

        #return inds
  

    def get_temperature_sides(self):

          return self.temp_indices
    

    def get_robin_sides(self):

          return self.robin_indices
 
    def get_robin_values(self, b, s,t):
      
     if len(self.robin_corr) == 0:
         return 0,0
     
     return jax.lax.switch(self.robin_corr[s],self.robin_funcs, b, s, t)

    def get_temperature_values(self, b, s,t):
      
    
     if len(self.temp_corr) == 0:
         return 0
     
     return jax.lax.switch(self.temp_corr[s],self.temp_funcs, b, s, t)
    
            
    
    def flux(self,geometry_func,flux_func):

        #Get the geometry 
        inds = self.geo.select_boundary(geometry_func)

        self.flux_corr = jnp.concatenate((self.flux_corr,len(self.flux_funcs)*jnp.ones(len(inds),dtype=int)))

        self.flux_funcs.append(flux_func)

        self.flux_indices = np.concatenate((self.flux_indices,inds))

        if len(self.remaining) == 0:
            self.remaining = np.arange(len(self.geo.boundary_sides))

        self.remaining = np.setdiff1d(self.remaining, self.flux_indices) 

        #return inds


    def get_flux_sides(self):

          return jnp.concatenate((self.flux_indices,self.remaining))

   
    def get_flux_values(self, b, s,t,Tb):
     
     num_flux_funcs = len(self.flux_funcs)
    
     #def zero_flux_func(b, s, t,Tb):
     #   return 0.

   
     # Combine all functions into a tuple for jax.lax.switch
     all_funcs = tuple(self.flux_funcs + [self.default_flux])

     if len(self.flux_corr) > 0:
      
      index = jnp.where(s < len(self.flux_corr), self.flux_corr[s], num_flux_funcs)
     else:
      index = num_flux_funcs 

     #jax.debug.print("🤯 {x} 🤯", x=index)
 

     # Use jax.lax.switch to select the correct function
     return jax.lax.switch(index, all_funcs, b, s, t,Tb)
            

     

    def get_robin(self,t,T):

        #Concatenate functions
        temperatures =  jnp.empty((self.n_bcs,0), jnp.float32)
        conductances =  jnp.empty((self.n_bcs,0), jnp.float32)
        for func in self.temp_robin_funcs:
            temperatures = jnp.concatenate((temperatures,func(t)),axis=1)

        for func in self.cond_robin_funcs:
            conductances = jnp.concatenate((conductances,func(t,T)),axis=1)

           
        return self.robin_indices,temperatures,conductances
    