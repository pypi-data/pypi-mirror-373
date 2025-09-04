# from bokeh.plotting import figure
# from bokeh.io import export_png
# import numpy as np

# fig = figure(
#     title=r"$$\pi$$",
#     x_axis_label=r"$$\pi$$",
# )
# fig.line(np.array([1,2,3]), np.array([1,2,3]))
# export_png(fig, filename="test.png")

# import array_api_strict as xp
# import numpy as np
# import fftarray as fa
# import jax.numpy as jnp
# import jax
# fa.jax_register_pytree_nodes()
# fa.set_default_xp(jnp)

# dim_x = fa.Dimension("x", 4, 0.5, 0., 0., dynamically_traced_coords=True)

# @jax.jit
# def my_fun(dim1, dim2):
#     arr1 = fa.coords_from_dim(dim1, "pos")
#     arr2 = fa.coords_from_dim(dim2, "pos")
#     return arr1+arr2

# print(my_fun(dim_x, dim_x))

# fa_arr = fa.array(5., [], [])
# fa_arr2 = fa.array(5., [], [])
# xp_arr = xp.asarray(2.)

# print(fa_arr + xp_arr)
# print(xp_arr + fa_arr)

# import fftarray as fa
# import jax
# import jax.numpy as jnp
# fa.jax_register_pytree_nodes()

# dim_x = fa.dim("x", 4, 0.1, 0., 0.)
# arr: fa.Array = fa.coords_from_dim(dim_x, "pos", xp=jnp)

# ### Concrete index value
# concerete_index_value = 3
# def indexing(arr):
#     return arr.isel(x=concerete_index_value)

# static_indexer = jax.jit(indexing)
# static_indexer(arr) # no error

# ### Mark index arg as static
# def indexing(arr, indexer: int):
#     return arr.isel(x=indexer)

# static_indexer = jax.jit(indexing, static_argnames="indexer")

# # static_indexer(arr, 3) # no error
# import fftarray as fa
# fa.jax_register_pytree_nodes()
# import jax.numpy as jnp
# x_dim = fa.dim(name="x", n=8, d_pos=0.4, pos_min=0, freq_min=0)
# arr: fa.Array = fa.coords_from_dim(x_dim, "pos", xp=jnp)

# from functools import partial
# import jax

# @jax.jit
# def compile_time_indexing(arr):
#     """
#         The index is computed at compile time.
#     """
#     concerete_index_value = 3
#     return arr.sel(x=1.6)
#     # return arr.isel(x=concerete_index_value)

# compile_time_indexing(arr)

# import fftarray as fa
# import numpy as np
# print(repr(fa.dim_from_constraints("x", n=2048, pos_min=-100., pos_max=50.,
# freq_middle=0.)))
# print(repr( fa.dim_from_constraints("x", d_pos=0.1, d_freq=0.05, pos_min=-9.,
# freq_min=-6.4, n="power_of_two", loose_params=["d_pos"])))

# dim = fa.dim_from_constraints("x", d_pos=0.1, d_freq=0.05, pos_min=-9.,
# freq_min=-6.4, n="power_of_two", loose_params=["d_pos"])
# print(dim.values("pos"))
# print(fa.coords_from_dim(dim, "pos"))

# dim_x: fa.Dimension = fa.dim("x", pos_min=-0.1, freq_min=0., d_pos=0.2, n=4)
# print(dim_x)
# arr_x: fa.Array = fa.coords_from_dim(dim_x, "pos")
# print(arr_x)
# dim_x = fa.dim("x", pos_min=-0.1, freq_min=0., d_pos=0.2, n=4)
# np_values = np.array([5.,6.,7.,8.])
# arr_pos = fa.array(np_values, [dim_x], "pos")
# print(arr_pos)
# import numpy as np

# arr_freq = arr_pos.into_space("freq") # change space: "pos" -> "freq"
# arr_pos = arr_freq.into_space("pos") # change space: "freq" -> "pos"
# arr_pos = arr_pos.into_space("pos") # No operation done because unnecessary.


# dim_x = fa.dim_from_constraints("x", pos_min=-1., pos_max=0., n=2, freq_middle=0.)
# dim_y = fa.dim_from_constraints("y", pos_min=-2., pos_max=1., n=4, freq_middle=0.)
# arr_x = fa.coords_from_dim(dim_x, "pos")
# arr_y = fa.coords_from_dim(dim_y, "pos")
# arr_gauss_2d = fa.exp(-(arr_x**2 + arr_y**2)/0.2) # same width along x and y, centered around (x,y)=(0,0)
# print(arr_gauss_2d)
# print(arr_gauss_2d.sel({"x": dim_x.pos_middle, "y": dim_y.pos_middle}, method="nearest"))
# print(arr_gauss_2d.isel({"y": slice(0,3)}))

# import fftarray as fa

# # Compute the dimension properties.
# dim_x = fa.dim_from_constraints("x", pos_min=-1., pos_max=1., n=1024, freq_middle=0.)

# # Initialize the coordinate grids in position and frequency space.
# # Those are real-valued and therefore have to have factors_applied=True.
# # They default to eager=False.
# arr_x = fa.coords_from_dim(dim_x, "pos")
# arr_f = fa.coords_from_dim(dim_x, "freq") # $\samplesFreq$

# # The result of the square with factors_applied=True is again factors_applied=True
# arr_pos1 = arr_x**2 # $\samplesPos$
# # Changing the space leaves the array with factors_applied=False. The factors have not been applied yet.
# arr_freq1 = arr_pos1.into_space("freq")

# arr_freq2 = arr_freq1 * arr_f

# # Because arr_freq2 is in the fft representation (G^fft_m) the ifft can be applied directly.
# # Therefore this is only a call to ifft, no factors in frequency or position space necessary before the transformation.
# arr_pos2 = arr_freq2.into_space("pos") # $\samplesPosFFT$
# # eager=False acts as a tie breaker, so the result has factors_applied=False.
# arr_freq3 = arr_freq2 + 5

# arr_freq3 = fa.exp(arr_freq2)
# np_arr_freq2 = arr_freq2.values("freq")

# arr_freq4 = fa.abs(arr_freq2)

# import jax.numpy as jnp
# import fftarray as fa
# dim_x = fa.dim_from_constraints("x", pos_min=-1., pos_max=1., n=4, freq_middle=0.)
# arr_g_x_jax = fa.coords_from_dim(dim_x, "pos", xp=jnp)
# print(arr_g_x_jax)
# arr_lin_jax = fa.array(jnp.linspace(0., 1.5, 4), dim_x, "pos")
# print(arr_lin_jax)

# import pytest
# import fftarray as fa
# import jax
# fa.jax_register_pytree_nodes()
# fa.set_default_xp(jax.numpy)

# dim_x = fa.Dimension("x", 4, 0.5, 0., 0., dynamically_traced_coords=True)

# @jax.jit
# def my_fun(dim1: fa.Dimension) -> fa.Array:
#     arr1 = fa.coords_from_dim(dim1, "pos")
#     arr2 = fa.coords_from_dim(dim1, "pos")

#     # Works, because both arrays use the same dimension with the same tracers.
#     return arr1+arr2

# my_fun(dim_x)

# @jax.jit
# def my_fun_not_dynamic(dim1: fa.Dimension, dim2: fa.Dimension) -> fa.Array:
#     arr1 = fa.coords_from_dim(dim1, "pos")
#     arr2 = fa.coords_from_dim(dim2, "pos")

#     # Addition requires all dimensions with the same name to be equal, this is explicitly checked before the operation.
#     # The check for equality fails with a `jax.errors.TracerBoolConversionError` because the coordinate grids' values of the `Dimension`s are only known at runtime.
#     # If `dynamically_traced_coords` above were set to False, the exact values of `dim1` and `dim2` were available at trace time and therefore this addition would succeed.
#     return arr1+arr2



# with pytest.raises(jax.errors.TracerBoolConversionError):
#     my_fun_not_dynamic(dim_x, dim_x)

# import numpy as np
# import fftarray as fa

# # Test function and its derivative
# g = lambda x: fa.cos(x)*fa.exp(-(x-1.25)**2/25.)
# g_d1 = lambda x: ((-(2*(x-1.25))/25.)*fa.cos(x) - fa.sin(x))*fa.exp(-(x-1.25)**2/25.)

# dim_x = fa.dim_from_constraints("x", # dimension name
#     pos_min=-40., pos_max=50., d_pos=.5, # position space grid
#     freq_middle=0., # frequency grid offset
#     loose_params=["d_pos"], # The resulting d_pos in dim_x will be made smaller than the input d_pos such that N is a power of two.
# )
# x = fa.coords_from_dim(dim_x, "pos") # position space coordinate grid
# f = fa.coords_from_dim(dim_x, "freq") # frequency space coordinate grid
# sampled_fn = g(x) # sample the function in position space

# # Compute the derivative
# order = 1 # Order of the derivative
# derivative_kernel = (2*np.pi*1.j*f)**order
# g_d1_numeric = (sampled_fn.into_space("freq")*derivative_kernel).into_space("pos")

# # Compute the expected result directly from the analytic derivative.
# d1_analytic = g_d1(x)

# # Compare the numeric and analytical result.
# # In this example with these domains they are equal to at least eleven decimal digits.
# np.testing.assert_array_almost_equal(g_d1_numeric.values("pos"), d1_analytic.values("pos"), decimal=11)


from scipy.constants import hbar
import numpy as np
import fftarray as fa

def split_step(psi0: fa.Array, *,
               dt: float,
               mass: float,
               V: fa.Array,
            ) -> fa.Array:
    k_sq = 0.
    for dim in psi0.dims:
        # Using coords_from_arr ensures that attributes
        # like eager and xp do match the ones of psi.
        k_sq = k_sq + (2*np.pi*fa.coords_from_arr(psi0, dim.name, "freq"))**2

    psi1 = psi0.into_space("freq") * fa.exp((-1.j * hbar/(2*mass) * dt/2) * k_sq)
    psi2 = psi1.into_space("pos") * fa.exp((-1.j * hbar * dt) * V)
    psi3 = psi2.into_space("freq") * fa.exp((-1.j * hbar/(2*mass) * dt/2) * k_sq)
    return psi3

import numpy as np
from scipy.constants import hbar

# Rb87 mass in kg
mass_rb87: float = 86.909 * 1.66053906660e-27
# Rb87 D2 transition wavelength in m
lambda_L: float = 780 * 1e-9
# Bragg beam wave vector
k_L: float = 2 * np.pi / lambda_L
hbark: float = hbar * k_L
# Single-Photon recoil frequency
w_r = hbar * k_L**2 / (2 * mass_rb87)

def simulate_bragg(t_arr, dt: float, rabi_frequency, ramp_arr, xp=np, dtype=np.float64):
    # Returns the wave function after applying the Bragg beam potential to a Gaussian input state with 0.01 hbark initial momentum width. The beam is assumed to be spatially homogeneous.
    # t_arr: NumPy array containing the $t$ of each time step.
    # dt: Size of a time step
    # rabi_frequency: Sets the magnitude of $\Omega(t)$, determined by the concretely used atom transition and laser detuning and intensity.
    # ramp_arr: Scaling factor for $\Omega(t)$ for each time step.
    # $\Omega(t)$ = rabi_frequency*ramp_arr


    # Dimension for full sequence based on expected matter wave size and expansion speed
    dim_x: fa.Dimension = fa.dim_from_constraints("x",
        pos_extent = 2e-3,
        pos_middle = 0,
        freq_middle = 0.,
        freq_extent = 32. * k_L/(2*np.pi),
        loose_params = ["freq_extent"]
    )
    # Initialize array with position coordinates.
    x: fa.Array = fa.coords_from_dim(dim_x, "pos", xp=xp, dtype=dtype)

    # Initialize harmonic oscillator ground state
    sigma_p=0.01*hbark
    psi: fa.Array = (2 * sigma_p**2 / (np.pi*hbar**2))**(1./4.) * fa.exp(-(sigma_p**2 / hbar**2) * x**2)
    # Numerically normalize so that the norm is `1.` even though the tails of the Gaussian are cut off.
    psi *= fa.sqrt(1./fa.integrate(fa.abs(psi)**2))

    # For each time step, compute the potential and evolve the wave function in it
    for t, ramp in zip(t_arr, ramp_arr):
        V = rabi_frequency * ramp * 2. * hbar * fa.cos(
            k_L * x - 2. * w_r * t
        )**2
        psi: fa.Array = split_step(
            psi,
            dt=dt,
            mass=mass_rb87,
            V=V,
        )

    return psi

rabi_frequency = 50*w_r
n_steps = 200
t_arr, dt = np.linspace(0., 1e-6, n_steps, retstep=True, endpoint=False)
ramp_arr = np.full(n_steps, 1.)
# psi = simulate_bragg(t_arr, dt, rabi_frequency, ramp_arr)

# Use an odd number of steps to symmetrically sample the Gaussian
# and hit its peak at t=0 with a sample.
# Note that this snippet does not start at t=0 like above, but is symmetric around t=0.
n_steps = 401
# Rabi frequency. This specific value was found as a binary search to
# optimize a 50/50 split of the two momentum classes for this specific beam
# splitter duration and pulse form.
rabi_frequency = 25144.285917282104 # Hz
sigma_bs = 25e-6 # temporal pulse width (s)
# The Gaussian is sampled  from -4*sigma_bs to 4*sigma_bs
sampling_range_mult = 4.
t_arr, dt = np.linspace(
    start=-sampling_range_mult*sigma_bs,
    stop=sampling_range_mult*sigma_bs,
    num=n_steps,
    retstep=True,
)
# Gaussian density function
gauss = lambda t, sigma: np.exp(-0.5 * (t / sigma)**2)
# Remove the value of the Gauss at the beginning of the pulse so that
# the intensity starts and ends at zero.
gauss_offset = gauss(t = t_arr[0], sigma = sigma_bs)
ramp_arr = gauss(t = t_arr, sigma = sigma_bs) - gauss_offset

# psi = simulate_bragg(t_arr, dt, rabi_frequency, ramp_arr)

omega = 0.5*2.*np.pi

dim_x = fa.dim_from_constraints("x",
    pos_min=-100e-6,
    pos_max=100e-6,
    freq_middle=0.,
    n=2048,
)
y_dim = fa.dim_from_constraints("y",
    pos_min=-100e-6,
    pos_max=100e-6,
    freq_middle=0.,
    n=2048,
)

V: fa.Array = 0. # type: ignore
for dim in [dim_x, y_dim]:
    V = V + 0.5 * mass_rb87 * omega**2. * fa.coords_from_dim(dim, "pos")**2

k_sq = 0.
for dim in [dim_x, y_dim]:
    k_sq = k_sq + (2*np.pi*fa.coords_from_dim(dim, "freq"))**2

# Initialize psi as a constant function with value 1.
psi = fa.full(dim_x, "pos", 1.) * fa.full(y_dim, "pos", 1.)
for _ in range(n_steps):

    psi = psi.into_space("pos") * fa.exp((-0.5 / hbar * dt) * V)
    psi = psi.into_space("freq") * fa.exp((-1. * dt * hbar / (2*mass_rb87)) * k_sq)
    psi = psi.into_space("pos") * fa.exp((-0.5 / hbar * dt) * V)

    state_norm = fa.integrate(fa.abs(psi)**2)
    psi = psi * fa.sqrt(1./state_norm)

import jax.numpy as jnp
from functools import reduce

def split_step_imaginary_time(
    psi: fa.Array,
    V: fa.Array,
    dt: float,
    mass: float,
) -> fa.Array:
    """Perform an imaginary time split-step of second order in VPV configuration."""

    # Calculate half step imaginary time potential propagator
    V_prop = fa.exp((-0.5*dt / hbar) * V)
    # Calculate full step imaginary time kinetic propagator (k_sq = kx^2 + ky^2 + kz^2)
    k_sq = reduce(lambda a,b: a+b, [
        (2*np.pi * fa.coords_from_dim(dim, "freq", xp=jnp, dtype=jnp.float64))**2
        for dim in psi.dims
    ])
    T_prop = fa.exp(-dt * hbar * k_sq / (2*mass))

    # Apply half potential propagator
    psi = V_prop * psi.into_space("pos")

    # Apply full kinetic propagator
    psi = T_prop * psi.into_space("freq")

    # Apply half potential propagator
    psi = V_prop * psi.into_space("pos")

    # Normalize after step
    state_norm = fa.integrate(fa.abs(psi)**2)
    psi = psi / fa.sqrt(state_norm)

    return psi