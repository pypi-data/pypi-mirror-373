import gdspy
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure
import matplotlib.pylab as plt
import time
from matinverse import IO


def WriteVTK(geo,variables,filename='output.vtk',batch_size=1):
  
       
       grid = np.array(geo.grid)
       size = np.array(geo.size)
      
       n_nodes = np.prod(grid+1)
       n_elems = np.prod(grid)
       dim     = len(grid)
       #-----------------
       x = np.linspace(-size[0]/2,size[0]/2,grid[0]+1)
       y = np.linspace(-size[1]/2,size[1]/2,grid[1]+1)
       z = np.linspace(-size[2]/2,size[2]/2,grid[2]+1)

       # Create 3D grid of points
       X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

       # Flatten the grids to get a list of points
       nodes = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T

       nx,ny,nz = grid+1
    
       i, j, k = np.meshgrid(np.arange(nx-1), np.arange(ny-1), np.arange(nz-1), indexing='ij')
  
    
       base = k * ny * nz + j * nx + i
       voxels = np.stack([
          base,
          base + 1,
          base + nz,
          base + nz + 1,
          base + ny * nz,
          base + ny * nz + 1,
          base + ny * nz + nz,
          base + ny * nz + nz + 1,
         ], axis=-1)
    
    
      
       voxels=voxels.reshape(-1, 8)[geo.mask.flatten()]
     
       n_elems = voxels.shape[0]

       #Recover variables from solvers
       strc   ='# vtk DataFile Version 2.0\n'
       strc  +='MatInverse Data\n'
       strc  +='ASCII\n'
       strc  +='DATASET UNSTRUCTURED_GRID\n'
       strc  +='POINTS ' + str(n_nodes) +   ' double\n'
       
       #write points--
       for n in range(n_nodes):
         for i in range(dim): 
           strc +=str(nodes[n,i])+' '
         if dim == 2:
            strc +='0.0'+' '
         strc +='\n'


       #write elems--
       if dim == 2:
          m = 4 
          ct = '9'
       else:
        m = 8 
        ct = '11'
       n = m+1

       strc +='CELLS ' + str(n_elems) + ' ' + str(n*n_elems) + ' ' +  '\n'
      
       for k in range(n_elems):
        strc +=str(m) + ' '
        for i in range(n-1): 
          strc +=str(voxels[k][i])+' '
        strc +='\n'
       
       strc +='CELL_TYPES ' + str(n_elems) + '\n'
       for i in range(n_elems): 
         strc +=ct + ' '
       strc +='\n'

       strc +='CELL_DATA ' + str(n_elems) + '\n'
 
       for n,(key, value) in enumerate(variables.items()):

         data = value['data'] 
         if batch_size == 1:
            data = data[np.newaxis, :]

         for k in range(batch_size):   

          name = f'{key}[{k}]_[{value["units"]}]' if batch_size > 1 else f'{key}_[{value["units"]}]'
         

          if data[k].ndim == 1: #scalar
            
            strc +='SCALARS ' + name + ' double\n'
            strc +='LOOKUP_TABLE default\n'
            strc += ' '.join(np.array(data[k]).astype(str)) + '\n'
            
    

          elif data[k].ndim == 2: #vector
           strc +='VECTORS ' + name + ' double\n'
           strc += '\n'.join('  '.join(map(str, row)) for row in np.array(data[k]))

          elif data[k].ndim == 3: #tensor
           
           strc +='TENSORS ' + name + ' double\n'
           for i in np.array(data[k]):
            for j in i:
              strc += '  '.join(map(str, j)) + '\n'
           strc += '\n'

         with open(filename,'w') as f:
            f.write(strc)

def plot_paths(paths,L,x,flip=False):

 #fig = plt.figure()
 for p in paths:
    a = np.array(p)
    if flip: a = np.flip(a)
    plt.plot(a[:,0],a[:,1],'g',lw=3)

 plt.gca().set_aspect('equal')
 plt.imshow(x)
 #plt.plot([-L/2,-L/2,L/2,L/2,-L/2],[-L/2,L/2,L/2,-L/2,-L/2],ls='--')
 plt.axis('off')
 plt.show()

def find_irreducible_shapes(cs,L) :

    #find all close circles
    output = []
    for c in cs:
        if np.linalg.norm(c[0]-c[-1]) == 0:
           output.append(c)

    pp = np.array([[-L,0],[-L,L],[0,L],[L,L],[L,0],[L,-L],[0,-L],[-L,-L],\
                   [-2*L,0],[-2*L,L],[-2*L,2*L],[-L,2*L],[0,2*L],[L,2*L],[2*L,2*L],[2*L,L],[2*L,0],[2*L,-L],[2*L,-2*L],[L,-2*L],[0,-2*L],[-L,-2*L],[-2*L,-2*L],[-2*L,-L]])

    n = len(output)
    ##find irredicuble shape

    new = []
    for i in range(n):
        repeated = False
        for c2 in new:
            for p in pp:
              f = output[i] + p[np.newaxis,:]
              d = np.linalg.norm(np.mean(f,axis=0) - np.mean(c2,axis=0))
              if d < 1e-1:
                  repeated = True
                  pass

        if not repeated:
             new.append(output[i])

    #center to the first shape---
    c = np.mean(new[0],axis=0)

    cs = [i - c[np.newaxis,:]  for i in new]

    return cs

def periodic_numpy2gds(x,L,D,filename,plot_contour=False):

  x = np.where(x<0.5,1e-12,1)
  grid = int(np.sqrt(x.shape[0]))
  x = x.reshape((grid,grid))

  x = 1-np.array(x)
  N = x.shape[0]
  resolution = x.shape[0]/L #pixel/um
  x = np.pad(x,N,mode='wrap')

  #Find contour
  x = gaussian_filter(x, sigma=1)
  #for the paper it was 0.8
  contours = measure.find_contours(x,0.5)
  if plot_contour:
   plot_paths(contours)

  new_contours = []
  for contour in contours:
        new_contours.append(np.array(contour)/resolution)

  contours = find_irreducible_shapes(new_contours,L)


  unit_cell = gdspy.Cell("Unit", exclude_from_current=True)
  unit_cell.add(gdspy.PolygonSet(contours))

  #Repeat
  num = int(D/L/2)
  circle_cell = gdspy.Cell("Circular", exclude_from_current=True)

  # Iterate over each potential position for a unit cell
  contours_tot = []
  n_rep = 0
  for i in range(-num,num):
    for j in range(-num,num):
        # Calculate the center of the current unit cell
        center_x = (i+0.5)  * L
        center_y = (j+0.5)  * L

        # Check if the center is within the circle
        if np.sqrt(center_x ** 2 + center_y ** 2) <= D/2:
            # If it is, create a new instance of the unit cell at this position
            circle_cell.add(gdspy.CellReference(unit_cell, (center_x, center_y)))
            n_rep +=1

            for c in contours:
                    contours_tot.append(np.array(c) + np.array([[center_x,center_y]]))


  # IO.save('paths_to_FIB',{'paths':contours_tot,'L':L})
  #if write_path:
  #     with open('path.json','wb') as f:
  #      pickle.dump(contours_tot,f)

  lib = gdspy.GdsLibrary()
  lib.add(circle_cell)
  lib.write_gds(filename + '.gds')

   





    



