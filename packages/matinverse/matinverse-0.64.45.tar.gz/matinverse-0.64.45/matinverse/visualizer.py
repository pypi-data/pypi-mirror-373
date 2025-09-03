import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numpy.ma import masked_array
import matplotlib.cm as cm
import plotly.graph_objects as go
from jax import numpy as jnp
import jax
from matplotlib.animation import FuncAnimation, PillowWriter
import cv2
import matplotlib.cm as cm
import numpy as np
import matplotlib.patches as patches




def cube_mesh(x0, y0, z0, size=1.0):
    # Cube vertices relative to (x0, y0, z0)
    vertices = np.array([
        [0, 0, 0], [1, 0, 0],
        [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1],
        [1, 1, 1], [0, 1, 1]
    ]) * size + np.array([x0, y0, z0])

    # Triangles (two per face, 6 faces)
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 5, 6], [4, 6, 7],  # top
        [0, 1, 5], [0, 5, 4],  # front
        [1, 2, 6], [1, 6, 5],  # right
        [2, 3, 7], [2, 7, 6],  # back
        [3, 0, 4], [3, 4, 7],  # left
    ])
    return vertices, faces



def plot3D(data,write=False):

    voxels = np.where(data>0.5,1,0)

    filled = np.argwhere(voxels)

    all_vertices = []
    all_faces = []
    offset = 0

    for (x, y, z) in filled:
     verts, faces = cube_mesh(x, y, z)
     all_vertices.append(verts)
     all_faces.append(faces + offset)
     offset += verts.shape[0]

    all_vertices = np.concatenate(all_vertices, axis=0)
    all_faces = np.concatenate(all_faces, axis=0)

    # Extract Mesh3d inputs
    X, Y, Z = all_vertices.T
    I, J, K = all_faces.T

    mesh = go.Mesh3d(
     x=X, y=Y, z=Z,
     i=I, j=J, k=K,
     opacity=1,
     color='lightcoral',
     flatshading=True
    )


    fig = go.Figure(data=[mesh])



    fig.update_layout(
     scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='cube'
     ),
     margin=dict(l=0, r=0, b=0, t=0),
     paper_bgcolor='rgba(0,0,0,0)',  # transparent outer area
     plot_bgcolor='rgba(0,0,0,0)'    # transparent 3D plot area
    )

    fig.update_layout(scene_aspectmode='cube')

    if write:
     fig.write_html('voxels.html',config={'displayModeBar': False})

    fig.show()
def plot2D(data,geo,**argv):
    """Plot Masked data"""


    data = jnp.zeros((geo.N)).at[geo.local2global].set(data.flatten()).reshape(geo.grid)


    #Design mask
    design_mask = argv.setdefault('design_mask', jnp.ones_like(geo.mask)).reshape(geo.grid)
    design_mask = jnp.where(design_mask>0.5,1,0)


    #Mask for excluding part of the domain from the simulation
    mask = np.logical_and(geo.mask,design_mask)



    #mask = np.logical_not(total_mask.T)[1:-1,1:-1]

    Lx,Ly = geo.size

    N = data.shape[0]
    kx = 1
    ky = 1
    Px = 0
    Py = 0
    if geo.periodic[0]:
        kx = 3
        Px = N #Because it is extended
        Lx *=3
    if geo.periodic[1]:
        ky = 3
        Py = N #Because it is extended
        Ly *=3

    if not 'axis' in argv.keys():
       ax = plt.gca()
    else:
       ax = argv['axis']



    #plot the unit cell
    if geo.periodic[0] and geo.periodic[1]:
       ax.plot([-geo.size[0]/2,-geo.size[0]/2,geo.size[0]/2,geo.size[0]/2,-geo.size[0]/2],[-geo.size[1]/2,geo.size[1]/2,geo.size[1]/2,-geo.size[1]/2,-geo.size[1]/2],'r--',linewidth=2)


    data = np.pad(data,(Px,Py),'wrap')
    #mask = np.pad(geo.mask,(Px,Py),'wrap')


    mask = np.pad(np.logical_not(mask),(Px,Py),'wrap')


    data = masked_array(data, mask=mask)


    extent= [-geo.size[0]/2*kx,geo.size[0]/2*kx,-geo.size[1]/2*ky,geo.size[1]/2*ky]

    cmap = argv.setdefault('cmap','viridis')


    vmin = argv.setdefault('vmin',data.min())
    vmax = argv.setdefault('vmax',data.max())
    img = ax.imshow(data,extent = extent,cmap=cmap,aspect='equal',vmin=vmin,vmax=vmax)


    #Plot contours
    DX = geo.size[0]/geo.grid[0]
    DY = geo.size[1]/geo.grid[1]
    for contour in argv.setdefault('contours',[]):


        contour = jnp.where(contour>0.5,1,0)

        I1 = jnp.logical_xor(contour.flatten()[geo.smap[:,0]],contour.flatten()[geo.smap[:,1]])
        I1 = jnp.where(I1)[0]
        I_vertical = I1[jnp.where(I1  < len(geo.face_centroids)//2)[0]]
        I_horizontal = I1[jnp.where(I1  >= len(geo.face_centroids)//2)[0]]

        PP = [[0,0]]
        if geo.periodic[0]:
              PP.append([geo.size[0],0])
              PP.append([-geo.size[0],0])
        if geo.periodic[1]:
              PP.append([0,geo.size[1]])
              PP.append([0,-geo.size[1]])
        if geo.periodic[0] and geo.periodic[1]:
              PP.append([geo.size[0],geo.size[1]])
              PP.append([-geo.size[0],-geo.size[1]])
              PP.append([geo.size[0],-geo.size[1]])
              PP.append([-geo.size[0],geo.size[1]])

        for P in PP:


         for a in I_vertical:
           c = geo.face_centroids[a]
           ax.plot([c[0]+P[0],c[0]+P[0]],[c[1]-DY/2+P[1],c[1] + DY/2+P[1]],'r',lw=1,zorder=4)

         for a in I_horizontal:
           c = geo.face_centroids[a]
           ax.plot([c[0]-DX/2+P[0],c[0] + DX/2+P[0]],[c[1]+P[1],c[1]+P[1]],'r',lw=1,zorder=4)


    #if geo.periodic[0] or geo.periodic[1]:
    #   ax.plot([-Lx/2,-Lx/2,Lx/2,Lx/2,-Lx/2],[-Ly/2,Ly/2,Ly/2,-Ly/2,-Ly/2],'r',linewidth=2)

    #plt.ioff()

    #Line contours
    line_contours = argv.setdefault('line_contours',[])
    if len(line_contours) > 0:
        ax.contour(np.flipud(data), extent=extent, levels=line_contours, colors='white')

    #Flux lines #This does not work with PBCs yet
    flux_lines = argv.setdefault('flux_lines',[])
    if len(flux_lines) > 0:
        xc = np.linspace(-Lx / 2, Lx / 2, N)
        yc = np.linspace(-Ly / 2, Ly / 2, N)
        ax.streamplot(xc, yc, jnp.flipud(flux_lines[:, 0].reshape(geo.grid).T), jnp.flipud(flux_lines[:, 1].reshape(geo.grid).T), color='w')

    #Add a border
    if argv.setdefault('border',False):

     rect = patches.Rectangle(
      (-Lx/2, -Ly/2), Lx, Ly,
      linewidth=2, edgecolor='red', facecolor='none')

     ax.add_patch(rect)

    ax.axis('off')
    ax.set_aspect('equal')
    ax.set_xlim([-Lx/2,Lx/2])
    ax.set_ylim([-Ly/2,Ly/2])
    if argv.setdefault('colorbar',False):
     cbar = plt.colorbar(img)
     cbar.set_label(argv['colorbar_title'], fontsize=12)

    if argv.setdefault('write',False):
        plt.savefig('data.png', dpi=argv.setdefault('dpi',100),bbox_inches='tight', pad_inches=0)

    if not 'axis' in argv.keys():
     plt.tight_layout()
     plt.ioff()
     plt.show()

    return img


def save_video(data,  geo,
                      mask_color=(0, 0, 0), 
                      fps=100, 
                      filename="video.mp4", 
                      cmap_name='viridis',
                      scale=10):
    """
    Save a colormapped video with an optional mask and upscaling.

    Parameters:
        data (ndarray): Shape (T, H, W) — video frames.
        mask (ndarray or None): Shape (H, W), bool — True to keep, False to mask. Default: None (no mask).
        mask_color (tuple): RGB color for masked regions, in [0, 1]. Default: black.
        fps (int): Frames per second. Default: 100.
        filename (str): Output video filename. Default: "video.mp4".
        scale (int): Scaling factor for output resolution. E.g., 10 → 30x30 → 300x300 video.
    """

    NT = len(data) #NT is the optimization iteration, not the time step

    data = jnp.zeros((NT,geo.N)).at[:,geo.local2global].set(data).reshape(((NT,) + tuple(geo.grid))) 

    mask = geo.mask

    if geo.periodic[0]:
        data = jnp.pad(data, ((0, 0), (geo.grid[0], geo.grid[0]), (0, 0)), mode='wrap')
        mask = jnp.pad(mask, (geo.grid[0], geo.grid[0]), mode='wrap')
    if geo.periodic[1]:
        data = jnp.pad(data, ((0, 0), (0, 0), (geo.grid[1], geo.grid[1])), mode='wrap')
        mask = jnp.pad(mask, (0, 0), mode='wrap')

    T, H, W = data.shape
    out_size = (W * scale, H * scale)

    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*"mp4v"), fps, out_size)
    #out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'avc1'), fps, out_size)

   
   

    for frame in data:
        mframe = np.ma.masked_array(frame, mask=~mask)
        norm = (mframe - mframe.min()) / (mframe.ptp() + 1e-8)
        norm_filled = norm.filled(np.nan)

        cmap = cm.get_cmap(cmap_name)

         # Apply the colormap
        rgba = cmap(norm_filled)
        #rgba = cm.viridis(norm_filled)
        rgba[np.isnan(norm_filled)] = list(mask_color) + [1.0]

        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        # Upscale
        bgr_resized = cv2.resize(bgr, out_size, interpolation=cv2.INTER_NEAREST)

        out.write(bgr_resized)

    out.release()



def movie(data, geo, **argv):


    NT = len(data) #NT is the optimization iteration, not the time step

    data = jnp.zeros((NT,geo.N)).at[:,geo.local2global].set(data).reshape(((NT,) + tuple(geo.grid))) 
    

  
    NT, grid, grid = data.shape

    #Init design mask

    mask = geo.mask
    #--------


    # fig, ax = plt.subplots()
    # fig.patch.set_alpha(0.0)  # Make the figure background transparent
    # ax.set_facecolor((1, 1, 1, 0))  # Make the axes background transparent
    # ax.axis('off')
    # plt.tight_layout()


    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((1, 1, 1, 0))
    ax.axis('off')

     #plot the unit cell
    if geo.periodic[0] and geo.periodic[1]:
       unit_cell, = ax.plot([-geo.size[0]/2,-geo.size[0]/2,geo.size[0]/2,geo.size[0]/2,-geo.size[0]/2],[-geo.size[1]/2,geo.size[1]/2,geo.size[1]/2,-geo.size[1]/2,-geo.size[1]/2],'r--',linewidth=2)
    else:
         unit_cell, = ax.plot([], [], 'r--', linewidth=0)

    vmax = data.max()

    kx = 1
    ky = 1
    Px = 1
    Py = 1
    if geo.periodic[0]:
        kx = 3
        Px = grid
    if geo.periodic[1]:
        ky = 3
        Py = grid

    data = np.pad(data, ((0, 0), (Px, Px), (Py, Py)), mode='wrap')
    mask = np.pad(mask, ((Px, Px), (Py, Py)), mode='wrap')

    cmap = argv.setdefault('cmap', 'viridis')

    # cax = ax.imshow(
    #     data[0, :, :], cmap=cmap, 
    #     extent=[-geo.size[0] / 2 * kx, geo.size[0] / 2 * kx, 
    #             -geo.size[1] / 2 * ky, geo.size[1] / 2 * ky],vmin=0,vmax=1
    # )

    cax = ax.imshow(
        data[0, :, :], cmap=cmap, 
        extent=[-geo.size[0] / 2 * kx, geo.size[0] / 2 * kx, 
                -geo.size[1] / 2 * ky, geo.size[1] / 2 * ky]
    )
    cax.set_clim(0, data[0, :, :].max())
    ax.set_xlim([-geo.size[0] / 2 * kx, geo.size[0] / 2 * kx])
    ax.set_ylim([-geo.size[1] / 2 * ky, geo.size[1] / 2 * ky])


  

    def update(frame):
     
     cax.set_data(data[frame, :, :])  # Transpose data for correct orientation

     return cax,unit_cell


    # Creating the animation
    ani = FuncAnimation(fig, update, frames=NT, blit=True, interval=0.5, repeat=False)

    #ani.save('animation.gif',writer=PillowWriter(fps=100), savefig_kwargs={'transparent': True,'pad_inches': 0})  # Save with transparency

    #ani.save('animation.gif', writer='ffmpeg', fps=100, 
    #     extra_args=['-r', '100'], savefig_kwargs={'transparent': True})
    
    #ani.save('animation.mp4', writer='ffmpeg',
    #     extra_args=['-r', '100'], 
    #     savefig_kwargs={'transparent': True})

    filename = argv.setdefault('filename', 'animation.gif')
    ani.save(filename, writer=PillowWriter(fps=200), 
         savefig_kwargs={'transparent': True, 'pad_inches': 0})
    
    if argv.setdefault('show',True):
     plt.ioff()
     plt.tight_layout()
     plt.show()



    
# def create_squares(geo):

#     normals   = geo.boundary_normals
#     centers = geo.boundary_centroids
#     size =  np.array([geo.size[0]/geo.grid[0], geo.size[1]/geo.grid[1], geo.size[2]/geo.grid[2]])
#     normals = normals.astype(float)
    
#     # Create a vector for cross product calculations
#     cross_vec1 = np.array([1, 0, 0], dtype=float)
#     cross_vec2 = np.array([0, 0, 1], dtype=float)
    
#     # Calculate two orthogonal vectors to the normal vectors
#     use_cross_vec1 = normals[:, 2] != 0
#     use_cross_vec2 = ~use_cross_vec1
    
#     u = np.cross(normals, cross_vec1 * use_cross_vec1[:, np.newaxis] + cross_vec2 * use_cross_vec2[:, np.newaxis])
#     u /= np.linalg.norm(u, axis=1)[:, np.newaxis]
    
#     v = np.cross(normals, u)
#     v /= np.linalg.norm(v, axis=1)[:, np.newaxis]


#     # Calculate the four vertices of the squares
#     d = size / 2
#     vertices = np.zeros((len(centers), 4, 3))
#     vertices[:, 0] = centers + d * (u + v)
#     vertices[:, 1] = centers + d * (u - v)
#     vertices[:, 2] = centers + d * (-u - v)
#     vertices[:, 3] = centers + d * (-u + v)
    
#     return vertices
    

# def plot_boundary(geo,bcs):

#     vertices = create_squares(geo)


#     fig = go.Figure()

#     def plot_partial(inds,name):
     
#      x = vertices[inds, :, 0].flatten()
#      y = vertices[inds, :, 1].flatten()
#      z = vertices[inds, :, 2].flatten()
    
#      # Define the faces
#      i = []
#      j = []
#      k = []
    
#      for idx in range(vertices[inds].shape[0]):
#       base_idx = idx * 4
#       # Two triangles for each quadrilateral face with consistent ordering
#       i.extend([base_idx, base_idx+1, base_idx+2, base_idx, base_idx+2, base_idx+3])
#       j.extend([base_idx+1, base_idx+2, base_idx, base_idx+2, base_idx+3, base_idx+1])
#       k.extend([base_idx+2, base_idx, base_idx+1, base_idx+3, base_idx, base_idx+2])

#      # Create the 3D mesh plot
#      fig.add_trace(go.Mesh3d(
#         x=x,
#         y=y,
#         z=z,
#         i=i,
#         j=j,
#         k=k,
#         name=name,showlegend=True))

    

#     plot_partial(bcs.temp_indices,'temp')
#     plot_partial(bcs.robin_indices,'robin')
#     plot_partial(bcs.flux_indices,'flux')

    
#     # Update the layout
#     fig.update_layout(
#     title='3D Scatter Plot of Vertices with Values',
#     scene=dict(
#         xaxis_title='X',
#         yaxis_title='Y',
#         zaxis_title='Z'
#     )
#     )

    
#     x_range = np.ptp(vertices[:, :, 0])  # Peak to peak (max - min)
#     y_range = np.ptp(vertices[:, :, 1])
#     z_range = np.ptp(vertices[:, :, 2])
#     aspect_ratio = [x_range, y_range, z_range]

#     # Set the scene with the calculated aspect ratio
#     fig.update_layout(scene=dict(
#       aspectmode='manual',
#       aspectratio=dict(x=aspect_ratio[0], y=aspect_ratio[1], z=aspect_ratio[2]),
#       xaxis=dict(visible=False),
#       yaxis=dict(visible=False),
#       zaxis=dict(visible=False)
#     ))


#     # Show the plot
#     fig.show()

