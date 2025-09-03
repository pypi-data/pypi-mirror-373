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

#import numpy as cp
#from scipy.spatial.distance import cdist

def sd_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the SD (Scatter and Discriminant) Index for evaluating the quality of a clustering solution.
    The SD Index combines two components to measure clustering quality:
    1. **Scatter (SCAT)**: Evaluates the compactness of clusters by measuring the ratio of intra-cluster variance to the global standard deviation.
    2. **Discriminant (DIS)**: Measures the separation between clusters relative to their distance from the global mean.
    A lower SD Index indicates better clustering quality, reflecting compact and well-separated clusters.
    :param np.ndarray x: A 2D array of shape (n_samples, n_features) representing the feature vectors of the data points.
    :param np.ndarray y: A 1D array of shape (n_samples,) containing the cluster labels for each data point.
    :returns: The SD Index value. Lower values indicate better clustering quality with more compact and well-separated clusters.
    :rtype: float
    :example:
    >>> X, y = make_blobs(n_samples=800, centers=2, n_features=3, random_state=0, cluster_std=0.1)
    >>> Statistics.sd_index(x=X, y=y)
    :references:
    .. [1] Halkidi, M., Vazirgiannis, M., Batistakis, Y. (2000). Quality Scheme Assessment in the Clustering Process. In: Zighed, D.A., Komorowski, J., Żytkow, J. (eds) Principles of Data Mining and Knowledge Discovery. PKDD 2000.
           Lecture Notes in Computer Science(), vol 1910. Springer, Berlin, Heidelberg. https://doi.org/10.1007/3-540-45372-5_26
    """
    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=(int,), accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=sd_index.__name__, min=2)
    x, y = cp.array(x), cp.array(y)
    global_std = cp.std(x)
    global_m = cp.mean(x, axis=0)
    unique_clusters = cp.unique(y)
    cnt_y = unique_clusters.shape[0]
    scat, dis = 0, 0
    centroids = cp.full(shape=(cnt_y, x.shape[1]), fill_value=-1.0, dtype=cp.float32)
    for cnt, cluster in enumerate(unique_clusters):
        cluster_data = x[y == cluster]
        centroids[cnt] = cp.mean(cluster_data, axis=0)
        scat += cp.mean(cp.std(cluster_data, axis=0)) / global_std
    for i in range(cnt_y):
        for j in range(i + 1, cnt_y):
            dist_between_clusters = cp.linalg.norm(centroids[i] - centroids[j])
            dist_to_global = (cp.linalg.norm(centroids[i] - global_m) + cp.linalg.norm(centroids[j] - global_m)) / 2
            dis += dist_between_clusters / dist_to_global
    scat /= cnt_y
    dis /= (cnt_y * (cnt_y - 1) / 2)
    return scat + dis

import time
X, y = make_blobs(n_samples=2000000, centers=25, n_features=400, random_state=0, cluster_std=0.1)
start = time.perf_counter()
p = sd_index(x=X, y=y)
end = time.perf_counter()
print(end-start)
print(type(p), p)