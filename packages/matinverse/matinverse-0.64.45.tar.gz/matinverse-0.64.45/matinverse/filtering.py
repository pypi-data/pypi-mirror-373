from jax import numpy as jnp
#from scipy.signal import convolve2d as convolve2d_scipy
from jax.scipy.signal import convolve2d,convolve,fftconvolve
import jax
import numpy as np
import matplotlib.pylab as plt
import time

def PartialSpaceTimeConic2D(geo,spatial_background,spatial_dof,timestamps,R,RT):

    
   C_norm = jnp.linalg.norm(geo.centroids,axis=1)
   N = len(C_norm)
   grid = int(jnp.sqrt(N))
   tmp = C_norm/R
   space_kernel = jnp.where(tmp<1,1-tmp,0).reshape((grid,grid))
   space_kernel /= space_kernel.sum()

   #Time kernel
   mtime       = (jnp.max(timestamps) - jnp.min(timestamps))/2
   NT          = len(timestamps)
   tmp         = jnp.sqrt(jnp.power(timestamps-mtime,2))/RT
   time_kernel = jnp.where(tmp<1,1-tmp,0)
   time_kernel /= time_kernel.sum()
   #-------------------

   kernel      = jnp.einsum('t,ij->tij',time_kernel,space_kernel)

   #Create mask 
   mask = jnp.zeros(N).at[spatial_dof].set(1)
   mask = mask.reshape((grid,grid))
   scale = convolve2d(mask,space_kernel,mode='same', boundary='fill', fillvalue=0)
   scale = jnp.where(scale > 0, 1 / jnp.where(scale > 0, scale, 1), 0)*mask
    
   spatial_background = jnp.tile(spatial_background,(NT,1))

   def convolution(x) :

      x = jnp.zeros((NT,N)).at[:,spatial_dof].set(x.reshape((NT,-1))).reshape((NT,grid,grid))
      result = (jax.scipy.signal.convolve(x, kernel, mode='same',method='fft')*scale[jnp.newaxis,:,:]).reshape((NT,-1)) 

      #x = spatial_background.at[:,spatial_dof].set(x.reshape((NT,-1))).reshape((NT,grid,grid))
      #result = jax.scipy.signal.convolve(x, kernel, mode='same',method='fft').reshape((NT,-1)) 

      return spatial_background.at[:,spatial_dof].set(result[:,spatial_dof]).flatten()


   return convolution


@jax.jit
def convolve_shortcut(x,y):

    return jax.scipy.signal.convolve(x,y,mode='same',method='fft')

@jax.jit
def convolve_periodic(x,y):

    N = x.shape[0]
    x = jnp.pad(x,N,mode='wrap')

    return jax.scipy.signal.convolve(x,y,mode='same')[N:2*N,N:2*N]



def Conic2D(geometry, R, \
                    mask     = [],
                    normalize_at_border = True,
                    FFT = True,
                    ):
    
  
    C_norm = jnp.linalg.norm(geometry.centroids, axis=1)
    grid = np.array(geometry.grid)
    tmp = C_norm / R
    kernel = jnp.where(tmp < 1, 1 - tmp, 0).reshape(grid)


    kernel_shifted_FFT = jnp.fft.fft2(jnp.fft.ifftshift(kernel))

   
    #dx = geometry.size[0]/geometry.grid[0]



    def get_convolve_function():
     
    
     #return lambda x, y: jax.scipy.signal.convolve(x, y, mode='same', method='fft')  
     if geometry.periodic[0] and not geometry.periodic[1]:
        # Periodic in the first axis only
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((grid[0], grid[0]), (0, 0)), mode='wrap'), y, mode='same', method='fft'
        )[grid[0]:2*grid[0], :]

     elif geometry.periodic[1] and not geometry.periodic[0]:
        # Periodic in the second axis only
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((0, 0), (grid[1], grid[1])), mode='wrap'), y, mode='same', method='fft'
        )[:, grid[1]:2*grid[1]]

     elif not geometry.periodic[1] and not geometry.periodic[0]:
        # Non-periodic in both axes
        return lambda x, y: jax.scipy.signal.convolve(x, y, mode='same', method='fft')

     elif geometry.periodic[1] and geometry.periodic[0]:
        
        if FFT: 
         return lambda x, y: jnp.real(jnp.fft.ifft2(jnp.fft.fft2(x) * kernel_shifted_FFT))
        else:
         return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((grid[0], grid[0]), (grid[1], grid[1])), mode='wrap'), y, mode='same', method='fft'
        )[grid[0]:2*grid[0], grid[1]:2*grid[1]]  
 

        #return lambda x, y: jnp.real(jnp.fft.ifft2(jnp.fft.fft2(x) * jnp.fft.fft2(kernel)))
     
        # Periodic in both axes
        #
    convolve = get_convolve_function()

    if len(mask)==0:
       mask = jnp.ones_like(kernel)
    mask  = mask.reshape((grid[0],grid[1]))   

    # Precompute the scaling factor
    if normalize_at_border:
        normalization = convolve(mask,kernel)
        scale = jnp.where( normalization > 0, 1 /  normalization, 0)
    else:
     scale = 1/kernel.sum()

  
    #@jax.jit
    def convolution(x):

        x = x.reshape(grid)
       
        # Perform convolution on the masked input
        output = convolve(x*mask,kernel)

        return jnp.where(mask, output*scale, x)

    return convolution




def Conic3D(geometry, R, \
                      mask     = [],
                      normalize_at_border = True
                      ):
    
  
    C_norm = jnp.linalg.norm(geometry.centroids, axis=1)
    grid = np.array(geometry.grid)
    tmp = C_norm / R
    kernel = jnp.where(tmp < 1, 1 - tmp, 0).reshape(grid)

    kernel_shifted_FFT = jnp.fft.fftn(jnp.fft.ifftshift(kernel))

    #dx = geometry.size[0]/geometry.grid[0]


    def get_convolve_function():
     
    
       
     if geometry.periodic[0] and not geometry.periodic[1] and not geometry.periodic[2]:
        # [1,0,0]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((grid[0], grid[0]), (0, 0),(0, 0)), mode='wrap'), y, mode='same', method='fft'
        )[grid[0]:2*grid[0], :,:]

     elif not geometry.periodic[0] and geometry.periodic[1] and not geometry.periodic[2]:
        # [0,1,0]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((0, 0), (grid[1], grid[1]),(0,0)), mode='wrap'), y, mode='same', method='fft'
        )[:, grid[1]:2*grid[1],:]

     elif not geometry.periodic[0] and not geometry.periodic[1] and not geometry.periodic[2]:
        # [0,0,0]
        
        return lambda x, y: jax.scipy.signal.convolve(x, y, mode='same', method='fft')

     elif geometry.periodic[0] and geometry.periodic[1] and geometry.periodic[2]:
        # [1,1,1]

        return lambda x, y: jnp.real(jnp.fft.ifftn(jnp.fft.fftn(x) *  kernel_shifted_FFT))
        # return lambda x, y: jax.scipy.signal.convolve(
        #     jnp.pad(x, ((grid[0], grid[0]), (grid[1], grid[1]),(grid[2],grid[2])), mode='wrap'), y, mode='same', method='fft'
        # )[grid[0]:2*grid[0], grid[1]:2*grid[1],grid[2]:2*grid[2]]  
     

     elif not geometry.periodic[0] and not geometry.periodic[1] and geometry.periodic[2]:
        # [0,0,1]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((0,0), (0, 0),(grid[2],grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[:,:,grid[2]:2*grid[2]]  
     
     elif not geometry.periodic[0] and geometry.periodic[1] and geometry.periodic[2]:
        # [0,1,1]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((0,0), (grid[1], grid[1]),(grid[2],grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[:,grid[1]:2*grid[1],grid[2]:2*grid[2]]  
     
     elif  geometry.periodic[0] and  not geometry.periodic[1] and geometry.periodic[2]:
        # [1,0,1]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((grid[0],grid[0]), (0, 0),(grid[2],grid[2])), mode='wrap'), y, mode='same', method='fft'
        )[grid[0]:2*grid[0],:,grid[2]:2*grid[2]] 
     
     elif  geometry.periodic[0] and  geometry.periodic[1] and not geometry.periodic[2]:
        # [1,1,0]
        return lambda x, y: jax.scipy.signal.convolve(
            jnp.pad(x, ((grid[0],grid[0]), (grid[1], grid[1]),(0,0)), mode='wrap'), y, mode='same', method='fft'
        )[grid[0]:2*grid[0],grid[1]:2*grid[1],:] 
     
     
 
    convolve = get_convolve_function()

    if len(mask)==0:
       mask = jnp.ones_like(kernel)
    mask  = mask.reshape(grid)   

    # Precompute the scaling factor
    if normalize_at_border:
        normalization = convolve(mask,kernel)
        scale = jnp.where( normalization > 0, 1 /  normalization, 0)
    else:
     scale = 1/kernel.sum()

  

    @jax.jit
    def convolution(x):

        x = x.reshape(grid)
      
        # Perform convolution on the masked input
        output = convolve(x*mask,kernel)
 
        #return jnp.where(mask, output*scale, x).flatten()
        return jnp.where(mask, output*scale, x)

    return convolution




# def Conic3D(geometry, R, \
#                     mask     = [],
#                     normalize_at_border = True
#                     ):
    

  
#     C_norm = jnp.linalg.norm(geometry.centroids, axis=1)
#     grid = np.array(geometry.grid)
#     tmp = C_norm / R
#     kernel = jnp.where(tmp < 1, 1 - tmp, 0).reshape(grid)


#     def get_convolve_function():
    
#         # Non-periodic in both axes
#         return lambda x, y: jax.scipy.signal.convolve(x, y, mode='same', method='fft')

 
#     convolve = get_convolve_function()

#     if len(mask)==0:
#        mask = jnp.ones_like(kernel)
#     mask  = mask.reshape((grid[0],grid[1],grid[2]))   

#     # Precompute the scaling factor
#     if normalize_at_border:
#      normalization = convolve(mask,kernel)
#      scale = jnp.where( normalization > 0, 1 / normalization, 0)
#     else:
#      scale = 1/kernel.sum()
#     # print(scale.shape)

#     @jax.jit
#     def convolution(x):

#         x = x.reshape(grid)
      
#         # Perform convolution on the masked input
#         output = convolve(x*mask,kernel)
 
#         #return jnp.where(mask, output*scale, x).flatten()
#         return jnp.where(mask, output*scale, x).flatten()

#     return convolution



def TimeConic(timestamps,RT):

    NT = len(timestamps)

    mtime = (jnp.max(timestamps) - jnp.min(timestamps))/2

    tmp = jnp.sqrt(jnp.power(timestamps-mtime,2))/RT

    kernel = jnp.where(tmp<1,1-tmp,0)

    if not (jnp.sum(kernel) == 0):
       kernel /= jnp.sum(kernel)

    @jax.jit
    def new(x):
     X = x.reshape((NT,-1))
     X =  jax.vmap(lambda x : jnp.convolve(x,kernel,mode='same'),in_axes=(1,),out_axes = (1))(X)

     return X.flatten()



    return new




def SpaceTimeConic2D(geometry,timestamps,R,RT):

    N = int(np.sqrt(geometry.iNDOFs))
    NT = len(timestamps)

    tmp = jnp.linalg.norm(geometry.centroids,axis=1)/R
    space_kernel = jnp.where(tmp<1,1-tmp,0).reshape((N,N))

    mtime = (jnp.max(timestamps) - jnp.min(timestamps))/2
    tmp = jnp.sqrt(jnp.power(timestamps-mtime,2))/RT
    time_kernel = jnp.where(tmp<1,1-tmp,0)
    time_kernel /= time_kernel.sum()
    space_kernel /= space_kernel.sum()
    
    kernel = jnp.einsum('t,ij->tij',time_kernel,space_kernel)


    #if not (jnp.sum(kernel) == 0):
    #  kernel /= jnp.sum(kernel)

    #@jax.jit
    def new(x):
     x = x.reshape((NT, N, N))
     #padded_x = jnp.pad(x,N, mode='wrap')
     #print(x.shape)
     #quit()
     #result = jax.scipy.signal.convolve(padded_x, kernel, mode='same', method='fft')

     #x_padded = jnp.pad(x,, mode='wrap')

     #quit()

     #padded_x = jax.vmap(lambda x: jnp.pad(x,N,mode='wrap'),in_axes=(0,),out_axes=(0))(x)
       
     #result = convolve(jnp.ones_like(padded_x), kernel, mode='same', method='fft')[:,N:2*N,N:2*N]

     #x_padded = jnp.pad(x,N,mode='wrap')
     #result = convolve(x_padded,kernel,mode='same', method='fft')#[N:N+NT,N:2*N,N:2*N]


     result = convolve(x,kernel, mode='same',method='fft')

     #result =  (jax.vmap(lambda x : convolve2d(x,space_kernel,mode='same', boundary='fill', fillvalue=0),in_axes=(0,),out_axes = (0))(x)).flatten()

     #jax.debug.print("{x}",x=result.shape)
     #jax.debug.print("{x}",x=jnp.max(x_padded))
     #jax.debug.print("{x}",x=jnp.min(x_padded))
     #quit()
     return result.flatten()#[N:N+NT, N:2*N, N:2*N].flatten()
     



    return new







