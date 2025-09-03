from typing import Optional
import numpy as np
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from numba import njit, prange, jit, float32, types, int8, float64, bool_, boolean, int64
from scipy import stats
from simba.utils.checks import check_valid_array, check_str, check_int, check_float
from simba.utils.enums import Formats, Options
from simba.utils.data import bucket_data


@njit([(float32[:], boolean), (float32[:], types.misc.Omitted(True))])
def local_maxima_minima(data: np.ndarray, maxima: Optional[bool] = True) -> np.ndarray:
    """
    Jitted compute of the local maxima or minima defined as values which are higher or lower than immediately preceding and proceeding time-series neighbors, repectively.
    Returns 2D np.ndarray with columns representing idx and values of local maxima.

    .. image:: _static/img/local_maxima_minima.png
       :width: 600
       :align: center

    :param np.ndarray data: Time-series data.
    :param bool maxima: If True, returns maxima. Else, minima.
    :return: 2D np.ndarray with columns representing idx in input data in first column and values of local maxima in second column.
    :rtype: np.ndarray

    :example:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> local_maxima_minima(data=data, maxima=True)
    >>> [[1, 7.5], [4, 7.5], [9, 9.5]]
    >>> local_maxima_minima(data=data, maxima=False)
    >>> [[0, 3.9], [2, 4.2], [5, 3.9]]

    """
    if not maxima:
        data = -data
    results = np.full((data.shape[0], 2), -1.0)
    if data[0] >= data[1]:
        if not maxima:
            results[0, :] = np.array([0, -data[0]])
        else:
            results[0, :] = np.array([0, data[0]])
    if data[-1] >= data[-2]:
        if not maxima:
            results[-1, :] = np.array([data.shape[0] - 1, -data[-1]])
        else:
            results[-1, :] = np.array([data.shape[0] - 1, data[-1]])
    for i in prange(1, data.shape[0] - 1):
        if data[i - 1] < data[i] > data[i + 1]:
            if not maxima:
                results[i, :] = np.array([i, -data[i]])
            else:
                results[i, :] = np.array([i, data[i]])

    return results[np.argwhere(results[:, 0].T != -1).flatten()].astype(np.float32)


@njit("(float32[:], float64)")
def crossings(data: np.ndarray, val: float) -> int:
    """
    Jitted compute of the count in time-series where sequential values crosses a defined value.

    .. image:: _static/img/crossings.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_crossings`

    :param np.ndarray data: Time-series data.
    :param float val: Cross value. E.g., to count the number of zero-crossings, pass `0`.
    :return: Count of events where sequential values crosses ``val``.
    :rtype: int

    :example:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> crossings(data=data, val=7)
    >>> 5
    """

    cnt, last_val = 0, -1
    if data[0] > val:
        last_val = 1
    for i in prange(1, data.shape[0]):
        current_val = -1
        if data[i] > val:
            current_val = 1
        if last_val != current_val:
            cnt += 1
        last_val = current_val
    return cnt

@njit("(float32[:], float64,  float64[:], int64,)")
def sliding_crossings(data: np.ndarray, val: float, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Compute the number of crossings over sliding windows in a data array.
    Computes the number of times a value in the data array crosses a given threshold
    value within sliding windows of varying sizes. The number of crossings is computed for each
    window size and stored in the result array where columns represents time windows.

    .. note::
       For frames occurring before a complete time window, -1.0 is returned.
    .. image:: _static/img/sliding_crossings.png
       :width: 1500
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.crossings`

    :param np.ndarray data: Input data array.
    :param float val: Threshold value for crossings.
    :param np.ndarray time_windows: Array of window sizes (in seconds).
    :param int sample_rate: Sampling rate of the data in samples per second.
    :return: An array containing the number of crossings for each window size and data point. The shape of the result array is (data.shape[0], window_sizes.shape[0]).
    :rtype: np.ndarray

    :example:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> results = sliding_crossings(data=data, time_windows=np.array([1.0]), fps=2, val=7.0)
    """

    results = np.full((data.shape[0], time_windows.shape[0]), -1.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            cnt, last_val = 0, -1
            if sample[0] > val:
                last_val = 1
            for j in prange(1, sample.shape[0]):
                current_val = -1
                if sample[j] > val:
                    current_val = 1
                if last_val != current_val:
                    cnt += 1
                last_val = current_val
            results[r - 1, i] = cnt
    return results.astype(np.int32)


@njit("(float32[:], int64, int64, )", cache=True, fastmath=True)
def percentile_difference(data: np.ndarray, upper_pct: int, lower_pct: int) -> float:
    """
    Jitted compute of the difference between the ``upper`` and ``lower`` percentiles of the data as
    a percentage of the median value. Helps understand the spread or variability of the data within specified percentiles.

    .. note::
       Adapted from `cesium <https://github.com/cesium-ml/cesium>`_.

    .. image:: _static/img/percentile_difference.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_percentile_difference`

    :param np.ndarray data: 1D array of representing time-series.
    :param int upper_pct: Upper-boundary percentile.
    :param int lower_pct: Lower-boundary percentile.
    :returns: The difference between the ``upper`` and ``lower`` percentiles of the data as a percentage of the median value.
    :rtype: float

    :examples:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> percentile_difference(data=data, upper_pct=95, lower_pct=5)
    >>> 0.7401574764125177
    """

    upper_val, lower_val = np.percentile(data, upper_pct), np.percentile(data, lower_pct)
    return np.abs(upper_val - lower_val) / np.median(data)

@njit("(float32[:], int64, int64, float64[:], int64, )", cache=True, fastmath=True)
def sliding_percentile_difference( data: np.ndarray, upper_pct: int, lower_pct: int, window_sizes: np.ndarray, fps: int) -> np.ndarray:
    """
    Jitted computes the difference between the upper and lower percentiles within a sliding window for each position
    in the time series using various window sizes. It returns a 2D array where each row corresponds to a position in the time series,
    and each column corresponds to a different window size. The results are calculated as the absolute difference between
    upper and lower percentiles divided by the median of the window.

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.percentile_difference`

    :param np.ndarray data: The input time series data.
    :param int upper_pct: The upper percentile value for the window (e.g., 95 for the 95th percentile).
    :param int lower_pct: The lower percentile value for the window (e.g., 5 for the 5th percentile).
    :param np.ndarray window_sizes: An array of window sizes (in seconds) to use for the sliding calculation.
    :param int sample_rate: The sampling rate (samples per second) of the time series data.
    :return: A 2D array containing the difference between upper and lower percentiles for each window size.
    :rtype: np.ndarray
    """

    results = np.full((data.shape[0], window_sizes.shape[0]), -1.0)
    for i in prange(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * fps)
        for l, r in zip(
            prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)
        ):
            sample = data[l:r]
            upper_val, lower_val = np.percentile(sample, upper_pct), np.percentile(
                sample, lower_pct
            )
            median = np.median(sample)
            if median != 0:
                results[r - 1, i] = np.abs(upper_val - lower_val) / median
            else:
                results[r - 1, i] = -1.0
    return results.astype(np.float32)

@njit("(float64[:], float64,)")
def percent_beyond_n_std(data: np.ndarray, n: float) -> float:
    """
    Jitted compute of the ratio of values in time-series more than N standard deviations from the mean of the time-series.
    .. note::
       Adapted from `cesium <https://github.com/cesium-ml/cesium>`_.
       Oddetity: mean calculation is incorrect if passing float32 data but correct if passing float64.

    .. image:: _static/img/percent_beyond_n_std.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_percent_beyond_n_std`

    :parameter np.ndarray data: 1D array representing time-series.
    :parameter float n: Standard deviation cut-off.
    :return: Ratio of values in ``data`` that fall more than ``n`` standard deviations from mean of ``data``.
    :rtype: float

    :examples:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> percent_beyond_n_std(data=data, n=1)
    >>> 0.1
    """

    m = np.mean(data)
    std = np.std(data)
    target = m + (std * n)
    return np.argwhere(data > target).shape[0] / data.shape[0]


@njit([(float32[:], float64[:], int64), (int64[:], float64[:], int64)])
def sliding_unique(x: np.ndarray, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Compute the number of unique values in a sliding window over an array of feature values.

    :param x: 1D array of feature values for which the unique values are to be counted.
    :param time_windows: Array of window sizes (in seconds) for which the unique values are counted.
    :param int fps: The frame rate in frames per second, which is used to calculate the window size in samples.
    :return: A 2D array where each row corresponds to a time window, and each element represents the count of unique values in the corresponding sliding window of the array `x`.
    :rtype: np.ndarray
    """
    results = np.full((x.shape[0], time_windows.shape[0]), -1)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for l, r in zip(range(0, x.shape[0] + 1), range(window_size, x.shape[0] + 1)):
            sample = x[l:r]
            unique_cnt = np.unique(sample)
            results[r - 1, i] = unique_cnt.shape[0]

    return results


@njit("(float32[:], int64, int64, )", fastmath=True)
def percent_in_percentile_window(data: np.ndarray, upper_pct: int, lower_pct: int) -> float:
    """
    Jitted compute of the ratio of values in time-series that fall between the ``upper`` and ``lower`` percentile.

    .. note::
       Adapted from `cesium <https://github.com/cesium-ml/cesium>`_.

    .. image:: _static/img/percent_in_percentile_window.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_percent_in_percentile_window`

    :param np.ndarray data: 1D array of representing time-series.
    :param int upper_pct: Upper-boundary percentile.
    :param int lower_pct: Lower-boundary percentile.
    :returns: Ratio of values in ``data`` that fall within ``upper_pct`` and ``lower_pct`` percentiles.
    :rtype: float

    :example:
    >>> data = np.array([3.9, 7.5,  4.2, 6.2, 7.5, 3.9, 6.2, 6.5, 7.2, 9.5]).astype(np.float32)
    >>> percent_in_percentile_window(data, upper_pct=70, lower_pct=30)
    >>> 0.4
    """

    upper_val, lower_val = np.percentile(data, upper_pct), np.percentile(data, lower_pct)
    return (np.argwhere((data <= upper_val) & (data >= lower_val)).flatten().shape[0]/ data.shape[0])


@njit("(float32[:], int64, int64, float64[:], int64)", cache=True, fastmath=True)
def sliding_percent_in_percentile_window(data: np.ndarray,
                                         upper_pct: int,
                                         lower_pct: int,
                                         window_sizes: np.ndarray,
                                         sample_rate: int) -> np.ndarray:
    """
    Jitted compute of the percentage of data points falling within a percentile window in a sliding manner.
    The function computes the percentage of data points within the specified percentile window for each position in the time series
    using various window sizes. It returns a 2D array where each row corresponds to a position in the time series, and each column
    corresponds to a different window size. The results are given as a percentage of data points within the percentile window.

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.percent_in_percentile_window`

    :param np.ndarray data: The input time series data.
    :param int upper_pct: The upper percentile value for the window (e.g., 95 for the 95th percentile).
    :param int lower_pct: The lower percentile value for the window (e.g., 5 for the 5th percentile).
    :param np.ndarray window_sizes: An array of window sizes (in seconds) to use for the sliding calculation.
    :param int sample_rate: The sampling rate (samples per second) of the time series data.
    :return: A 2D array containing the percentage of data points within the percentile window for each window size.
    :rtype: np.ndarray
    """

    results = np.full((data.shape[0], window_sizes.shape[0]), -1.0)
    upper_val, lower_val = np.percentile(data, upper_pct), np.percentile(data, lower_pct)
    for i in prange(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            results[r - 1, i] = (np.argwhere((sample <= upper_val) & (sample >= lower_val)).flatten().shape[0]/ sample.shape[0])

        return results.astype(np.float32)

@njit("(float32[:],)", fastmath=True)
def line_length(data: np.ndarray) -> float:
    """
    Calculate the line length of a 1D array.
    Line length is a measure of signal complexity and is computed by summing the absolute
    differences between consecutive elements of the input array. Used in EEG
    analysis and other signal processing applications to quantify variations in the signal.

    .. math::
        LL = \sum_{i=1}^{N-1} |x[i] - x[i-1]|

    where:
    :math:`LL` is the line length.
    :math:`N` is the number of elements in the input data array.
    :math:`x[i]` represents the value of the data at index i.

    .. image:: _static/img/line_length.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_line_length`

    :param numpy.ndarray data: The 1D array for which the line length is to be calculated.
    :return: The line length of the input array, indicating its complexity.
    :rtype: float

    :example:
    >>> data = np.array([1, 4, 2, 3, 5, 6, 8, 7, 9, 10]).astype(np.float32)
    >>> line_length(data=data)
    >>> 12.0
    """

    diff = np.abs(np.diff(data.astype(np.float64)))
    return np.sum(diff)

@njit("(float32[:], float64[:], int64)", fastmath=True)
def sliding_line_length(data: np.ndarray, window_sizes: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Jitted compute of  sliding line length for a given time series using different window sizes.
    The function computes line length for the input data using various window sizes. It returns a 2D array where each row
    corresponds to a position in the time series, and each column corresponds to a different window size. The line length
    is calculated for each window, and the results are returned as a 2D array of float32 values.

    .. image:: _static/img/sliding_line_length.png
       :width: 600
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.line_length`

    :param np.ndarray data: 1D array input data.
    :param window_sizes: An array of window sizes (in seconds) to use for line length calculation.
    :param sample_rate: The sampling rate (samples per second) of the time series data.
    :return: A 2D array containing line length values for each window size at each position in the time series.
    :rtype: np.ndarray

    :examples:
    >>> data = np.array([1, 4, 2, 3, 5, 6, 8, 7, 9, 10]).astype(np.float32)
    >>> sliding_line_length(data=data, window_sizes=np.array([1.0]), sample_rate=2)
    """

    results = np.full((data.shape[0], window_sizes.shape[0]), -1.0)
    for i in prange(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            results[r - 1, i] = np.sum(np.abs(np.diff(sample.astype(np.float64))))
    return results.astype(np.float32)

@njit("(float32[:], float64[:], int64)", fastmath=True, cache=True)
def sliding_variance(data: np.ndarray, window_sizes: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Jitted compute of the variance of data within sliding windows of varying sizes applied to
    the input data array. Variance is a measure of data dispersion or spread.

    .. image:: _static/img/sliding_variance.png
       :width: 600
       :align: center

    :param data: 1d input data array.
    :param window_sizes: Array of window sizes (in seconds).
    :param sample_rate: Sampling rate of the data in samples per second.
    :return: Variance values for each window size and data point. The shape of the result array is (data.shape[0], window_sizes.shape[0]).

    :example:
    >>> data = np.array([1, 2, 3, 1, 2, 9, 17, 2, 10, 4]).astype(np.float32)
    >>> sliding_variance(data=data, window_sizes=np.array([0.5]), sample_rate=10)
    >>> [[-1.],[-1.],[-1.],[-1.],[ 0.56],[ 8.23],[35.84],[39.20],[34.15],[30.15]])
    """

    results = np.full((data.shape[0], window_sizes.shape[0]), -1.0)
    for i in prange(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l:r]
            results[r - 1, i] = np.var(sample)
    return results.astype(np.float32)


@njit(
    "(float32[:], float64[:], float64, types.ListType(types.unicode_type))",
    fastmath=True,
    cache=True,
)
def sliding_descriptive_statistics(data: np.ndarray, window_sizes: np.ndarray, sample_rate: float, statistics: Literal["var", "max", "min", "std", "median", "mean", "mad", "sum", "mac", "rms", "absenergy"]) -> np.ndarray:
    """
    Jitted compute of descriptive statistics over sliding windows in 1D data array.
    Computes various descriptive statistics (e.g., variance, maximum, minimum, standard deviation,
    median, mean, median absolute deviation) for sliding windows of varying sizes applied to the input data array.

    :param np.ndarray data: 1D input data array.
    :param np.ndarray window_sizes: Array of window sizes (in seconds).
    :param int sample_rate: Sampling rate of the data in samples per second.
    :param types.ListType(types.unicode_type) statistics: List of statistics to compute. Options: 'var', 'max', 'min', 'std', 'median', 'mean', 'mad', 'sum', 'mac', 'rms', 'abs_energy'.
    :return: Array containing the selected descriptive statistics for each window size, data point, and statistic type. The shape of the result array is (len(statistics), data.shape[0], window_sizes.shape[0).
    :rtype: np.ndarray

    .. note::
       The `statistics` parameter should be a list containing one or more of the following statistics:
        * 'var' (variance)
        * 'max' (maximum)
        * 'min' (minimum)
        * 'std' (standard deviation)
        * 'median' (median)
        * 'mean' (mean)
        * 'mad' (median absolute deviation)
        * 'sum' (sum)
        * 'mac' (mean absolute change)
        * 'rms' (root mean square)
        * 'absenergy' (absolute energy)
       E.g., If the statistics list is ['var', 'max', 'mean'], the 3rd dimension order in the result array will be: [variance, maximum, mean]

    :example:
    >>> data = np.array([1, 4, 2, 3, 5, 6, 8, 7, 9, 10]).astype(np.float32)
    >>> results = sliding_descriptive_statistics(data=data, window_sizes=np.array([1.0, 5.0]), sample_rate=2, statistics=typed.List(['var', 'max']))
    """

    results = np.full((len(statistics), data.shape[0], window_sizes.shape[0]), -1.0)
    for j in prange(len(statistics)):
        for i in prange(window_sizes.shape[0]):
            window_size = int(window_sizes[i] * sample_rate)
            for l, r in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
                sample = data[l:r]
                if statistics[j] == "var":
                    results[j, r - 1, i] = np.var(sample)
                elif statistics[j] == "max":
                    results[j, r - 1, i] = np.max(sample)
                elif statistics[j] == "min":
                    results[j, r - 1, i] = np.min(sample)
                elif statistics[j] == "std":
                    results[j, r - 1, i] = np.std(sample)
                elif statistics[j] == "median":
                    results[j, r - 1, i] = np.median(sample)
                elif statistics[j] == "mean":
                    results[j, r - 1, i] = np.mean(sample)
                elif statistics[j] == "sum":
                    results[j, r - 1, i] = np.sum(sample)
                elif statistics[j] == "mad":
                    results[j, r - 1, i] = np.median(np.abs(sample - np.median(sample)))
                elif statistics[j] == "mac":
                    results[j, r - 1, i] = np.mean(np.abs(sample[1:] - sample[:-1]))
                elif statistics[j] == "rms":
                    results[j, r - 1, i] = np.sqrt(np.mean(sample**2))
                elif statistics[j] == "absenergy":
                    results[j, r - 1, i] = np.sqrt(np.sum(sample**2))

    return results.astype(np.float32)

@njit(
    [
        (float32[:], float64, boolean),
        (float32[:], float64, types.misc.Omitted(True)),
    ]
)
def longest_strike(data: np.ndarray, threshold: float, above: bool = True) -> int:

    """
    Jitted compute of the length of the longest consecutive sequence of values in the input data that either exceed
    or fall below a specified threshold.

    .. image:: _static/img/longest_strike.png
       :width: 700
       :align: center

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_longest_strike`

    :param np.ndarray data: The input 1D NumPy array containing the values to be analyzed.
    :param float threshold: The threshold value used for the comparison.
    :param bool above: If True, the function looks for strikes where values are above or equal to the threshold. If False, it looks for strikes where values are below or equal to the threshold.
    :return: The length of the longest strike that satisfies the condition.
    :rtype: int

    :example:
    >>> data = np.array([1, 8, 2, 10, 8, 6, 8, 1, 1, 1]).astype(np.float32)
    >>> longest_strike(data=data, threshold=7, above=True)
    >>> 2
    >>> longest_strike(data=data, threshold=7, above=False)
    >>> 3
    """

    result, l, r, cnt = -np.inf, 0, 0, 0
    while l < data.shape[0]:
        if above:
            if data[l] >= threshold:
                cnt, r = cnt + 1, r + 1
                while data[r] >= threshold and r < data.shape[0]:
                    cnt, r = cnt + 1, r + 1
        else:
            if data[l] <= threshold:
                cnt, r = cnt + 1, r + 1
                while data[r] <= threshold and r < data.shape[0]:
                    cnt, r = cnt + 1, r + 1
        l += 1
        if cnt > result:
            result = cnt
        if data.shape[0] - l < result:
            break
        r, cnt = l, 0

    return int(result)


@njit([(float32[:], float64, float64[:], int64, boolean), (float32[:], float64, float64[:], int64, types.misc.Omitted(True))])
def sliding_longest_strike( data: np.ndarray, threshold: float, time_windows: np.ndarray, sample_rate: int, above: bool) -> np.ndarray:
    """
    Jitted compute of the length of the longest strike of values within sliding time windows that satisfy a given condition.
    Calculates the length of the longest consecutive sequence of values in a 1D NumPy array, where each
    sequence is determined by a sliding time window. The condition is specified by a threshold, and
    you can choose whether to look for values above or below the threshold.

    .. image:: _static/img/sliding_longest_strike.png
       :width: 700
       :align: center
    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.longest_strike`

    :param np.ndarray data: The input 1D NumPy array containing the values to be analyzed.
    :param float threshold: The threshold value used for the comparison.
    :param np.ndarray time_windows: An array containing the time window sizes in seconds.
    :param int sample_rate: The sample rate in samples per second.
    :param bool above: If True, the function looks for strikes where values are above or equal to the threshold. If False, it looks for strikes where values are below or equal to the threshold.
    :return: A 2D NumPy array with dimensions (data.shape[0], time_windows.shape[0]). Each element in the array represents the length of the longest strike that satisfies the condition for the corresponding time window.
    :rtype: np.ndarray

    :example:
    >>> data = np.array([1, 8, 2, 10, 8, 6, 8, 1, 1, 1]).astype(np.float32)
    >>> sliding_longest_strike(data=data, threshold=7, above=True, time_windows=np.array([1.0]), sample_rate=2)
    >>> [[-1.][ 1.][ 1.][ 1.][ 2.][ 1.][ 1.][ 1.][ 0.][ 0.]]
    >>> sliding_longest_strike(data=data, threshold=7, above=True, time_windows=np.array([1.0]), sample_rate=2)
    >>> [[-1.][ 1.][ 1.][ 1.][ 0.][ 1.][ 1.][ 1.][ 2.][ 2.]]
    """
    results = np.full((data.shape[0], time_windows.shape[0]), -1.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * sample_rate)
        for l1, r1 in zip(prange(0, data.shape[0] + 1), prange(window_size, data.shape[0] + 1)):
            sample = data[l1:r1]
            result, l, r, cnt = -np.inf, 0, 0, 0
            while l < sample.shape[0]:
                if above:
                    if sample[l] >= threshold:
                        cnt, r = cnt + 1, r + 1
                        while sample[r] >= threshold and r < sample.shape[0]:
                            cnt, r = cnt + 1, r + 1
                else:
                    if sample[l] <= threshold:
                        cnt, r = cnt + 1, r + 1
                        while sample[r] <= threshold and r < sample.shape[0]:
                            cnt, r = cnt + 1, r + 1
                l += 1
                if cnt > result:
                    result = cnt
                if data.shape[0] - l < result:
                    results[r - 1, i] = result
                    break
                r, cnt = l, 0
            results[r1 - 1, i] = result

    return results


@njit([(float32[:], float64, int64, boolean), (float32[:], float64, int64, types.misc.Omitted(True))])
def time_since_previous_target_value(data: np.ndarray, value: float, fps: int, inverse: Optional[bool] = False) -> np.ndarray:
    """
    Calculate the time duration (in seconds) since the previous occurrence of a specific value in a data array.
    Calculates the time duration, in seconds, between each data point and the previous occurrence
    of a specific value within the data array.

    .. image:: _static/img/time_since_previous_target_value.png
       :width: 700
       :align: center
    .. seealso::

       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.time_since_previous_threshold`

    :param np.ndarray data: The input 1D array containing the time series data.
    :param float value: The specific value to search for in the data array.
    :param int sample_rate: The sampling rate which data points were collected. It is used to calculate the time duration in seconds.
    :param bool inverse: If True, the function calculates the time since the previous value that is NOT equal to the specified 'value'. If False, it calculates the time since the previous occurrence of the specified 'value'.
    :returns: A 1D NumPy array containing the time duration (in seconds) since the previous occurrence of the specified 'value' for each data point.
    :rtype: np.ndarray

    :example:
    >>> data = np.array([8, 8, 2, 10, 8, 6, 8, 1, 1, 1]).astype(np.float32)
    >>> time_since_previous_target_value(data=data, value=8.0, inverse=False, sample_rate=2.0)
    >>> [0. , 0. , 0.5, 1. , 0. , 0.5, 0. , 0.5, 1. , 1.5])
    >>> time_since_previous_target_value(data=data, value=8.0, inverse=True, sample_rate=2.0)
    >>> [-1. , -1. ,  0. ,  0. ,  0.5,  0. ,  0.5,  0. ,  0. ,  0. ]
    """

    results = np.full((data.shape[0]), -1.0)
    if not inverse:
        criterion_idx = np.argwhere(data == value).flatten()
    else:
        criterion_idx = np.argwhere(data != value).flatten()
    if criterion_idx.shape[0] == 0:
        return np.full((data.shape[0]), -1.0)
    for i in prange(data.shape[0]):
        if not inverse and (data[i] == value):
            results[i] = 0
        elif inverse and (data[i] != value):
            results[i] = 0
        else:
            x = criterion_idx[np.argwhere(criterion_idx < i).flatten()]
            if len(x) > 0:
                results[i] = (i - x[-1]) / fps
    return results


@njit("(int32[:,:], float64[:], float64, float64)")
def sliding_displacement(x: np.ndarray, time_windows: np.ndarray, fps: float, px_per_mm: float) -> np.ndarray:
    """
    Calculate sliding Euclidean displacement of a body-part point over time windows.

    .. image:: _static/img/sliding_displacement.png
       :width: 600
       :align: center

    :param np.ndarray x: An array of shape (n, 2) representing the time-series sequence of 2D points.
    :param np.ndarray time_windows: Array of time windows (in seconds).
    :param float fps: The sample rate (frames per second) of the sequence.
    :param float px_per_mm: Pixels per millimeter conversion factor.
    :return: 1D array containing the calculated displacements.
    :rtype: np.ndarray

    :example:
    >>> x = np.random.randint(0, 50, (100, 2)).astype(np.int32)
    >>> sliding_displacement(x=x, time_windows=np.array([1.0]), fps=1.0, px_per_mm=1.0)
    """

    results = np.full((x.shape[0], time_windows.shape[0]), -1.0)
    for i in range(time_windows.shape[0]):
        w = int(time_windows[i] * fps)
        for j in range(w, x.shape[0]):
            c, s = x[j], x[j - w]
            results[j, i] = (np.sqrt((s[0] - c[0]) ** 2 + (s[1] - c[1]) ** 2)) / px_per_mm
    return results.astype(np.float32)

@njit("(float64[:], float64[:], float64[:], float64, boolean, float64)")
def sliding_two_signal_crosscorrelation(x: np.ndarray, y: np.ndarray, windows: np.ndarray, sample_rate: float, normalize: bool, lag: float) -> np.ndarray:
    """
    Calculate sliding (lagged) cross-correlation between two signals, e.g., the movement and velocity of two animals.

    .. note::
        If no lag needed, pass lag 0.0.

    :param np.ndarray x: The first input signal.
    :param np.ndarray y: The second input signal.
    :param np.ndarray windows: Array of window lengths in seconds.
    :param float sample_rate: Sampling rate of the signals (in Hz or FPS).
    :param bool normalize: If True, normalize the signals before computing the correlation.
    :param float lag: Time lag between the signals in seconds.
    :return: 2D array of sliding cross-correlation values. Each row corresponds to a time index, and each column corresponds to a window size specified in the `windows` parameter.
    :rtype: np.ndarray

    :example:
    >>> x = np.random.randint(0, 10, size=(20,))
    >>> y = np.random.randint(0, 10, size=(20,))
    >>> sliding_two_signal_crosscorrelation(x=x, y=y, windows=np.array([1.0, 1.2]), sample_rate=10, normalize=True, lag=0.0)
    """

    results = np.full((x.shape[0], windows.shape[0]), 0.0)
    lag = int(sample_rate * lag)
    for i in prange(windows.shape[0]):
        W_s = int(windows[i] * sample_rate)
        for cnt, (l1, r1) in enumerate(zip(range(0, x.shape[0] + 1), range(W_s, x.shape[0] + 1))):
            l2 = l1 - lag
            if l2 < 0:
                l2 = 0
            r2 = r1 - lag
            if r2 - l2 < W_s:
                r2 = l2 + W_s
            X_w = x[l1:r1]
            Y_w = y[l2:r2]
            if normalize:
                X_w = (X_w - np.mean(X_w)) / (np.std(X_w) * X_w.shape[0])
                Y_w = (Y_w - np.mean(Y_w)) / np.std(Y_w)
            v = np.correlate(a=X_w, v=Y_w)[0]
            if np.isnan(v):
                results[r1 - 1, i] = 0.0
            else:
                results[int(r1 - 1), i] = v
    return results.astype(np.float32)


def sliding_pct_in_top_n(x: np.ndarray, windows: np.ndarray, n: int, fps: float) -> np.ndarray:

    """
    Compute the percentage of elements in the top 'n' frequencies in sliding windows of the input array.

    .. note::
      To compute percentage of elements in the top 'n' frequencies in entire array, use :func:`simba.mixins.statistics_mixin.Statistics.pct_in_top_n`.

    :param np.ndarray x: Input 1D array.
    :param np.ndarray windows: Array of window sizes in seconds.
    :param int n: Number of top frequencies.
    :param float fps: Sampling frequency for time convesrion.
    :return: 2D array of computed percentages of elements in the top 'n' frequencies for each sliding window.
    :rtype: np.ndarray

    :example:
    >>> x = np.random.randint(0, 10, (100000,))
    >>> results = sliding_pct_in_top_n(x=x, windows=np.array([1.0]), n=4, fps=10)
    """

    check_valid_array( data=x, source=f"{sliding_pct_in_top_n.__name__} x", accepted_ndims=(1,), accepted_dtypes=(np.float32, np.float64, np.int64, np.int32, int, float))
    check_valid_array(data=windows, source=f"{sliding_pct_in_top_n.__name__} windows", accepted_ndims=(1,), accepted_dtypes=(np.float32, np.float64, np.int64, np.int32, int, float))
    check_int(name=f"{sliding_pct_in_top_n.__name__} n", value=n, min_value=1)
    check_float(name=f"{sliding_pct_in_top_n.__name__} fps", value=n, min_value=10e-6)
    results = np.full((x.shape[0], windows.shape[0]), -1.0)
    for i in range(windows.shape[0]):
        W_s = int(windows[i] * fps)
        for cnt, (l, r) in enumerate(zip(range(0, x.shape[0] + 1), range(W_s, x.shape[0] + 1))):
            sample = x[l:r]
            cnts = np.sort(np.unique(sample, return_counts=True)[1])[-n:]
            results[int(r - 1), i] = np.sum(cnts) / sample.shape[0]

    return results


def path_aspect_ratio(x: np.ndarray, px_per_mm: float) -> float:
   """
   Calculates the aspect ratio of the bounding box that encloses a given path.
   .. image:: _static/img/path_aspect_ratio.webp
      :width: 400
      :align: center

   :param np.ndarray x: A 2D array of shape (N, 2) representing the path, where N is the number of points and each point has two spatial coordinates (e.g., x and y for 2D space). The path should be in the form of an array of consecutive (x, y) points.
   :param float px_per_mm: Convertion factor representing the number of pixels per millimeter
   :return: The aspect ratio of the bounding box enclosing the path. If the width or height of the bounding box is zero (e.g., if all points are aligned vertically or horizontally), returns -1.
   :rtype: float

   :example:
   >>> x = np.random.randint(0, 500, (10, 2))
   >>> path_aspect_ratio(x=x)
   """

   check_valid_array(data=x, source=path_aspect_ratio.__name__, accepted_ndims=(2,), accepted_axis_1_shape=[2, ], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
   check_float(name=path_aspect_ratio.__name__, value=px_per_mm)
   xmin, ymin = np.min(x[:, 0]), np.min(x[:, 1])
   xmax, ymax = np.max(x[:, 0]), np.max(x[:, 1])
   w, h = (xmax - xmin), (ymax - ymin)
   if w == 0 or h == 0:
       return -1
   else:
       return (w / h) * px_per_mm

def avg_kinetic_energy(x: np.ndarray, mass: float, sample_rate: float) -> float:
    """
    Calculate the average kinetic energy of an object based on its velocity.

    :param np.ndarray x: A 2D NumPy array of shape (n, 2), where each row contains the x and y  position coordinates of the object at each time step.
    :param float mass: The mass of the object.
    :param float sample_rate: The sampling rate (Hz), i.e., the number of data points per second.
    :return: The average kinetic energy of the animal.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 500, (200, 2))
    >>> avg_kinetic_energy(x=x, mass=35, sample_rate=30)
    """
    delta_t = np.round(1 / sample_rate, 2)
    vx, vy = np.gradient(x[:, 0], delta_t), np.gradient(x[:, 1], delta_t)
    speed = np.sqrt(vx ** 2 + vy ** 2)
    kinetic_energy = 0.5 * mass * speed ** 2
    y = float(np.mean(kinetic_energy).astype(np.float32))
    return y
