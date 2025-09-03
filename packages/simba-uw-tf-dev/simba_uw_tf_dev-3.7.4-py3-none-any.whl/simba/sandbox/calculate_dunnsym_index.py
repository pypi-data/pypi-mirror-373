import numpy as np
from sklearn.datasets import make_blobs
from scipy.spatial.distance import cdist
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
from simba.utils.read_write import get_unique_values_in_iterable



def dunn_symmetry_idx(x: np.ndarray, y: np.ndarray) -> float:
    """
    DunnSym index output range positive real numbers 0 -> ∞ where 0 is extremely poor clustering and higher values represent better cluster separation.

    :param x: 2D array representing the data points. Shape (n_samples, n_features/n_dimension).
    :param y: 2D array representing cluster labels for each data point. Shape (n_samples,).
    :return float: Dynn-Symmetry index.

    :references:
       .. [1]  Ikotun, A. M., Habyarimana, F., & Ezugwu, A. E. (2025). Cluster validity indices for automatic clustering: A comprehensive review. Heliyon, 11(2), e41953. https://doi.org/10.1016/j.heliyon.2025.e41953
       .. [2]  Hassan, B. A., Tayfor, N. B., Hassan, A. A., Ahmed, A. M., Rashid, T. A., & Abdalla, N. N. (2024). From A-to-Z review of clustering validation indices. arXiv. https://doi.org/10.48550/arXiv.2407.20246

    :example:
    >>> x, y = make_blobs(n_samples=1000, n_features=2, centers=5, random_state=42, cluster_std=0.1)
    >>> dunn_symmetry_idx(x=x, y=y)
    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=dunn_symmetry_idx.__name__, min=2)
    unique_clusters = np.unique(y)
    min_inter_distance, max_intra_diameter = np.inf, -np.inf
    for i in range(len(unique_clusters)):
        for j in range(i + 1, len(unique_clusters)):
            i_points = x[y == i]
            j_points = x[y == j]
            min_inter_distance = min(min_inter_distance, np.min(cdist(i_points, j_points)))

    for i in range(len(unique_clusters)):
        i_points = x[y == i]
        max_intra_diameter = max(max_intra_diameter, np.max(cdist(i_points, i_points)))

    return min_inter_distance / max_intra_diameter








x, y = make_blobs(n_samples=1000, n_features=2, centers=5, random_state=42, cluster_std=0.1)
dunn_symmetry_idx(x=x, y=y)


