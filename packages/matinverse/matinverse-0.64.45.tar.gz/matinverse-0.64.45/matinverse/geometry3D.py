import equinox as eqx
import jax
from jax import numpy as jnp
import matplotlib.pylab as plt
from typing import List,Callable
import time
import numpy as np
from functools import partial
from typing import List


def shift(arr, shift, axis, fill_value=False):
    arr = np.asarray(arr)
    result = np.full_like(arr, fill_value)

    if shift == 0:
        return arr.copy()

    src = [slice(None)] * arr.ndim
    dst = [slice(None)] * arr.ndim

    if shift > 0:
        src[axis] = slice(0, -shift)
        dst[axis] = slice(shift, None)
    else:
        src[axis] = slice(-shift, None)
        dst[axis] = slice(0, shift)

    result[tuple(dst)] = arr[tuple(src)]
    return result

class Geometry3D(eqx.Module):
    """
   3D Finite Volume Geometry Class
   
   Coordinate convention:
   - i: x-axis (left → right)
   - j: y-axis (back → front, with j-flip for intuitive ordering)  
   - k: z-axis (bottom → top)
   
   User input: grid=[nx, ny, nz], size=[Lx, Ly, Lz]
   Internal: self.grid=[nz, ny, nx] for k,j,i indexing
   """

   
   
    N                  : int
    nDOFs              : int
    size               : List
    grid               : List
    dim                : int = 3
    mask               : jax.Array
    V                  : float = 1
    boundary_centroids : jax.Array
    boundary_normals   : jax.Array
    boundary_sides     : jax.Array
    boundary_areas     : jax.Array
    boundary_dists     : jax.Array
    smap               : jax.Array
    normals            : jax.Array
    centroids          : jax.Array
    face_centroids     : jax.Array
    areas              : jax.Array
    dists              : jax.Array
    local2global       : jax.Array
    global2local       : jax.Array
    periodic           : List


    def __init__(self,grid,size,periodic=[False,False,False],\
                 domain = None):
      
        # User specifies grid = [grid_x, grid_y, grid_z]
        # But internal system needs [grid_z, grid_y, grid_x] for k,j,i indexing
        self.grid = [grid[2], grid[1], grid[0]]  # Reorder: [z, y, x]
        self.size = size
        DX      = self.size[0]/self.grid[2]  # x uses grid[2] (which is original grid_x)
        DY      = self.size[1]/self.grid[1]  # y uses grid[1] (which is original grid_y) 
        DZ      = self.size[2]/self.grid[0]  # z uses grid[0] (which is original grid_z)
        V       = DX*DY*DZ
        self.N       = self.grid[0]*self.grid[1]*self.grid[2] 
        self.periodic = periodic
      
        
        k,j,i = np.indices(self.grid)  
      

        # Flip j indices so y goes from back (low values) to front (high values)
        #j = self.grid[1] - 1 - j

        #i = x [left -> right]
        #j = y [back -> front] (low to high values)
        #k = z [bottom -> top]

       
        k_center  =  i     % self.grid[2]  +   (j       % self.grid[1]) * self.grid[2]   + (k         % self.grid[0]) * (self.grid[1] * self.grid[2]) 
        k_left    = (i-1)  % self.grid[2]  +   (j       % self.grid[1]) * self.grid[2]   + (k         % self.grid[0]) * (self.grid[1] * self.grid[2]) 
        k_right   = (i+1)  % self.grid[2]  +   (j       % self.grid[1]) * self.grid[2]   + (k         % self.grid[0]) * (self.grid[1] * self.grid[2])
        k_back   =   i     % self.grid[2]  +   ((j - 1) % self.grid[1]) * self.grid[2]   + (k         % self.grid[0]) * (self.grid[1] * self.grid[2])
        k_front   =  i     % self.grid[2]  +   ((j + 1) % self.grid[1]) * self.grid[2]   + (k         % self.grid[0]) * (self.grid[1] * self.grid[2])
        k_bottom  = (i     % self.grid[2]) +   (j       % self.grid[1]) * self.grid[2]   + ((k - 1)   % self.grid[0]) * (self.grid[1] * self.grid[2])
        k_top     = (i     % self.grid[2]) +   (j       % self.grid[1]) * self.grid[2]   + ((k + 1)   % self.grid[0]) * (self.grid[1] * self.grid[2])

       
        
        # Compute the centroids of the elements
        centroids_x = -self.size[0] / 2 + DX / 2 + i * DX
        centroids_y = -self.size[1] / 2 + DY / 2 + j * DY
        centroids_z = -self.size[2] / 2 + DZ / 2 + k * DZ
        centroids   = jnp.stack((centroids_x, centroids_y,centroids_z), axis=-1).reshape(-1, 3)

        #Setting up maps----------------
        self.mask = jnp.ones(self.grid[0]*self.grid[1]*self.grid[2],dtype=bool)
        if domain:
         self.mask = np.logical_and(jax.vmap(domain)(centroids),self.mask)
        self.mask = self.mask.reshape(self.grid)

      

        #------
        self.nDOFs = np.count_nonzero(self.mask)

        self.local2global = self.mask.flatten().nonzero()[0]
        self.global2local = jnp.zeros(self.N,dtype=int).at[self.local2global].set(jnp.arange(self.nDOFs))
      
       
        #Shift along x (right)
        mask = np.logical_and(self.mask,shift(self.mask,-1,2, fill_value=True if periodic[0] else False))  
 

        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((k_center[mask],k_right[mask])).T

       

        #face centroids
        face_centroids  = jnp.stack((            -self.size[0]/2   +(i[mask]+1)*DX,\
                                                 -self.size[1]/2   + j[mask]*DY+DY/2,\
                                                 -self.size[2]/2   + k[mask]*DZ +DZ/2), axis=-1).reshape(-1, 3)
        
              
        areas =                                   DY * DZ  * jnp.ones(Nm)
        dists =                                   DX      * jnp.ones(Nm)
        normals =                                 jnp.tile(jnp.array([1, 0, 0]),(Nm,1))
       

        #Shift along the second axis (y) [front]
        mask = np.logical_and(self.mask,shift(self.mask,-1,1, fill_value=True if periodic[1] else False))

        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((smap,jnp.vstack((k_center[mask],k_front[mask])).T))

     
      

        face_centroids  = jnp.vstack((face_centroids,jnp.stack((             -self.size[0]/2 + i[mask]* DX + DX/2,\
                                                                             -self.size[1]/2 + (j[mask]+1)*DY ,\
                                                                             -self.size[2]/2 + k[mask]*DZ + DZ/2), axis=-1).reshape(-1, 3)))

        
        areas   = jnp.concatenate((areas,DX*DZ    * jnp.ones(Nm)))
        dists   = jnp.concatenate((dists,DY       * jnp.ones(Nm))) 
        normals = jnp.vstack((normals,jnp.tile(jnp.array([0, 1, 0 ]),(Nm,1))))


        #Moving top (k)
        mask = np.logical_and(self.mask,shift(self.mask,-1,0, fill_value=True if periodic[2] else False))
        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((smap,jnp.vstack((k_center[mask],k_top[mask])).T))

        face_centroids  = jnp.vstack((face_centroids,jnp.stack(( -self.size[0]/2 + i[mask]*DX + DX/2,\
                                                                 -self.size[1]/2 + j[mask]*DY + DY/2,\
                                                                 -self.size[2]/2 + (k[mask]+1)*DZ), axis=-1).reshape(-1, 3)))

        areas = jnp.concatenate((areas,DX*DY * jnp.ones(Nm)))
        dists = jnp.concatenate((dists,DZ    * jnp.ones(Nm)))

        normals = jnp.vstack((normals,jnp.tile(jnp.array([0,0,1]),(Nm,1))))

        
        #Boundary right
        #Create a mask that is true only for the elements host a boundary
        I      = shift(self.mask,shift=-1,axis=2)
        mask   = np.logical_and(self.mask,np.logical_not(I))

        if periodic[0]: mask[:,:,-1] = False
        Nm = np.count_nonzero(mask)  
        boundary_centroids = jnp.where((i[mask]==self.grid[2]-1)[:, None] ,centroids[k_center[mask]] + jnp.array([DX/2,0,0]),(centroids[k_center[mask]] + centroids[k_right[mask]])/2)
        boundary_sides   =  k_center[mask]
        boundary_areas   =  DY * DZ * jnp.ones(Nm)
        boundary_dists   =  DX/2    * jnp.ones(Nm)
        boundary_normals =  jnp.tile(jnp.array([1,0,0]),(Nm,1))

        


        #Boundary left
        I = shift(self.mask,shift=1,axis=2)   
        mask   = np.logical_and(self.mask,np.logical_not(I))
         
        if periodic[0]: mask[0,:,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((i[mask]==0)[:, None] ,centroids[k_center[mask]] - jnp.array([DX/2,0,0]),(centroids[k_center[mask]] + centroids[k_left[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DY * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DX/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ -1,0,0]),(Nm,1))),axis=0)


  
        #Boundary front
        I = shift(self.mask,shift=-1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,0,:] = False
        Nm = np.count_nonzero(mask)         
        
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((j[mask]==grid[1]-1)[:, None] ,centroids[k_center[mask]] + jnp.array([0,DY/2,0]),(centroids[k_center[mask]] + centroids[k_front[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,1,0]),(Nm,1))),axis=0)

        #Boundary back
        I = shift(self.mask,shift=1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[1]: mask[:,-1,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((j[mask]==0)[:, None] ,centroids[k_center[mask]] - jnp.array([0,DY/2,0]),(centroids[k_center[mask]] + centroids[k_back[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DZ* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,-1,0]),(Nm,1))),axis=0)

        

        #Boundary top
        I = shift(self.mask,shift=-1,axis=0)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[2]: mask[:,:,-1] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((k[mask]==self.grid[0]-1)[:, None] ,centroids[k_center[mask]] + jnp.array([0,0,DZ/2]),(centroids[k_center[mask]] + centroids[k_top[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DY* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DZ/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,0,1]),(Nm,1))),axis=0)

        #Boundary bottom
        I = shift(self.mask,shift=1,axis=0)
        mask   = np.logical_and(self.mask,np.logical_not(I))
        if periodic[2]: mask[:,:,0] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((k[mask]==0)[:, None] ,centroids[k_center[mask]] - jnp.array([0,0,DZ/2]),(centroids[k_center[mask]] + centroids[k_bottom[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * DY* jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DZ/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,0,-1]),(Nm,1))),axis=0)


        self.boundary_centroids = boundary_centroids
        self.boundary_normals = boundary_normals 
        self.boundary_areas = boundary_areas 
        self.boundary_dists = boundary_dists 
        self.smap = self.global2local[smap]
        self.boundary_sides = self.global2local[boundary_sides]
        self.normals = normals 
        self.centroids = centroids[self.mask.flatten()]
        self.face_centroids = face_centroids 
        self.areas = areas 
        self.dists = dists 
        self.V = V
     

    def select_boundary(self,func):
        """Get select boundaries""" 

        if isinstance(func,str):
           if   func == 'left':
                func = lambda p  : jnp.isclose(p[0], -self.size[0]/2)
           elif func == 'right':   
                func = lambda p  : jnp.isclose(p[0], self.size[0]/2)
           elif func == 'front':   
                func = lambda p  : jnp.isclose(p[1],  self.size[1]/2)
           elif func == 'back':   
                func = lambda p  : jnp.isclose(p[1], -self.size[1]/2)   
           elif func == 'bottom':   
                func = lambda p  : jnp.isclose(p[2], -self.size[2]/2)
           elif func == 'top':   
                func = lambda p  : jnp.isclose(p[2], self.size[2]/2)               
           elif func == 'everywhere':   
                return jnp.arange(len(self.boundary_centroids))
        
        
        #return jax.vmap(func)(self.boundary_centroids).nonzero()[0]
        return func(self.boundary_centroids.T).nonzero()[0]
      
          
    
    def compute_function(self,func):
       """Get select boundaries""" 

       return func(self.centroids.T)
    
    def select_internal_boundary(self,func):
       """Get select boundaries""" 

       return func(self.face_centroids.T).nonzero()[0]


    def cell2side(self,func):

        return partial(func,i=self.smap[:,0],j=self.smap[:,1])
    
   
