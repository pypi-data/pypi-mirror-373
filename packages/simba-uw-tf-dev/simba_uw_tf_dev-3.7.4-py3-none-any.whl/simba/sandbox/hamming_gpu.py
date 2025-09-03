import numpy as np
from numba import prange, cuda, jit
from typing import Optional

from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
import time
THREADS_PER_BLOCK = 1024

@jit(nopython=True)
def hamming_distance(x: np.ndarray,
                     y: np.ndarray,
                     sort: Optional[bool] = False,
                     w: Optional[np.ndarray] = None) -> float:
    """
    Jitted compute of the Hamming similarity between two vectors.

    The Hamming similarity measures the similarity between two binary vectors by counting the number of positions at which the corresponding elements are different.

    .. note::
       If w is not provided, equal weights are assumed. Adapted from `pynndescent <https://pynndescent.readthedocs.io/en/latest/>`_.

    .. math::

       \\text{Hamming distance}(x, y) = \\frac{{\\sum_{i=1}^{n} w_i}}{{n}}

    where:
       - :math:`n` is the length of the vectors,
       - :math:`w_i` is the weight associated with the math:`i`th element of the vectors.

    :param np.ndarray x: First binary vector.
    :param np.ndarray x: Second binary vector.
    :param Optional[np.ndarray] w: Optional weights for each element. Can be classification probabilities. If not provided, equal weights are assumed.
    :param Optional[bool] sort: If True, sorts x and y prior to hamming distance calculation. Default, False.
    :return: Hamming similarity
    :rtype: float

    :example:
    >>> x, y = np.random.randint(0, 2, (10,)).astype(np.int8), np.random.randint(0, 2, (10,)).astype(np.int8)
    >>> Statistics().hamming_distance(x=x, y=y)
    >>> 0.91
    """
    # pass
    if w is None:
        w = np.ones(x.shape[0]).astype(np.float32)

    results = 0.0
    if sort:
        x, y = np.sort(x), np.sort(y)
    for i in prange(x.shape[0]):
        if x[i] != y[i]:
            results += 1.0 * w[i]
    return results / x.shape[0]

@cuda.jit(device=True)
def _cuda_are_rows_equal(x, y, idx_1, idx_2):
    """Helper to check if two rows in two 2D arrays are equal"""
    for i in range(x.shape[1]):
        if x[idx_1, i] != y[idx_2, i]:
            return False
    return True





@cuda.jit()
def _hamming_kernel(x, y, w, r):
    idx = cuda.grid(1)
    if idx < 0 or idx >= x.shape[0]:
        return
    if not _cuda_are_rows_equal(x, y, idx, idx):
        r[idx] = 1.0 * w[idx]

def hamming_distance_gpu(x: np.ndarray,
                         y: np.ndarray,
                         w: Optional[np.ndarray] = None) -> float:

    check_valid_array(data=x, source=f'{hamming_distance_gpu.__name__} x', accepted_ndims=(1, 2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{hamming_distance_gpu.__name__} y', accepted_ndims=(x.ndim,), accepted_axis_0_shape=[x.shape[0]], accepted_axis_1_shape=[x.shape[1]] if x.ndim==2 else None, accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    if w is None:
        w = np.ones(x.shape[0]).astype(np.float32)
    check_valid_array(data=w, source=f'{hamming_distance_gpu.__name__} w', accepted_ndims=(1,), accepted_axis_0_shape=[x.shape[0]], accepted_dtypes=Formats.NUMERIC_DTYPES.value)

    results = np.full(shape=(x.shape[0],), fill_value=0.0, dtype=np.bool_)
    x_dev = cuda.to_device(x)
    y_dev = cuda.to_device(y)
    w_dev = cuda.to_device(w)
    results_dev = cuda.to_device(results)


    bpg = (x.shape[0] + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK
    _hamming_kernel[bpg, THREADS_PER_BLOCK](x_dev, y_dev, w_dev, results_dev)
    return np.sum(results_dev.copy_to_host()) / x.shape[0]




Y = 1


for N in [1000, 10000, 100_000, 1_000_000, 10_000_000, 100_000_000, 250_000_000, 500_000_000, 1000_000_000]:
    x, y = np.random.randint(0, 2, (N, Y)).astype(np.int8), np.random.randint(0, 2, (N, Y)).astype(np.int8)
    start = time.perf_counter()
    gpu_hamming = hamming_distance_gpu(x=x, y=y)
    end = time.perf_counter()
    elapsed_gpu = end - start
    start = time.perf_counter()
    cpu_hamming = hamming_distance(x=x, y=y)
    end = time.perf_counter()
    elapsed_cpu = end - start
    print(N, '\t' *4 , 'gpu \t', elapsed_gpu, 'cpu \t', elapsed_cpu)



