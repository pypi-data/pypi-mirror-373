import jax
import jax.numpy as jnp

arr = jnp.array([1,2,3,4])*1.j

def step_fun(arr, _):
    arr = jnp.fft.fftn(arr)
    return arr, None

jax.lax.scan(
    step_fun,
    init=arr,
    length=2,
)