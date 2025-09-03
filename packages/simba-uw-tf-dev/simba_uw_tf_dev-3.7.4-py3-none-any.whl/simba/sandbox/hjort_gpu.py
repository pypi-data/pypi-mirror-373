import math
import time

import numpy as np
from numba import njit, prange, cuda, float64
from simba.utils.checks import check_valid_array, check_int
from simba.utils.enums import Formats
from simba.data_processors.cuda.utils import _cuda_nanvariance, _cuda_nanmean, _cuda_diff

MAX_HJORTH_WINDOW = 512

@njit("(float32[:], float64[:], int64)")
def sliding_hjort_parameters(data: np.ndarray, window_sizes: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Jitted compute of Hjorth parameters, including mobility, complexity, and activity, for
    sliding windows of varying sizes applied to the input data array.

    .. seealso::
       For single pass, see :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.hjort_parameters`

    :param np.ndarray data: Input data array.
    :param np.ndarray window_sizes: Array of window sizes (in seconds).
    :param int sample_rate: Sampling rate of the data in samples per second.
    :return: An array containing Hjorth parameters for each window size and data point. The shape of the result array is (3, data.shape[0], window_sizes.shape[0]).  The three parameters are stored in the first dimension (0 - mobility, 1 - complexity, 2 - activity), and the remaining dimensions correspond to data points and window sizes.
    :rtype: np.ndarray

    """
    results = np.full((3, data.shape[0], window_sizes.shape[0]), -1.0)
    for i in range(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            dx = np.diff(np.ascontiguousarray(sample))
            ddx = np.diff(np.ascontiguousarray(dx))
            x_var, dx_var = np.var(sample), np.var(dx)
            if (x_var <= 0) or (dx_var <= 0):
                results[0, r, i] = 0
                results[1, r, i] = 0
                results[2, r, i] = 0
            else:
                ddx_var = np.var(ddx)
                mobility = np.sqrt(dx_var / x_var)
                complexity = np.sqrt(ddx_var / dx_var) / mobility
                activity = np.var(sample)
                results[0, r-1, i] = mobility
                results[1, r-1, i] = complexity
                results[2, r-1, i] = activity

    return results.astype(np.float32)


@cuda.jit
def _sliding_hjort_parameters_kernel(x, y, results):
    r_idx, y_idx = cuda.grid(2)
    if r_idx >= x.shape[0] or y_idx >= y.shape[0]:
        return

    win_size = y[y_idx]
    l_idx = int(r_idx - win_size + 1)
    if l_idx < 0:
        return

    x_win = cuda.local.array(MAX_HJORTH_WINDOW, dtype=float64)
    dx = cuda.local.array(MAX_HJORTH_WINDOW, dtype=float64)
    ddx = cuda.local.array(MAX_HJORTH_WINDOW, dtype=float64)

    N = win_size
    for i in range(N):
        x_win[i] = x[l_idx + i]

    _cuda_diff(x, l_idx, r_idx + 1, dx)
    _cuda_diff(dx, 0, N, ddx)

    activity = _cuda_nanvariance(x_win, N)
    dx_var = _cuda_nanvariance(dx, N)
    ddx_var = _cuda_nanvariance(ddx, N)

    if activity == 0 or dx_var == 0:
        return

    mobility = math.sqrt(dx_var / activity)
    complexity = math.sqrt(ddx_var / dx_var) / mobility

    results[0, r_idx, y_idx] = mobility
    results[1, r_idx, y_idx] = complexity
    results[2, r_idx, y_idx] = activity


def sliding_hjort_parameters_gpu(data: np.ndarray, window_sizes: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Compute Hjorth parameters over sliding windows on the GPU.

    .. seelalso::
       For CPU implementation, see :`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.hjort_parameters`

    :param np.ndarray data: 1D numeric array of signal data.
    :param np.ndarray window_sizes: 1D numeric array of window sizes (in seconds).
    :param int sample_rate: Sampling rate of the data (samples per second).
    :returns: 3D array of shape (3, len(data), len(window_sizes)) containing Hjorth parameters computed for each data point and window size.
    :rtype: np.ndarray

    :example:
    >>> x = np.random.randint(0, 500, (10,)).astype(np.float32)
    >>> window_sizes = np.array([1.0, 0.5]).astype(np.float64)
    >>> sample_rate = 10
    >>> H = sliding_hjort_parameters_gpu(data=x, window_sizes=window_sizes, sample_rate=sample_rate)
    """

    THREADS_PER_BLOCK = (32, 16)
    check_valid_array(data=data, source=f'{sliding_hjort_parameters_gpu.__name__} data', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_axis_0=1)
    check_valid_array(data=window_sizes, source=f'{sliding_hjort_parameters_gpu.__name__} window_sizes', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_int(name=f'{sliding_hjort_parameters_gpu.__name__} sample_rate', value=sample_rate)
    data = np.ascontiguousarray(data).astype(np.float64)
    results = np.full((3, data.shape[0], window_sizes.shape[0]), -1.0)
    window_sizes = np.ceil(window_sizes * sample_rate).astype(np.float64)
    data_dev = cuda.to_device(data)
    window_sizes_dev = cuda.to_device(window_sizes)
    results_dev = cuda.to_device(results)
    grid_x = (data.shape[0] + THREADS_PER_BLOCK[0] -1) // THREADS_PER_BLOCK[0]
    grid_y = (window_sizes.shape[0] + THREADS_PER_BLOCK[1] -1) // THREADS_PER_BLOCK[1]
    bpg = (grid_x, grid_y)
    _sliding_hjort_parameters_kernel[bpg, THREADS_PER_BLOCK](data_dev, window_sizes_dev, results_dev)
    return results_dev.copy_to_host()


x = np.random.randint(0, 500, (100000000,)).astype(np.float32)
window_sizes = np.array([1.0]).astype(np.float64)
sample_rate = 100

start = time.perf_counter()
b = sliding_hjort_parameters_gpu(data=x, window_sizes=window_sizes, sample_rate=sample_rate)
end = time.perf_counter()
print(end - start)

start = time.perf_counter()
p = sliding_hjort_parameters(data=x, window_sizes=window_sizes, sample_rate=sample_rate)
end = time.perf_counter()
print(end - start)
#print(b.shape)
#print(b)