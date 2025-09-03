
import numpy as np
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats

def geometric_mean(x: np.ndarray) -> float:
    """
    Computes the geometric mean of a 1D NumPy array.

    :param x: A 1D NumPy array of numeric type containing non-negative values. Must have at least two elements.
    :return: The geometric mean of the values in `x`.
    :rtype: float
    """

    check_valid_array(data=x,
                      source=f'{geometric_mean.__name__} x',
                      accepted_ndims=(1,),
                      accepted_dtypes=Formats.NUMERIC_DTYPES.value,
                      min_value=0,
                      min_axis_0=2)

    return np.prod(x) ** (1 / x.shape[0])





x = np.random.randint(0, 100, (10, )).astype(np.float32)
geometric_mean(x=x)