import numba
import numpy as np
from numba import prange
import time

@numba.njit()
def circular_kantorovich(x, y, p=1):
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


    mu = np.median((x_cdf - y_cdf) ** p)

    # Now we just want minkowski distance on the CDFs shifted by mu
    result = 0.0
    if p > 2:
        for i in range(x_cdf.shape[0]):
            result += np.abs(x_cdf[i] - y_cdf[i] - mu) ** p

        return result ** (1.0 / p)

    elif p == 2:
        for i in range(x_cdf.shape[0]):
            val = x_cdf[i] - y_cdf[i] - mu
            result += val * val

        return np.sqrt(result)

    elif p == 1:
        for i in range(x_cdf.shape[0]):
            result += np.abs(x_cdf[i] - y_cdf[i] - mu)

        return result

    else:
        raise ValueError("Invalid p supplied to Kantorvich distance")


@numba.njit()
def circular_euclidean_kantorovich(x: np.ndarray, y: np.ndarray):
    """
    Compute the circular Euclidean Kantorovich (Wasserstein) distance between two discrete distributions.

    Suitable for comparing distributions of circular data such as angles, time-of-day, phase etc.

    :param: np.ndarray x: 1D array representing the first discrete distribution or histogram.
    :param: np.ndarray x: 1D array representing the second discrete distribution or histogram.

    .. note::
       Distance metric: smaller values represent similar distributions.
       Adapted from `pynndescent <https://pynndescent.readthedocs.io/en/latest/>`_.

    :example:
    >>> x, y = np.random.normal(loc=65, scale=10, size=10000000), np.random.normal(loc=90, scale=1, size=10000000)
    >>> b =circular_euclidean_kantorovich(x, y)
    """
    x_sum, y_sum = np.sum(x), np.sum(y)
    x_cdf, y_cdf = x / x_sum, y / y_sum
    x_cdf, y_cdf = np.cumsum(x_cdf), np.cumsum(y_cdf)
    mu = np.median((x_cdf - y_cdf) ** 2)
    result = 0.0
    for i in prange(x_cdf.shape[0]):
        val = x_cdf[i] - y_cdf[i] - mu
        result += val * val
    return np.sqrt(result)



    #
    # elif p == 1:
    #     for i in range(x_cdf.shape[0]):
    #         result += np.abs(x_cdf[i] - y_cdf[i] - mu)
    #
    #     return result
    #
    # else:
    #     raise ValueError("Invalid p supplied to Kantorvich distance")
    #



x, y = np.random.normal(loc=80, scale=1, size=100000000), np.random.normal(loc=90, scale=1, size=100000000)

start = time.time()
a = circular_kantorovich(x, y, 2)
print(time.time() - start)

start = time.time()
b =circular_euclidean_kantorovich(x, y)
print(time.time() - start)

