
from ._src.defaults import (
    set_default_xp as set_default_xp,
    get_default_xp as get_default_xp,
    default_xp as default_xp,
    set_default_eager as set_default_eager,
    get_default_eager as get_default_eager,
    default_eager as default_eager,
)

from ._src.space import Space as Space
from ._src.dimension import (
    Dimension as Dimension,
    dim as dim,
)

from ._src.array import (
    abs as abs,
    Array as Array,
)

from ._src.creation_functions import (
   array as array,
   coords_from_dim as coords_from_dim,
   coords_from_arr as coords_from_arr,
   full as full,
)
from ._src.statistical_functions import (
    integrate as integrate,
    max as max,
    mean as mean,
    min as min,
    prod as prod,
    sum as sum,
)
from ._src.manipulation_functions import (
    permute_dims as permute_dims
)


from ._src.tools import (
    shift_freq as shift_freq,
    shift_pos as shift_pos,
)

from ._src.jax_pytrees import jax_register_pytree_nodes as jax_register_pytree_nodes

from ._src.elementwise_functions import (
    acos as acos,
    acosh as acosh,
    add as add,
    angle as angle,
    asin as asin,
    asinh as asinh,
    atan as atan,
    atan2 as atan2,
    atanh as atanh,
    bitwise_and as bitwise_and,
    bitwise_left_shift as bitwise_left_shift,
    bitwise_invert as bitwise_invert,
    bitwise_or as bitwise_or,
    bitwise_right_shift as bitwise_right_shift,
    bitwise_xor as bitwise_xor,
    ceil as ceil,
    clip as clip,
    conj as conj,
    copysign as copysign,
    cos as cos,
    cosh as cosh,
    divide as divide,
    equal as equal,
    exp as exp,
    expm1 as expm1,
    floor as floor,
    floor_divide as floor_divide,
    greater as greater,
    greater_equal as greater_equal,
    hypot as hypot,
    imag as imag,
    isfinite as isfinite,
    isinf as isinf,
    isnan as isnan,
    less as less,
    less_equal as less_equal,
    log as log,
    log1p as log1p,
    log2 as log2,
    log10 as log10,
    logaddexp as logaddexp,
    logical_and as logical_and,
    logical_not as logical_not,
    logical_or as logical_or,
    logical_xor as logical_xor,
    maximum as maximum,
    minimum as minimum,
    multiply as multiply,
    negative as negative,
    not_equal as not_equal,
    positive as positive,
    pow as pow,
    real as real,
    remainder as remainder,
    round as round,
    sign as sign,
    signbit as signbit,
    sin as sin,
    sinh as sinh,
    square as square,
    sqrt as sqrt,
    subtract as subtract,
    tan as tan,
    tanh as tanh,
    trunc as trunc,
)

try:
   from ._src.constraint_solver import dim_from_constraints as dim_from_constraints
except ModuleNotFoundError:
    from typing import Optional, Literal, Union, List
    def dim_from_constraints(
         name: str,
         *,
         n: Union[int, Literal["power_of_two", "even"]] = "power_of_two",
         d_pos: Optional[float] = None,
         d_freq: Optional[float] = None,
         pos_min: Optional[float] = None,
         pos_max: Optional[float] = None,
         pos_middle: Optional[float] = None,
         pos_extent: Optional[float] = None,
         freq_min: Optional[float] = None,
         freq_max: Optional[float] = None,
         freq_extent: Optional[float] = None,
         freq_middle: Optional[float] = None,
         loose_params: Optional[Union[str, List[str]]] = None,
         dynamically_traced_coords: bool = False,
    ) -> Dimension:
      raise ModuleNotFoundError("You need to install `fftarray[dimsolver]` to use the constraint solver.")


__all__ = [
    g for g in globals() if (
       not g.startswith("_") and g not in ["Optional", "List", "Union", "Literal"]
    )
]
