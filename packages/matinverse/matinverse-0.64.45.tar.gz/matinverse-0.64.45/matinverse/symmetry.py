import numpy as np
from jax import numpy as jnp
import jax

def eight_fold_symmetry(x):
    x1 = x
    x2 = jnp.rot90(x, 1)          # Rotate 90 degrees
    x3 = jnp.rot90(x, 2)          # Rotate 180 degrees
    x4 = jnp.rot90(x, 3)          # Rotate 270 degrees
    x5 = jnp.flipud(x)            # Flip vertically
    x6 = jnp.flipud(jnp.rot90(x, 1))  # Flip vertically and rotate 90 degrees
    x7 = jnp.flipud(jnp.rot90(x, 2))  # Flip vertically and rotate 180 degrees
    x8 = jnp.flipud(jnp.rot90(x, 3))  # Flip vertically and rotate 270 degrees

    return 0.125 * (x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8)


def four_fold_symmetry(x):
    x1 = x
    x2 = jnp.flipud(x)
    x3 = jnp.fliplr(x)
    x4 = jnp.flipud(jnp.fliplr(x))

    return 0.25 * (x1 + x2 + x3 + x4)


def get_symmetry(geo,sym):

   N = geo.grid[0]
   def preprocess(x):

       return x.reshape((N,N))

   
   if sym == '8-fold':
      return lambda x:eight_fold_symmetry(preprocess(x))
   
   if sym == '4-fold':
      return  lambda x:four_fold_symmetry(preprocess(x))
   
   #elif sym == None:
   #     return N,lambda x:x
   
   else:
        raise f'Symmetry not recognized: {sym}'
        
      
