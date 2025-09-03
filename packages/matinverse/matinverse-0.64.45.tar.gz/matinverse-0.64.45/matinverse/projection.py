from jax import numpy as jnp
import jax
from functools import partial
import equinox as eqx
from matinverse.utils import compute_gradient,compute_hessian


@partial(jax.jit, static_argnames=['eta'])
def tanh_projection(x: jnp.array, 
                    beta: float,
                    eta: float) -> jnp.array:

    def step(x):    
        return jnp.where(x > eta, 1.0, 0.)
    
 
    def general(x):
        
        return (jnp.tanh(beta * eta) + jnp.tanh(beta * (x - eta))) / (
            jnp.tanh(beta * eta) + jnp.tanh(beta * (1 - eta))
        )
    

    return jax.lax.cond(beta == jnp.inf,step,general,x)



@eqx.filter_jit
def projection(
    rho_filtered: jnp.array,
    beta: float,
    resolution: float,
    eta: float = 0.5,
    SSP2: bool = False,
    periodic: list[bool] = [False, False],
    gradient_order: str = 'linear',
    hessian_order: str = 'cubic2',
    padding: bool = True
    ):   
       
        dx          = 1 / resolution
        dy          = 1 / resolution
        R_smoothing = 0.55 * dx
        
        rho_projected = tanh_projection(rho_filtered, beta=beta, eta=eta)


        if not SSP2:
          
       

         rho_filtered_grad = compute_gradient(rho_filtered,periodic=periodic,d=[dx,dy],order=gradient_order,padding=padding)

         den_helper = rho_filtered_grad[0]** 2 + rho_filtered_grad[1] ** 2

       
        else:
 
        
         rho_filtered_grad    = compute_gradient(rho_filtered,periodic=periodic,d=[dx,dy],order=gradient_order,padding=padding)
         rho_filtered_hessian = compute_hessian(rho_filtered,periodic=periodic,d=[dx,dy],order=hessian_order,padding=padding)



         rho_filtered_grad_helper    = rho_filtered_grad[0]**2      + rho_filtered_grad[1]**2
         rho_filtered_hessian_helper = rho_filtered_hessian[0,0]**2 + rho_filtered_hessian[0,1]**2  + rho_filtered_hessian[1,0]**2 + rho_filtered_hessian[1,1]**2
         den_helper   = rho_filtered_grad_helper + rho_filtered_hessian_helper * R_smoothing**2

         #den_helper = den_helper.T


        nonzero_norm = jnp.abs(den_helper) > 0

        den_norm = jnp.sqrt(jnp.where(nonzero_norm, den_helper, 1))

        den_eff = jnp.where(nonzero_norm, den_norm, 1)

        # The distance for the center of the pixel to the nearest interface
        d = (eta - rho_filtered)/ den_eff


        #return d

        # Only need smoothing if an interface lies within the voxel. Since d is
        # actually an "effective" d by this point, we need to ignore values that may
        # have been sanitized earlier on.
        needs_smoothing = nonzero_norm & (jnp.abs(d) < R_smoothing)


        # The fill factor is used to perform simple, first-order subpixel smoothing.
        # We use the (2D) analytic expression that comes when assuming the smoothing
        # kernel is a circle. Note that because the kernel contains some
        # expressions that are sensitive to NaNs, we have to use the "double where"
        # trick to avoid the Nans in the backward trace. This is a common problem
        # with array-based AD tracers, apparently. See here:
        # https://github.com/google/jax/issues/1052#issuecomment-5140833520
        d_R = d / R_smoothing

        F_plus = jnp.where(
            needs_smoothing, 0.5 - 15 / 16 * d_R + 5 / 8 * d_R**3 - 3 / 16 * d_R**5, 1.0
        )
        # F(-d)
        F_minus = jnp.where(
            needs_smoothing, 0.5 + 15 / 16 * d_R - 5 / 8 * d_R**3 + 3 / 16 * d_R**5, 1.0
        )

        # Determine the upper and lower bounds of materials in the current pixel (before projection).
        rho_filtered_minus = rho_filtered - R_smoothing * den_eff * F_plus
        rho_filtered_plus  = rho_filtered + R_smoothing * den_eff * F_minus

        # Finally, we project the extents of our range.
        rho_minus_eff_projected = tanh_projection(rho_filtered_minus, beta=beta, eta=eta)
        rho_plus_eff_projected = tanh_projection(rho_filtered_plus, beta=beta, eta=eta)


        # Only apply smoothing to interfaces
        rho_projected_smoothed = (
            (1-F_plus)
        ) * rho_minus_eff_projected + F_plus * rho_plus_eff_projected



        return jnp.where(
            needs_smoothing,
            rho_projected_smoothed,
            rho_projected
        )
    


# @jax.jit
# def projection(
#     rho_filtered: jnp.array,
#     beta: float,
#     resolution: float,
#     eta: float = 0.5
#     ):   
       
#         dx          = 1 / resolution
#         dy          = 1 / resolution
#         R_smoothing = 0.55 * dx

       
#         #N = int(np.sqrt(len(rho_filtered)))
#         #rho_filtered = rho_filtered.reshape((N, N))

#         #Reshape to 2D
#         rho_projected = tanh_projection(rho_filtered, beta=beta, eta=eta)

#         # Compute the spatial gradient (using finite differences) of the *filtered*
#         # field, which will always be smooth and is the key to our approach. This
#         # gradient essentially represents the normal direction pointing the
#         # nearest inteface.
       
#         rho_filtered_grad = jnp.gradient(rho_filtered)
#         rho_filtered_grad_helper = (rho_filtered_grad[0] / dx) ** 2 + (
#             rho_filtered_grad[1] / dy
#         ) ** 2


#         # Note that a uniform field (norm=0) is problematic, because it creates
#         # divide by zero issues and makes backpropagation difficult, so we sanitize
#         # and determine where smoothing is actually needed. The value where we don't
#         # need smoothings doesn't actually matter, since all our computations our
#         # purely element-wise (no spatial locality) and those pixels will instead
#         # rely on the standard projection. So just use 1, since it's well behaved.
#         nonzero_norm = jnp.abs(rho_filtered_grad_helper) > 0

#         rho_filtered_grad_norm = jnp.sqrt(
#             jnp.where(nonzero_norm, rho_filtered_grad_helper, 1)
#         )
#         rho_filtered_grad_norm_eff = jnp.where(nonzero_norm, rho_filtered_grad_norm, 1)

#         # The distance for the center of the pixel to the nearest interface
#         d = (eta - rho_filtered) / rho_filtered_grad_norm_eff

#         # Only need smoothing if an interface lies within the voxel. Since d is
#         # actually an "effective" d by this point, we need to ignore values that may
#         # have been sanitized earlier on.
#         needs_smoothing = nonzero_norm & (jnp.abs(d) < R_smoothing)


#         # The fill factor is used to perform simple, first-order subpixel smoothing.
#         # We use the (2D) analytic expression that comes when assuming the smoothing
#         # kernel is a circle. Note that because the kernel contains some
#         # expressions that are sensitive to NaNs, we have to use the "double where"
#         # trick to avoid the Nans in the backward trace. This is a common problem
#         # with array-based AD tracers, apparently. See here:
#         # https://github.com/google/jax/issues/1052#issuecomment-5140833520
#         d_R = d / R_smoothing
#         F_plus = jnp.where(
#             needs_smoothing, 0.5 - 15 / 16 * d_R + 5 / 8 * d_R**3 - 3 / 16 * d_R**5, 1.0
#         )
#         # F(-d)
#         F_minus = jnp.where(
#             needs_smoothing, 0.5 + 15 / 16 * d_R - 5 / 8 * d_R**3 + 3 / 16 * d_R**5, 1.0
#         )

#         # Determine the upper and lower bounds of materials in the current pixel (before projection).
#         rho_filtered_minus = rho_filtered - R_smoothing * rho_filtered_grad_norm_eff * F_plus
#         rho_filtered_plus  =  rho_filtered + R_smoothing * rho_filtered_grad_norm_eff * F_minus
        

#         # Finally, we project the extents of our range.
#         rho_minus_eff_projected = tanh_projection(rho_filtered_minus, beta=beta, eta=eta)
#         rho_plus_eff_projected = tanh_projection(rho_filtered_plus, beta=beta, eta=eta)

       
#         rho_projected_smoothed = (1-F_plus) * rho_minus_eff_projected + F_plus * rho_plus_eff_projected
#         return jnp.where(
#             needs_smoothing,
#             rho_projected_smoothed,
#             rho_projected,
#         ).flatten()
    
