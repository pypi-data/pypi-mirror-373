import numpy as np
import cupy as cp
import time
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats



def calinski_harabasz_gpu(x: np.ndarray, y: np.ndarray):
    check_valid_array(data=x, source=f'{calinski_harabasz_gpu.__name__} x', accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_ndims=(2,))
    check_valid_array(data=y, source=f'{calinski_harabasz_gpu.__name__} y', accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_ndims=(1,), accepted_axis_0_shape=[x.shape[0],])

    x, y = cp.array(x), cp.array(y)
    lbs = cp.unique(y)
    n_lbls = lbs.shape[0]
    global_means = cp.mean(x, axis=0)
    extra_dispersion, intra_dispersion = 0.0, 0.0
    for k in range(n_lbls):
        cluster_k = x[cp.argwhere(y == lbs[k]).flatten(), :]
        means_k = cp.mean(cluster_k, axis=0)
        extra_dispersion += len(cluster_k) * cp.sum((means_k - global_means) ** 2)
        intra_dispersion += cp.sum((cluster_k - means_k) ** 2)
    denominator = intra_dispersion * (n_lbls - 1.0)
    if denominator == 0.0:
        return 0.0
    else:
        results = extra_dispersion * (x.shape[0] - n_lbls) / denominator
        return results.get()



def calinski_harabasz(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the Calinski-Harabasz score to evaluate clustering quality.

    The Calinski-Harabasz score is a measure of cluster separation and compactness.
    It is calculated as the ratio of the between-cluster dispersion to the
    within-cluster dispersion. A higher score indicates better clustering.

    .. note::
       Modified from `scikit-learn <https://github.com/scikit-learn/scikit-learn/blob/8721245511de2f225ff5f9aa5f5fadce663cd4a3/sklearn/metrics/cluster/_unsupervised.py#L326>`_

    The Calinski-Harabasz score (CH) is calculated as:

    .. math::

        CH = \\frac{B}{W} \\times \\frac{N - k}{k - 1}

    where:
    - :math:`B` is the sum of squared distances between cluster centroids,
    - :math:`W` is the sum of squared distances from each point to its assigned cluster centroid,
    - :math:`N` is the total number of data points,
    - :math:`k` is the number of clusters.

    :param x: 2D array representing the data points. Shape (n_samples, n_features/n_dimension).
    :param y: 2D array representing cluster labels for each data point. Shape (n_samples,).
    :return: Calinski-Harabasz score.
    :float: float

    :example:
    :example:
    >>> x = np.random.random((100, 2)).astype(np.float32)
    >>> y = np.random.randint(0, 100, (100,)).astype(np.int64)
    >>> Statistics.calinski_harabasz(x=x, y=y)
    """

    n_labels = np.unique(y).shape[0]
    labels = np.unique(y)
    extra_dispersion, intra_dispersion = 0.0, 0.0
    global_mean = np.full((x.shape[1]), np.nan)
    for i in range(x.shape[1]):
        global_mean[i] = np.mean(x[:, i].flatten())
    for k in range(n_labels):
        cluster_k = x[np.argwhere(y == labels[k]).flatten(), :]
        mean_k = np.full((cluster_k.shape[1]), np.nan)
        for i in range(cluster_k.shape[1]):
            mean_k[i] = np.mean(cluster_k[:, i].flatten())
        extra_dispersion += len(cluster_k) * np.sum((mean_k - global_mean) ** 2)
        intra_dispersion += np.sum((cluster_k - mean_k) ** 2)

    denominator = intra_dispersion * (n_labels - 1.0)
    if denominator == 0.0:
        return 0.0
    else:
        return extra_dispersion * (x.shape[0] - n_labels) / denominator


from sklearn.datasets import make_blobs
start = time.time()

x, y = make_blobs(n_samples=200000, n_features=500, centers=70, cluster_std=5, center_box=(5, 10))
score_gpu = calinski_harabasz_gpu(x=x, y=y)
print(time.time() - start)

start = time.time()

score_cpu = calinski_harabasz(x=x, y=y)

print(score_cpu, score_gpu)
print(time.time() - start)