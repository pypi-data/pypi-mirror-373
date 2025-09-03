import numpy as np
import nlopt
import jax
from jax import value_and_grad as value_and_grad
import jax.numpy as jnp
import matplotlib as mpl
import sys
from jax.lax import conv
import jax.scipy as jsp
from dataclasses import dataclass, field
from typing import List
import pickle
import gc
from functools import partial
import msgpack
import msgpack_numpy as m
from dataclasses import dataclass
from typing import Callable, Tuple, Union, List
import jax.numpy as jnp


#mpl.interactive(True)

@dataclass
class State:
    objective_function: List = field(default_factory=lambda: [])
    save_evolution: bool = True
    save_all_aux: bool = True
    save_constraint_aux: bool = True
    evolution: List = field(default_factory=list)
    aux: List = field(default_factory=list)
    constraint: List = field(default_factory=list)
    constraint_aux: List[List] = field(default_factory=lambda: [[]])
    solution: np.ndarray = None

    def _convert_jax_to_numpy(self, obj):
        """Recursively convert JAX arrays to NumPy before saving."""
        if isinstance(obj, jax.Array):
            return jax.device_get(obj)
        elif isinstance(obj, list):
            return [self._convert_jax_to_numpy(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_jax_to_numpy(v) for k, v in obj.items()}
        return obj  # Keep other types unchanged

    def save(self, filename: str):
        """Save the current state to a msgpack file."""
        data = self._convert_jax_to_numpy(self.__dict__)  # Convert all JAX arrays

        with open(filename, "wb") as f:
            f.write(msgpack.packb(data, default=m.encode))

    @classmethod
    def load(cls, filename: str):
        """Load a State object from a msgpack file."""
        with open(filename, "rb") as f:
            data = msgpack.unpackb(f.read(), object_hook=m.decode)
        return cls(**data)  # Restore the object


   
def colored(text,color,start,end):

 if color == 'green':
    return start+'\033[32m' + text + '\033[39m' + end
 elif color =='red':  
    return start+'\033[31m' + text + '\033[39m' + end
 elif color =='blue':  
    return start+'\033[34m' + text + '\033[39m' + end
 elif color =='white':  
    return start+'\033[39m' + text + '\033[39m' + end
 else:   
      raise "No color recognized"


def get_logger():

    def func(x,color = 'white',end='\n',start=''):

        print(colored(x,color,start,end),end='')  

    return func

logger       = get_logger()


#https://github.com/google/jax/pull/762#issuecomment-1002267121
def value_and_jacrev(f, x):
  y, pullback,aux = jax.vjp(f, x,has_aux=True)
  basis = jnp.eye(y.size, dtype=y.dtype)
  jac = jax.vmap(pullback)(basis)
  return (y,aux), jac





def enhance_inequality_constraint(func_original, state, index,is_last=False, adapt=False,state_verbosity=1):

    if not adapt:
        func = func_original
    else:
        def func(x):
            output, *args = func_original(x)
            return jnp.array([output]), *args

    def constraint(results, x, grad):

        # Compute function value and gradient
        (results[...], (to_print, aux)), (grad[...],) = value_and_jacrev(func, x)

        if state_verbosity > 0:
            # Print results
            for key, value in to_print.items():
                print(key + ': ', end=' ')
                if jnp.isscalar(value):
                    value = [value]
            for v in value:
                print(f"{v:12.3E} ", end=' ')

            if is_last:
             print()

        #Expand list to match number of constraints
        if index > len(state.constraint_aux)-1:
               state.constraint_aux.append([])

        # Save auxiliary data only if needed
        if state.save_constraint_aux:            
            state.constraint_aux[index].append(aux)
        else:
           #SAve only last one [WARNING: this does not necessarily corresponds to the best solution]
           state.constraint_aux[index] = [aux]
     
            #del aux  # Explicitly delete aux if not saved
            #gc.collect()  # Force garbage collection

        # Save results
        if index > len(state.constraint)-1:
               state.constraint.append([])
        state.constraint[index].append(results.tolist())
        


        #state.constraint.append(results.tolist())

        # Block until computation is ready to free memory
        jax.block_until_ready(results)

        return None

    return constraint





def enhance_objective_function(func,state,has_inequality,scale,state_verbosity=1):
    """Make func compatible with NlOpt"""
 
    
    def objective_optimizer(x,grad):

          n_iter = len(state.objective_function)

        #   if n_iter == 1:
        #      carry = initial_carry
        #   else:
        #      carry = state.aux[-1]   
        

          #(output,(to_print,aux)),grad[:]    = jax.value_and_grad(func,has_aux=True)(x,**carry)
          (output,(to_print,aux)),grad_output    =  jax.value_and_grad(func,has_aux=True)(x)
    
          grad[:] = np.array(grad_output.ravel(),dtype=np.float64) 
         
          if state_verbosity >  0:
           print(f"Iter: {n_iter:4d} ",end='')
           for key, value in to_print.items():
           
             print(key + ': ',end='')
             if jnp.isscalar(value): value = [value]
             
             for v in value:
               print(f"{v:12.3E}", end='')
             print(' ',end='')  
          
          
           if not has_inequality:    
            print() 
           else:
            print('  ',end=' ') 
          
          output = float(output)
          

          if state.save_evolution:
            state.evolution.append(np.array(x))

          if state.save_all_aux:
            state.aux.append(aux)
          else:
            if  len(state.objective_function) == 0:
               state.aux = [aux]  
            else:   
             if output < state.objective_function[-1]:
               #Save only for the best g
               state.aux = [aux]   

          state.objective_function.append(output)     

          #Scale the objective function if needed
          if scale is not None:
             output = 1 + output/scale*99
            
            

          return output
    
  
    return objective_optimizer  



def flatten_params_to_vector(params):
    """
    Convert nested parameter structure to a single 1D vector.
    
    Args:
        params: Nested structure of parameters (e.g., list of tuples of arrays)
        
    Returns:
        flat_vector: 1D jnp.array containing all parameters
        unflatten_fn: Function to convert flat vector back to original structure
        bounds: N×2 array where each row is [lower_bound, upper_bound]
    """
    # Step 1: Flatten tree structure to list of arrays
    flat_params, tree_def = jax.tree_util.tree_flatten(params)
    
    # Step 2: Store shapes for reconstruction
    shapes = [p.shape for p in flat_params]
    
    # Step 3: Flatten each array and concatenate into single vector
    flat_vector = jnp.concatenate([p.flatten() for p in flat_params])

    
    # Step 6: Create unflatten function
    def unflatten_fn(vector):
        """Convert 1D vector back to original parameter structure."""
        reconstructed_arrays = []
        start_idx = 0
        
        for shape in shapes:
            size = int(jnp.prod(jnp.array(shape)))
            end_idx = start_idx + size
            array = vector[start_idx:end_idx].reshape(shape)
            reconstructed_arrays.append(array)
            start_idx = end_idx
            
        return jax.tree_util.tree_unflatten(tree_def, reconstructed_arrays)
    
    return flat_vector, unflatten_fn


def CCSA(func,param,lower_bound,upper_bound,maxiter=100):

    params_flat,unflatten_fn = flatten_params_to_vector(param)

    if np.isscalar(lower_bound):
       lower_bound = lower_bound * jnp.ones(len(params_flat))
       upper_bound = upper_bound * jnp.ones(len(params_flat))
    else:
      
       lower_bound,_ = flatten_params_to_vector(lower_bound)  
       upper_bound,_ = flatten_params_to_vector(upper_bound)

    bounds =  jnp.column_stack([lower_bound,upper_bound])

    

    def enhanced_func(x):
        params = unflatten_fn(x)
        g = func(params)
        return g, ({'Loss':g}, {})

    state    = State()
    x        = MMA(enhanced_func,
                    bounds  = bounds,
                    nDOFs   = len(params_flat),
                    x0      = params_flat,
                    state   = state,
                    verbose= True,
                    maxiter = maxiter) 

    return unflatten_fn(x),state.objective_function

       
     
    



def MMA(objective,**kwargs):


    #Parse options---
    nDOFs      = int(kwargs['nDOFs'])

    #Scale
    scale = kwargs.setdefault('scaling',None)

    state_verbosity = kwargs.setdefault('state_verbosity',1)

    #This works only if 2D and square grid
    #nDOFs,unfolds = get_symmetry(N_full,kwargs.setdefault('symmetry',None))

    state = kwargs['state']

    bounds  = kwargs.setdefault('bounds',[]) 
    if len(bounds) == 0:
       upper_bounds =  np.ones(nDOFs)
       lower_bounds =  np.ones(nDOFs)*1e-18
    elif bounds.ndim == 1:  

       #bounds = np.array(bounds).repeat((1,nDOFs),axis=0).T
       bounds = np.tile(bounds, (nDOFs, 1))
       lower_bounds = bounds[:,0]  
       upper_bounds = bounds[:,1]  
    else:    
       lower_bounds = bounds[:,0]  
       upper_bounds = bounds[:,1]  



    #--------------------------------------   
    
    constraints = kwargs.setdefault('constraints',[])
    #First guess---------------------------
    #carry = kwargs.setdefault('carry',{})
    x  = kwargs.setdefault('x0',[])
    if len(x) == 0:
        x = lower_bounds +  np.random.rand(nDOFs)*(upper_bounds-lower_bounds)
    else:
        x = jnp.array(x, dtype=jnp.float64)    


        
    shape_in                   = jax.ShapeDtypeStruct((nDOFs,), jnp.float64)

    max_iter                   = kwargs.setdefault('maxiter',40)
    rel_tol                    = kwargs.setdefault('rel_tol',None)
    abs_tol                    = kwargs.setdefault('abs_tol',None)
    constraint_tol             = kwargs.setdefault('constraint_tol',1e-12)
    verbose                    = kwargs.setdefault('verbose',False)

    #Init 
    #transform = kwargs.setdefault('transform',lambda x:x)

    opt = nlopt.opt(nlopt.LD_CCSAQ,nDOFs)
    #opt = nlopt.opt(nlopt.LD_MMA,nDOFs)

    #opt = nlopt.opt(nlopt.LD_LBFGS,nDOFs)
    

    
    opt.set_lower_bounds(lower_bounds)
    opt.set_upper_bounds(upper_bounds)
   

    all_none = all(x is None for x in constraints)

    opt.set_min_objective(enhance_objective_function(objective,state,not all_none,scale,state_verbosity=state_verbosity))

 
    #Add inequality constraints
    for k,constraint in enumerate(constraints):
        
        if constraint is None:
           continue
        
        adapt=False
 
        if len(jax.eval_shape(constraint, shape_in)[0].shape) == 0:
         N_constraints = 1
         adapt = True
        else:
         N_constraints = jax.eval_shape(constraint, shape_in)[0].shape[0]

        opt.add_inequality_mconstraint(enhance_inequality_constraint(constraint,state,k,k==len(constraints)-1,adapt=adapt,state_verbosity=state_verbosity),N_constraints*[constraint_tol])


    opt.set_maxeval(max_iter)

    if rel_tol is not None:
         opt.set_ftol_rel(rel_tol)

    if abs_tol is not None:
         opt.set_ftol_abs(abs_tol)

    if verbose:
         opt.set_param("verbosity",1)
    #opt.set_stopval(tol)
  

    x = opt.optimize(x)

    state.solution = x

    
    return jnp.array(x)
  


@dataclass
class Optimizer:
    func: Callable[[jnp.ndarray], jnp.ndarray]     
    low_bounds:  jnp.ndarray
    high_bounds: jnp.ndarray
    maxiter: int = 50 
    verbose: bool = True 
   

    def regression(self,F_target,x0=jnp.array([])):

          #set up objective
          @jax.jit
          def objective(x):

             output = self.func(x.reshape(self.low_bounds.shape))

             g = jnp.linalg.norm(output-F_target)/jnp.linalg.norm(F_target)

             return g,({'g':g},{'x':jnp.array(x).reshape(self.low_bounds.shape),'output':output})
          
          bounds = jnp.column_stack((self.low_bounds.flatten(),self.high_bounds.flatten()))

          state    = State()
          x        = MMA(objective,
                     bounds = bounds,
                     nDOFs = len(self.low_bounds.flatten()) ,
                     x0 = x0.flatten() if len(x0) > 0 else [],
                     state = state,
                     state_verbosity = self.verbose,
                     maxiter=self.maxiter) 
          
    
          evolution = [i['x'] for i in state.aux]

          output_evolution = [i['output'] for i in state.aux]

          aux = {'evolution': jnp.array(evolution), 'output_evolution': jnp.array(output_evolution),'cost_function':state.objective_function}

          return x.reshape(self.low_bounds.shape), aux



    
    def MSE(self,x,y,params):

          @jax.jit
          def objective(params):

             output = self.func(params,x)

             g = jnp.linalg.norm(output-y)/jnp.linalg.norm(y)

             return g,({'g':g},{})
          
          bounds = jnp.column_stack((self.low_bounds.flatten(),self.high_bounds.flatten()))

          state    = State()
          
          params        = MMA(objective,
                         bounds = bounds,
                         nDOFs = len(params) ,
                         x0 =params,
                         state = state,
                         state_verbosity = self.verbose,
                         maxiter=self.maxiter) 
          
          return params,state.objective_function[-1]
    
          

    def test_regression(self,x0: jnp.ndarray= None,x_target: jnp.ndarray= None,rtol: float = 1e-5,atol: float = 1e-5):
       """Test the regression capability of the optimizer."""

       key        = jax.random.PRNGKey(0)
       key1, key2 = jax.random.split(key)

       if x_target is None:
           x_target   =  jax.random.uniform(key1, shape=self.low_bounds.shape, minval=self.low_bounds, maxval=self.high_bounds)

       if x0 is None:
           x0        =  jax.random.uniform(key2, shape=self.low_bounds.shape, minval=self.low_bounds, maxval=self.high_bounds)


       F_target = self.func(x_target)

       x_opt = self.regression(F_target,x0)[0]

       print(jnp.allclose(x_opt, x_target, rtol=rtol,atol=atol))