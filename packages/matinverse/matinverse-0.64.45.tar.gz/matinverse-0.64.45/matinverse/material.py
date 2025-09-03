from dataclasses import dataclass,field
import jax
from functools import partial
from jax import numpy as jnp
import pickle
from sqlitedict import SqliteDict
from matinverse.interpolation import fast_interpolation
from jax.scipy.sparse.linalg import cg
import matplotlib.pyplot as plt



@partial(jax.tree_util.register_dataclass,
          data_fields=['S','W_od','W_RTA','T_weigths','kappa','Q_weigths'], meta_fields=['n_phi'])
@dataclass
class Gray2D:

   
    W_RTA:     jax.Array
    W_od:      jax.Array
    S:         jax.Array
    kappa:     jax.Array
    T_weigths: jax.Array
    Q_weigths: jax.Array
    n_phi:     int 

    def __init__(self,MFP,kappa,n_phi=48):
        #2D Transport
        #"""\kappa = \frac{1}{2}C/\tau\Lambda^2 = \frac{1}{2}\eta \Lambda^2"""
        
        self.n_phi = n_phi
        #Compute ballistic transport coefficients--------------------
        phi        = jnp.linspace(0,2.0*jnp.pi,self.n_phi,endpoint=False)
        Dphi       = 2*jnp.pi/self.n_phi
        fphi       = jnp.sinc(Dphi/2.0/jnp.pi)
        self.S     = 2/self.n_phi*kappa/MFP*fphi*jnp.array([jnp.sin(phi),jnp.cos(phi)]).T #W/m/K

      
        #self.W     = 2/self.n_phi*kappa/MFP/MFP*(jnp.eye(self.n_phi)-jnp.ones((self.n_phi,self.n_phi))/self.n_phi) #W/m^2/K
        self.W_RTA = 2/self.n_phi*kappa/MFP/MFP*jnp.ones(self.n_phi)#W/m^2/K
        self.W_od  = -2/self.n_phi**2*kappa/MFP/MFP*jnp.ones((self.n_phi,self.n_phi)) #W/m^2/K

        #Compute kappa from scattering operator
        W = jnp.diag(self.W_RTA) + self.W_od #W/m^2/K
        self.kappa     = jnp.einsum('ui,uv,vj->ij',self.S,jnp.linalg.pinv(W),self.S)
        self.T_weigths = 1/self.n_phi*jnp.ones(self.n_phi)
        self.Q_weigths = 1/self.n_phi*jnp.ones(self.n_phi)
       


#MFP = 10e-9 #m
#kappa = 1 #W/K

#Gray2D(MFP,kappa)

#Compute scattering operator ----------------------------------
        #eta     = 2/self.n_phi*kappa/MFP/MFP*jnp.ones(self.n_phi)
        #eta_tot = eta.sum()
        #eta_bar = eta/eta_tot
        #self.W  = eta_tot*(jnp.diag(eta_bar) - jnp.outer(eta_bar,eta_bar)) #W/m^2/K
        #-------------------------------------------------------------
        #phi       = jnp.linspace(0,2.0*jnp.pi,self.n_phi,endpoint=False)
        #Dphi      = 2*jnp.pi/self.n_phi
        #fphi      = jnp.sinc(Dphi/2.0/jnp.pi)
        #F         = MFP*fphi*jnp.array([jnp.sin(phi),jnp.cos(phi)]).T
        #self.S    = jnp.einsum('q,qi->qi',eta,F) #W/m/K#
        #kappa = jnp.einsum('ui,u,uj->ij',self.S,1/eta,self.S)
        #print(kappa)


@partial(jax.tree_util.register_dataclass,
          data_fields=['S','W_od','W_RTA','T_weigths','kappa','Q_weigths'], meta_fields=['n_phi'])
@dataclass
class RTA2D:

   
    W_RTA:     jax.Array
    W_od:      jax.Array
    S:         jax.Array
    kappa:     jax.Array
    T_weigths: jax.Array
    Q_weigths: jax.Array
    n_phi:     int = 48

    def __init__(self,filename,**kwargs):
         

        #Process input
        n_phi = kwargs.setdefault('n_phi',48)
        n_mfp = kwargs.setdefault('n_mfp',50)
        #-----------
        #Load data
        data =  dict(SqliteDict(filename + '.db',encode=pickle.dumps, decode=pickle.loads))

     
        tau      = data['scattering_time']
        sigma    = jnp.einsum('k,ki->ki',data['heat_capacity'],data['group_velocity'][:,:2])
        F = jnp.einsum('ki,k->ki',data['group_velocity'],tau)
        f = jnp.where(tau != 0, jnp.ones_like(tau) / tau, jnp.zeros_like(tau))
        Wdiag    = data['heat_capacity']*f

        freq = data['frequency']

      

      
        #Filtering low-MFP data out
        r = jnp.linalg.norm(F[:,:2],axis=1)
        I = jnp.where(r>1e-10)
        r = r[I]
        F = F[I]
        Wdiag = Wdiag[I]
        sigma = sigma[I]
        freq = freq[I]

                
        # # Compute magnitudes of the vectors
        # magnitudes = jnp.linalg.norm(F, axis=1)

        # # Get indices of the top 16 magnitudes
        # top_indices = jnp.argsort(magnitudes)[-4:]

        # # Extract the corresponding vectors
        # F_top = F[top_indices]

        # print(F_top)

       


        #Kappa mode fine
        kappa_mode = jnp.einsum('qi,q,qj->ij',F,Wdiag,F)
       


        #Create MFP bins uniformly spaced in log10 
        mfp_max     = kwargs.setdefault('mfp_max', jnp.max(r) * 1.1)
        mfp_min     = kwargs.setdefault('mfp_min', jnp.min(r) * 0.9)
 
        mfp_min_log = jnp.log10(mfp_min)
        mfp_max_log = jnp.log10(mfp_max)
        DMFP_log    = (mfp_max_log - mfp_min_log) / n_mfp

        mfp_sampled = jnp.power(10, jnp.linspace(mfp_min_log + DMFP_log / 2,
                                                mfp_max_log - DMFP_log / 2, n_mfp))

        mfp_bounds  = jnp.power(10, jnp.linspace(mfp_min_log, mfp_max_log, n_mfp + 1))
        map_mfp     = jnp.digitize(r, mfp_bounds) - 1
        map_mfp     = jnp.clip(map_mfp, 0, n_mfp - 1)
        #------------------------------

        # Compute polar angles from vector components
        phi_bulk = jnp.arctan2(F[:, 0], F[:, 1])
        phi_bulk = jnp.where(phi_bulk < 0, phi_bulk + 2 * jnp.pi, phi_bulk)  # wrap to [0, 2π]

        # Define angular bins
        Dphi = 2 * jnp.pi / n_phi
        phi = jnp.linspace(0, 2 * jnp.pi, n_phi, endpoint=False)              # bin centers
        phi_bounds = jnp.linspace(0, 2 * jnp.pi, n_phi + 1)                   # bin edges

        # Assign each vector to a bin
        map_phi = jnp.digitize(phi_bulk, phi_bounds) - 1
        map_phi = jnp.where(map_phi == n_phi, 0, map_phi)  # wrap last bin to 0


        global_map = jnp.array(map_mfp * n_phi + map_phi, dtype=jnp.int32)


        N_coarse = n_mfp * n_phi

        # Generate sampled directions on the polar grid
        polar = jnp.stack([jnp.sin(phi), jnp.cos(phi)], axis=1)  # shape (n_phi, 2)
        F_sampled = jnp.einsum('m,ld->mld', mfp_sampled, polar)

        freq = jnp.array(freq)
        N_fine = len(freq)

        g = jnp.zeros((N_coarse , N_coarse))

      

        @jax.jit
        def func(f1,f2):
              return (f1 - f2)**2

        # th = 0.0
        # for i in range(N_fine):
        #     a = func(freq[i],freq)
        #     g.at[global_map[i], global_map[a>th]].add(a[a>th])
        #     print(float(i)/float(N_fine))

            
        @jax.jit
        def compute(freq, global_map):
         def body(i, g):
            a = func(freq[i], freq)
            gi = global_map[i]
            gj = global_map
            return g.at[gi, gj].add(a)
        
         g_init = jnp.zeros((N_coarse, N_coarse))
         g_final = jax.lax.fori_loop(0,N_fine, body, g_init)
         return g_final
        
        g = compute(freq, global_map)

       
        
        # Nf = len(freq)     
        # g = jnp.zeros((n_mfp,n_phi,n_mfp,n_phi))
        # for i in range(Nf):
        #     for j in range(Nf):
        #         g = g.at[map_mfp[i],map_phi[i],map_mfp[j],map_phi[j]].add(func(i,j))


        # @jax.jit
        # def accumulate_sparse_static(freq, global_map):
        #     Nf = freq.shape[0]
        #     g = jnp.zeros((N_coarse , N_coarse))

        #     def outer(i, g):
        #         gi = global_map[i]
        #         fi = freq[i]

        #         def inner(j, g_inner):
        #             gj = global_map[j]
        #             fj = freq[j]
        #             return g_inner.at[gi, gj].add(fi + fj)
                
        #         return jax.lax.fori_loop(0, Nf, inner, g)

        #     return jax.lax.fori_loop(0, Nf, outer, g)


       



        # g = accumulate_sparse_static(freq, global_map)

        # #map_mfp = jnp.array(map_mfp, dtype=jnp.int32)
        # #map_phi = jnp.array(map_phi, dtype=jnp.int32)

        # Nf = len(freq)
        # g = jnp.zeros((N_coarse, N_coarse))
 
        
        # def body(i, g):
        #     gi = global_map[i]
        #     fi = freq[i]
            
        #     def inner(j, g_inner):
        #         gj = global_map[j]
        #         fj = freq[j]
        #         return g_inner.at[gi, gj].add(fi + fj)
            
        #     g = jax.lax.fori_loop(0, Nf, inner, g)
        #     return g

        # g = jax.lax.fori_loop(0, Nf, body, g)

        
        #g = g.at[global_map[:, None], global_map].add(freq[:, None] + freq)

        quit() 
       
        

        #g = g.at[map_mfp[:, None], map_phi[:, None], map_mfp, map_phi].add(freq[:, None]- freq)

        # def update_g(g, i):
        #     def body(j, g):
        #         val = func(i, j)
        #         return g.at[map_mfp[i], map_phi[i], map_mfp[j], map_phi[j]].add(val)
        #     g = jax.lax.fori_loop(0, Nf, body, g)
        #     return g

        # def outer_loop_body(i, g):
        #     return update_g(g, i)

        # g = jax.lax.fori_loop(0, Nf, outer_loop_body, g)


        quit()

        # Nf = len(freq)
        # i_idx, j_idx = jnp.meshgrid(jnp.arange(Nf), jnp.arange(Nf), indexing='ij')

        # # Compute g_val using broadcasting
        # g_val = freq[i_idx] + freq[j_idx]  # Shape (Nf, Nf)

        # # Compute the corresponding mfp and phi indices
        # mfp_i = map_mfp[i_idx]
        # phi_i = map_phi[i_idx]
        # mfp_j = map_mfp[j_idx]
        # phi_j = map_phi[j_idx]

        # # Flatten all index arrays and values
        # g = jnp.zeros((n_mfp, n_phi, n_mfp, n_phi))
        # g = g.at[mfp_i.ravel(), phi_i.ravel(), mfp_j.ravel(), phi_j.ravel()].add(g_val.ravel())        


        #g = jnp.array()

        # Compute the frequency difference
        #freq_diff = jnp.array([func(i,j) for i in range(len(freq)) for j in range(len(freq))])
    

        quit()   

         
        # print(freq.shape)
        # quit()
        # #Compute diffuse coefficients R


        # #------------------
        # quit()



        #for n in range(24):
        # print(jnp.linalg.norm(F_sampled[0,n] + F_sampled[0,n+24]))

         #print(n,F_sampled[0,n])
         #print(n+24,F_sampled[0,n+24])
        #diff = F_sampled + jnp.roll(F_sampled, n_phi // 2, axis=1)
        #print("|F + F(pi)|:", jnp.linalg.norm(diff))

      

        #quit()


        # Combine MFP and angular indices
        maps = jnp.stack((map_mfp, map_phi), axis=1)

        # Accumulate weights into sampled grid
        Wdiag_sampled = jnp.zeros((n_mfp, n_phi)).at[(maps[:, 0], maps[:, 1])].add(Wdiag)


        
        #Wdiag_sampled  = Wdiag_sampled.at[:,:int(n_phi/2)].set(Wdiag_sampled[:,int(n_phi/2):])

        #Wdiag_sampled = 0.5 * (Wdiag_sampled + jnp.roll(Wdiag_sampled, n_phi // 2, axis=1))


        ax = plt.subplot(111, projection='polar')
        # for m in range(n_mfp):
        
        ax.plot(phi, Wdiag_sampled[-1, :], ls='none', marker='o')
        ax.plot(phi, Wdiag_sampled[-2, :], ls='none', marker='o')
        ax.plot(phi, Wdiag_sampled[-3, :], ls='none', marker='o')
        ax.plot(phi, Wdiag_sampled[-4, :], ls='none', marker='o')
        ax.plot(phi, Wdiag_sampled[-5, :], ls='none', marker='o')
        plt.show()
        quit()

        kappa_mode = jnp.einsum('mli,ml,mlj->ij',F_sampled,Wdiag_sampled,F_sampled)


        print(kappa_mode)
        quit()
        for m in range(n_mfp):
            
         kappa_mode = jnp.einsum('li,l,lj->ij',F_sampled[m],Wdiag_sampled[m],F_sampled[m])

         print(kappa_mode)
         print()


        
        quit()




        quit()
        
        
      
        

        #Kappa mode coarse
        print(kappa_mode)

        quit()
 

        
        

       

 
    
      




        # scale = jnp.sum(Wdiag)

        # sigma_bar = sigma/scale
        # r_gen = jnp.linalg.norm(sigma_bar[:,:2],axis=1)
        # print((sigma/scale).max())
        # #print(scale)
        # quit()
        # print(sigma.max())
        # quit()
        #Generalized MFP
        # sigma_bar = sigma/Wdiag.sum()
        # r_gen = jnp.linalg.norm(sigma_bar[:,:2],axis=1)
        # # #Regular MFP
        # # #plt.plot(r,ls='none',marker='o')
        # plt.plot(r_gen,ls='none',marker='o')
        # # #plt.legend(['Regular MFP','Generalized MFP'])
 
        # plt.yscale('log')
        # plt.show()
        # quit()



        # quit()
        # #kappa_mode        = jnp.einsum('qi,q,qj->ij',F,Wdiag,F)
          
        # gamma  = jnp.sum(Wdiag)
        # eta_bar = Wdiag/gamma
        # sigma_bar = sigma/gamma
        # def func(x):
          
        #      return jnp.einsum('i,id->id',eta_bar,x) - jnp.einsum('i,j,jd->id',eta_bar,eta_bar,x)
    
        # #A = cg(func,sigma_bar, tol=1e-6)[0]

        # kappa_mode = gamma*jnp.einsum('qi,qj->ij',sigma_bar,cg(func,sigma_bar, tol=1e-6)[0])
   

      
        #-------------------
       
     
        # #Interpolation in the MFPs
        # a1,a2,m1,m2 = fast_interpolation(r,mfp_sampled,bound='extent',scale='linear')
        # #Interpolation in phi---
        # b1,b2,p1,p2 = fast_interpolation(phi_bulk,phi,bound='periodic')
              
        


        # F_sampled = jnp.einsum('m,qi->mqi',mfp_sampled,polar_ave)
        # Wdiag_sampled = jnp.zeros((n_mfp,n_phi))
        # sigma_sampled = jnp.zeros((n_mfp,n_phi,2)) 


        # Wdiag_sampled = Wdiag_sampled.at[(m1, p1)].add(a1 * b1 * Wdiag)
        # Wdiag_sampled = Wdiag_sampled.at[(m1, p2)].add(a1 * b2 * Wdiag)
        # Wdiag_sampled = Wdiag_sampled.at[(m2, p1)].add(a2 * b1 * Wdiag)
        # Wdiag_sampled = Wdiag_sampled.at[(m2, p2)].add(a2 * b2 * Wdiag)


        #Enforce symmetry
        Wdiag_sampled  = Wdiag_sampled.at[:,:int(n_phi/2)].set(Wdiag_sampled[:,int(n_phi/2):])
        #---------

        #Wdiag_inv = jnp.where(Wdiag_sampled != 0, 1 / Wdiag_sampled, 0)

        #t_coeff = Wdiag_sampled/np.sum(Wdiag_sampled)
        sigma_sampled = jnp.einsum('mq,mqi->mqi',Wdiag_sampled,F_sampled)

        kappa_mode        = jnp.einsum('mqi,mq,mqj->mqij',F_sampled,Wdiag_sampled,F_sampled)
        kappa_sampled     = jnp.sum(kappa_mode,axis=(0,1))
        sigma_sampled     = sigma_sampled.reshape((n_phi*n_mfp,2))
        Wdiag_sampled     = Wdiag_sampled.flatten()

        #print(kappa_sampled)

        #Pruning
      
        I = jnp.linalg.norm(sigma_sampled,axis=1)> 0

        
        eta = Wdiag_sampled[I].sum()
        eta_bar = Wdiag_sampled[I]/eta
        self.W_RTA =  Wdiag_sampled[I] #W/m^3/K
        self.W_od  =  -eta*jnp.outer(eta_bar,eta_bar) #W/m^3/K
        self.S     =  sigma_sampled[I] #W/m^2/K
        self.T_weigths = eta_bar
        self.Q_weigths = eta_bar



@partial(jax.tree_util.register_dataclass,
          data_fields=['S','W_od','W_RTA','T_weigths','kappa','Q_weigths'], meta_fields=['n_phi'])
@dataclass
class RTA2D_old:

   
    W_RTA:     jax.Array
    W_od:      jax.Array
    S:         jax.Array
    kappa:     jax.Array
    T_weigths: jax.Array
    Q_weigths: jax.Array
    n_phi:     int = 48

    def __init__(self,filename,**kwargs):
         
        #Load data
        data =  dict(SqliteDict(filename + '.db',encode=pickle.dumps, decode=pickle.loads))
        tau      = data['scattering_time']
        sigma    = jnp.einsum('k,ki->ki',data['heat_capacity'],data['group_velocity'][:,:2])
        F = jnp.einsum('ki,k->ki',data['group_velocity'][:,:2],tau)
        f = jnp.where(tau != 0, jnp.ones_like(tau) / tau, jnp.zeros_like(tau))
        Wdiag    = data['heat_capacity']*f

      
        #Filtering low-MFP data out
        r = jnp.linalg.norm(F[:,:2],axis=1)
        I = jnp.where(r>1e-10)
        r = r[I]
        F = F[I]
        phi_bulk = F[I]
        Wdiag = Wdiag[I]
        sigma = sigma[I]


        phi_bulk = jnp.arctan2(F[:, 0], F[:, 1])
        phi_bulk = phi_bulk.at[jnp.where(phi_bulk < 0) ].set(2*jnp.pi + phi_bulk[jnp.where(phi_bulk <0)])
        #----------------------------------------

        #Start interpolation
        n_phi = kwargs.setdefault('n_phi',48)
        n_mfp = kwargs.setdefault('n_mfp',50)
        Dphi = 2*jnp.pi/n_phi
        phi = jnp.linspace(0,2.0*jnp.pi,n_phi,endpoint=False)
        polar_ave = jnp.array([jnp.sin(phi),jnp.cos(phi)]).T
        #-------------------

        mfp_max     = kwargs.setdefault('mfp_max',jnp.max(r)*1.1)
        mfp_min     = kwargs.setdefault('mfp_min',jnp.min(r)*0.9)
        mfp_sampled = jnp.logspace(jnp.log10(mfp_min),jnp.log10(mfp_max),n_mfp,endpoint=True)
        F_sampled = jnp.einsum('m,qi->mqi',mfp_sampled,polar_ave)
        Wdiag_sampled = jnp.zeros((n_mfp,n_phi))
        sigma_sampled = jnp.zeros((n_mfp,n_phi,2)) 

     
        #Interpolation in the MFPs
        a1,a2,m1,m2 = fast_interpolation(r,mfp_sampled,bound='extent',scale='linear')
        #Interpolation in phi---
        b1,b2,p1,p2 = fast_interpolation(phi_bulk,phi,bound='periodic')
              

        Wdiag_sampled = Wdiag_sampled.at[(m1, p1)].add(a1 * b1 * Wdiag)
        Wdiag_sampled = Wdiag_sampled.at[(m1, p2)].add(a1 * b2 * Wdiag)
        Wdiag_sampled = Wdiag_sampled.at[(m2, p1)].add(a2 * b1 * Wdiag)
        Wdiag_sampled = Wdiag_sampled.at[(m2, p2)].add(a2 * b2 * Wdiag)


        #Enforce symmetry
        Wdiag_sampled  = Wdiag_sampled.at[:,:int(n_phi/2)].set(Wdiag_sampled[:,int(n_phi/2):])
        #---------

        #Wdiag_inv = jnp.where(Wdiag_sampled != 0, 1 / Wdiag_sampled, 0)

        #t_coeff = Wdiag_sampled/np.sum(Wdiag_sampled)
        sigma_sampled = jnp.einsum('mq,mqi->mqi',Wdiag_sampled,F_sampled)

        kappa_mode        = jnp.einsum('mqi,mq,mqj->mqij',F_sampled,Wdiag_sampled,F_sampled)
        kappa_sampled     = jnp.sum(kappa_mode,axis=(0,1))
        sigma_sampled     = sigma_sampled.reshape((n_phi*n_mfp,2))
        Wdiag_sampled     = Wdiag_sampled.flatten()

        #print(kappa_sampled)

        #Pruning
      
        I = jnp.linalg.norm(sigma_sampled,axis=1)> 0

        
        eta = Wdiag_sampled[I].sum()
        eta_bar = Wdiag_sampled[I]/eta
        self.W_RTA =  Wdiag_sampled[I] #W/m^3/K
        self.W_od  =  -eta*jnp.outer(eta_bar,eta_bar) #W/m^3/K
        self.S     =  sigma_sampled[I] #W/m^2/K
        self.T_weigths = eta_bar
        self.Q_weigths = eta_bar
       
