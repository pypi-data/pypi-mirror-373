import numpy as np
from jax import numpy as jnp
from matinverse import Geometry2D

def generate_correlated_pores(**argv):

 #---------------READ Parameters-------
 N = argv['N']
 #L = argv['l']
 #d = L/N
 #p = L
 le  = argv['length']
 phi = argv['porosity']
 #------------------------------------
 #NOTE: Variance is 1 because we only take the smallest number up to a certain point
 #gen = [np.exp(-2/le/le * np.sin(d*np.pi*i/p) ** 2) for i in range(N)]
 gen    = [np.exp(-2/le/le * np.sin(np.pi*i/N) ** 2) for i in range(N)]
 kernel = np.array([[  gen[abs(int(s/N) - int(t/N))]*gen[abs(s%N-t%N)]  for s in range(N*N)] for t in range(N*N)])
 y = np.random.multivariate_normal(np.zeros(N*N), kernel)
 h = y.argsort()
 idxl = h[0:int(N*N*(1-phi))]

 x = np.ones(N*N)

 x[idxl] = 0

 return x



def import_evolution(name):

   name = os.getcwd() + '/' + name 
   data = []



def staggered_2D(grid,porosity):

      geo = Geometry2D(grid=grid,size=(1,1))

      centroids = geo.centroids
      vec = np.zeros(len(centroids))
   
      C = [[0,0],[1/2,1/2],[1/2,-1/2],[-1/2,-1/2],[-1/2,1/2]]
      r = np.sqrt(porosity/np.pi/2)
      final = jnp.ones(grid[0]*grid[0])
      delta = 1e-12
      for c in C:
       tmp   = jnp.power((centroids[:,0]-c[0])/r,2) + jnp.power((centroids[:,1]-c[1])/r,2)
       final = final.at[jnp.where(tmp<1)].set(delta)

      return final

def get_guess(**options):

 grid  = options['grid']
 dim  = options.setdefault('dim',2)
 N    = int(grid**dim)
 #Number of elements--- 
 #---------------------
 model = options.setdefault('guess','random')

 if model == 'load':
    final = np.load('x',allow_pickle=True)

 elif model =='evolution':

    data =  import_evolution(options['name'])
    final = data[-1][0]

 elif model =='solid':
    final = np.ones(N)

 elif model =='gaussian':
  options['N'] = grid
  
  final = 1-generate_correlated_pores(**options)

 elif model =='random':
 
    if dim == 3:
     final = np.random.rand(int(N/8))
     final = reflect_3D(final)
    if dim == 2: 
     final = np.random.rand(int(N/4))
     final = reflect_2D(final)

 elif model in 'aligned':
     
      centroids = get_grid(grid,dim)['centroids']
      phi = options['porosity']
      vec = np.zeros(len(centroids))
      radii_ratio = options.setdefault('radii_ratio',1)
   
      C = [[0,0]]
      r = np.sqrt(phi/np.pi/radii_ratio)
      final = jnp.ones(len(centroids))
      delta = 1e-12
      for c in C:
       tmp   = jnp.power((centroids[:,0]-c[0])/r,2) + jnp.power((centroids[:,1]-c[1])/r,2)
       final = final.at[jnp.where(tmp<1)].set(delta)
      return final 


 elif model in 'staggered':

    if options.setdefault('dim',2) == 3:
      centroids = get_grid(grid,dim)['centroids']*L

      L  = options['L']
      C = L/2*np.array([[ 0,0 ,0],\
           [-1,-1,-1],\
           [-1, 1, 1],\
           [ 1,-1, 1],\
           [ 1, 1,-1],\
           [-1,-1, 1],\
           [-1, 1,-1],\
           [ 1,-1,-1],\
           [ 1, 1, 1]])

      phi = options['porosity']

      r = L*(phi*3/8/np.pi)**(1.0/3.0) 

      vec = np.zeros(len(centroids))
      for c in C:
       tmp  =  jnp.power((centroids[:,0]-c[0])/r,2) + jnp.power((centroids[:,1]-c[1])/r,2) + jnp.power((centroids[:,2]-c[2])/r,2)
       vec +=  jnp.where(tmp<1,1,0)
      
      final = 1-vec

      return final


    else:    

      centroids = get_grid(grid,dim)['centroids']
      phi = options['porosity']
      vec = np.zeros(len(centroids))
      radii_ratio = options.setdefault('radii_ratio',1)
   
      C = [[0,0],[1/2,1/2],[1/2,-1/2],[-1/2,-1/2],[-1/2,1/2]]
      r = np.sqrt(phi/np.pi/radii_ratio/2)
      final = jnp.ones(len(centroids))
      delta = 1e-12
      for c in C:
       tmp   = jnp.power((centroids[:,0]-c[0])/r,2) + jnp.power((centroids[:,1]-c[1])/r,2)
       final = final.at[jnp.where(tmp<1)].set(delta)

      if options.setdefault('hole',False):
       r *= 0.5
       for k,c in enumerate(C):
            tmp = jnp.power((centroids[:,0]-c[0])/r,2) + jnp.power((centroids[:,1]-c[1])/r,2)
            final = final.at[jnp.where(tmp<1)].set(1)

      return final

 if options.setdefault('show',False):
     plot(final,**{'replicate':True,'invert':True,'unitcell':True,'color_unitcell':'r','write':True})

 return final


def plot(x,**options):
 
 if type(x)==list: x = np.array(x)

 if x.ndim == 1:
  #Reshape    
  x = x.reshape(int(np.sqrt(len(x))), -1).T
 N = x.shape[0]
 #--------------------
 
 #Init figure---------
 if 'ax' in options.keys():
   ax = options['ax']
 else:  
   fig = plt.figure(figsize=(6,6), num='Evolution', frameon=False)
   ax = plt.Axes(fig, [0., 0., 1., 1.])
   fig.add_axes(ax)
 ax.set_axis_off()  # This line is important to remove the axis
 #--------------------


 #if 'filter_gradient' in options.keys():
 #  """Filter based on the gradient of the solution. This eliminates disconnected islands"""

 #  T = options_plot_structure['filter_gradient'].reshape((Ns,Ns))
 #  d = np.gradient(T)
 #  gradient_norm = (np.linalg.norm(d,axis=0)).flatten()
 #  x[gradient_norm < 1e-10] = 0
 #  x = np.where(x>0.5,1,0)


 L = options.setdefault('size',1)
 extent = options.setdefault('extent',[3*L,3*L])


 repeat = options.setdefault('repeat',1)

 for _ in range(repeat):
  Ns = x.shape[0]
  x = jnp.pad(x,Ns,mode='wrap')
  delta = L/N*0.5
  ax.plot([-0.5*L+delta,0.5*L+delta,0.5*L+delta,-0.5*L+delta,-0.5*L+delta],[-0.5*L-delta,-0.5*L-delta,0.5*L-delta,0.5*L-delta,-0.5*L-delta],color='c',ls='--')
  L *= 3

 #Plot the structure
 bound = options.setdefault('bounds','natural')
 if bound == 'natural':
     vmin = np.min(x); vmax = np.max(x)
 else:
     vmin = 0; vmax = 1

 im = ax.imshow(x,cmap=options.setdefault('cmap','binary'),extent=[-L/2,L/2,-L/2,L/2],vmin=vmin,vmax=vmax)

 #Apply mask
 #if 'mask' in options_plot_structure.keys():
 #   xm = options['mask']
 #   xm = x.reshape(int(np.sqrt(len(xm))), -1)
 #   x = jnp.pad(x,Ns,mode='wrap')
 #   masked = np.ma.masked_where(x > 0.5, 1-x)
    #if options_plot_structure.setdefault('invert_mask',False): masked = 1-masked
    #plt.imshow(masked,cmap='gray',vmin=0,vmax=1);

 #vmax = options_plot_structure.setdefault('max',np.max(x))
 #if options_plot_structure.setdefault('normalize','binary') == 'binary':
 #   im = ax.imshow(x,vmin=0,vmax=1,cmap=cmap,animated=True)
 #else:   
 #   im = ax.imshow(x,vmin=np.min(x),vmax=np.max(x),cmap=cmap,animated=True)

 #ax.axis('off')
#plt.tight_layout()

 #Plot linewidth
 #Apply extent
 #plt.xlim([-extent[0]/2,extent[0]/2])
 #plt.ylim([-extent[1]/2,extent[1]/2])

 if options.setdefault('minimum_linewidth',None):
  lw = options['minimum_linewidth']   
  c = plt.Circle((0,options.setdefault('size',1)),radius=lw/2,color='orange',zorder=10)
  ax.add_artist(c)

 if options.setdefault('save',False):
  plt.savefig('figure.png',dpi=600,bbox_inches='tight')   

 #plt.tight_layout(pad=0,h_pad=0,w_pad=0)
 #if options.setdefault('show',True):
 plt.ioff()
 if not 'ax' in options.keys():
  plt.show()
 #else: 
 # plt.ion()
 # plt.show()
 # plt.pause(0.1)



 return im

