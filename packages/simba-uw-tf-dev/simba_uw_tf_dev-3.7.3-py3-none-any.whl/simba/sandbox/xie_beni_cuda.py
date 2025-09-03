import numpy as np
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
from sklearn.datasets import make_blobs
from simba.utils.read_write import get_unique_values_in_iterable

try:
    import cupy as cp
    from cupyx.scipy.spatial.distance import cdist
except:
    print('GPU not detected')
    import numpy as cp
    from scipy.spatial.distance import cdist

# import numpy as cp
# from scipy.spatial.distance import cdist

def xie_beni(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the Xie-Beni index for clustering evaluation.

    The score is calculated as the ratio between the average intra-cluster variance and the squared minimum distance between cluster centroids. This ensures that the index penalizes both loosely packed clusters and clusters that are too close to each other.

    A lower Xie-Beni index indicates better clustering quality, signifying well-separated and compact clusters.

    .. seealso::
       To compute Xie-Beni on the CPU, use :func:`~simba.mixins.statistics_mixin.Statistics.xie_beni`

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The Xie-Beni score for the dataset.
    :rtype: float

    :example:
    >>> from sklearn.datasets import make_blobs
    >>> X, y = make_blobs(n_samples=100000, centers=40, n_features=600, random_state=0, cluster_std=0.3)
    >>> xie_beni(x=X, y=y)

    :references:
    .. [1] X. L. Xie, G. Beni (1991). A validity measure for fuzzy clustering.
           In: IEEE Transactions on Pattern Analysis and Machine Intelligence 13(8), 841 - 847. DOI: 10.1109/34.85677
    """
    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=xie_beni.__name__, min=2)
    x, y = cp.array(x), cp.array(y)
    cluster_ids = cp.unique(y)
    centroids = cp.full(shape=(cluster_ids.shape[0], x.shape[1]), fill_value=-1.0, dtype=cp.float32)
    intra_centroid_distances = cp.full(shape=(y.shape[0]), fill_value=-1.0, dtype=cp.float32)
    obs_cnt = 0
    for cnt, cluster_id in enumerate(cluster_ids):
        cluster_obs = x[cp.argwhere(y == cluster_id).flatten()]
        centroids[cnt] = cp.mean(cluster_obs, axis=0)
        intra_dist = cp.linalg.norm(cluster_obs - centroids[cnt], axis=1)
        intra_centroid_distances[obs_cnt: cluster_obs.shape[0] + obs_cnt] = intra_dist
        obs_cnt += cluster_obs.shape[0]
    compactness = cp.mean(cp.square(intra_centroid_distances))
    cluster_dists = cdist(centroids, centroids).flatten()
    d = cp.sqrt(cluster_dists[cp.argwhere(cluster_dists > 0).flatten()])
    separation = cp.min(d)
    xb = compactness / separation
    return xb



import time


X, y = make_blobs(n_samples=1000000, centers=25, n_features=400, random_state=0, cluster_std=0.1)
xie_beni_cuda(x=X, y=y)
start = time.perf_counter()
p = xie_beni_cuda(x=X, y=y)
end = time.perf_counter()
print(end-start)
print(type(p), p)


