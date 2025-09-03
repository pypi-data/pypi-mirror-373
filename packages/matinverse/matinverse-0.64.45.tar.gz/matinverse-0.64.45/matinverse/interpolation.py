import jax.numpy as jnp

def fast_interpolation(fine, coarse, bound=False, scale='linear'):
    """Vectorized Interpolation in JAX"""
    if scale == 'log':
        fine = jnp.log10(fine)
        coarse = jnp.log10(coarse)

    # Find indices for interpolation
    m2 = jnp.argmax(coarse >= fine[:, None], axis=1)
    m1 = m2 - 1

    # Calculate weights
    a2 = (fine - coarse[m1]) / (coarse[m2] - coarse[m1])
    a1 = 1 - a2

    if bound == 'periodic':
        Delta = coarse[-1] - coarse[-2]
        a = jnp.where(m2 == 0)[0]
        m1 = m1.at[a].set(len(coarse) - 1)
        m2 = m2.at[a].set(0)
        fine = fine.at[fine < Delta / 2].add(2 * jnp.pi)
        a2 = a2.at[a].set((fine[a] - coarse[-1]) / Delta)
        a1 = 1 - a2

    elif bound == 'extent':
        # Small values
        al = jnp.where(fine < coarse[0])[0]
        m1 = m1.at[al].set(0)
        m2 = m2.at[al].set(1)
        a2 = a2.at[al].set((fine[al] - coarse[0]) / (coarse[1] - coarse[0]))
        a1 = 1 - a2

        # Large values
        ar = jnp.where(fine > coarse[-1])[0]
        m1 = m1.at[ar].set(len(coarse) - 2)
        m2 = m2.at[ar].set(len(coarse) - 1)
        a2 = a2.at[ar].set((fine[ar] - coarse[-2]) / (coarse[-1] - coarse[-2]))
        a1 = 1 - a2

    return a1, a2, m1, m2
