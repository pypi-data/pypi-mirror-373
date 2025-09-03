try:
    import cupy as cp
    from cupyx.scipy.spatial.distance import cdist
except:
    import numpy as cp
    from scipy.spatial.distance import cdist
import numpy as np

from simba.data_processors.cuda.utils import _is_cuda_available
from sklearn.datasets import make_blobs
from simba.utils.errors import SimBAGPUError
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
from numba import cuda
import time


THREADS_PER_BLOCK = 1024



@cuda.jit()
def _silhouette_score_kernel(distances, y, unique_y, results):
    i = cuda.grid(1)
    if i >= distances.shape[0]:
        return
    cluster_id, obs_dists = y[i], distances[i]
    a, a_count = 0, 0
    for idx_intra in range(y.shape[0]):
        if (idx_intra != i) and (y[idx_intra] == cluster_id):
            a += obs_dists[idx_intra]
            a_count += 1
    if a_count != 0:
        a_i = (a / a_count)
    else:
        a_i = 0

    b_i = np.inf
    for inter_cluster_id in unique_y:
        if inter_cluster_id != cluster_id:
            b, b_cnt = 0, 0
            for idx_inter in range(y.shape[0]):
                if y[idx_inter] == inter_cluster_id:
                    b += obs_dists[idx_inter]
                    b_cnt += 1
            b_i = min(b_i, (b / b_cnt))
            results[i] = (b_i - a_i) / max(a_i, b_i)


        #     a_i = (a / a_count)
        # else:
        #     a_i = 0


def silhouette_score(x: np.ndarray, y: np.ndarray) -> float:
    is_available = _is_cuda_available()[0]
    if not is_available: raise SimBAGPUError(msg='No GPU detected', source=silhouette_score.__name__)
    check_valid_array(data=x, source=silhouette_score.__name__, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=silhouette_score.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0]])
    distances = cdist(XA=x, XB=x, metric='euclidean')
    results = np.full(x.shape[0], fill_value=-1.0, dtype=np.float32)
    unique_y = np.unique(y)

    distances_dev = cuda.to_device(distances)
    results_dev = cuda.to_device(results)
    y_dev = cuda.to_device(y)
    unique_y_dev = cuda.to_device(unique_y)

    bpg = (x.shape[0] + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK
    _silhouette_score_kernel[bpg, THREADS_PER_BLOCK](distances_dev, y_dev, unique_y_dev, results_dev)
    results = results_dev.copy_to_host()
    return np.mean(results)






x, y = make_blobs(n_samples=10000, n_features=100, centers=5, cluster_std=10)
start = time.perf_counter()
c = silhouette_score(x=x, y=y)
print(time.perf_counter() - start)


from sklearn.metrics import silhouette_score as sklearn_silhouette  # SKLEARN ALTERNATIVE
start = time.perf_counter()
score_sklearn = sklearn_silhouette(x, y)

#print(c, score_sklearn)
print(time.perf_counter() - start)





