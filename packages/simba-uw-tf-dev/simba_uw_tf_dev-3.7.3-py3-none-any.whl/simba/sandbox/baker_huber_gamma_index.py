import numpy as np
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
from sklearn.datasets import make_blobs
from simba.utils.read_write import get_unique_values_in_iterable
from cupyx.scipy.spatial.distance import cdist
import cupy as cp
from numba import cuda

@cuda.jit()
def baker_huber_gamma_index_kernel(distances, lbls):
    x, y = cuda.grid(2)
    if x >= distances.shape[0] and y >= distances.shape[1]:
        pass
    data_loc = distances[x][y]
    for h in range(distances.shape[0]):
        for k in range(h + 1, distances.shape[1]):
            ref_loc = distances[h][k]



def baker_huber_gamma_index(x: np.ndarray,
                            y: np.ndarray,
                            batch_size: int = 3e+3) -> float:

    distances = cdist(x, x)
    cp.fill_diagonal(distances, np.nan)
    distances = np.ascontiguousarray(distances.get())
    distances_dev = cuda.to_device(x)
    y_dev = cuda.to_device(y)
    grid_x = (distances.shape[0] + 16 - 1) // 16
    grid_y = (distances.shape[1] + 16 - 1) // 16
    grid_z = 3
    threads_per_block = (16, 16, 1)
    blocks_per_grid = (grid_y, grid_x, grid_z)
    baker_huber_gamma_index_kernel[blocks_per_grid, threads_per_block](distances_dev, y_dev)



    # same_idx = []
    # for cluster_id in unique_labels:
    #     cluster_idx = np.argwhere(y == cluster_id).flatten()
    #     same_idx.extend(list(itertools.combinations(cluster_idx, 2)))
    # for idx in same_idx:
    #     cluster_matrix[idx[0]][idx[1]] = 1
    # #m_idx = list(itertools.product(range(x.shape[0]), range(x.shape[0])))
    # #m_idx = [(x[0], x[1]) for x in m_idx if x[0] != x[1]]
    # for i in range(cluster_matrix.shape[0]):
    #     for j in range(i + 1, cluster_matrix.shape[1]):
    #         for h in range(cluster_matrix.shape[0]):
    #             for k in range(h + 1, cluster_matrix.shape[1]):
    #                 print(i, j, h, k)


from sklearn.datasets import make_blobs
X, labels = make_blobs(n_samples=100000, centers=5, random_state=42, n_features=10, cluster_std=100)
score = baker_huber_gamma_index(X, labels)
print(f"{score}")