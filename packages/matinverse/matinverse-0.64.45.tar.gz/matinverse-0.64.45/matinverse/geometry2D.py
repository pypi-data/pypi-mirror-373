import equinox as eqx
import jax
from jax import numpy as jnp
import matplotlib.pylab as plt
from typing import List,Callable
import time
import numpy as np
from functools import partial
from typing import List
import msgpack
import msgpack_numpy as m



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

class Geometry2D(eqx.Module):

   
   
    N                  : int
    nDOFs              : int
    size               : List
    grid               : List
    dim                : int = 2
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


    def __init__(self,grid,size,periodic=[False,False],\
                 domain = None,mask=[]):
        """i: y coordinate (top to down) 
           j: x coordinate (left to right)
           Follow imshow conventions:
             A[i,j] address the pixel whose centroid is at y = size[1]-i*DY - DY/2 and x = -size[0]/2 + DX/2 + j*DX
        """

        self.grid = grid
        self.size = size
        DY      = self.size[0]/self.grid[0]
        DX      = self.size[1]/self.grid[1]
        V       = DX*DY
        self.N       = grid[0]*grid[1] 
        self.periodic = periodic
      
        
        i,j = np.indices(grid)  
        k_center     =   j    % grid[1] +  ( i       % grid[0]) * grid[1] 
        k_left       =  (j-1) % grid[1] +  ( i       % grid[0]) * grid[1]
        k_right      =  (j+1) % grid[1] +  ( i       % grid[0]) * grid[1]
        k_down       =   j    % grid[1] +  ((i + 1)  % grid[0]) * grid[1]
        k_up         =   j    % grid[1] +  ((i - 1)  % grid[0]) * grid[1] 
        k_up_left    =  (j-1) % grid[1] +  ((i - 1)  % grid[0]) * grid[1]
        k_up_right   =  (j+1) % grid[1] +  ((i - 1)  % grid[0]) * grid[1]
        k_down_left  =  (j-1) % grid[1] +  ((i + 1)  % grid[0]) * grid[1]
        k_down_right =  (j+1) % grid[1] +  ((i + 1)  % grid[0]) * grid[1]

        # Compute the centroids of the elements
        centroids_x = -self.size[1] / 2 + DX / 2 + j * DX
        centroids_y =  self.size[0] / 2 - DY / 2 - i * DY
        centroids   = jnp.stack((centroids_x, centroids_y), axis=-1).reshape(-1, 2)

        
        

         
        #Setting up maps----------------
        #The initial mask is in case there a map is provided
        if len(mask) > 0:
         self.mask = mask.reshape(grid[0]*grid[1]) 
        else:
         self.mask = jnp.ones(grid[0]*grid[1],dtype=bool)
         
        if domain:
         self.mask = np.logical_and(jax.vmap(domain)(centroids),self.mask)
        self.mask = self.mask.reshape(grid)
        #------
        self.nDOFs = np.count_nonzero(self.mask)

        self.local2global = self.mask.flatten().nonzero()[0]
        self.global2local = jnp.zeros(self.N,dtype=int).at[self.local2global].set(jnp.arange(self.nDOFs))
      
       
        #Shift along second axis (x) [right]
        mask = np.logical_and(self.mask,shift(self.mask,-1,1, fill_value=True if periodic[0] else False))  
        

        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((k_center[mask],k_right[mask])).T
     

        face_centroids  = jnp.stack((            -size[0]/2+(j[mask]+1)*DX,\
                                                  size[1]/2-i[mask]*DY-DY/2), axis=-1).reshape(-1, 2)
              
        areas =                                   DY    * jnp.ones(Nm)
        dists =                                   DX    * jnp.ones(Nm)
        normals =                                 jnp.tile(jnp.array([1, 0]),(Nm,1))

        #Compute 

        #Shift along first axis (y) [down]
        mask = np.logical_and(self.mask,shift(self.mask,-1,0, fill_value=True if periodic[0] else False))
   
        Nm = np.count_nonzero(mask)
        smap = jnp.vstack((smap,jnp.vstack((k_center[mask],k_down[mask])).T))
       

        face_centroids  = jnp.vstack(          (face_centroids,jnp.stack((             -size[0]/2 + DX/2 + j[mask]*DX,\
                                                size[1]/2-(i[mask]+1)*DY), axis=-1).reshape(-1, 2)))
        
        areas   = jnp.concatenate((areas,DX    * jnp.ones(Nm)))
        dists   = jnp.concatenate((dists,DY    * jnp.ones(Nm))) 
        normals = jnp.vstack((normals,jnp.tile(jnp.array([0, -1]),(Nm,1))))


        #Boundary right
        #Create a mask that is true only for the elements hosting a boundary
        I_horizontal = shift(self.mask,shift=-1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I_horizontal))
        if periodic[0]: mask[:,-1] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.where((j[mask]==grid[1]-1)[:, None] ,centroids[k_center[mask]] + jnp.array([DX/2, 0]),(centroids[k_center[mask]] + centroids[k_right[mask]])/2)
        boundary_sides   =  k_center[mask]
        boundary_areas   =  DY * jnp.ones(Nm)
        boundary_dists   =  DX/2 * jnp.ones(Nm)
        boundary_normals =  jnp.tile(jnp.array([1, 0]),(Nm,1))


        #Boundary left
        #Create a mask that is true only for the elements hosting a boundary
        I_horizontal = shift(self.mask,shift=1,axis=1)
        mask   = np.logical_and(self.mask,np.logical_not(I_horizontal))
        if periodic[0]: mask[:,0] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((j[mask]==0)[:, None] ,centroids[k_center[mask]] - jnp.array([DX/2, 0]),(centroids[k_center[mask]] + centroids[k_left[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DY * jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DX/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ -1, 0]),(Nm,1))),axis=0)


        #Boundary bottom
        I_vertical = shift(self.mask,shift=-1,axis=0)
        mask   = np.logical_and(self.mask,np.logical_not(I_vertical))
        if periodic[1]: mask[-1,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((i[mask]==grid[0]-1)[:, None] ,centroids[k_center[mask]] - jnp.array([0,DY/2]),(centroids[k_center[mask]] + centroids[k_down[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([0, -1]),(Nm,1))),axis=0)


        #Boundary top
        I_vertical = shift(self.mask,shift=1,axis=0)
        mask   = np.logical_and(self.mask,np.logical_not(I_vertical))
        if periodic[1]: mask[0,:] = False
        Nm = np.count_nonzero(mask)         
        boundary_centroids = jnp.vstack((boundary_centroids,jnp.where((i[mask]==0)[:, None] ,centroids[k_center[mask]] + jnp.array([0,DY/2]),(centroids[k_center[mask]] + centroids[k_up[mask]])/2)))
        boundary_sides   = jnp.concatenate((boundary_sides,k_center[mask]))
        boundary_areas   = jnp.concatenate((boundary_areas, DX * jnp.ones(Nm)))
        boundary_dists   = jnp.concatenate((boundary_dists, DY/2 * jnp.ones(Nm)))
        boundary_normals = jnp.concatenate((boundary_normals,jnp.tile(jnp.array([ 0,1]),(Nm,1))),axis=0)



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
     

    def plot(self):
        
         xc = jnp.linspace(-self.size[0]/2,self.size[0]/2,self.grid[0]+1)
         plt.vlines(xc,ymin=-self.size[1]/2,ymax = self.size[1]/2,colors='g')

         yc = jnp.linspace(-self.size[1]/2,self.size[0]/2,self.grid[1]+1)
         plt.hlines(yc,xmin=-self.size[0]/2,xmax = self.size[0]/2,colors='g')
         plt.gca().axis('equal')
         
         #Elem centroids
         #for p in centroids:
         #    plt.scatter(p[0],p[1],color='k')

         # # #Face centroids
         # for p in face_centroids:
         #      plt.scatter(p[0],p[1],color='b')
        
         # for p in boundary_centroids:
         #   plt.scatter(p[0],p[1],color='c')

         #for p in boundary_sides:
         #  plt.scatter(centroids[p][0],centroids[p][1],color='r')  

        

      
         # #Boundary map
         #for a in bmap:
             
         #     c1 = centroids[a[0]]
         #     c2 = centroids[a[1]]
         #     plt.plot([c1[0],c2[0]],[c1[1],c2[1]],'r')
         #     plt.scatter(c2[0],c2[1],color='r')

         #Side map
         for a in self.smap:
             c1 = self.centroids[a[0]]
             c2 = self.centroids[a[1]]
             
             plt.plot([c1[0],c2[0]],[c1[1],c2[1]],'orange')

         
         #data = I.reshape(extended_grid).T
         # 
         #ax = plt.imshow(data,extent=[-extended_size[0]/2,extended_size[0]/2,-extended_size[1]/2,extended_size[1]/2],cmap='Oranges')
       
         plt.xlim([-self.size[0]/2,self.size[0]/2])
         plt.ylim([-self.size[1]/2,self.size[1]/2])
         plt.axis('off')
        
         plt.ioff()   
         plt.show()


    def select_boundary(self,func):
        """Get select boundaries""" 

        if isinstance(func,str):
           if   func == 'left':
                func = lambda p  : jnp.isclose(p[0], -self.size[0]/2)
           elif func == 'right':   
                func = lambda p  : jnp.isclose(p[0], self.size[0]/2)
           elif func == 'bottom':   
                func = lambda p  : jnp.isclose(p[1], -self.size[1]/2)
           elif func == 'top':   
                func = lambda p  : jnp.isclose(p[1], self.size[1]/2)               
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


