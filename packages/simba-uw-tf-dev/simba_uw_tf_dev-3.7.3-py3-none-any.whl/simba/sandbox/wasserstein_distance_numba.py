from numba import njit, jit, prange
import numpy as np


@njit(fastmath=True)
def minkowski(x, y, p=2):
    r"""Minkowski distance.

    .. math::
        D(x, y) = \left(\sum_i |x_i - y_i|^p\right)^{\frac{1}{p}}

    This is a general distance. For p=1 it is equivalent to
    manhattan distance, for p=2 it is Euclidean distance, and
    for p=infinity it is Chebyshev distance. In general it is better
    to use the more specialised functions for those distances.
    """
    result = 0.0
    for i in range(x.shape[0]):
        result += (np.abs(x[i] - y[i])) ** p

    return result ** (1.0 / p)


@njit(fastmath=True)
def wasserstein_1d(x, y, p=1):
    x_sum = 0.0
    y_sum = 0.0
    for i in range(x.shape[0]):
        x_sum += x[i]
        y_sum += y[i]

    x_cdf = x / x_sum
    y_cdf = y / y_sum

    for i in range(1, x_cdf.shape[0]):
        x_cdf[i] += x_cdf[i - 1]
        y_cdf[i] += y_cdf[i - 1]

    return minkowski(x_cdf, y_cdf, p)




def wasserstein_1d():
    pass


x, y = np.random.randint(0, 2, (10, )).astype(np.int8), np.random.randint(0, 2, (10, )).astype(np.int8)
wasserstein_1d(x=x, y=y)




