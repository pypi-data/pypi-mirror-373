import numpy as np
from numba import cuda, jit , njit, float64, float32, prange
from typing import Optional
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats

THREADS_PER_BLOCK = 1024

@njit(cache=True, fastmath=True)
def sokal_sneath(x: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> float64:
    """
    Jitted calculate of the sokal sneath coefficient between two binary vectors (e.g., to classified behaviors). 0 represent independence, 1 represents complete interdependence.

    .. math::
       Sokal-Sneath = \\frac{{f_t + t_f}}{{2 \cdot (t_{{cnt}} + f_{{cnt}}) + f_t + t_f}}

    .. note::
       Adapted from `pynndescent <https://pynndescent.readthedocs.io/en/latest/>`_.

    :param np.ndarray x: First binary vector.
    :param np.ndarray x: Second binary vector.
    :param Optional[np.ndarray] w: Optional weights for each element. Can be classification probabilities. If not provided, equal weights are assumed.
    :returns: sokal sneath coefficient
    :rtype: float

    :example:
    >>> x = np.array([0, 1, 0, 0, 1]).astype(np.int8)
    >>> y = np.array([1, 0, 1, 1, 0]).astype(np.int8)
    >>> Statistics().sokal_sneath(x, y)
    >>> 0.0
    """
    if w is None:
        w = np.ones(x.shape[0]).astype(float32)
    t_cnt, f_cnt, t_f, f_t = 0.0, 0.0, 0.0, 0.0
    for i in prange(x.shape[0]):
        if (x[i] == 1) and (y[i] == 1):
            t_cnt += 1.0 * w[i]
        elif (x[i] == 0) and (y[i] == 0):
            f_cnt += 1.0 * w[i]
        elif (x[i] == 0) and (y[i] == 1):
            f_t += 1.0 * w[i]
        elif (x[i] == 1) and (y[i] == 0):
            t_f += 1.0 * w[i]

    if t_f + f_t == 0.0:
        return 0.0
    else:
        return (f_t + t_f) / (2 * (t_cnt + f_cnt) + f_t + t_f)

@cuda.jit()
def _sokal_sneath_kernel(x, y, w, c):
    idx = cuda.grid(1)
    if idx < 0 or idx >= x.shape[0]:
        return
    if (x[idx] == 1) and (y[idx] == 1):
        cuda.atomic.add(c, 0, 1 * w[idx])
    elif (x[idx] == 1) and (y[idx] == 0):
        cuda.atomic.add(c, 1, 1 * w[idx])
    elif (x[idx] == 0) and (y[idx] == 1):
        cuda.atomic.add(c, 2, 1 * w[idx])


def sokal_sneath_gpu(x: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> float:
    check_valid_array(data=x, source=f'{sokal_sneath_gpu.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{sokal_sneath_gpu.__name__} y', accepted_ndims=(x.ndim,), accepted_axis_0_shape=[x.shape[0]], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    if w is None:
        w = np.ones(x.shape[0]).astype(np.float32)
    check_valid_array(data=w, source=f'{sokal_sneath_gpu.__name__} w', accepted_ndims=(1,), accepted_axis_0_shape=[x.shape[0]], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    x_dev = cuda.to_device(x)
    y_dev = cuda.to_device(y)
    w_dev = cuda.to_device(w)
    counter = cuda.to_device(np.zeros(3, dtype=np.float32))
    bpg = (x.shape[0] + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK
    _sokal_sneath_kernel[bpg, THREADS_PER_BLOCK](x_dev, y_dev, w_dev, counter)
    result = counter.copy_to_host()
    a, b, c = result[0], result[1], result[2]
    denom = a + 2 * (b + c)
    return a / denom if denom != 0.0 else 1.0



def sokal_sneath_score(a: np.ndarray, b: np.ndarray) -> float:
    a1 = np.logical_and(a == 1, b == 1).sum()
    b1 = np.logical_and(a == 1, b == 0).sum()
    c1 = np.logical_and(a == 0, b == 1).sum()
    return a1 / (a1 + 2 * (b1 + c1)) if (a1 + 2 * (b1 + c1)) != 0 else 0.0

import time
N = 1000_000_000



x, y = np.random.randint(0, 2, (N, )).astype(np.int8), np.random.randint(0, 2, (N, )).astype(np.int8)

start = time.perf_counter()
gpu_results = sokal_sneath_gpu(x=x, y=y)
end = time.perf_counter()
elapsed_gpu = end - start
start = time.perf_counter()
cpu_results = sokal_sneath_score(a=x, b=y)
end = time.perf_counter()
elapsed_cpu = end - start


print(elapsed_cpu, elapsed_gpu)



