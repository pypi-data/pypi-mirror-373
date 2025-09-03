import numpy as np
from typing import Optional
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from numba import njit, prange, jit, float32, types, int8, float64, bool_
from scipy import stats
from simba.utils.checks import check_valid_array, check_str, check_int
from simba.utils.enums import Formats, Options
from simba.utils.data import bucket_data


@jit(nopython=True)
def _hist_1d(data: np.ndarray, bin_count: int, range: np.ndarray, normalize: Optional[bool] = False) -> np.ndarray:
    """
    Jitted helper to compute 1D histograms with counts or rations (if normalize is True)

    .. note::
       For non-heuristic rules for bin counts and bin ranges, see ``simba.data.freedman_diaconis`` or simba.data.bucket_data``.

    :param np.ndarray data: 1d array containing feature values.
    :param int bin_count: The number of bins.
    :param: np.ndarray range: 1d array with two values representing minimum and maximum value to bin.
    :param: Optional[bool] normalize: If True, then the counts are returned as a ratio of all values. If False, then the raw counts. Pass normalize as True if the datasets are unequal counts. Default: True.
    """

    hist = np.histogram(data, bin_count, (range[0], range[1]))[0]
    if normalize:
        total_sum = np.sum(hist)
        if total_sum == 0:
            pass
        else:
            return hist / total_sum
    return hist.astype(np.float64)


def symmetry_index(x: np.ndarray, y: np.ndarray, agg_type: Literal['mean', 'median'] = 'mean') -> float:
    """
    Calculate the Symmetry Index (SI) between two arrays of measurements, `x` and `y`, over a given time series.
    The Symmetry Index quantifies the relative difference between two measurements at each time point, expressed as a percentage.
    The function returns either the mean or median Symmetry Index over the entire series, based on the specified aggregation type.

    Zero indicates perfect symmetry. Positive values pepresent increasing asymmetry between the two measurements.

    The Symmetry Index (SI) is calculated as:

    .. math::
       SI = \frac{|x_i - y_i|}{0.5 \times (x_i + y_i)} \times 100

    where :math:`x_i` and :math:`y_i` are the values of the two measurements at each time point.

    :param np.ndarray x: A 1-dimensional array of measurements from one side (e.g., left side), representing a time series or sequence of measurements.
    :param np.ndarray y: A 1-dimensional array of measurements from the other side (e.g., right side), of the same length as `x`.
    :param Literal['mean', 'median'] agg_type: The aggregation method used to summarize the Symmetry Index across all time points.
    :return: The aggregated Symmetry Index over the series, either as the mean or median SI.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 155, (100,))
    >>>y = np.random.randint(0, 155, (100,))
    >>> symmetry_index(x=x, y=y)
    """

    check_valid_array(data=x, source=f'{symmetry_index.__name__} x', accepted_ndims=(1,), min_axis_0=1, accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=x, source=f'{symmetry_index.__name__} y', accepted_ndims=(1,), min_axis_0=1, accepted_axis_0_shape=[x.shape[0]], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f'{symmetry_index.__name__} agg_type', value=agg_type, options=('mean', 'median'))
    si_values = np.abs(x - y) / (0.5 * (x + y)) * 100
    if agg_type == 'mean':
        return np.float32(np.nanmean(si_values))
    else:
        return np.float32(np.nanmedian(si_values))


def normalized_google_distance(x: np.ndarray, y: np.ndarray) -> float:
    r"""
    Compute the Normalized Google Distance (NGD) between two vectors or matrices.
    Normalized Google Distance is a measure of similarity between two sets based on
    the relationship between the sums and minimum values of their elements.

    The NGD is calculated as:

    .. math::
      NGD(x, y) = \\frac{\\max(\\sum x, \\sum y) - \\sum \\min(x, y)}{(\\sum x + \\sum y) - \\min(\\sum x, \\sum y)}

    where:
    - :math:`\\sum x` is the sum of elements in `x`
    - :math:`\\sum y` is the sum of elements in `y`
    - :math:`\\sum \\min(x, y)` is the sum of element-wise minimums of `x` and `y`

    .. note::
       This function assumes x and y have the same shape. It computes NGD based on the sum of elements and the minimum values between corresponding elements of x and y.

    :param np.ndarray x: First numerical matrix with shape (m, n).
    :param np.ndarray y: Second array or matrix with shape (m, n).
    :return:  Normalized Google Distance between x and y.
    :rtype: float

    :example:
    >>> x, y = np.random.randint(0, 500, (1000,200)), np.random.randint(0, 500, (1000,200))
    >>> normalized_google_distance(x=y, y=x)
    """
    check_valid_array(data=x, source=f'{normalized_google_distance.__name__} x', accepted_ndims=(1, 2), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{normalized_google_distance.__name__} y', accepted_ndims=(x.ndim,), accepted_shapes=[x.shape,], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    sum_x, sum_y = np.sum(x), np.sum(y)
    sum_min = np.sum(np.minimum(x, y))
    D = (sum_x + sum_y) - np.min([sum_x, sum_y])
    N = np.max([sum_x, sum_y]) - sum_min
    if D == 0:
        return -1.0
    else:
        return N / D

def gower_distance(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute Gower-like distance vector between corresponding rows of two numerical matrices.
    Gower distance is a measure of dissimilarity between two vectors (or rows in this case).
    .. note::
       This function assumes x and y have the same shape and only considers numerical attributes.
        Each observation in x is compared to the corresponding observation in y based on normalized
        absolute differences across numerical columns.

    :param np.ndarray x: First numerical matrix with shape (m, n).
    :param np.ndarray y: Second numerical matrix with shape (m, n).
    :return: Gower-like distance vector with shape (m,).
    :rtype: np.ndarray

    :example:
    >>> x, y = np.random.randint(0, 500, (1000, 6000)), np.random.randint(0, 500, (1000, 6000))
    >>> gower_distance(x=x, y=y)
    """

    check_valid_array(data=x, source=f'{gower_distance.__name__} x', accepted_ndims=(1, 2), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{gower_distance.__name__} y', accepted_ndims=(x.ndim,), accepted_shapes=[x.shape,], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    field_ranges = np.max(x, axis=0) - np.min(x, axis=0)
    results = np.full((x.shape[0]), np.nan)
    for i in range(x.shape[0]):
        u, v = x[i], y[i]
        dist = 0.0
        for j in range(u.shape[0]):
            if field_ranges[j] != 0:
                dist += np.abs(u[j] - v[j]) / field_ranges[j]
        results[i] = dist / u.shape[0]
    return results


def wave_hedges_distance(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the Wave-Hedges distance between two 1-dimensional arrays `x` and `y`. The Wave-Hedges distance is a measure of dissimilarity between arrays.

    .. note::
        Wave-Hedges distance score of 0 indicate identical arrays. There is no upper bound.

    :param np.ndarray x: 1D array representing the first feature values.
    :param np.ndarray y: 1D array representing the second feature values.
    :returns: Wave-Hedges distance
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 500, (1000,))
    >>> y = np.random.randint(0, 500, (1000,))
    >>> wave_hedges_distance(x=x, y=y)
    """
    check_valid_array(data=x, source=f'{wave_hedges_distance.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{wave_hedges_distance.__name__} y', accepted_ndims=(1,), accepted_shapes=[x.shape,], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    x_y = abs(x - y)
    xy_max = np.maximum(x, y)

    return np.sum(np.where(((x_y != 0) & (xy_max != 0)), x_y / xy_max, 0))


def kumar_hassebrook_similarity(x: np.ndarray, y: np.ndarray) -> float:

    """
    Kumar-Hassebrook similarity is a measure used to quantify the similarity between two vectors.

    .. note::
        Kumar-Hassebrook similarity score of 1 indicates identical vectors and 0 indicating no similarity

    :param np.ndarray x: 1D array representing the first feature values.
    :param np.ndarray y: 1D array representing the second feature values.
    :return: Kumar-Hassebrook similarity between vectors x and y.
    :rtype: float

    :example:
    >>> x, y = np.random.randint(0, 500, (1000,)), np.random.randint(0, 500, (1000,))
    >>> kumar_hassebrook_similarity(x=x, y=y)
    """

    check_valid_array(data=x, source=f'{kumar_hassebrook_similarity.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{kumar_hassebrook_similarity.__name__} y', accepted_ndims=(1,), accepted_shapes=[x.shape,], accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    dot_product = np.dot(x, y)
    norm_x = np.linalg.norm(x)
    norm_y = np.linalg.norm(y)

    return dot_product / (norm_x ** 2 + norm_y ** 2 - dot_product)


@njit(["(int64[:], int64[:], float64[:])", "(int64[:], int64[:], types.misc.Omitted(None))",
       "(int64[:, :], int64[:, :], float64[:])", "(int64[:, :], int64[:, :], types.misc.Omitted(None))"])
def sokal_michener(x: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> float:
    r"""
    Jitted compute of the Sokal-Michener dissimilarity between two binary vectors or matrices.
    Higher values indicate more dissimilar vectors or matrices, while lower values indicate more similar vectors or matrices.
    The Sokal-Michener dissimilarity is a measure of dissimilarity between two sets
    based on the presence or absence of similar attributes. This implementation supports weighted dissimilarity.

    .. note::
       Adapted from `umap <https://github.com/lmcinnes/umap/blob/e7f2fb9e5e772edd5c8f38612365ec6a35a54373/umap/distances.py#L468>`_.

    .. math::
       D(x, y) = \\frac{2 \cdot \sum_{i} w_i \cdot \mathbb{1}(x_i \neq y_i)}{N + \sum_{i} w_i \cdot \mathbb{1}(x_i \neq y_i)}

    where:
    - :math:`x` and :math:`y` are the binary vectors or matrices.
    - :math:`w_i` is the weight for the i-th element.
    - :math:`\mathbb{1}(x_i \neq y_i)` is an indicator function that is 1 if :math:`x_i \neq y_i` and 0 otherwise.
    - :math:`N` is the total number of elements in :math:`x` or :math:`y`.

    :param np.ndarray x: First binary vector or matrix.
    :param np.ndarray y: Second binary vector or matrix.
    :param Optional[np.ndarray] w: Optional weight vector. If None, all weights are considered as 1.
    :return: Sokal-Michener dissimilarity between `x` and `y`.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 2, (200,))
    >>> y = np.random.randint(0, 2, (200,))
    >>> sokal_michener = sokal_michener(x=x, y=y)
    """
    if w is None:
        w = np.ones(x.shape[0]).astype(np.float64)
    unequal_cnt = 0.0
    for i in np.ndindex(x.shape):
        x_i, y_i = x[i], y[i]
        if x_i != y_i:
            unequal_cnt += 1 * w[i[0]]
    return (2.0 * unequal_cnt) / (x.size + unequal_cnt)


@jit(nopython=True)
def czebyshev_distance(sample_1: np.ndarray, sample_2: np.ndarray) -> float:

    r"""
    Calculate the Czebyshev distance between two N-dimensional samples.
    The Czebyshev distance is defined as the maximum absolute difference
    between the corresponding elements of the two arrays.

    .. note::
       Normalize arrays sample_1 and sample_2 before passing it to ensure accurate results.

    The equation for the Czebyshev distance is given by :math:`D_\infty(p, q) = \max_i \left| p_i - q_i \right|`.

    .. seealso:
       :func:`simba.mixins.statistics_mixin.Statistics.sliding_czebyshev_distance`

    :param np.ndarray sample_1: The first sample, an N-dimensional NumPy array.
    :param np.ndarray sample_2: The second sample, an N-dimensional NumPy array.
    :return: The Czebyshev distance between the two samples.
    :rtype: float

    :example:
    >>> sample_1 = np.random.randint(0, 10, (10000,100))
    >>> sample_2 = np.random.randint(0, 10, (10000,100))
    >>> czebyshev_distance(sample_1=sample_1, sample_2=sample_2)
    """

    c = 0.0
    for idx in np.ndindex(sample_1.shape):
        c = max((c, np.abs(sample_1[idx] - sample_2[idx])))
    return c

@njit(["(float32[:, :], float64[:], int64)", ])
def sliding_czebyshev_distance(x: np.ndarray, window_sizes: np.ndarray, sample_rate: float) -> np.ndarray:

    """
    Calculate the sliding Chebyshev distance for a given signal with different window sizes.
    This function computes the sliding Chebyshev distance for a signal `x` using
    different window sizes specified by `window_sizes`. The Chebyshev distance measures
    the maximum absolute difference between the corresponding elements of two signals.

    .. note::
       Normalize array x before passing it to ensure accurate results.

    .. seealso:
       For simple 2-sample comparison, use :func:`simba.mixins.statistics_mixin.Statistics.czebyshev_distance`

    :param np.ndarray x: Input signal, a 2D array with shape (n_samples, n_features).
    :param np.ndarray window_sizes: Array containing window sizes for sliding computation.
    :param float sample_rate: Sampling rate of the signal.
    :return: 2D array of Chebyshev distances for each window size and position.
    :rtype: np.ndarray

    :example:
    >>> sample_1 = np.random.randint(0, 10, (200,5)).astype(np.float32)
    >>> sample_2 = np.random.randint(0, 10, (10000,100))
    >>> sliding_czebyshev_distance(x=sample_1, window_sizes=np.array([1.0, 2.0]), sample_rate=10.0)
    """
    result = np.full((x.shape[0], window_sizes.shape[0]), 0.0)
    for i in range(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(range(0, x.shape[0] + 1), range(window_size, x.shape[0] + 1)):
            sample, c = x[l:r, :], 0.0
            for j in range(sample.shape[1]):
                c = max(c, (np.abs(np.min(sample[:, j]) - np.max(sample[:, j]))))
            result[r - 1, i] = c
    return result


@jit('(float32[:,:],)')
def mahalanobis_distance_cdist(data: np.ndarray) -> np.ndarray:
    """
    Compute the Mahalanobis distance between every pair of observations in a 2D array using numba.
    The Mahalanobis distance is a measure of the distance between a point and a distribution. It accounts for correlations between variables and the scales of the variables, making it suitable for datasets where features are not independent and have different variances.

    .. note::
       Significantly reduced runtime versus Mahalanobis scipy.cdist only with larger feature sets ( > 10-50).

    However, Mahalanobis distance may not be suitable in certain scenarios, such as:
    - When the dataset is small and the covariance matrix is not accurately estimated.
    - When the dataset contains outliers that significantly affect the estimation of the covariance matrix.
    - When the assumptions of multivariate normality are violated.

    :param np.ndarray data: 2D array with feature observations. Frames on axis 0 and feature values on axis 1
    :return: Pairwise Mahalanobis distance matrix where element (i, j) represents the Mahalanobis distance between  observations i and j.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 50, (1000, 200)).astype(np.float32)
    >>> x = mahalanobis_distance_cdist(data=data)
    """

    covariance_matrix = np.cov(data, rowvar=False)
    inv_covariance_matrix = np.linalg.inv(covariance_matrix).astype(np.float32)
    n = data.shape[0]
    distances = np.zeros((n, n))
    for i in prange(n):
        for j in range(n):
            diff = data[i] - data[j]
            diff = diff.astype(np.float32)
            distances[i, j] = np.sqrt(np.dot(np.dot(diff, inv_covariance_matrix), diff.T))
    return distances


def manhattan_distance_cdist(data: np.ndarray) -> np.ndarray:
    """
    Compute the pairwise Manhattan distance matrix between points in a 2D array.
    Can be preferred over Euclidean distance in scenarios where the movement is restricted
    to grid-based paths and/or the data is high dimensional.

    .. math::
       D_{\text{Manhattan}} = |x_2 - x_1| + |y_2 - y_1|

    :param data: 2D array where each row represents a featurized observation (e.g., frame)
    :return: Pairwise Manhattan distance matrix where element (i, j) represents the distance between points i and j.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 50, (10000, 2))
    >>> manhattan_distance_cdist(data=data)
    """
    check_valid_array(data=data, source=f'{manhattan_distance_cdist} data', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    differences = np.abs(data[:, np.newaxis, :] - data)
    results = np.sum(differences, axis=-1)
    return results

def jaccard_distance(x: np.ndarray, y: np.ndarray) -> float:

    """
    Calculate the Jaccard distance between two 1D NumPy arrays.
    The Jaccard distance is a measure of dissimilarity between two sets. It is defined as the size of the
    intersection of the sets divided by the size of the union of the sets.

    :param np.ndarray x: The first 1D NumPy array.
    :param np.ndarray y: The second 1D NumPy array.
    :return: The Jaccard distance between arrays x and y.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 5, (100))
    >>> y = np.random.randint(0, 7, (100))
    >>> jaccard_distance(x=x, y=y)
    >>> 0.2857143
    """
    check_valid_array(data=x, source=f'{jaccard_distance.__name__} x', accepted_ndims=(1,))
    check_valid_array(data=y, source=f'{jaccard_distance.__name__} y', accepted_ndims=(1,), accepted_dtypes=[x.dtype.type])
    u_x, u_y = np.unique(x), np.unique(y)
    return np.float32(1 -(len(np.intersect1d(u_x, u_y)) / len(np.unique(np.hstack((u_x, u_y))))))

@njit((float32[:], float32[:]))
def _hellinger_helper(x: np.ndarray, y: np.ndarray):
    """Jitted helper for computing Hellinger distances from ``hellinger_distance``"""
    result, norm_x, norm_y = 0.0, 0.0, 0.0
    for i in range(x.shape[0]):
        result += np.sqrt(x[i] * y[i])
        norm_x += x[i]
        norm_y += y[i]
    if norm_x == 0 and norm_y == 0:
        return 0.0
    elif norm_x == 0 or norm_y == 0:
        return 1.0
    else:
        return np.sqrt(1 - result / np.sqrt(norm_x * norm_y))

def hellinger_distance(self, x: np.ndarray, y: np.ndarray, bucket_method: Optional[Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"]] = "auto") -> float:

    r"""
    Compute the Hellinger distance between two vector distributions.
    .. note::
       The Hellinger distance is bounded and ranges from 0 to √2. Distance of √2 indicates that the two distributions are maximally dissimilar

    .. math::
       H(P, Q) = \frac{1}{\sqrt{2}} \sqrt{ \sum_{i=1}^{n} (\sqrt{P(i)} - \sqrt{Q(i)})^2 }

    where:
    - :math:`P(i)` is the probability of the :math:`i`-th event in distribution :math:`P`,
    - :math:`Q(i)` is the probability of the :math:`i`-th event in distribution :math:`Q`,
    - :math:`n` is the number of events.

    :param np.ndarray x: First 1D array representing a probability distribution.
    :param np.ndarray y: Second 1D array representing a probability distribution.
    :param Optional[Literal['fd', 'doane', 'auto', 'scott', 'stone', 'rice', 'sturges', 'sqrt']] bucket_method: Method for computing histogram bins. Default is 'auto'.
    :returns: Hellinger distance between the two input probability distributions.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 9000, (500000,))
    >>> y = np.random.randint(0, 9000, (500000,))
    >>> hellinger_distance(x=x, y=y, bucket_method='auto')
    """
    check_valid_array(data=x, source=f'{hellinger_distance.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{hellinger_distance.__name__} y', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f"{hellinger_distance.__name__} method", value=bucket_method, options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=x, method=bucket_method)
    s1_h = self._hist_1d(data=x, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    s2_h = self._hist_1d(data=y, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    return self._hellinger_helper(x=s1_h.astype(np.float32), y=s2_h.astype(np.float32))


@njit([(float32[:, :], float32[:, :]), (float32[:, :], types.misc.Omitted(None))])
def bray_curtis_dissimilarity(x: np.ndarray, w: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Jitted compute of the Bray-Curtis dissimilarity matrix between samples based on feature values.
    The Bray-Curtis dissimilarity measures the dissimilarity between two samples based on their feature values.
    It is useful for finding similar frames based on behavior.
    Useful for finding similar frames based on behavior.

    .. note::
       Adapted from `pynndescent <https://pynndescent.readthedocs.io/en/latest/>`_.

    :param np.ndarray x: 2d array with likely normalized feature values.
    :param Optional[np.ndarray] w: Optional 2d array with weights of same size as x. Default None and all observations will have the same weight.
    :returns: 2d array with same size as x representing dissimilarity values. 0 and the observations are identical and at 1 the observations are completly disimilar.
    :rtype: np.ndarray

    :example:
    >>> x = np.array([[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1]]).astype(np.float32)
    >>> bray_curtis_dissimilarity(x=x)
    >>> [[0, 1., 1., 0.], [1., 0., 0., 1.], [1., 0., 0., 1.], [0., 1., 1., 0.]]
    """
    if w is None:
        w = np.ones((x.shape[0], x.shape[0])).astype(np.float32)
    results = np.full((x.shape[0], x.shape[0]), 0.0)
    for i in prange(x.shape[0]):
        for j in range(i + 1, x.shape[0]):
            s1, s2, num, den = x[i], x[j], 0.0, 0.0
            for k in range(s1.shape[0]):
                num += np.abs(s1[k] - s2[k])
                den += np.abs(s1[k] + s2[k])
            if den == 0.0:
                val = 0.0
            else:
                val = (float(num) / den) * w[i, j]
            results[i, j] = val
            results[j, i] = val
    return results.astype(float32)


@njit([(int8[:], int8[:], types.misc.Omitted(None)), (int8[:], int8[:], float32[:])])
def sokal_sneath(x: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> float64:
    """
    Jitted calculate of the sokal sneath coefficient between two binary vectors (e.g., two classified behaviors). 0 represent independence, 1 represents complete interdependence.

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
    >>> sokal_sneath(x, y)
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


@njit([(int8[:], int8[:], float32[:]), (int8[:], int8[:], types.misc.Omitted(None))])
def yule_coef(x: np.ndarray, y: np.ndarray, w: Optional[np.ndarray] = None) -> float64:

    """
    Jitted calculate of the yule coefficient between two binary vectors (e.g., to classified behaviors). 0 represent independence, 2 represents
    complete interdependence.

    .. math::
       Yule Coefficient = \\frac{{2 \cdot t_f \cdot f_t}}{{t_t \cdot f_f + t_f \cdot f_t}}

    .. note::
       Adapted from `pynndescent <https://pynndescent.readthedocs.io/en/latest/>`_.

    :param np.ndarray x: First binary vector.
    :param np.ndarray x: Second binary vector.
    :param Optional[np.ndarray] w: Optional weights for each element. Can be classification probabilities. If not provided, equal weights are assumed.
    :returns: yule coefficient
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 2, (50,)).astype(np.int8)
    >>> y = x ^ 1
    >>> yule_coef(x=x, y=y)
    >>> 2
    >>> random_indices = np.random.choice(len(x), size=len(x)//2, replace=False)
    >>> y = np.copy(x)
    >>> y[random_indices] = 1 - y[random_indices]
    >>> yule_coef(x=x, y=y)
    >>> 0.99
    """
    if w is None:
        w = np.ones(x.shape[0]).astype(np.float32)
    f_f, t_t, t_f, f_t = 0.0, 0.0, 0.0, 0.0
    for i in prange(x.shape[0]):
        if (x[i] == 1) and (y[i] == 1):
            t_t += 1 * w[i]
        if (x[i] == 0) and (y[i] == 0):
            f_f += 1 * w[i]
        if (x[i] == 0) and (y[i] == 1):
            f_t += 1 * w[i]
        if (x[i] == 1) and (y[i] == 0):
            t_f += 1 * w[i]
    if t_f == 0.0 or f_t == 0.0:
        return 0.0
    else:
        return (2.0 * t_f * f_t) / (t_t * f_f + t_f * f_t)


@njit(
    [
        (int8[:], int8[:], types.misc.Omitted(value=False), float32[:]),
        (
            int8[:],
            int8[:],
            types.misc.Omitted(value=False),
            types.misc.Omitted(None),
        ),
        (int8[:], int8[:], bool_, float32[:]),
        (int8[:], int8[:], bool_, types.misc.Omitted(None)),
    ]
)
def hamming_distance(x: np.ndarray,
                     y: np.ndarray,
                     sort: Optional[bool] = False,w: Optional[np.ndarray] = None) -> float:
    """
    Jitted compute of the Hamming similarity between two vectors. The Hamming similarity measures the similarity between two binary vectors by counting the number of positions at which the corresponding elements are different.

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
    >>> hamming_distance(x=x, y=y)
    >>> 0.91
    """

    if w is None:
        w = np.ones(x.shape[0]).astype(np.float32)
    results = 0.0
    if sort:
        x, y = np.sort(x), np.sort(y)
    for i in prange(x.shape[0]):
        if x[i] != y[i]:
            results += 1.0 * w[i]
    return results / x.shape[0]



def population_stability_index(sample_1: np.ndarray, sample_2: np.ndarray, fill_value: Optional[int] = 1, bucket_method: Optional[     Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"] ] = "auto") -> float:
    r"""
    Compute Population Stability Index (PSI) comparing two distributions.
    The Population Stability Index (PSI) is a measure of the difference in distribution
    patterns between two groups of data. A low PSI value indicates a minimal or negligible change in the distribution patterns between the two samples.

    A high PSI value suggests a significant difference in the distribution patterns between the two samples.

    .. note::
       Empty bins (0 observations in bin) in is replaced with ``fill_value``. The PSI value ranges from 0 to positive infinity.

    The Population Stability Index (PSI) is calculated as:

    .. math::
       PSI = \\sum \\left(\\frac{{p_2 - p_1}}{{ln(p_2 / p_1)}}\\right)

    where:
        - \( p_1 \) and \( p_2 \) are the proportions of observations in the bins for sample 1 and sample 2 respectively.

    .. seealso::
       For time-series based rolling comparisons, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_population_stability_index`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param Optional[int] fill_value: Empty bins (0 observations in bin) in is replaced with ``fill_value``. Default 1.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: PSI distance between ``sample_1`` and ``sample_2``
    :rtype: float

    :example:
    >>> sample_1, sample_2 = np.random.randint(0, 100, (100,)), np.random.randint(0, 10, (100,))
    >>> population_stability_index(sample_1=sample_1, sample_2=sample_2, fill_value=1, bucket_method='auto')
    >>> 3.9657026867553817
    """
    check_valid_array(data=sample_1, source=population_stability_index.__name__, accepted_sizes=[1])
    check_valid_array(data=sample_2, source=population_stability_index.__name__, accepted_sizes=[1])
    check_int(name=population_stability_index.__name__, value=fill_value)
    check_str(name=population_stability_index.__name__,value=bucket_method,options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
    sample_1_hist = _hist_1d( data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_2_hist = _hist_1d( data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_1_hist[sample_1_hist == 0] = fill_value
    sample_2_hist[sample_2_hist == 0] = fill_value
    sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
    samples_diff = sample_2_hist - sample_1_hist
    log = np.log(sample_2_hist / sample_1_hist)
    return np.sum(samples_diff * log)


def total_variation_distance(x: np.ndarray, y: np.ndarray, bucket_method: Optional[Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"]] = "auto"):

    """
    Calculate the total variation distance between two probability distributions.

    :param np.ndarray x: A 1-D array representing the first sample.
    :param np.ndarray y: A 1-D array representing the second sample.
    :param Optional[str] bucket_method: The method used to determine the number of bins for histogram computation. Supported methods are 'fd' (Freedman-Diaconis), 'doane', 'auto', 'scott', 'stone', 'rice', 'sturges', and 'sqrt'. Defaults to 'auto'.
    :return: The total variation distance between the two distributions.
    :rtype: float

    .. math::
       TV(P, Q) = 0.5 \sum_i |P_i - Q_i|

    where :math:`P_i` and :math:`Q_i` are the probabilities assigned by the distributions :math:`P` and :math:`Q`
    to the same event :math:`i`, respectively.

    :example:
    >>> total_variation_distance(x=np.array([1, 5, 10, 20, 50]), y=np.array([1, 5, 10, 100, 110]))
    >>> 0.3999999761581421
    """
    check_valid_array(data=x, source=total_variation_distance.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=total_variation_distance.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f"{total_variation_distance.__name__} method", value=bucket_method, options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=x, method=bucket_method)
    s1_h = _hist_1d(data=x,bin_count=bin_count,range=np.array([0, int(bin_width * bin_count)]), normalize=True)
    s2_h = _hist_1d(data=y, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]), normalize=True,)
    return 0.5 * np.sum(np.abs(s1_h - s2_h))



def rolling_wasserstein_distance(data: np.ndarray,time_windows: np.ndarray,fps: int,bucket_method: Literal[    "fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"] = "auto") -> np.ndarray:
    """
    Compute rolling Wasserstein distance comparing the current time-window of size N to the preceding window of size N.

    .. seealso::
       For simple two distribution earth mover comparison, see :func:`simba.mixins.statistics_mixin.Statistics.wasserstein_distance`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param np.ndarray[ints] time_windows: Time windows to compute JS for in seconds.
    :param int fps: Frame-rate of recorded video.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: Size data.shape[0] x window_sizes.shape with Wasserstein distance. Columns represent different time windows.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 100, (100,))
    >>> rolling_wasserstein_distance(data=data, time_windows=np.array([1, 2]), fps=30)
    """
    check_valid_array(data=data, source=rolling_wasserstein_distance.__name__, accepted_sizes=[1])
    check_valid_array(data=time_windows, source=rolling_wasserstein_distance.__name__, accepted_sizes=[1])
    check_int(name=f"{rolling_wasserstein_distance.__name__} fps", value=fps, min_value=1)
    check_str(name=f"{rolling_wasserstein_distance.__name__} bucket_method",value=bucket_method,options=Options.BUCKET_METHODS.value)
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
            sample_1_hist = _hist_1d(data=sample_1,bin_count=bin_count,range=np.array([0, int(bin_width * bin_count)]))
            sample_2_hist = _hist_1d(data=sample_2,bin_count=bin_count,range=np.array([0, int(bin_width * bin_count)]))
            sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
            w = stats.wasserstein_distance(u_values=sample_1_hist, v_values=sample_2_hist)
            results[window_start:window_end, i] = w
    return results


def wasserstein_distance(sample_1: np.ndarray, sample_2: np.ndarray, bucket_method: Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt" ] = "auto") -> float:
    """
    Compute Wasserstein distance between two distributions.

    .. note::
       Uses ``stats.wasserstein_distance``. I have tried to move ``stats.wasserstein_distance`` to jitted method extensively,
       but this doesn't give significant runtime improvement. Rate-limiter appears to be the _hist_1d.

    .. seealso::
       For time-series based comparisons, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_wasserstein_distance`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: Wasserstein distance between ``sample_1`` and ``sample_2``
    :rtype: float

    :example:
    >>> sample_1 = np.random.normal(loc=10, scale=2, size=10)
    >>> sample_2 = np.random.normal(loc=10, scale=3, size=10)
    >>> wasserstein_distance(sample_1=sample_1, sample_2=sample_2)
    >>> 0.020833333333333332

    """
    check_valid_array(data=sample_1, source=wasserstein_distance.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array( data=sample_2, source=wasserstein_distance.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f"{wasserstein_distance.__name__} bucket_method",value=bucket_method,options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
    sample_1_hist = _hist_1d(data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_2_hist = _hist_1d( data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
    return stats.wasserstein_distance(u_values=sample_1_hist, v_values=sample_2_hist)

def rolling_jensen_shannon_divergence(data: np.ndarray, time_windows: np.ndarray, fps: int, bucket_method: Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"] = "auto",) -> np.ndarray:
    """
    Compute rolling Jensen-Shannon divergence comparing the current time-window of size N to the preceding window of size N.

    .. seealso::
       For simple two distribution comparison, see :func:`simba.mixins.statistics_mixin.Statistics.jensen_shannon_divergence`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param np.ndarray[ints] time_windows: Time windows to compute JS for in seconds.
    :param int fps: Frame-rate of recorded video.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: Array of size data.shape[0] x window_sizes.shape[0] with Jensen-Shannon divergence. Columns represents different time windows.
    :rtype: np.ndarray

    """
    check_valid_array(data=data, source=rolling_jensen_shannon_divergence.__name__, accepted_sizes=[1])
    check_valid_array(data=time_windows, source=rolling_jensen_shannon_divergence.__name__, accepted_sizes=[1])
    check_int(name=f"{rolling_jensen_shannon_divergence.__name__} fps", value=fps, min_value=1)
    check_str(name=f"{rolling_jensen_shannon_divergence.__name__} bucket_method", value=bucket_method, options=Options.BUCKET_METHODS.value)
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
            sample_1_hist = _hist_1d(data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
            sample_2_hist = _hist_1d(data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
            sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
            mean_hist = np.mean([sample_1_hist, sample_2_hist], axis=0)
            kl_sample_1, kl_sample_2 = stats.entropy(pk=sample_1_hist, qk=mean_hist), stats.entropy(pk=sample_2_hist, qk=mean_hist)
            js = (kl_sample_1 + kl_sample_2) / 2
            results[window_start:window_end, i] = js
    return results



def jensen_shannon_divergence(
    sample_1: np.ndarray,
    sample_2: np.ndarray,
    bucket_method: Literal[
        "fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"
    ] = "auto",
) -> float:

    r"""
    Compute Jensen-Shannon divergence between two distributions. Useful for (i) measure drift in datasets, and (ii) featurization of distribution shifts across
    sequential time-bins.
    .. note::
       JSD = 0: Indicates that the two distributions are identical.
       0 < JSD < 1: Indicates a degree of dissimilarity between the distributions, with values closer to 1 indicating greater dissimilarity.
       JSD = 1: Indicates that the two distributions are maximally dissimilar.

    .. math::
       JSD = \frac{KL(P_1 || M) + KL(P_2 || M)}{2}

    .. seealso::
       For rolling comparisons in a timeseries, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_jensen_shannon_divergence`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators.
    :returns: Jensen-Shannon divergence between ``sample_1`` and ``sample_2``
    :rtype: float

    :example:
    >>> sample_1, sample_2 = np.array([1, 2, 3, 4, 5, 10, 1, 2, 3]), np.array([1, 5, 10, 9, 10, 1, 10, 6, 7])
    >>> .jensen_shannon_divergence(sample_1=sample_1, sample_2=sample_2, bucket_method='fd')
    >>> 0.30806541358219786
    """
    check_valid_array(data=sample_1, source=jensen_shannon_divergence.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array( data=sample_2, source=jensen_shannon_divergence.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f"{jensen_shannon_divergence.__name__} bucket_method", value=bucket_method, options=Options.BUCKET_METHODS.value)
    bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
    sample_1_hist = _hist_1d(data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_2_hist = _hist_1d(data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    mean_hist = np.mean([sample_1_hist, sample_2_hist], axis=0)
    kl_sample_1, kl_sample_2 = stats.entropy(pk=sample_1_hist, qk=mean_hist), stats.entropy(pk=sample_2_hist, qk=mean_hist)
    return (kl_sample_1 + kl_sample_2) / 2




def rolling_kullback_leibler_divergence(data: np.ndarray, time_windows: np.ndarray, fps: int, fill_value: int = 1, bucket_method: Literal[     "fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt" ] = "auto",) -> np.ndarray:

    """
    Compute rolling Kullback-Leibler divergence comparing the current time-window of
    size N to the preceding window of size N.

    .. note::
       Empty bins (0 observations in bin) in is replaced with ``fill_value``.

    .. seealso::
       For single comparison between two distributions, see :func:`simba.mixins.statistics_mixin.Statistics.kullback_leibler_divergence`

    :param ndarray sample_1: 1d array representing feature values.
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :param np.ndarray[floats] time_windows: Time windows to compute JS for in seconds.
    :param int fps: Frame-rate of recorded video.
    :returns: Size data.shape[0] x window_sizes.shape with Kullback-Leibler divergence. Columns represents different tiem windows.
    :rtype: np.ndarray

    :example:
    >>> sample_1, sample_2 = np.random.normal(loc=10, scale=700, size=5), np.random.normal(loc=50, scale=700, size=5)
    >>> data = np.hstack((sample_1, sample_2))
    >>> .rolling_kullback_leibler_divergence(data=data, time_windows=np.array([1]), fps=2)
    """
    check_valid_array(data=data, source=rolling_kullback_leibler_divergence.__name__, accepted_sizes=[1])
    check_valid_array(data=time_windows, source=rolling_kullback_leibler_divergence.__name__, accepted_sizes=[1])
    check_int(name=f"{rolling_kullback_leibler_divergence.__name__} fps", value=fps, min_value=1)
    check_str(name=f"{rolling_kullback_leibler_divergence.__name__} bucket_method", value=bucket_method, options=Options.BUCKET_METHODS.value)
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
            sample_1_hist = _hist_1d(data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
            sample_2_hist = _hist_1d( data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
            sample_1_hist[sample_1_hist == 0] = fill_value
            sample_2_hist[sample_2_hist == 0] = fill_value
            sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
            kl = stats.entropy(pk=sample_1_hist, qk=sample_2_hist)
            results[window_start:window_end, i] = kl
    return results

def kullback_leibler_divergence(sample_1: np.ndarray, sample_2: np.ndarray, fill_value: Optional[int] = 1, bucket_method: Literal[     "fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt" ] = "auto") -> float:

    r"""
    Compute Kullback-Leibler divergence between two distributions.

    .. note::
       Empty bins (0 observations in bin) in is replaced with passed ``fill_value``.
       Its range is from 0 to positive infinity. When the KL divergence is zero, it indicates that the two distributions are identical. As the KL divergence increases, it signifies an increasing difference between the distributions.

    .. math::
       \text{KL}(P || Q) = \sum{P(x) \log{\left(\frac{P(x)}{Q(x)}\right)}}

    .. seealso::
       For rolling comparisons in a timeseries, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_kullback_leibler_divergence`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param Optional[int] fill_value: Optional pseudo-value to use to fill empty buckets in ``sample_2`` histogram
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: Kullback-Leibler divergence between ``sample_1`` and ``sample_2``
    :rtype: float

    """
    check_valid_array(data=sample_1, source=kullback_leibler_divergence.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array( data=sample_2, source=kullback_leibler_divergence.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_str(name=f"{kullback_leibler_divergence.__name__} bucket_method", value=bucket_method, options=Options.BUCKET_METHODS.value,)
    check_int(name=f"{kullback_leibler_divergence.__name__} fill value", value=fill_value, min_value=1)
    bin_width, bin_count = bucket_data(data=sample_1, method=bucket_method)
    sample_1_hist = _hist_1d(data=sample_1, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_2_hist =_hist_1d(data=sample_2, bin_count=bin_count, range=np.array([0, int(bin_width * bin_count)]))
    sample_1_hist[sample_1_hist == 0] = fill_value
    sample_2_hist[sample_2_hist == 0] = fill_value
    sample_1_hist, sample_2_hist = sample_1_hist / np.sum(sample_1_hist), sample_2_hist / np.sum(sample_2_hist)
    return stats.entropy(pk=sample_1_hist, qk=sample_2_hist)