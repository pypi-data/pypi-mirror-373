import numpy as np
import pandas as pd
from typing import Optional, Tuple, Union, List
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from numba import njit, prange, jit, float32, types, float64
from scipy import stats
from scipy.stats.distributions import chi2
from simba.utils.checks import check_valid_array, check_str, check_int, check_float, check_valid_lst
from simba.utils.enums import Formats
from simba.utils.data import fast_mean_rank
from statsmodels.stats.libqsturng import psturng
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from simba.utils.errors import CountError, InvalidInputError
import pickle

@njit("(float32[:], float64, float64)", cache=True)
def rolling_independent_sample_t(data: np.ndarray, time_window: float, fps: float) -> np.ndarray:

    r"""
    Jitted compute independent-sample t-statistics for sequentially binned values in a time-series.
    E.g., compute t-test statistics when comparing ``Feature N`` in the current 1s
    time-window, versus ``Feature N`` in the previous 1s time-window.

    .. image:: _static/img/independent_t_tests.png
       :width: 700
       :align: center

    .. attention::
       Each window is compared to the prior window. Output for the windows without a prior window (the first window) is ``-1``.

    .. seealso::
       For single non-timeseries independent t, see :func:`simba.mixins.statistics_mixin.Statistics.independent_samples_t`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param int group_size_s: The size of the buckets in seconds.
    :param fps: Frame-rate of recorded video.
    :rtype: int

    :example:
    >>> data_1, data_2 = np.random.normal(loc=10, scale=2, size=10), np.random.normal(loc=20, scale=2, size=10)
    >>> data = np.hstack([data_1, data_2])
    >>> rolling_independent_sample_t(data, time_window=1, fps=10)
    >>> [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389, -6.88741389])
    """
    results = np.full((data.shape[0]), -1.0)
    window_size = int(time_window * fps)
    data = np.split(data, list(range(window_size, data.shape[0], window_size)))
    for cnt, i in enumerate(prange(1, len(data))):
        start, end = int((cnt + 1) * window_size), int(((cnt + 1) * window_size) + window_size)
        mean_1, mean_2 = np.mean(data[i - 1]), np.mean(data[i])
        stdev_1, stdev_2 = np.std(data[i - 1]), np.std(data[i])
        pooled_std = np.sqrt(((len(data[i - 1]) - 1) * stdev_1**2 + (len(data[i]) - 1) * stdev_2**2) / (len(data[i - 1]) + len(data[i]) - 2))
        results[start:end] = (mean_1 - mean_2) / (pooled_std * np.sqrt(1 / len(data[i - 1]) + 1 / len(data[i])))

    return results


@njit([(float32[:], float32[:], float64[:, :]), (float32[:], float32[:], types.misc.Omitted(None))])
def independent_samples_t(sample_1: np.ndarray,sample_2: np.ndarray,critical_values: Optional[np.ndarray] = None) -> Tuple[float, Union[None, bool]]:

    r"""
    Jitted compute independent-samples t-test statistic and boolean significance between two distributions.

    .. note::
       Critical values are stored in simba.assets.lookups.critical_values_**.pickle

    The t-statistic for independent samples t-test is calculated using the following formula:
    .. math::
       t = \frac{\bar{x}_1 - \bar{x}_2}{s_p \sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}

    where:
    - :math:`\bar{x}_1` and :math:`\bar{x}_2` are the means of the two samples,
    - :math:`s_p` is the pooled standard deviation,
    - :math:`n_1` and :math:`n_2` are the sizes of the two samples.

    .. seealso::
       :func:`simba.mixins.statistics_mixin.Statistics.rolling_independent_sample_t`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param ndarray critical_values: 2d array where the first column represents degrees of freedom and second column represents critical values.
    :returns t_statistic, p_value: Size-2 tuple representing t-statistic and associated probability value. p_value is ``None`` if critical_values is None. Else True or False with True representing significant.
    :rtype: Tuple[float, Union[None, bool]]

    :example:
    >>> sample_1 = np.array([1, 2, 3, 1, 3, 2, 1, 10, 8, 4, 10])
    >>> sample_2 = np.array([2, 5, 10, 4, 8, 10, 7, 10, 7, 10, 10])
    >>> independent_samples_t(sample_1=sample_1, sample_2=sample_2)
    >>> (-2.5266046804590183, None)
    >>> critical_values = pickle.load(open("simba/assets/lookups/critical_values_05.pickle","rb"))['independent_t_test']['one_tail'].values
    >>> independent_samples_t(sample_1=sample_1, sample_2=sample_2, critical_values=critical_values)
    >>> (-2.5266046804590183, True)
    """

    significance_bool = None
    m1, m2 = np.mean(sample_1), np.mean(sample_2)
    std_1 = np.sqrt(np.sum((sample_1 - m1) ** 2) / (len(sample_1) - 1))
    std_2 = np.sqrt(np.sum((sample_2 - m2) ** 2) / (len(sample_2) - 1))
    pooled_std = np.sqrt(((len(sample_1) - 1) * std_1**2 + (len(sample_2) - 1) * std_2**2) / (len(sample_1) + len(sample_2) - 2))
    t_statistic = (m1 - m2) / (pooled_std * np.sqrt(1 / len(sample_1) + 1 / len(sample_2)))
    if critical_values is not None:
        dof = (sample_1.shape[0] + sample_2.shape[0]) - 2
        critical_value = np.interp(dof, critical_values[:, 0], critical_values[:, 1])
        if critical_value < abs(t_statistic):
            significance_bool = True
        else:
            significance_bool = False

    return t_statistic, significance_bool


@njit("(float64[:], float64[:])", cache=True)
def cohens_d(sample_1: np.ndarray, sample_2: np.ndarray) -> float:

    r"""
    Jitted compute of Cohen's d between two distributions.
    Cohen's d is a measure of effect size that quantifies the difference between the means of two distributions in terms of their standard deviation. It is calculated as the difference between the means of the two distributions divided by the pooled standard deviation.
    Higher values indicate a larger effect size, with 0.2 considered a small effect, 0.5 a medium effect, and 0.8 or above a large effect. Negative values indicate that the mean of sample 2 is larger than the mean of sample 1.

    .. seealso::
       For time-series based method, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_cohens_d`

    .. math::
       d = \\frac{{\bar{x}_1 - \bar{x}_2}}{{\\sqrt{{\\frac{{s_1^2 + s_2^2}}{2}}}}}

    where:
       - :math:`\bar{x}_1` and :math:`\bar{x}_2` are the means of sample_1 and sample_2 respectively,
       - :math:`s_1` and :math:`s_2` are the standard deviations of sample_1 and sample_2 respectively.

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns: Cohens D statistic.
    :rtype: float

    :example:
    >>> sample_1 = [2, 4, 7, 3, 7, 35, 8, 9]
    >>> sample_2 = [4, 8, 14, 6, 14, 70, 16, 18]
    >>> cohens_d(sample_1=sample_1, sample_2=sample_2)
    >>> -0.5952099775170546
    """

    return (np.mean(sample_1) - np.mean(sample_2)) / (np.sqrt((np.std(sample_1) ** 2 + np.std(sample_2) ** 2) / 2))


@njit("(float64[:], float64[:], float64)", cache=True)
def rolling_cohens_d(data: np.ndarray, time_windows: np.ndarray, fps: float) -> np.ndarray:
    """
    Jitted compute of rolling Cohen's D statistic comparing the current time-window of
    size N to the preceding window of size N.

    .. seealso::
       For single non-timeseries comparison, see :func:`simba.mixins.statistics_mixin.Statistics.cohens_d`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param np.ndarray[ints] time_window: Time windows to compute ANOVAs for in seconds.
    :param int fps: Frame-rate of recorded video.
    :returns: Array of size data.shape[0] x window_sizes.shape[1] with Cohens D.
    :rtype: np.ndarray

    :example:
    >>> sample_1, sample_2 = np.random.normal(loc=10, scale=1, size=4), np.random.normal(loc=11, scale=2, size=4)
    >>> sample = np.hstack((sample_1, sample_2))
    >>> rolling_cohens_d(data=sample, window_sizes=np.array([1]), fps=4)
    >>> [[0.],[0.],[0.],[0.],[0.14718302],[0.14718302],[0.14718302],[0.14718302]])
    """

    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            d = (np.mean(sample_1) - np.mean(sample_2)) / (np.sqrt((np.std(sample_1) ** 2 + np.std(sample_2) ** 2) / 2))
            results[window_start:window_end, i] = d

    return results


@njit("(float32[:], float64, float64)")
def rolling_two_sample_ks(data: np.ndarray, time_window: float, fps: float) -> np.ndarray:
    """
    Jitted compute Kolmogorov two-sample statistics for sequentially binned values in a time-series.
    E.g., compute KS statistics when comparing ``Feature N`` in the current 1s time-window, versus ``Feature N`` in the previous 1s time-window.

    .. seealso::
       For single non-timeseries based comparison, see :func:`simba.mixins.statistics_mixin.Statistics.two_sample_ks`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param float time_window: The size of the buckets in seconds.
    :param int fps: Frame-rate of recorded video.
    :return: Array of size data.shape[0] with KS statistics
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(low=0, high=100, size=(200)).astype('float32')
    >>> results = rolling_two_sample_ks(data=data, time_window=1, fps=30)
    """

    window_size, results = int(time_window * fps), np.full((data.shape[0]), -1.0)
    data = np.split(data, list(range(window_size, data.shape[0], window_size)))
    for cnt, i in enumerate(prange(1, len(data))):
        start, end = int((cnt + 1) * window_size), int(((cnt + 1) * window_size) + window_size)
        sample_1, sample_2 = data[i - 1], data[i]
        combined_samples = np.sort(np.concatenate((sample_1, sample_2)))
        ecdf_sample_1 = np.searchsorted(sample_1, combined_samples, side="right") / len(sample_1)
        ecdf_sample_2 = np.searchsorted(sample_2, combined_samples, side="right") / len(sample_2)
        ks = np.max(np.abs(ecdf_sample_1 - ecdf_sample_2))
        results[start:end] = ks
    return results

@njit([(float32[:], float32[:], float64[:, :]), (float32[:], float32[:], types.misc.Omitted(None))])
def two_sample_ks( sample_1: np.ndarray, sample_2: np.ndarray, critical_values: Optional[float64[:, :]] = None) -> Tuple[float, Union[bool, None]]:
    """
    Jitted compute the two-sample Kolmogorov-Smirnov (KS) test statistic and, optionally, test for statistical significance.
    The two-sample KS test is a non-parametric test that compares the cumulative distribution functions (ECDFs) of two independent samples to assess whether they come from the same distribution.
    KS statistic (D) is calculated as the maximum absolute difference between the empirical cumulative distribution functions (ECDFs) of the two samples.

    .. math::
       D = \\max(| ECDF_1(x) - ECDF_2(x) |)

    If `critical_values` are provided, the function checks the significance of the KS statistic against the critical values.

    .. seealso::
       For rolling timeseries based comparison, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_two_sample_ks`

    :param np.ndarray data: The first sample array for the KS test.
    :param np.ndarray data: The second sample array for the KS test.
    :param Optional[float64[:, :]] critical_values: An array of critical values for the KS test. If provided, the function will also check the significance of the KS statistic against the critical values. Default: None.
    :returns: Returns a tuple containing the KS statistic and a boolean indicating whether the test is statistically significant.
    :rtype: Tuple[float Union[bool, None]]

    :example:
    >>> sample_1 = np.array([1, 2, 3, 1, 3, 2, 1, 10, 8, 4, 10]).astype(np.float32)
    >>> sample_2 = np.array([10, 5, 10, 4, 8, 10, 7, 10, 7, 10, 10]).astype(np.float32)
    >>> critical_values = pickle.load(open("simba/assets/lookups/critical_values_5.pickle", "rb"))['two_sample_KS']['one_tail'].values
    >>> two_sample_ks(sample_1=sample_1, sample_2=sample_2, critical_values=critical_values)
    >>> (0.7272727272727273, True)
    """
    significance_bool = None
    combined_samples = np.sort(np.concatenate((sample_1, sample_2)))
    ecdf_sample_1 = np.searchsorted(sample_1, combined_samples, side="right") / len(sample_1 )
    ecdf_sample_2 = np.searchsorted(sample_2, combined_samples, side="right") / len(sample_2)
    ks = np.max(np.abs(ecdf_sample_1 - ecdf_sample_2))
    if critical_values is not None:
        combined_sample_size = len(sample_1) + len(sample_2)
        critical_value = np.interp(combined_sample_size, critical_values[:, 0], critical_values[:, 1])
        if critical_value < abs(ks):
            significance_bool = True
        else:
            significance_bool = False

    return (ks, significance_bool)

@jit(nopython=True)
def one_way_anova( sample_1: np.ndarray, sample_2: np.ndarray, critical_values: Optional[np.ndarray] = None) -> Tuple[float, float]:
    r"""
    Compute the one-way ANOVA F-statistic and associated p-value for two distributions.
    This method calculates the F-statistic to determine if there is a significant difference
    between the means of the two samples, based on their variances. The F-statistic is computed as:

    .. math::
      F = \\frac{MS_{\\text{between}}}{MS_{\\text{within}}}

    where:
    - :math:`SS_{\\text{between}}` is the sum of squares between the groups.
    - :math:`SS_{\\text{within}}` is the sum of squares within each group.
    - :math:`MS_{\\text{between}} = \\frac{SS_{\\text{between}}}{df_{\\text{between}}}`
    - :math:`MS_{\\text{within}} = \\frac{SS_{\\text{within}}}{df_{\\text{within}}}`

    .. seealso::
       For rolling comparisons in a timeseries, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_one_way_anova`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns: Tuple representing ANOVA F statistic and associated probability value.
    :rtype: Tuple[float, float]

    :example:
    >>> saxfmple_1 = np.array([1, 2, 3, 1, 3, 2, 1, 10, 8, 4, 10])
    >>> sample_2 = np.array([8, 5, 5, 8, 8, 9, 10, 1, 7, 10, 10])
    >>> one_way_anova(sample_1=sample_2, sample_2=sample_1)
    """

    significance_bool = None
    n1, n2 = len(sample_1), len(sample_2)
    m1, m2 = np.mean(sample_1), np.mean(sample_2)
    ss_between = (n1 * (m1 - np.mean(np.concatenate((sample_1, sample_2)))) ** 2 + n2 * (m2 - np.mean(np.concatenate((sample_1, sample_2)))) ** 2)
    ss_within = np.sum((sample_1 - m1) ** 2) + np.sum((sample_2 - m2) ** 2)
    df_between, df_within = 1, n1 + n2 - 2
    ms_between, ms_within = ss_between / df_between, ss_within / df_within
    f = ms_between / ms_within
    if critical_values is not None:
        critical_values = critical_values[:, np.array([0, df_between])]
        critical_value = np.interp(df_within, critical_values[:, 0], critical_values[:, 1])
        if f > critical_value:
            significance_bool = True
        else:
            significance_bool = False
    return (f, significance_bool)


@njit("(float32[:], float64[:], float64)", cache=True)
def rolling_one_way_anova(data: np.ndarray, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Jitted compute of rolling one-way ANOVA F-statistic comparing the current time-window of
    size N to the preceding window of size N.

    .. image:: _static/img/rolling_anova.png
       :width: 600
       :align: center

    .. seealso::
       For single comparison, see :func:`simba.mixins.statistics_mixin.Statistics.one_way_anova`

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param np.ndarray[ints] time_windows: Time windows to compute ANOVAs for in seconds.
    :param int fps: Frame-rate of recorded video.
    :returns: 2D numpy array with F values comparing the current time-window to the immedidatly preceeding time-window.
    :rtype: np.ndarray

    :example:
    >>> sample = np.random.normal(loc=10, scale=1, size=10).astype(np.float32)
    >>> rolling_one_way_anova(data=sample, time_windows=np.array([1.0]), fps=2)
    >>> [[0.00000000e+00][0.00000000e+00][2.26221263e-06][2.26221263e-06][5.39119950e-03][5.39119950e-03][1.46725486e-03][1.46725486e-03][1.16392111e-02][1.16392111e-02]]
    """
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            n1, n2 = len(sample_1), len(sample_2)
            m1, m2 = np.mean(sample_1), np.mean(sample_2)
            ss_between = (n1 * (m1 - np.mean(np.concatenate((sample_1, sample_2)))) ** 2 + n2 * (m2 - np.mean(np.concatenate((sample_1, sample_2)))) ** 2)
            ss_within = np.sum((sample_1 - m1) ** 2) + np.sum((sample_2 - m2) ** 2)
            df_between, df_within = 1, n1 + n2 - 2
            ms_between, ms_within = ss_between / df_between, ss_within / df_within
            f = ms_between / ms_within
            results[window_start:window_end, i] = f
    return results


@njit("(float64[:], float64[:])", cache=True)
def kruskal_wallis(sample_1: np.ndarray, sample_2: np.ndarray) -> float:
    """
    Compute the Kruskal-Wallis H statistic between two distributions.
    The Kruskal-Wallis test is a non-parametric method for testing whether samples originate from the same distribution.
    It ranks all the values from the combined samples, then calculates the H statistic based on the ranks.

    .. math::
       H = \\frac{{12}}{{n(n + 1)}} \\left(\\frac{{(\\sum R_{\text{sample1}})^2}}{{n_1}} + \\frac{{(\\sum R_{\text{sample2}})^2}}{{n_2}}\\right) - 3(n + 1)

    where:
    - :math:`n` is the total number of observations,
    - :math:`n_1` and :math:`n_2` are the number of observations in sample 1 and sample 2 respectively,
    - :math:`R_{\text{sample1}}` and :math:`R_{\text{sample2}}` are the sums of ranks for sample 1 and sample 2 respectively.

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns: Kruskal-Wallis H statistic.
    :rtype: float

    :example:
    >>> sample_1 = np.array([1, 1, 3, 4, 5]).astype(np.float64)
    >>> sample_2 = np.array([6, 7, 8, 9, 10]).astype(np.float64)
    >>> kruskal_wallis(sample_1=sample_1, sample_2=sample_2)
    >>> 39.4
    """
    # sample_1 = np.concatenate((np.zeros((sample_1.shape[0], 1)), sample_1.reshape(-1, 1)), axis=1)
    # sample_2 = np.concatenate((np.ones((sample_2.shape[0], 1)), sample_2.reshape(-1, 1)), axis=1)
    data = np.vstack((sample_1, sample_2))
    ranks = fast_mean_rank(data=data[:, 1], descending=False)
    data = np.hstack((data, ranks.reshape(-1, 1)))
    sample_1_summed_rank = np.sum(data[0 : sample_1.shape[0], 2].flatten())
    sample_2_summed_rank = np.sum(data[sample_1.shape[0] :, 2].flatten())
    h1 = 12 / (data.shape[0] * (data.shape[0] + 1))
    h2 = (np.square(sample_1_summed_rank) / sample_1.shape[0]) + (np.square(sample_2_summed_rank) / sample_2.shape[0])
    h3 = 3 * (data.shape[0] + 1)
    return h1 * h2 - h3

def pct_in_top_n(x: np.ndarray, n: float) -> float:
    """
    Compute the percentage of elements in the top 'n' frequencies in the input array.
    This function calculates the percentage of elements that belong to the 'n' most
    frequent categories in the input array 'x'.

    :param np.ndarray x: Input array.
    :param float n: Number of top frequencies.
    :return: Percentage of elements in the top 'n' frequencies.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 10, (100,))
    >>> pct_in_top_n(x=x, n=5)
    """
    check_valid_array(data=x, accepted_ndims=(1,), source=pct_in_top_n.__name__)
    check_int(name=pct_in_top_n.__name__, value=n, max_value=x.shape[0])
    cnts = np.sort(np.unique(x, return_counts=True)[1])[-n:]
    return np.sum(cnts) / x.shape[0]


@njit("(float64[:], float64[:])", cache=True)
def mann_whitney(sample_1: np.ndarray, sample_2: np.ndarray) -> float:

    """
    Jitted compute of Mann-Whitney U between two distributions.
    The Mann-Whitney U test is used to assess whether the distributions of two groups
    are the same or different based on their ranks. It is commonly used as an alternative
    to the t-test when the assumptions of normality and equal variances are violated.

    .. math::
       U = \\min(U_1, U_2)

    Where:
          - :math:`U` is the Mann-Whitney U statistic,
          - :math:`U_1` is the sum of ranks for sample 1,
          - :math:`U_2` is the sum of ranks for sample 2.

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns : The Mann-Whitney U statistic.
    :rtype: float

    :references:
    `Modified from James Webber gist on GitHub <https://gist.github.com/jamestwebber/38ab26d281f97feb8196b3d93edeeb7b>`__.

    :example:
    >>> sample_1 = np.array([1, 1, 3, 4, 5])
    >>> sample_2 = np.array([6, 7, 8, 9, 10])
    >>> results = mann_whitney(sample_1=sample_1, sample_2=sample_2)
    """

    n1, n2 = sample_1.shape[0], sample_2.shape[0]
    ranked = fast_mean_rank(np.concatenate((sample_1, sample_2)))
    u1 = n1 * n2 + (n1 * (n1 + 1)) / 2.0 - np.sum(ranked[:n1], axis=0)
    u2 = n1 * n2 - u1
    return min(u1, u2)

@jit(nopython=True, cache=True)
def levenes(sample_1: np.ndarray, sample_2: np.ndarray, critical_values: Optional[np.ndarray] = None) -> Tuple[float, Union[bool, None]]:
    """
    Compute Levene's W statistic, a test for the equality of variances between two samples.
    Levene's test is a statistical test used to determine whether two or more groups have equal variances. It is often
    used as an alternative to the Bartlett test when the assumption of normality is violated. The function computes the
    Levene's W statistic, which measures the degree of difference in variances between the two samples.

    .. seealso::
       For time-series based rolling comparisons, see :func:`simba.mixins.statistics_mixin.Statistics.rolling_levenes`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param ndarray critical_values: 2D array with where first column represent dfn first row dfd with values represent critical values. Can be found in ``simba.assets.critical_values_05.pickle``
    :returns: Levene's W statistic and a boolean indicating whether the test is statistically significant (if critical values is not None).
    :rtype: Tuple[float, Union[bool, None]]

    :examples:
    >>> sample_1 = np.array(list(range(0, 50)))
    >>> sample_2 = np.array(list(range(25, 100)))
    >>> levenes(sample_1=sample_1, sample_2=sample_2)
    >>> 12.63909108903254
    >>> critical_values = pickle.load(open("simba/assets/lookups/critical_values_5.pickle","rb"))['f']['one_tail'].values
    >>> levenes(sample_1=sample_1, sample_2=sample_2, critical_values=critical_values)
    >>> (12.63909108903254, True)
    """

    significance_bool = None
    Ni_x, Ni_y = len(sample_1), len(sample_2)
    Yci_x, Yci_y = np.median(sample_1), np.median(sample_2)
    Ntot = Ni_x + Ni_y
    Zij_x, Zij_y = np.abs(sample_1 - Yci_x).astype(np.float32), np.abs(sample_2 - Yci_y).astype(np.float32)
    Zbari_x, Zbari_y = np.mean(Zij_x), np.mean(Zij_y)
    Zbar = ((Zbari_x * Ni_x) + (Zbari_y * Ni_y)) / Ntot
    numer = (Ntot - 2) * np.sum(np.array([Ni_x, Ni_y]) * (np.array([Zbari_x, Zbari_y]) - Zbar) ** 2)
    dvar = np.sum((Zij_x - Zbari_x) ** 2) + np.sum((Zij_y - Zbari_y) ** 2)
    denom = (2 - 1.0) * dvar
    l_statistic = numer / denom
    if critical_values is not None:
        dfn, dfd = 1, (Ni_x + Ni_y) - 2
        idx = (np.abs(critical_values[0][1:] - dfd)).argmin() + 1
        critical_values = critical_values[1:, np.array([0, idx])]
        critical_value = np.interp(dfd, critical_values[:, 0], critical_values[:, 1])
        if l_statistic >= critical_value:
            significance_bool = True
        else:
            significance_bool = False
    return (l_statistic, significance_bool)

@njit("(float64[:], float64[:], float64)", cache=True)
def rolling_levenes(data: np.ndarray, time_windows: np.ndarray, fps: float) -> np.ndarray:
    """
    Jitted compute of rolling Levene's W comparing the current time-window of size N to the preceding window of size N.

    .. note::
       First time bin (where has no preceding time bin) will have fill value ``0``

    .. seealso::
       For simple two-sample comparison, see :func:`simba.mixins.statistics_mixin.Statistics.levenes`

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns: Levene's W data of size len(data) x len(time_windows).
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 50, (100)).astype(np.float64)
    >>> rolling_levenes(data=data, time_windows=np.array([1]).astype(np.float64), fps=5.0)
    """
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            Ni_x, Ni_y = len(sample_1), len(sample_2)
            Yci_x, Yci_y = np.median(sample_1), np.median(sample_2)
            Ntot = Ni_x + Ni_y
            Zij_x, Zij_y = np.abs(sample_1 - Yci_x).astype(np.float32), np.abs(sample_2 - Yci_y).astype(np.float32)
            Zbari_x, Zbari_y = np.mean(Zij_x), np.mean(Zij_y)
            Zbar = ((Zbari_x * Ni_x) + (Zbari_y * Ni_y)) / Ntot
            numer = (Ntot - 2) * np.sum(np.array([Ni_x, Ni_y]) * (np.array([Zbari_x, Zbari_y]) - Zbar) ** 2)
            dvar = np.sum((Zij_x - Zbari_x) ** 2) + np.sum((Zij_y - Zbari_y) ** 2)
            denom = (2 - 1.0) * dvar
            w = numer / denom
            results[window_start:window_end, i] = w

    return results

@jit(nopython=True, cache=True)
def brunner_munzel(sample_1: np.ndarray, sample_2: np.ndarray) -> float:

    r"""
    Jitted compute of Brunner-Munzel W between two distributions.
    The Brunner-Munzel W statistic compares the central tendency and the spread of two independent samples. It is useful
    for comparing the distribution of a continuous variable between two groups, especially when the assumptions of
    parametric tests like the t-test are violated.

    .. note::
       Modified from `scipy.stats.brunnermunzel <https://github.com/scipy/scipy/blob/7dcd8c59933524986923cde8e9126f5fc2e6b30b/scipy/stats/_stats_py.py#L9387>`_

    .. math::
       W = -\frac{{n_x \\cdot n_y \\cdot (\bar{R}_y - \bar{R}_x)}}{{(n_x + n_y) \\cdot \\sqrt{{n_x \\cdot S_x + n_y \\cdot S_y}}}}

    where:
       - :math:`n_x` and :math:`n_y` are the sizes of sample_1 and sample_2 respectively,
       - :math:`\bar{R}_x` and :math:`\bar{R}_y` are the mean ranks of sample_1 and sample_2, respectively.
       - :math:`S_x` and :math:`S_y` are the dispersion statistics of sample_1 and sample_2 respectively.

    :parameter ndarray sample_1: First 1d array representing feature values.
    :parameter ndarray sample_2: Second 1d array representing feature values.
    :returns: Brunner-Munzel W.
    :rtype: float

    :example:
    >>> sample_1, sample_2 = np.random.normal(loc=10, scale=2, size=10), np.random.normal(loc=20, scale=2, size=10)
    >>> brunner_munzel(sample_1=sample_1, sample_2=sample_2)
    >>> 0.5751408161437165
    """
    nx, ny = len(sample_1), len(sample_2)
    rankc = fast_mean_rank(np.concatenate((sample_1, sample_2)))
    rankcx, rankcy = rankc[0:nx], rankc[nx : nx + ny]
    rankcx_mean, rankcy_mean = np.mean(rankcx), np.mean(rankcy)
    rankx, ranky = fast_mean_rank(sample_1), fast_mean_rank(sample_2)
    rankx_mean, ranky_mean = np.mean(rankx), np.mean(ranky)
    Sx = np.sum(np.power(rankcx - rankx - rankcx_mean + rankx_mean, 2.0)) / nx - 1
    Sy = np.sum(np.power(rankcy - ranky - rankcy_mean + ranky_mean, 2.0)) / ny - 1
    wbfn = nx * ny * (rankcy_mean - rankcx_mean)
    wbfn /= (nx + ny) * np.sqrt(nx * Sx + ny * Sy)
    return -wbfn

@njit("(float32[:], float64[:], float64)", cache=True)
def rolling_barletts_test(data: np.ndarray, time_windows: np.ndarray, fps: float) -> np.ndarray:
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            n_1 = len(sample_1)
            n_2 = len(sample_2)
            N = n_1 + n_2
            mean_variance_1 = np.sum((sample_1 - np.mean(sample_1)) ** 2) / (n_1 - 1)
            mean_variance_2 = np.sum((sample_2 - np.mean(sample_2)) ** 2) / (n_2 - 1)
            numerator = (N - 2) * (np.log(mean_variance_1) + np.log(mean_variance_2))
            denominator = 1 / (n_1 - 1) + 1 / (n_2 - 1)
            u = numerator / denominator
            results[window_start:window_end, i] = u
    return results

@njit("(float32[:], float32[:])")
def pearsons_r(sample_1: np.ndarray, sample_2: np.ndarray) -> float:
    r"""
    Calculate the Pearson correlation coefficient (Pearson's r) between two numeric samples.
    Pearson's r is a measure of the linear correlation between two sets of data points. It quantifies the strength and
    direction of the linear relationship between the two variables. The coefficient varies between -1 and 1, with
    -1 indicating a perfect negative linear relationship, 1 indicating a perfect positive linear relationship, and 0
    indicating no linear relationship.

    Pearson's r is calculated using the formula:

    .. math::
       r = \frac{\sum{(x_i - \bar{x})(y_i - \bar{y})}}{\sqrt{\sum{(x_i - \bar{x})^2}\sum{(y_i - \bar{y})^2}}}

    where:
       - :math:`x_i` and :math:`y_i` are individual data points in sample_1 and sample_2, respectively.
       - :math:`\bar{x}` and :math:`\bar{y}` are the means of sample_1 and sample_2, respectively.

    .. seealso::
       For timeseries-based sliding comparison, see :func:`simba.mixins.statistics_mixin.Statistics.sliding_pearsons_r`

    :param np.ndarray sample_1: First numeric sample.
    :param np.ndarray sample_2: Second numeric sample.
    :return: Pearson's correlation coefficient between the two samples.
    :rtype: float

    :example:
    >>> sample_1 = np.array([7, 2, 9, 4, 5, 6, 7, 8, 9]).astype(np.float32)
    >>> sample_2 = np.array([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]).astype(np.float32)
    >>> pearsons_r(sample_1=sample_1, sample_2=sample_2)
    >>> 0.47
    """
    m1, m2 = np.mean(sample_1), np.mean(sample_2)
    numerator = np.sum((sample_1 - m1) * (sample_2 - m2))
    denominator = np.sqrt(np.sum((sample_1 - m1) ** 2) * np.sum((sample_2 - m2) ** 2))
    r = numerator / denominator
    return r


@njit("(float32[:], float32[:])")
def spearman_rank_correlation(sample_1: np.ndarray, sample_2: np.ndarray) -> float:
    """
    Jitted compute of Spearman's rank correlation coefficient between two samples.
    Spearman's rank correlation coefficient assesses how well the relationship between two variables can be described using a monotonic function.
    It computes the strength and direction of the monotonic relationship between ranked variables.

    .. seealso::
       For time-series based sliding comparisons, see :func:`simba.mixins.statistics.StatisticsMixin.sliding_spearman_rank_correlation`
       For time-series based sliding comparisons with GPU acceleration, see :func:`simba.data_processors.cuda.statistics.sliding_spearman_rank_correlation`

    :param np.ndarray sample_1: First 1D array containing feature values.
    :param np.ndarray sample_2: Second 1D array containing feature values.
    :return: Spearman's rank correlation coefficient.
    :rtype: float

    :example:
    >>> sample_1 = np.array([7, 2, 9, 4, 5, 6, 7, 8, 9]).astype(np.float32)
    >>> sample_2 = np.array([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]).astype(np.float32)
    >>> spearman_rank_correlation(sample_1=sample_1, sample_2=sample_2)
    >>> 0.0003979206085205078
    """
    rank_x, rank_y = np.argsort(np.argsort(sample_1)), np.argsort(np.argsort(sample_2))
    d_squared = np.sum((rank_x - rank_y) ** 2)
    return 1 - (6 * d_squared) / (len(sample_1) * (len(sample_2) ** 2 - 1))

@njit("(float32[:], float32[:], float64[:], int64)")
def sliding_pearsons_r(sample_1: np.ndarray, sample_2: np.ndarray, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Given two 1D arrays of size N, create sliding window of size time_windows[i] * fps and return Pearson's R
    between the values in the two 1D arrays in each window. Address "what is the correlation between Feature 1 and
    Feature 2 in the current X.X seconds of the video".

    .. image:: _static/img/sliding_pearsons.png
       :width: 600
       :align: center

    .. seealso::
       For simple two sample comparison, see :func:`simba.mixins.statistics_mixin.Statistics.pearsons_r`

    :param ndarray sample_1: First 1D array with feature values.
    :param ndarray sample_1: Second 1D array with feature values.
    :param float time_windows: The length of the sliding window in seconds.
    :param int fps: The fps of the recorded video.
    :returns: 2d array of Pearsons R of size len(sample_1) x len(time_windows). Note, if sliding window is 10 frames, the first 9 entries will be filled with 0.
    :rtype: np.ndarray

    :example:
    >>> sample_1 = np.random.randint(0, 50, (10)).astype(np.float32)
    >>> sample_2 = np.random.randint(0, 50, (10)).astype(np.float32)
    >>> sliding_pearsons_r(sample_1=sample_1, sample_2=sample_2, time_windows=np.array([0.5]), fps=10)
    >>> [[-1.][-1.][-1.][-1.][0.227][-0.319][-0.196][0.474][-0.061][0.713]]
    """

    results = np.full((sample_1.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for left, right in zip(
            prange(0, sample_1.shape[0] + 1),
            prange(window_size, sample_1.shape[0] + 1),
        ):
            s1, s2 = sample_1[left:right], sample_2[left:right]
            m1, m2 = np.mean(s1), np.mean(s2)
            numerator = np.sum((s1 - m1) * (s2 - m2))
            denominator = np.sqrt(np.sum((s1 - m1) ** 2) * np.sum((s2 - m2) ** 2))
            if denominator != 0:
                r = numerator / denominator
                results[right - 1, i] = r
            else:
                results[right - 1, i] = -1.0
    return results

@njit(
    [
        "(float32[:], float32[:], float64[:,:], types.unicode_type)",
        '(float32[:], float32[:], float64[:,:], types.misc.Omitted("goodness_of_fit"))',
        "(float32[:], float32[:], types.misc.Omitted(None), types.unicode_type)",
        '(float32[:], float32[:], types.misc.Omitted(None), types.misc.Omitted("goodness_of_fit"))',
    ]
)
def chi_square(
    sample_1: np.ndarray,
    sample_2: np.ndarray,
    critical_values: Optional[np.ndarray] = None,
    type: Optional[Literal["goodness_of_fit", "independence"]] = "goodness_of_fit") -> Tuple[float, Union[bool, None]]:

    """
    Jitted compute of chi square between two categorical distributions.

    .. note::
       Requires sample_1 and sample_2 has to be numeric. if working with strings, convert to
       numeric category values before using chi_square.

    .. warning:
       Non-overlapping values (i.e., categories exist in sample_1 that does not exist in sample2) or small values may cause inflated chi square values.
       If small contingency table small values, consider TODO Fisher's exact test

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :param ndarray critical_values: 2D array with where indexes represent degrees of freedom and values represent critical values. Can be found in ``simba.assets.critical_values_05.pickle``
    :returns: Size-2 tuple with the chi-square value and significance threshold boolean (if critical_values is not None).
    :rtype: Tuple[float, Union[bool, None]]

    :example:
    >>> sample_1 = np.array([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]).astype(np.float32)
    >>> sample_2 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).astype(np.float32)
    >>> critical_values = pickle.load(open("simba/assets/lookups/critical_values_5.pickle", "rb"))['chi_square']['one_tail'].values
    >>> chi_square(sample_1=sample_2, sample_2=sample_1, critical_values=critical_values, type='goodness_of_fit')
    >>> (8.333, False)
    >>>
    """
    chi_square, significance_bool = 0.0, None
    unique_categories = np.unique(np.concatenate((sample_1, sample_2)))
    sample_1_counts = np.zeros(len(unique_categories), dtype=np.int64)
    sample_2_counts = np.zeros(len(unique_categories), dtype=np.int64)
    for i in prange(len(unique_categories)):
        sample_1_counts[i], sample_2_counts[i] = np.sum(
            sample_1 == unique_categories[i]
        ), np.sum(sample_2 == unique_categories[i])
    for i in prange(len(unique_categories)):
        count_1, count_2 = sample_1_counts[i], sample_2_counts[i]
        if count_2 > 0:
            chi_square += ((count_1 - count_2) ** 2) / count_2
        else:
            chi_square += ((count_1 - count_2) ** 2) / (count_2 + 1)
    if critical_values is not None:
        if type == "goodness_of_fit":
            df = unique_categories.shape[0] - 1
        else:
            df = (len(sample_1_counts) - 1) * (len(sample_2_counts) - 1)
        critical_value = np.interp(df, critical_values[:, 0], critical_values[:, 1])
        if chi_square >= critical_value:
            significance_bool = True
        else:
            significance_bool = False
    return chi_square, significance_bool


@njit("(float32[:], float32, float32, float32[:,:], float32)")
def sliding_independent_samples_t(data: np.ndarray, time_window: float, slide_time: float, critical_values: np.ndarray, fps: float) -> np.ndarray:
    """
    Jitted compute of sliding independent sample t-test. Compares the feature values in current time-window
    to prior time-windows to find the length in time to the most recent time-window where a significantly different
    feature value distribution is detected.

    .. image:: _static/img/sliding_statistics.png
       :width: 1500
       :align: center
    .. seealso::

       For simple two distribution commparison, see :func:`simba.mixins.statistics_mixin.Statistics.independent_samples_t`

    :param ndarray data: 1D array with feature values.
    :param float time_window: The sizes of the two feature value windows being compared in seconds.
    :param float slide_time: The slide size of the second window.
    :param ndarray critical_values: 2D array with where indexes represent degrees of freedom and values represent critical T values. Can be found in ``simba.assets.critical_values_05.pickle``.
    :parameter int fps: The fps of the recorded video.
    :returns: 1D array of size len(data) with values representing time to most recent significantly different feature distribution.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 50, (10)).astype(np.float32)
    >>> critical_values = pickle.load(open("simba/assets/lookups/critical_values_05.pickle", "rb"))['independent_t_test']['one_tail'].values.astype(np.float32)
    >>> results = sliding_independent_samples_t(data=data, time_window=0.5, fps=5.0, critical_values=critical_values, slide_time=0.30)
    """
    results = np.full((data.shape[0]), 0.0)
    window_size, slide_size = int(time_window * fps), int(slide_time * fps)
    for i in range(1, data.shape[0]):
        sample_1_left, sample_1_right = i, i + window_size
        sample_2_left, sample_2_right = (
            sample_1_left - slide_size,
            sample_1_right - slide_size,
        )
        sample_1 = data[sample_1_left:sample_1_right]
        dof, steps_taken = (sample_1.shape[0] + sample_1.shape[0]) - 2, 1
        while sample_2_left >= 0:
            sample_2 = data[sample_2_left:sample_2_right]
            t_statistic = (np.mean(sample_1) - np.mean(sample_2)) / np.sqrt(
                (np.std(sample_1) / sample_1.shape[0])
                + (np.std(sample_2) / sample_1.shape[0])
            )
            critical_val = critical_values[dof - 1][1]
            if t_statistic >= critical_val:
                break
            else:
                sample_2_left -= 1
                sample_2_right -= 1
                steps_taken += 1
            if sample_2_left < 0:
                steps_taken = -1
        if steps_taken == -1:
            results[i + window_size] = -1
        else:
            results[i + window_size] = steps_taken * slide_time
    return results


@njit("(float32[:], float64[:], float32)")
def rolling_mann_whitney(data: np.ndarray, time_windows: np.ndarray, fps: float) -> np.ndarray:
    """
    Jitted compute of rolling Mann-Whitney U comparing the current time-window of
    size N to the preceding window of size N.

    .. note::
       First time bin (where has no preceding time bin) will have fill value ``0``
       `Modified from James Webber gist <https://gist.github.com/jamestwebber/38ab26d281f97feb8196b3d93edeeb7b>`__.

    .. seealso::
       For simple two-distribution comparion, see :func:`simba.mixins.statistics_mixin.Statistics.mann_whitney`.

    :param ndarray sample_1: First 1d array representing feature values.
    :param ndarray sample_2: Second 1d array representing feature values.
    :returns: Mann-Whitney U data of size len(data) x len(time_windows).
    :rtype: np.ndarray

    :examples:
    >>> data = np.random.randint(0, 4, (200)).astype(np.float32)
    >>> rolling_mann_whitney(data=data, time_windows=np.array([1.0]), fps=1)
    """

    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        data_split = np.split(data, list(range(window_size, data.shape[0], window_size)))
        for j in prange(1, len(data_split)):
            window_start = int(window_size * j)
            window_end = int(window_start + window_size)
            sample_1, sample_2 = data_split[j - 1].astype(np.float32), data_split[j].astype(np.float32)
            n1, n2 = sample_1.shape[0], sample_2.shape[0]
            ranked = fast_mean_rank(np.concatenate((sample_1, sample_2)))
            u1 = n1 * n2 + (n1 * (n1 + 1)) / 2.0 - np.sum(ranked[:n1], axis=0)
            u2 = n1 * n2 - u1
            u = min(u1, u2)
            results[window_start:window_end, i] = u

    return results

@njit("(int64[:, :]), bool_")
def concordance_ratio(x: np.ndarray, invert: bool) -> float:
    """
    Calculate the concordance ratio of a 2D numpy array. The concordance ratio is a measure of agreement in a dataset. It is calculated as the ratio of the number of
    rows that contain only one unique value to the total number of rows.

    The equation for the concordance ratio :math:`C` is given by:

    .. math::
       C = \\frac{N_c}{N_t}

    where:
       - :math:`N_c` is the count of rows with only one unique value,
       - :math:`N_t` is the total number of rows in the array.

    If the `invert` parameter is set to `True`, the function will return the disconcordance ratio instead, defined as:

    .. math::
        D = \\frac{N_d}{N_t}

    where:
       - :math:`N_d` is the count of rows with more than one unique value.

    :param np.ndarray x: A 2D numpy array with ordinals represented as integers.
    :param bool invert: If True, the concordance ratio is inverted, and disconcordance ratio is returned
    :return: The concordance ratio, representing the count of rows with only one unique value divided by the total number of rows in the array.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 2, (5000, 4))
    >>> results = concordance_ratio(x=x, invert=False)
    """

    conc_count = 0
    for i in prange(x.shape[0]):
        unique_cnt = np.unique((x[i])).shape[0]
        if unique_cnt == 1:
            conc_count += 1
    if invert:
        conc_count = x.shape[0] - conc_count
    return conc_count / x.shape[0]

@njit("(float32[:], float32[:], float64[:], int64)")
def sliding_spearman_rank_correlation(sample_1: np.ndarray, sample_2: np.ndarray, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Given two 1D arrays of size N, create sliding window of size time_windows[i] * fps and return Spearman's rank correlation
    between the values in the two 1D arrays in each window. Address "what is the correlation between Feature 1 and
    Feature 2 in the current X.X seconds of the video.

    .. image:: _static/img/sliding_spearman.png
       :width: 600
       :align: center

    .. seealso::
       For simple two-distribution comparion, see :func:`simba.mixins.statistics_mixin.Statistics.spearman_rank_correlation`.

    :param ndarray sample_1: First 1D array with feature values.
    :param ndarray sample_1: Second 1D array with feature values.
    :param float time_windows: The length of the sliding window in seconds.
    :param int fps: The fps of the recorded video.
    :returns: 2d array of Soearman's ranks of size len(sample_1) x len(time_windows). Note, if sliding window is 10 frames, the first 9 entries will be filled with 0. The 10th value represents the correlation in the first 10 frames.
    :rtype: np.ndarray

    :example:
    >>> sample_1 = np.array([9,10,13,22,15,18,15,19,32,11]).astype(np.float32)
    >>> sample_2 = np.array([11, 12, 15, 19, 21, 26, 19, 20, 22, 19]).astype(np.float32)
    >>> sliding_spearman_rank_correlation(sample_1=sample_1, sample_2=sample_2, time_windows=np.array([0.5]), fps=10)
    """
    results = np.full((sample_1.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for left, right in zip(range(0, sample_1.shape[0] + 1), range(window_size, sample_1.shape[0] + 1)):
            s1, s2 = sample_1[left:right], sample_2[left:right]
            rank_x, rank_y = np.argsort(np.argsort(s1)), np.argsort(np.argsort(s2))
            d_squared = np.sum((rank_x - rank_y) ** 2)
            n = s1.shape[0]
            s = 1 - (6 * d_squared) / (n * (n ** 2 - 1))
            results[right - 1, i] = s
    return results

@njit("(float32[:], float64, float64, float64)")
def sliding_autocorrelation(data: np.ndarray, max_lag: float, time_window: float, fps: float) -> np.ndarray:
    """
    Jitted computation of sliding autocorrelations, which measures the correlation of a feature with itself using lagged windows.

    :param np.ndarray data: 1D array containing feature values.
    :param float max_lag: Maximum lag in seconds for the autocorrelation window.
    :param float time_window: Length of the sliding time window in seconds.
    :param float fps: Frames per second, used to convert time-related parameters into frames.
    :return: 1D array containing the sliding autocorrelation values.
    :rtype: np.ndarray

    :example:
    >>> data = np.array([0,1,2,3,4, 5,6,7,8,1,10,11,12,13,14]).astype(np.float32)
    >>> sliding_autocorrelation(data=data, max_lag=0.5, time_window=1.0, fps=10)
    >>> [ 0., 0., 0.,  0.,  0., 0., 0.,  0. ,  0., -3.686, -2.029, -1.323, -1.753, -3.807, -4.634]
    """

    max_frm_lag, time_window_frms = int(max_lag * fps), int(time_window * fps)
    results = np.full((data.shape[0]), -1.0)
    for right in prange(time_window_frms - 1, data.shape[0]):
        left = right - time_window_frms + 1
        w_data = data[left : right + 1]
        corrcfs = np.full((max_frm_lag), np.nan)
        corrcfs[0] = 1
        for shift in range(1, max_frm_lag):
            c = np.corrcoef(w_data[:-shift], w_data[shift:])[0][1]
            if np.isnan(c):
                corrcfs[shift] = 1
            else:
                corrcfs[shift] = np.corrcoef(w_data[:-shift], w_data[shift:])[0][1]
        mat_ = np.zeros(shape=(corrcfs.shape[0], 2))
        const = np.ones_like(corrcfs)
        mat_[:, 0] = const
        mat_[:, 1] = corrcfs
        det_ = np.linalg.lstsq(mat_.astype(np.float32), np.arange(0, max_frm_lag).astype(np.float32))[0]
        results[right] = det_[::-1][0]
    return results

@njit("(float32[:], float32[:])")
def kendall_tau(sample_1: np.ndarray, sample_2: np.ndarray) -> Tuple[float, float]:
    """
    Jitted compute of Kendall Tau (rank correlation coefficient). Non-parametric method for computing correlation
    between two time-series features. Returns tau and associated z-score.

    Kendall Tau is a measure of the correspondence between two rankings. It compares the number of concordant
    pairs (pairs of elements that are in the same order in both rankings) to the number of discordant pairs
    (pairs of elements that are in different orders in the rankings).

    Kendall Tau is calculated using the following formula:

    .. math::
       \\tau = \\frac{{\\sum C - \\sum D}}{{\\sum C + \\sum D}}

    where :math:`C` is the count of concordant pairs and :math:`D` is the count of discordant pairs.

    .. seealso::
       For time-series based comparison, see :func:`simba.mixins.statistics_mixin.Statistics.sliding_kendall_tau`.

    :param ndarray sample_1: First 1D array with feature values.
    :param ndarray sample_1: Second 1D array with feature values.
    :returns: Size-2 tuple with Kendall Tau and associated z-score.
    :rtype: Tuple[float, float]

    :examples:
    >>> sample_1 = np.array([4, 2, 3, 4, 5, 7]).astype(np.float32)
    >>> sample_2 = np.array([1, 2, 3, 4, 5, 7]).astype(np.float32)
    >>> kendall_tau(sample_1=sample_1, sample_2=sample_2)
    >>> (0.7333333333333333, 2.0665401605809928)

    :references:
    .. [1] `Stephanie Glen, "Kendall’s Tau (Kendall Rank Correlation Coefficient)"  <https://www.statisticshowto.com/kendalls-tau/>`__.
    """

    rnks = np.argsort(sample_1)
    s1_rnk, s2_rnk = sample_1[rnks], sample_2[rnks]
    cncrdnt_cnts, dscrdnt_cnts = np.full((s1_rnk.shape[0] - 1), np.nan), np.full((s1_rnk.shape[0] - 1), np.nan)
    for i in range(s2_rnk.shape[0] - 1):
        cncrdnt_cnts[i] = (np.argwhere(s2_rnk[i + 1 :] > s1_rnk[i]).flatten().shape[0])
        dscrdnt_cnts[i] = (np.argwhere(s2_rnk[i + 1 :] < s1_rnk[i]).flatten().shape[0])
    t = (np.sum(cncrdnt_cnts) - np.sum(dscrdnt_cnts)) / (np.sum(cncrdnt_cnts) + np.sum(dscrdnt_cnts))
    z = (3 * t * (np.sqrt(s1_rnk.shape[0] * (s1_rnk.shape[0] - 1))) / np.sqrt(2 * ((2 * s1_rnk.shape[0]) + 5)))
    return t, z

@njit("(float32[:], float32[:], float64[:], int64)")
def sliding_kendall_tau(sample_1: np.ndarray, sample_2: np.ndarray, time_windows: np.ndarray, fps: float) -> np.ndarray:
    """
    Compute sliding Kendall's Tau correlation coefficient.
    Calculates Kendall's Tau correlation coefficient between two samples over sliding time windows. Kendall's Tau is a measure of correlation between two ranked datasets.

    The computation is based on the formula:
    .. math::
       \\tau = \\frac{{\\text{{concordant pairs}} - \\text{{discordant pairs}}}}{{\\text{{concordant pairs}} + \\text{{discordant pairs}}}}

    where concordant pairs are pairs of elements with the same order in both samples, and discordant pairs are pairs with different orders.

    .. seealso::
       For simple two-sample comparison, see :func:`simba.mixins.statistics_mixin.Statistics.kendall_tau`.

    :references:
    .. [1] `Stephanie Glen, "Kendall’s Tau (Kendall Rank Correlation Coefficient)"  <https://www.statisticshowto.com/kendalls-tau/>`_.

    :param np.ndarray sample_1: First sample for comparison.
    :param np.ndarray sample_2: Second sample for comparison.
    :param np.ndarray time_windows: Rolling time windows in seconds.
    :param float fps: Frames per second (FPS) of the recorded video.
    :return: Array of Kendall's Tau correlation coefficients corresponding to each time window.
    :rtype: np.ndarray

    """
    results = np.full((sample_1.shape[0], time_windows.shape[0]), 0.0)
    for time_window_cnt in range(time_windows.shape[0]):
        window_size = int(time_windows[time_window_cnt] * fps)
        for left, right in zip(range(0, sample_1.shape[0] + 1), range(window_size, sample_1.shape[0] + 1)):
            sliced_sample_1, sliced_sample_2 = (sample_1[left:right], sample_2[left:right])
            rnks = np.argsort(sliced_sample_1)
            s1_rnk, s2_rnk = sliced_sample_1[rnks], sliced_sample_2[rnks]
            cncrdnt_cnts, dscrdnt_cnts = np.full((s1_rnk.shape[0] - 1), np.nan), np.full((s1_rnk.shape[0] - 1), np.nan)
            for i in range(s2_rnk.shape[0] - 1):
                cncrdnt_cnts[i] = (np.argwhere(s2_rnk[i + 1 :] > s1_rnk[i]).flatten().shape[0])
                dscrdnt_cnts[i] = (np.argwhere(s2_rnk[i + 1 :] < s1_rnk[i]).flatten().shape[0])
            n = np.sum(cncrdnt_cnts) - np.sum(dscrdnt_cnts)
            d = np.sum(cncrdnt_cnts) + np.sum(dscrdnt_cnts)
            if d == 0:
                results[right][time_window_cnt] = -1
            else:
                results[right][time_window_cnt] = n / d
    return results


def rolling_shapiro_wilks(self, data: np.ndarray, time_window: float, fps: int) -> np.ndarray:
    """
    Compute Shapiro-Wilks normality statistics for sequentially binned values in a time-series. E.g., compute
    the normality statistics of ``Feature N`` in each window of ``time_window`` seconds.

    :param ndarray data: 1D array of size len(frames) representing feature values.
    :param int time_window: The size of the buckets in seconds.
    :param int fps: Frame-rate of recorded video.
    :return: Array of size data.shape[0] with Shapiro-Wilks normality statistics
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(low=0, high=100, size=(200)).astype('float32')
    >>> results = self.rolling_shapiro_wilks(data=data, time_window=1, fps=30)
    """
    check_valid_array(data=data, source=f"{rolling_shapiro_wilks.__name__} data", accepted_sizes=[1])
    check_float(name=f"{rolling_shapiro_wilks.__name__} data", value=time_window, min_value=0.1)
    check_int(name=f"{rolling_shapiro_wilks.__class__.__name__} data", value=time_window, min_value=1)
    window_size, results = int(time_window * fps), np.full((data.shape[0]), -1.0)
    data = np.split(data, list(range(window_size, data.shape[0], window_size)))
    for cnt, i in enumerate(prange(1, len(data))):
        start, end = int((cnt + 1) * window_size), int(((cnt + 1) * window_size) + window_size)
        results[start:end] = stats.shapiro(data[i])[0]
    return results

@njit("(float32[:], float64[:], int64,)")
def sliding_z_scores(data: np.ndarray, time_windows: np.ndarray, fps: int) -> np.ndarray:
    """
    Calculate sliding Z-scores for a given data array over specified time windows.

    This function computes sliding Z-scores for a 1D data array over different time windows. The sliding Z-score
    is a measure of how many standard deviations a data point is from the mean of the surrounding data within
    the specified time window. This can be useful for detecting anomalies or variations in time-series data.

    :param ndarray data: 1D NumPy array containing the time-series data.
    :param ndarray time_windows: 1D NumPy array specifying the time windows in seconds over which to calculate the Z-scores.
    :param int time_windows: Frames per second, used to convert time windows from seconds to the corresponding number of data points.
    :returns: A 2D NumPy array containing the calculated Z-scores. Each row corresponds to the Z-scores calculated for a specific time window. The time windows are represented by the columns.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 100, (1000,)).astype(np.float32)
    >>> z_scores = sliding_z_scores(data=data, time_windows=np.array([1.0, 2.5]), fps=10)
    """
    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in range(time_windows.shape[0]):
        window_size = int(time_windows[i] * fps)
        for right in range(window_size - 1, data.shape[0]):
            left = right - window_size + 1
            sample_data = data[left : right + 1]
            m, s = np.mean(sample_data), np.std(sample_data)
            vals = (sample_data - m) / s
            results[left : right + 1, i] = vals
    return results

def eta_squared(x: np.ndarray, y: np.ndarray) -> float:
    r"""
    Calculate eta-squared, a measure of between-subjects effect size.
    Eta-squared (\(\eta^2\)) is calculated as the ratio of the sum of squares between groups to the total sum of squares. Range from 0 to 1, where larger values indicate
    a stronger effect size.

    The equation for eta squared is defined as: :math:`\eta^2 = \frac{SS_{between}}{SS_{between} + SS_{within}}`

    where:
       - :math:`SS_{between}` is the sum of squares between groups,
       - :math:`SS_{within}` is the sum of squares within groups.

    .. seealso::
       For sliding time-windows comparisons, see :func:`simba.mixins.statistics_mixin.Statistics.sliding_eta_squared`.

    :param np.ndarray x: 1D array containing the dependent variable data.
    :param np.ndarray y: 1d array containing the grouping variable (categorical) data of same size as ``x``.
    :return: The eta-squared value representing the proportion of variance in the dependent variable that is attributable to the grouping variable.
    :rtype: float
    """
    check_valid_array(data=x, source=f'{eta_squared.__name__} x', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{eta_squared.__name__} y', accepted_shapes=[x.shape])
    sum_square_within, sum_square_between = 0, 0
    for lbl in np.unique(y):
        g = x[np.argwhere(y == lbl)]
        sum_square_within += np.sum((g - np.mean(g)) ** 2)
        sum_square_between += len(g) * (np.mean(g) - np.mean(x)) ** 2
    if sum_square_between + sum_square_within == 0:
        return 0.0
    else:
        return (sum_square_between / (sum_square_between + sum_square_within)) ** .5


@jit(nopython=True)
def sliding_eta_squared(x: np.ndarray, y: np.ndarray, window_sizes: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Calculate sliding window eta-squared, a measure of effect size for between-subjects designs,
    over multiple window sizes.

    .. seealso::
       For two-sample comparison, see :func:`simba.mixins.statistics_mixin.Statistics.eta_squared`

    :param np.ndarray x: The array containing the dependent variable data.
    :param np.ndarray y: The array containing the grouping variable (categorical) data.
    :param np.ndarray window_sizes: 1D array of window sizes in seconds.
    :param int sample_rate: The sampling rate of the data in frames per second.
    :return: Array of size  x.shape[0] x window_sizes.shape[0] with sliding eta squared values.
    :rtype: np.ndarray

    :example:
    >>> x = np.random.randint(0, 10, (10000,))
    >>> y = np.random.randint(0, 2, (10000,))
    >>> sliding_eta_squared(x=x, y=y, window_sizes=np.array([1.0, 2.0]), sample_rate=10)
    """

    results = np.full((x.shape[0], window_sizes.shape[0]), -1.0)
    for i in range(window_sizes.shape[0]):
        window_size = int(window_sizes[i] * sample_rate)
        for l, r in zip(range(0, x.shape[0] + 1), range(window_size, x.shape[0] + 1)):
            sample_x = x[l:r]
            sample_y = y[l:r]
            sum_square_within, sum_square_between = 0, 0
            for lbl in np.unique(sample_y):
                g = sample_x[np.argwhere(sample_y == lbl).flatten()]
                sum_square_within += np.sum((g - np.mean(g)) ** 2)
                sum_square_between += len(g) * (np.mean(g) - np.mean(sample_x)) ** 2
            if sum_square_between + sum_square_within == 0:
                results[r - 1, i] = 0.0
            else:
                results[r - 1, i] = (sum_square_between / (sum_square_between + sum_square_within)) ** .5
    return results


@njit("int64[:], int64[:],")
def cohens_h(sample_1: np.ndarray, sample_2: np.ndarray) -> float:
    """
    Jitted compute Cohen's h effect size for two samples of binary [0, 1] values. Cohen's h is a measure of effect size
    for comparing two independent samples based on the differences in proportions of the two samples.

    .. note:
       Modified from `DABEST <https://github.com/ACCLAB/DABEST-python/blob/fa7df50d20ab1c9cc687c66dd8bddf55d9a9dce3/dabest/_stats_tools/effsize.py#L216>`_
       `Cohen's h wiki <https://en.wikipedia.org/wiki/Cohen%27s_h>`_

    .. math::
       \\text{Cohen's h} = 2 \\arcsin\\left(\\sqrt{\\frac{\\sum\\text{sample\_1}}{N\_1}}\\right) - 2 \\arcsin\\left(\\sqrt{\\frac{\\sum\\text{sample\_2}}{N\_2}}\\right)

    Where :math:`N_1` and :math:`N_2` are the sample sizes of sample_1 and sample_2, respectively.

    :param np.ndarray sample_1: 1D array with binary [0, 1] values (e.g., first classifier inference values).
    :param np.ndarray sample_2: 1D array with binary [0, 1] values (e.g., second classifier inference values).
    :return: Cohen's h effect size.
    :rtype: float

    :example:
    >>> sample_1 = np.array([1, 0, 0, 1])
    >>> sample_2 = np.array([1, 1, 1, 0])
    >>> cohens_h(sample_1=sample_1, sample_2=sample_2)
    >>> -0.5235987755982985
    """
    sample_1_proportion = np.sum(sample_1) / sample_1.shape[0]
    sample_2_proportion = np.sum(sample_2) / sample_2.shape[0]
    phi_sample_1 = 2 * np.arcsin(np.sqrt(sample_1_proportion))
    phi_sample_2 = 2 * np.arcsin(np.sqrt(sample_2_proportion))
    return phi_sample_1 - phi_sample_2


@jit("(float32[:], float64[:], int64,)")
def sliding_skew(data: np.ndarray, time_windows: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Compute the skewness of a 1D array within sliding time windows.

    :param np.ndarray data: 1D array of input data.
    :param np.ndarray data: 1D array of time window durations in seconds.
    :param np.ndarray data: Sampling rate of the data in samples per second.
    :return np.ndarray: 2D array of skewness`1 values with rows corresponding to data points and columns corresponding to time windows.

    :example:
    >>> data = np.random.randint(0, 100, (10,))
    >>> skewness = sliding_skew(data=data.astype(np.float32), time_windows=np.array([1.0, 2.0]), sample_rate=2)
    """

    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = int(time_windows[i] * sample_rate)
        for j in range(window_size, data.shape[0] + 1):
            sample = data[j - window_size : j]
            mean, std = np.mean(sample), np.std(sample)
            results[j - 1][i] = (1 / sample.shape[0]) * np.sum(((data - mean) / std) ** 3)
    return results


@jit("(float32[:], float64[:], int64,)")
def sliding_kurtosis(data: np.ndarray, time_windows: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Compute the kurtosis of a 1D array within sliding time windows.

    :param np.ndarray data: Input data array.
    :param np.ndarray time_windows: 1D array of time window durations in seconds.
    :param np.ndarray sample_rate: Sampling rate of the data in samples per second.
    :return np.ndarray: 2D array of skewness`1 values with rows corresponding to data points and columns corresponding to time windows.

    :example:
    >>> data = np.random.randint(0, 100, (10,))
    >>> kurtosis = sliding_kurtosis(data=data.astype(np.float32), time_windows=np.array([1.0, 2.0]), sample_rate=2)
    """

    results = np.full((data.shape[0], time_windows.shape[0]), 0.0)
    for i in prange(time_windows.shape[0]):
        window_size = time_windows[i] * sample_rate
        for j in range(window_size, data.shape[0] + 1):
            sample = data[j - window_size : j]
            mean, std = np.mean(sample), np.std(sample)
            results[j - 1][i] = np.mean(((data - mean) / std) ** 4) - 3
    return results


@njit("(int64[:], int64[:])")
def cohens_kappa(sample_1: np.ndarray, sample_2: np.ndarray):
    """
    Jitted compute Cohen's Kappa coefficient for two binary samples.
    Cohen's Kappa coefficient measures the agreement between two sets of binary ratings, taking into account agreement occurring by chance.
    It ranges from -1 to 1, where 1 indicates perfect agreement, 0 indicates agreement by chance, and -1 indicates complete disagreement.

    .. math::
       \\kappa = 1 - \\frac{\sum{w_{ij} \\cdot D_{ij}}}{\\sum{w_{ij} \\cdot E_{ij}}}

    where:
       - :math:`\kappa` is Cohen's Kappa coefficient,
       - :math:`w_{ij}` are the weights,
       - :math:`D_{ij}` are the observed frequencies,
       - :math:`E_{ij}` are the expected frequencies.

    :param np.ndarray sample_1: The first binary sample, a 1D NumPy array of integers.
    :param np.ndarray sample_2: The second binary sample, a 1D NumPy array of integers.
    :return: Cohen's Kappa coefficient between the two samples.
    :rtype: float

    :example:
    >>> sample_1 = np.random.randint(0, 2, size=(10000,))
    >>> sample_2 = np.random.randint(0, 2, size=(10000,))
    >>> cohens_kappa(sample_1=sample_1, sample_2=sample_2))
    """

    sample_1 = np.ascontiguousarray(sample_1)
    sample_2 = np.ascontiguousarray(sample_2)
    data = np.hstack((sample_1.reshape(-1, 1), sample_2.reshape(-1, 1)))
    tp = len(np.argwhere((data[:, 0] == 1) & (data[:, 1] == 1)).flatten())
    tn = len(np.argwhere((data[:, 0] == 0) & (data[:, 1] == 0)).flatten())
    fp = len(np.argwhere((data[:, 0] == 1) & (data[:, 1] == 0)).flatten())
    fn = len(np.argwhere((data[:, 0] == 0) & (data[:, 1] == 1)).flatten())
    data = np.array(([tp, fp], [fn, tn]))
    sum0 = data.sum(axis=0)
    sum1 = data.sum(axis=1)
    expected = np.outer(sum0, sum1) / np.sum(sum0)
    w_mat = np.full(shape=(2, 2), fill_value=1)
    w_mat[0, 0] = 0
    w_mat[1, 1] = 0
    return 1 - np.sum(w_mat * data) / np.sum(w_mat * expected)


def d_prime(x: np.ndarray, y: np.ndarray, lower_limit: Optional[float] = 0.0001, upper_limit: Optional[float] = 0.9999) -> float:

    """
    Computes d-prime from two Boolean 1d arrays, e.g., between classifications and ground truth.
    D-prime (d') is a measure of signal detection performance, indicating the ability to discriminate between signal and noise.
    It is computed as the difference between the inverse cumulative distribution function (CDF) of the hit rate and the false alarm rate.

    .. math::
       d' = \\Phi^{-1}(hit\\_rate) - \\Phi^{-1}(false\\_alarm\\_rate)

    where:
    - :math:`\\Phi^{-1}` is the inverse of the cumulative distribution function (CDF) of the normal distribution,
    - :math:`hit\\_rate` is the proportion of true positives correctly identified,
    - :math:`false\\_alarm\\_rate` is the proportion of false positives incorrectly identified.

    :param np.ndarray x: Boolean 1D array of response values, where 1 represents presence, and 0 representing absence.
    :param np.ndarray y: Boolean 1D array of ground truth, where 1 represents presence, and 0 representing absence.
    :param Optional[float] lower_limit: Lower limit to bound hit and false alarm rates. Defaults to 0.0001.
    :param Optional[float] upper_limit: Upper limit to bound hit and false alarm rates. Defaults to 0.9999.
    :return: The calculated d' (d-prime) value.
    :rtype: float

    :example:
    >>> x = np.random.randint(0, 2, (1000,))
    >>> y = np.random.randint(0, 2, (1000,))
    >>> d_prime(x=x, y=y)
    """
    check_valid_array(data=x, source=d_prime.__name__, accepted_ndims=(1,), accepted_dtypes=(np.int64, np.int32, np.int8))
    check_valid_array(data=y, source=d_prime.__name__, accepted_ndims=(1,), accepted_dtypes=(np.int64, np.int32, np.int8))
    if len(list({x.shape[0], y.shape[0]})) != 1:
        raise CountError(msg=f"The two arrays has to be equal lengths but got: {x.shape[0], y.shape[0]}", source=d_prime.__name__)
    for i in [x, y]:
        additional = list(set(list(np.sort(np.unique(i)))) - {0, 1})
        if len(additional) > 0:
            raise InvalidInputError(msg=f"D-prime requires binary input data but found {additional}", source=d_prime.__name__)
    target_idx = np.argwhere(y == 1).flatten()
    hit_rate = np.sum(x[np.argwhere(y == 1)]) / target_idx.shape[0]
    false_alarm_rate = np.sum(x[np.argwhere(y == 0)]) / target_idx.shape[0]
    if hit_rate < lower_limit:
        hit_rate = lower_limit
    elif hit_rate > upper_limit:
        hit_rate = upper_limit
    if false_alarm_rate < lower_limit:
        false_alarm_rate = lower_limit
    elif false_alarm_rate > upper_limit:
        false_alarm_rate = upper_limit
    return stats.norm.ppf(hit_rate) - stats.norm.ppf(false_alarm_rate)


def mcnemar(x: np.ndarray, y: np.ndarray, ground_truth: np.ndarray, continuity_corrected: Optional[bool] = True) -> Tuple[float, float]:
    """
    Perform McNemar's test to compare the predictive accuracy of two models. This test is used
    to evaluate if the accuracies of two classifiers are significantly different when tested on the same data.
    The chi-squared statistic (with continuity correction if `continuity_corrected=True`) is calculated as:

    .. math::
      X^2 = \\frac{(|b - c| - 1)^2}{b + c} \\,\\text{ if corrected, or }\\, X^2 = \\frac{(b - c)^2}{b + c}

    where:
       - `b` is the number of instances misclassified by the first model but correctly classified by the second model.
       - `c` is the number of instances correctly classified by the first model but misclassified by the second model.

    .. note::
       Adapted from `mlextend <https://github.com/rasbt/mlxtend/blob/master/mlxtend/evaluate/mcnemar.py>`__.

    :param np.ndarray x: 1-dimensional Boolean array with predictions of the first model.
    :param np.ndarray y: 1-dimensional Boolean array with predictions of the second model.
    :param np.ndarray ground_truth: 1-dimensional Boolean array with ground truth labels.
    :param Optional[bool] continuity_corrected: Whether to apply continuity correction. Default is True.
    :returns: McNemar score are significance level.
    :rtype: Tuple[float, float]

    :example:
    >>> x = np.random.randint(0, 2, (100000, ))
    >>> y = np.random.randint(0, 2, (100000, ))
    >>> ground_truth = np.random.randint(0, 2, (100000, ))
    >>> mcnemar(x=x, y=y, ground_truth=ground_truth)
    """
    check_valid_array(data=x, source=mcnemar.__name__, accepted_ndims=(1,), accepted_dtypes=(np.int64, np.int32, np.int8))
    check_valid_array(data=y, source=mcnemar.__name__, accepted_ndims=(1,), accepted_dtypes=(np.int64, np.int32, np.int8))
    check_valid_array(data=ground_truth, source=mcnemar.__name__, accepted_ndims=(1,), accepted_dtypes=(np.int64, np.int32, np.int8))
    if len(list({x.shape[0], y.shape[0], ground_truth.shape[0]})) != 1:
        raise CountError(msg=f"The three arrays has to be equal lengths but got: {x.shape[0], y.shape[0], ground_truth.shape[0]}", source=mcnemar.__name__,)
    for i in [x, y, ground_truth]:
        additional = list(set(list(np.sort(np.unique(i)))) - {0, 1})
        if len(additional) > 0:
            raise InvalidInputError(msg=f"Mcnemar requires binary input data but found {additional}", source=mcnemar.__name__)
    data = np.hstack(
        (x.reshape(-1, 1), y.reshape(-1, 1), ground_truth.reshape(-1, 1))
    )
    b = (
        np.where((data == (0, 1, 0)).all(axis=1))[0].shape[0]
        + np.where((data == (1, 0, 1)).all(axis=1))[0].shape[0]
    )
    c = (
        np.where((data == (1, 0, 0)).all(axis=1))[0].shape[0]
        + np.where((data == (0, 1, 1)).all(axis=1))[0].shape[0]
    )
    if not continuity_corrected:
        x = (np.square(b - c)) / (b + c)
    else:
        x = (np.square(np.abs(b - c) - 1)) / (b + c)
    p = chi2.sf(x, 1)
    return x, p


def cochrans_q(data: np.ndarray) -> Tuple[float, float]:
    r"""
    Compute Cochrans Q for 2-dimensional boolean array.
    Cochran's Q statistic is used to test for significant differences between more than two proportions.

    It can be used to evaluate if the performance of multiple (>=2) classifiers on the same data is the same or significantly different.

    .. note::
       If two classifiers, consider :func:`simba.mixins.statistics.Statistics.mcnemar()`.
       Useful background: https://psych.unl.edu/psycrs/handcomp/hccochran.PDF

    :math:`Q = \frac{(k - 1) \left( kG^2 - \left( \sum_{j=1}^{k} C_j \right)^2 \right)}{kR - S}`

    where:
    - :math:`k` is the number of classifiers,
    - :math:`G = \sum_{j=1}^{k} C_j^2` (the sum of the squares of the column sums),
    - :math:`C_j` is the sum of the :math:`j`-th column (number of successes for the :math:`j`-th classifier),
    - :math:`R = \sum_{i=1}^{n} R_i` (the total number of successes across all classifiers),
    - :math:`S = \sum_{i=1}^{n} R_i^2` (the sum of the squares of the row sums),
    - :math:`R_i` is the sum of the :math:`i`-th row (number of successes for the :math:`i`-th observation).

    :param np.ndarray data: Two-dimensional array of boolean values where axis 1 represents classifiers or features and rows represent frames.
    :return: Cochran's Q statistic signidicance value.
    :rtype: Tuple[float, float]

    :example:
    >>> data = np.random.randint(0, 2, (100000, 4))
    >>> cochrans_q(data=data)
    """
    check_valid_array(data=data, source=cochrans_q.__name__, accepted_ndims=(2,))
    additional = list(set(list(np.sort(np.unique(data)))) - {0, 1})
    if len(additional) > 0:
        raise InvalidInputError(msg=f"Cochrans Q requires binary input data but found {additional}", source=cochrans_q.__name__)
    col_sums = np.sum(data, axis=0)
    row_sum_sum = np.sum(np.sum(data, axis=1))
    row_sum_square_sum = np.sum(np.square(np.sum(data, axis=1)))
    k = data.shape[1]
    g2 = np.sum(sum(np.square(col_sums)))
    nominator = (k - 1) * ((k * g2) - np.square(np.sum(col_sums)))
    denominator = (k * row_sum_sum) - row_sum_square_sum
    if nominator == 0 or denominator == 0:
        return -1.0, -1.0
    else:
        q = (nominator / denominator,)
        return q, stats.chi2.sf(q, k - 1)


def hartley_fmax(x: np.ndarray, y: np.ndarray) -> float:

    r"""
    Compute Hartley's Fmax statistic to test for equality of variances between two features or groups.
    Hartley's Fmax statistic is used to test whether two samples have equal variances.
    It is calculated as the ratio of the largest sample variance to the smallest sample variance.

    Values close to one represent closer to equal variance.

    .. math::
        \text{Hartley's } F_{max} = \frac{\max(\text{Var}(x), \text{Var}(y))}{\min(\text{Var}(x), \text{Var}(y))}

    where:
    - :math:`\text{Var}(x)` is the variance of sample :math:`x`,
    - :math:`\text{Var}(y)` is the variance of sample :math:`y`.

    :param np.ndarray x: 1D array representing numeric data of the first group/feature.
    :param np.ndarray x: 1D array representing numeric data of the second group/feature.
    :return: Hartley's Fmax statistic.
    :rtype: float

    :example:
    >>> x = np.random.random((100,))
    >>> y = np.random.random((100,))
    >>> hartley_fmax(x=x, y=y)
    """
    check_valid_array( data=x, source=hartley_fmax.__name__, accepted_ndims=(1,), accepted_dtypes=(np.float32, np.float64, np.int64, np.float32))
    check_valid_array( data=y, source=hartley_fmax.__name__, accepted_ndims=(1,), accepted_dtypes=(np.float32, np.float64, np.int64, np.float32))
    max_var = np.max((np.var(x), np.var(y)))
    min_var = np.min((np.var(x), np.var(y)))
    if (max_var == 0) or (min_var == 0):
        return -1.0
    return max_var / min_var


def wilcoxon(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """
    Perform the Wilcoxon signed-rank test for paired samples.
    Wilcoxon signed-rank test is a non-parametric statistical hypothesis test used
    to compare two related samples, matched samples, or repeated measurements on a single sample
    to assess whether their population mean ranks differ.

    :param np.ndarray x: 1D array representing the observations for the first sample.
    :param np.ndarray y: 1D array representing the observations for the second sample.
    :return: A tuple containing the test statistic (z-score) and the effect size (r).
    - The test statistic (z-score) measures the deviation of the observed ranks sum from the expected sum.
    - The effect size (r) measures the strength of association between the variables.
    :rtype: Tuple[float, float]
    """

    data = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))
    n = data.shape[0]
    diff = np.diff(data).flatten()
    diff_abs = np.abs(diff)
    rank_w_ties = fast_mean_rank(data=diff_abs, descending=False)
    signed_rank_w_ties = np.full((rank_w_ties.shape[0]), np.nan)
    t_plus, t_minus = 0, 0
    for i in range(diff.shape[0]):
        if diff[i] < 0:
            signed_rank_w_ties[i] = -rank_w_ties[i]
            t_minus += np.abs(rank_w_ties[i])
        else:
            signed_rank_w_ties[i] = rank_w_ties[i]
            t_plus += np.abs(rank_w_ties[i])
    u_w = (n * (n + 1)) / 4
    std_correction = 0
    for i in range(signed_rank_w_ties.shape[0]):
        same_rank_n = (np.argwhere(signed_rank_w_ties == signed_rank_w_ties[i]).flatten().shape[0])
        if same_rank_n > 1:
            std_correction += ((same_rank_n**3) - same_rank_n) / 2
    std = np.sqrt(((n * (n + 1)) * ((2 * n) + 1) - std_correction) / 24)
    W = np.min((t_plus, t_minus))
    z = (W - u_w) / std
    r = z / np.sqrt(n)
    return z, r


@njit("(float32[:], int64,)")
def mad_median_rule(data: np.ndarray, k: int) -> np.ndarray:
    """
    Detects outliers in the given data using the Median Absolute Deviation (MAD) rule.
    Returns a 1D array of size `data.shape[0]`, where `1` represents an outlier and `0`
    represents an inlier.

    .. seealso::
       :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_descriptive_statistics`
       :func:`simba.mixins.statistics_mixin.Statistics.sliding_mad_median_rule`

    :param np.ndarray data: A 1-dimensional array of numerical values to check for outliers.
    :param int k: The multiplier for the MAD threshold. Higher values make the rule less sensitive to deviations from the median.
    :returns: A 1D binary array of the same length as `data`, where each element is `1` if the corresponding element in `data` is classified as an outlier, and `0` otherwise.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 600, (9000000,)).astype(np.float32)
    >>> mad_median_rule(data=data, k=1)
    """

    median = np.median(data)
    mad = np.median(np.abs(data - median))
    threshold = k * mad
    outliers = np.abs(data - median) > threshold
    return outliers * 1

@njit("(float32[:], int64, float64[:], float64)")
def sliding_mad_median_rule(data: np.ndarray, k: int, time_windows: np.ndarray, fps: float) -> np.ndarray:
    """
    Count the number of outliers in a sliding time-window using the MAD-Median Rule.
    The MAD-Median Rule is a robust method for outlier detection. It calculates the median absolute deviation (MAD)
    and uses it to identify outliers based on a threshold defined as k times the MAD.


    .. seealso::
       For alternative method, see :func:`simba.mixins.timeseries_features_mixin.TimeseriesFeatureMixin.sliding_descriptive_statistics`
       For single dataset, use :func:`simba.mixins.statistics_mixin.Statistics.mad_median_rule`

    :param np.ndarray data: 1D numerical array representing feature.
    :param int k: The outlier threshold defined as k * median absolute deviation in each time window.
    :param np.ndarray time_windows: 1D array of time window sizes in seconds.
    :param float fps: The frequency of the signal.
    :return: Array of size (data.shape[0], time_windows.shape[0]) with counts if outliers detected.
    :rtype: np.ndarray

    :example:
    >>> data = np.random.randint(0, 50, (50000,)).astype(np.float32)
    >>> sliding_mad_median_rule(data=data, k=2, time_windows=np.array([20.0]), fps=1.0)
    """
    results = np.full((data.shape[0], time_windows.shape[0]), -1)
    for cnt, time_window in enumerate(time_windows):
        w = int(fps * time_window)
        for i in range(w, data.shape[0] + 1, 1):
            w_data = data[i - w : i]
            median = np.median(w_data)
            mad = np.median(np.abs(w_data - median))
            threshold = k * mad
            outliers = np.abs(w_data - median) > threshold
            results[i - 1][cnt] = np.sum(outliers * 1)
    return results

@njit("(float32[:], float64, float64)")
def sliding_iqr(x: np.ndarray, window_size: float, sample_rate: float) -> np.ndarray:
    """
    Compute the sliding interquartile range (IQR) for a 1D array of feature values.
    :param ndarray x: 1D array representing the feature values for which the IQR will be calculated.
    :param float window_size: Size of the sliding window, in seconds.  This value determines how many samples are included in each window.
    :param float sample_rate: The sampling rate in samples per second, e.g., fps.
    :returns : Sliding IQR values
    :rtype: np.ndarray

    :references:
        .. [1] Hession, Leinani E., Gautam S. Sabnis, Gary A. Churchill, and Vivek Kumar. “A Machine-Vision-Based Frailty Index for Mice.” Nature Aging 2, no. 8 (August 16, 2022): 756–66. https://doi.org/10.1038/s43587-022-00266-0.

    :example:
    >>> data = np.random.randint(0, 50, (90,)).astype(np.float32)
    >>> window_size = 0.5
    >>> sliding_iqr(x=data, window_size=0.5, sample_rate=10.0)
    """
    frm_win = max(1, int(window_size * sample_rate))
    results = np.full(shape=(x.shape[0],), dtype=np.float32, fill_value=-1.0)
    for r in range(frm_win, x.shape[0] + 1):
        sorted_sample = np.sort(x[r - frm_win:r])
        lower_idx = sorted_sample.shape[0] // 4
        upper_idx = (3 * sorted_sample.shape[0]) // 4
        lower_val = sorted_sample[lower_idx]
        upper_val = sorted_sample[upper_idx]
        results[r - 1] = upper_val - lower_val
    return results

def one_way_anova_scipy(x: np.ndarray,
                        y: np.ndarray,
                        variable_names: List[str],
                        x_name: str = '',
                        y_name: str = '') -> pd.DataFrame:
    """
    Compute one-way ANOVAs comparing each column (axis 1) on two arrays.
    .. notes::
       Use for computing and presenting aggregate statistics. Not suitable for featurization.
    .. seealso::
       For featurization instead use :func:`simba.mixins.statistics_mixin.Statistics.rolling_one_way_anova` or
       :func:`simba.mixins.statistics_mixin.Statistics.one_way_anova`
    :param np.ndarray x: First 2d array with observations rowwise and variables columnwise.
    :param np.ndarray y: Second 2d array with observations rowwise and variables columnwise. Must be same number of columns as x.
    :param List[str, ...] variable_names: Names of columnwise variable names. Same length as number of data columns.
    :param str x_name: Name of the first group (x).
    :param str y_name: Name of the second group (y).
    :return: Dataframe with one row per column representing the ANOVA F-statistic and P-values comparing the variables between x and y.
    :rtype: pd.DataFrame
    """
    check_valid_array(data=x, source=f'{one_way_anova_scipy.__name__} x', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{one_way_anova_scipy.__name__} y', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_1_shape=(x.shape[1],))
    check_str(name=f'{one_way_anova_scipy.__name__} x_name', value=x_name, allow_blank=True)
    check_str(name=f'{one_way_anova_scipy.__name__} y_name', value=y_name, allow_blank=True)
    check_valid_lst(source=f'{one_way_anova_scipy.__name__} variable_names', data=variable_names, valid_dtypes=(str,), exact_len=x.shape[1])
    results = pd.DataFrame(variable_names, columns=['FEATURE'])
    results[['GROUP_1', 'GROUP_2']] = x_name, y_name
    results['F-STATISTIC'], results['P-VALUE'] = stats.f_oneway(x, y)
    results['P-VALUE'] = results['P-VALUE'].round(8)
    return results

def kruskal_scipy(x: np.ndarray,
                  y: np.ndarray,
                  variable_names: List[str],
                  x_name: str = '',
                  y_name: str = '') -> pd.DataFrame:
    """
    Compute Kruskal-Wallis comparing each column (axis 1) on two arrays.

    .. notes::
       Use for computing and presenting aggregate statistics. Not suitable for featurization.

    .. seealso::
       For featurization instead use :func:`simba.mixins.statistics_mixin.Statistics.kruskal_wallis`

    :param np.ndarray x: First 2d array with observations rowwise and variables columnwise.
    :param np.ndarray y: Second 2d array with observations rowwise and variables columnwise. Must be same number of columns as x.
    :param List[str, ...] variable_names: Names of columnwise variable names. Same length as number of data columns.
    :param str x_name: Name of the first group (x).
    :param str y_name: Name of the second group (y).
    :return: Dataframe with one row per column representing the Kruskal-Wallis statistic and P-values comparing the variables between x and y.
    :rtype: pd.DataFrame

    """
    check_valid_array(data=x, source=f'{kruskal_scipy.__name__} x', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, source=f'{kruskal_scipy.__name__} y', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_1_shape=(x.shape[1],))
    check_str(name=f'{kruskal_scipy.__name__} x_name', value=x_name, allow_blank=True)
    check_str(name=f'{kruskal_scipy.__name__} y_name', value=y_name, allow_blank=True)
    check_valid_lst(source=f'{kruskal_scipy.__name__} variable_names', data=variable_names, valid_dtypes=(str,), exact_len=x.shape[1])
    results = pd.DataFrame(variable_names, columns=['FEATURE'])
    results[['GROUP_1', 'GROUP_2']] = x_name, y_name
    results['STATISTIC'], results['P-VALUE'] = stats.kruskal(x, y)
    results['P-VALUE'] = results['P-VALUE'].round(8)
    return results

def pairwise_tukeyhsd_scipy(data: np.ndarray,
                            group: np.ndarray,
                            variable_names: List[str],
                            verbose: bool = False) -> pd.DataFrame:
    """
    Compute pairwise grouped Tukey-HSD tests.

    .. notes::
       Use for computing and presenting aggregate statistics. Not suitable for featurization.

    :param np.ndarray data: 2D array  with observations rowwise (axis 0) and features columnwise (axis 1)
    :param np.ndarray group: 1D array with the same number of observations as rows in ``data`` containing the group for each sample.
    :param List[str, ...] variable_names: Names of columnwise variable names. Same length as number of data columns.
    :return: Dataframe comparing each group for each variable.
    :rtype: pd.DataFrame
    """
    check_valid_array(data=data, source=f'{pairwise_tukeyhsd_scipy.__name__} data', accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=group, source=f'{pairwise_tukeyhsd_scipy.__name__} group', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=(data.shape[0],))
    check_valid_lst(source=f'{pairwise_tukeyhsd_scipy.__name__} variable_names', data=variable_names, valid_dtypes=(str,), exact_len=data.shape[1])
    results = []
    for var in range(data.shape[1]):
        if verbose:
            print(f'Computing Tukey HSD for variable {var+1}/{data.shape[1]}...')
        tukey_data = pairwise_tukeyhsd(data[:, var], group)
        df = pd.DataFrame(data=tukey_data._results_table.data[1:], columns=tukey_data._results_table.data[0])
        df['P-VALUE'] = psturng(np.abs(tukey_data.meandiffs / tukey_data.std_pairs), len(tukey_data.groupsunique), tukey_data.df_total)
        df['FEATURE'] = variable_names[var]
        results.append(df)
    return pd.concat(results, axis=0)