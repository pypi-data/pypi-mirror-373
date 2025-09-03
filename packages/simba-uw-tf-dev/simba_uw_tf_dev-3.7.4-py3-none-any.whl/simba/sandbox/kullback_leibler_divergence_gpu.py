from cuml.metrics import kl_divergence
from typing import Literal
import numpy as np
from scipy import stats
from simba.utils.data import hist_1d, bucket_data
from simba.mixins.statistics_mixin import Statistics


def kullback_leibler_divergence_gpu(x: np.ndarray, y: np.ndarray, fill_value: int = 1, bucket_method: Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"] = "scott") -> float:
    """
    Compute Kullback-Leibler divergence between two distributions.

    .. note::
       Empty bins (0 observations in bin) in is replaced with passed ``fill_value``.

       Its range is from 0 to positive infinity. When the KL divergence is zero, it indicates that the two distributions are identical. As the KL divergence increases, it signifies an increasing difference between the distributions.

    :param ndarray x: First 1d array representing feature values.
    :param ndarray y: Second 1d array representing feature values.
    :param Optional[int] fill_value: Optional pseudo-value to use to fill empty buckets in ``y`` histogram
    :param Literal bucket_method: Estimator determining optimal bucket count and bucket width. Default: The maximum of the Sturges and Freedman-Diaconis estimators
    :returns: Kullback-Leibler divergence between ``x`` and ``y``
    :rtype: float

    :example:
    >>> x, y = np.random.normal(loc=150, scale=900, size=10000000), np.random.normal(loc=140, scale=900, size=10000000)
    >>> kl = kullback_leibler_divergence_gpu(x=x, y=y)
    """


    bin_width, bin_count = bucket_data(data=x, method=bucket_method)
    r = np.array([np.min(x), np.max(x)])
    x_hist = Statistics._hist_1d(data=x, bin_count=bin_count, range=r)
    y_hist = Statistics._hist_1d(data=y, bin_count=bin_count, range=r)
    y_hist[y_hist == 0] = fill_value
    x_hist, y_hist = x_hist / np.sum(x_hist), y_hist / np.sum(y_hist)
    return kl_divergence(P=x_hist.astype(np.float32), Q=y_hist.astype(np.float32), convert_dtype=False)


def kullback_leibler_divergence(x: np.ndarray, y: np.ndarray, fill_value: int = 1, bucket_method: Literal["fd", "doane", "auto", "scott", "stone", "rice", "sturges", "sqrt"] = "scott") -> float:
    bin_width, bin_count = bucket_data(data=x, method=bucket_method)
    r = np.array([np.min(x), np.max(x)])

    x_hist = Statistics._hist_1d(data=x, bin_count=bin_count, range=r)
    y_hist = Statistics._hist_1d(data=y, bin_count=bin_count, range=r)
    x_hist[x_hist == 0] = fill_value
    y_hist[y_hist == 0] = fill_value
    x_hist, y_hist = x_hist / np.sum(x_hist), y_hist / np.sum(y_hist)

    return stats.entropy(pk=x_hist, qk=y_hist)


x, y = np.random.normal(loc=150, scale=900, size=10000000), np.random.normal(loc=140, scale=900, size=10000000)
a = kullback_leibler_divergence_gpu(x=x, y=y)
#data = np.hstack((sample_1, sample_2))



a = kullback_leibler_divergence_gpu(x=x, y=y)
b = kullback_leibler_divergence(x=x, y=y)

