import itertools

import numpy as np
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
from simba.utils.read_write import get_unique_values_in_iterable
from scipy.spatial.distance import cdist


def banfeld_raftery_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the Banfeld-Raftery index for clustering evaluation.

    Smaller values represent better clustering. Values can be negative.

    :param x: 2D NumPy array of shape (n_samples, n_features) representing the dataset.
    :param y: 1D NumPy array of shape (n_samples,) containing cluster labels for each data point.
    :return: The Banfeld-Raftery index.
    :rtype: float

    :references:
       .. [1] Banfield, J. D., & Raftery, A. E. (1993). Model-based Gaussian and non-Gaussian clustering. Biometrics, 49(3), 803-821. https://doi.org/10.2307/2532201

    """
    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)
    val = 0.0
    for cluster_label in unique_labels:
        cluster_data = x[y == cluster_label]
        n_k = cluster_data.shape[0]
        covariance_matrix = np.cov(cluster_data, rowvar=False)
        determinant = np.linalg.det(covariance_matrix)
        determinant = max(determinant, 1e-10)
        val += n_k * np.log(determinant)

    return val


def scott_symons_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the Scott-Symons index for clustering evaluation.

    Smaller values represent better clustering. Values can be negative.

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The Scott-Symons index score.
    :rtype: float


    :references:
       .. [1] . J. Scott and M. J. Symons. Clustering methods based on likelihood ratio criteria. Biometrics, 27:387–397, 1971.

    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)
    val = 0.0

    for label in unique_labels:
        cluster_points = x[y == label]
        n_k = cluster_points.shape[0]
        cov_matrix = np.cov(cluster_points, rowvar=False)
        det_cov = np.linalg.det(cov_matrix)
        val += n_k * np.log(det_cov / n_k)

    return val


def wemmert_gancarski_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the Wemmert-Gançarski index for clustering evaluation.
    
    The best case is when the index approaches 1, indicating good clustering. The worst case is when the index approaches 0, indicating poor clustering.

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The Wemmert-Gançarski index score.
    :rtype: float

    :references:
       .. [1] Bernard Desgraupes, University Paris Ouest Lab Modal’X, https://cran.r-project.org/web/packages/clusterCrit/vignettes/clusterCrit.pdf
    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)
    N = x.shape[0]
    total_score = 0.0

    for label in unique_labels:
        cluster_points = x[y == label]
        n_k = cluster_points.shape[0]
        G_k = np.mean(cluster_points, axis=0)

        R_values = []
        for point in cluster_points:
            dist_to_G_k = np.linalg.norm(point - G_k)
            distances_to_other_centroids = [np.linalg.norm(point - np.mean(x[y == other_label], axis=0)) for other_label in unique_labels if other_label != label]
            min_dist_to_other_centroids = min(distances_to_other_centroids)
            R_values.append(dist_to_G_k / min_dist_to_other_centroids)

        J_k = max(0, 1 - (1 / n_k) * np.sum(R_values))
        total_score += n_k * J_k

    return total_score / N


def mclain_rao_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes the McClain-Rao Index, which measures the quality of clustering by evaluating the ratio of
    the mean within-cluster distances to the mean between-cluster distances.

    The McClain-Rao Index is computed by calculating the mean ratio of intra-cluster distances (distances
    between points within the same cluster) to inter-cluster distances (distances between points from
    different clusters). A lower value indicates a better clustering result, with clusters being compact and well-separated.

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The McClain-Rao Index score, a lower value indicates better clustering quality.
    :rtype: float

    :references:
       .. [1] McClain, J. O., & Rao, V. R. (1975). CLUSTISZ: A program to test for the quality of clustering of a set of objects.  *Journal of Marketing Research, 12*(4), 456-460. https://doi.org/10.1177/002224377501200410
    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)
    ratios = np.full(shape=(len(unique_labels)), fill_value=np.nan, dtype=np.float64)
    for cluster_cnt, cluster_id in enumerate(unique_labels):
        cluster_obs = x[np.argwhere(y == cluster_id).flatten()]
        noncluster_obs = x[np.argwhere(y != cluster_id).flatten()]
        intra_dists = cdist(cluster_obs, cluster_obs)
        np.fill_diagonal(intra_dists, np.nan)
        intra_dist_mean = np.nanmean(intra_dists)
        inter_dist_mean = np.mean(cdist(cluster_obs, noncluster_obs))
        ratios[cluster_cnt] = intra_dist_mean / inter_dist_mean

    return np.mean(ratios)


def s_dbw_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the S_Dbw index for evaluating the clustering quality.

    A lower value indicates a better clustering result.

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The S_Dbw index score.
    :rtype: float


    .. note::
       Behaves weird as the number of dimensions increase (> 20).

    :example:
    >>> from sklearn.datasets import make_blobs
    >>> X, labels = make_blobs(n_samples=5000, centers=5, random_state=42, n_features=3, cluster_std=2)
    >>> score = s_dbw_index(X, labels)

    :references:
       .. [1]  M. Halkidi and M. Vazirgiannis. Clustering validity assessment: Finding the optimal partitioning of a data set. Proceedings IEEE International Conference on Data Mining, pages 187–194, 2001.
    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    _ = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)
    K = len(unique_labels)
    centroids = np.array([x[y == label].mean(axis=0) for label in unique_labels])
    variances = np.array([np.var(x[y == label], axis=0) for label in unique_labels])
    sigma = np.sqrt(np.sum(np.linalg.norm(variances, axis=1)) / K)
    s_dbw = 0.0
    for k in range(K):
        for k_prime in range(k + 1, K):
            cluster_k = x[y == unique_labels[k]]
            cluster_k_prime = x[y == unique_labels[k_prime]]
            G_k = centroids[k]
            G_k_prime = centroids[k_prime]
            H_kk_prime = (G_k + G_k_prime) / 2
            density_at_Gk = np.sum(np.linalg.norm(cluster_k - G_k, axis=1) < sigma) + np.sum(np.linalg.norm(cluster_k_prime - G_k, axis=1) < sigma)
            density_at_Gk_prime = np.sum(np.linalg.norm(cluster_k - G_k_prime, axis=1) < sigma) + np.sum(np.linalg.norm(cluster_k_prime - G_k_prime, axis=1) < sigma)
            density_at_Hkk_prime = np.sum(np.linalg.norm(cluster_k - H_kk_prime, axis=1) < sigma) + np.sum(np.linalg.norm(cluster_k_prime - H_kk_prime, axis=1) < sigma)
            if max(density_at_Gk, density_at_Gk_prime) == 0:
                pass
            else:
                Rkk_prime = density_at_Hkk_prime / max(density_at_Gk, density_at_Gk_prime)
                s_dbw += Rkk_prime
    s_dbw /= (K * (K - 1)) / 2
    return s_dbw


def ray_turi_index(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute the Ray-Turi index for evaluating the clustering quality.

    A lower value indicates a better clustering result.

    :param np.ndarray x: The dataset as a 2D NumPy array of shape (n_samples, n_features).
    :param np.ndarray y: Cluster labels for each data point as a 1D NumPy array of shape (n_samples,).
    :returns: The Ray-Turi  index score.
    :rtype: float

    :example:
    >>> from sklearn.datasets import make_blobs
    >>> X, labels = make_blobs(n_samples=5000, centers=5, random_state=42, n_features=3, cluster_std=2)
    >>> score = s_dbw_index(X, labels)

    :references:
       .. [1] Ray, S., & Turi, R. H. (1999). Determination of number of clusters in k-means clustering and application in colour image segmentation. Proceedings of the 4th International Conference on Advances in Pattern Recognition and Digital Techniques, 137–143.
    """

    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    n_clusters = get_unique_values_in_iterable(data=y, name=banfeld_raftery_index.__name__, min=2)
    unique_labels = np.unique(y)

    centroids = np.array([x[y == label].mean(axis=0) for label in unique_labels])
    intra_dists = np.full(shape=(x.shape[0]), fill_value=np.nan, dtype=np.float32)
    min_cluster_distance = np.inf
    obs_cnt = 0
    for cnt, cluster_id in enumerate(unique_labels):
        cluster_obs = x[np.argwhere(y == cluster_id).flatten()]
        centroids[cnt] = np.mean(cluster_obs, axis=0)
        dists = np.linalg.norm(cluster_obs - centroids[cnt], axis=1) ** 2
        intra_dists[obs_cnt: obs_cnt+dists.shape[0]] = dists
        obs_cnt += dists.shape[0]

    for i in range(n_clusters):
        for j in range(i + 1, n_clusters):
            distance = np.sum((centroids[i] - centroids[j]) ** 2)
            min_cluster_distance = min(min_cluster_distance, distance)


    return np.mean(intra_dists) / min_cluster_distance
#

def baker_huber_gamma_index(x: np.ndarray, y: np.ndarray) -> float:
    distances = cdist(x, x)
    np.fill_diagonal(distances, np.nan)
    unique_labels = np.unique(y)
    cluster_matrix = np.full(shape=(x.shape[0], x.shape[0]), fill_value=0, dtype=np.float32)
    np.fill_diagonal(cluster_matrix, 1)

    same_idx = []
    for cluster_id in unique_labels:
        cluster_idx = np.argwhere(y == cluster_id).flatten()
        same_idx.extend(list(itertools.combinations(cluster_idx, 2)))
    for idx in same_idx:
        cluster_matrix[idx[0]][idx[1]] = 1
    #m_idx = list(itertools.product(range(x.shape[0]), range(x.shape[0])))
    #m_idx = [(x[0], x[1]) for x in m_idx if x[0] != x[1]]
    for i in range(cluster_matrix.shape[0]):
        for j in range(i + 1, cluster_matrix.shape[1]):
            for h in range(cluster_matrix.shape[0]):
                for k in range(h + 1, cluster_matrix.shape[1]):
                    print(i, j, h, k)




    #m_idx = list(itertools.combinations(m_idx, 2))
    # concordant, discordant = 0, 0
    # for (idx_pair_1, idx_pair_2) in m_idx:
    #     dist_p1, dist_p2 = distances[idx_pair_1], distances[idx_pair_2]
    #     p1_y = [0 if y[idx_pair_1[0]] == y[idx_pair_1[1]] else 1]
    #     p2_y = [0 if y[idx_pair_2[0]] == y[idx_pair_2[1]] else 1]
    #     if (dist_p1 < dist_p2) and (p1_y < p2_y):
    #         concordant += 1
    #     elif (dist_p1 > dist_p2) and (p1_y > p2_y):
    #         concordant += 1
    #     elif (dist_p1 > dist_p2) and (p1_y < p2_y):
    #         discordant += 1
    #     elif (dist_p1 < dist_p2) and (p1_y > p2_y):
    #         discordant += 1
    #
    # gamma = (concordant - discordant) / (concordant + discordant)
    # print(gamma)

from sklearn.datasets import make_blobs
X, labels = make_blobs(n_samples=1000, centers=5, random_state=42, n_features=10, cluster_std=100)
score = baker_huber_gamma_index(X, labels)
print(f"{score}")