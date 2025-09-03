from cuml.metrics.cluster.adjusted_rand_index import adjusted_rand_score
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats
import numpy as np
import time
from sklearn.metrics import (adjusted_mutual_info_score, adjusted_rand_score,
                             fowlkes_mallows_score)


def adjusted_rand_gpu(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate the Adjusted Rand Index (ARI) between two clusterings.

    The Adjusted Rand Index (ARI) is a measure of the similarity between two clusterings. It considers all pairs of samples and counts pairs that are assigned to the same or different clusters in both the true and predicted clusterings.

    The ARI is defined as:

    .. math::
       ARI = \\frac{TP + TN}{TP + FP + FN + TN}

    where:
        - :math:`TP` (True Positive) is the number of pairs of elements that are in the same cluster in both x and y,
        - :math:`FP` (False Positive) is the number of pairs of elements that are in the same cluster in y but not in x,
        - :math:`FN` (False Negative) is the number of pairs of elements that are in the same cluster in x but not in y,
        - :math:`TN` (True Negative) is the number of pairs of elements that are in different clusters in both x and y.

    The ARI value ranges from -1 to 1. A value of 1 indicates perfect clustering agreement, 0 indicates random clustering, and negative values indicate disagreement between the clusterings.

    .. note::
       Modified from `scikit-learn <https://github.com/scikit-learn/scikit-learn/blob/8721245511de2f225ff5f9aa5f5fadce663cd4a3/sklearn/metrics/cluster/_supervised.py#L353>`_

    .. seealso::
       For CPU call, see :func:`simba.mixins.statistics_mixin.Statistics.adjusted_rand`.


    :param np.ndarray x: 1D array representing the labels of the first model.
    :param np.ndarray y: 1D array representing the labels of the second model.
    :return: A value of 1 indicates perfect clustering agreement, a value of 0 indicates random clustering, and negative values indicate disagreement between the clusterings.
    :rtype: float

    :example:
    >>> x = np.array([0, 0, 0, 0, 0])
    >>> y = np.array([1, 1, 1, 1, 1])
    >>> Statistics.adjusted_rand(x=x, y=y)
    >>> 1.0
    """

    check_valid_array(data=x, source=f'{adjusted_rand_gpu.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.INTEGER_DTYPES.value, min_axis_0=1)
    check_valid_array(data=y, source=f'{adjusted_rand_gpu.__name__} y', accepted_ndims=(1,), accepted_dtypes=Formats.INTEGER_DTYPES.value, accepted_shapes=[(x.shape[0],)])
    return adjusted_rand_score(x, y)

x = np.random.randint(low=0, high=55, size=100000000)
y = np.random.randint(low=0, high=55, size=100000000)

start = time.time()
adjusted_rand_gpu(x=x, y=y)
print(time.time() - start)

start = time.time()
adjusted_rand_score(labels_true=x, labels_pred=y)
print(time.time() - start)