import pandas as pd

from simba.utils.checks import check_valid_array, check_float
from simba.utils.enums import Formats
import numpy as np


def fft_lowpass_filter(data: np.ndarray, cut_off: float = 0.1) -> np.ndarray:
    """
    Apply FFT-based lowpass filter to 1D or 2D data.

    :param np.ndarray data: Input data array (1D or 2D)
    :param float cut_off: Cutoff frequency as fraction of Nyquist frequency (0 < cut_off < 1)
    :return np.ndarray: Filtered data with same shape and dtype as input

    :example:
    >>> from simba.utils.read_write import read_df
    >>> IN_PATH = r"C:\troubleshooting\RAT_NOR\project_folder\csv\outlier_corrected_movement_location\2022-06-20_NOB_DOT_4.csv"
    >>> OUT_PATH = r"C:\troubleshooting\RAT_NOR\project_folder\csv\outlier_corrected_movement_location\2022-06-20_NOB_DOT_4_filtered.csv"
    >>> df = read_df(file_path=IN_PATH)
    >>> data = df.values
    >>> x = fft_lowpass_filter(data=data, cut_off=0.1)
    """

    check_valid_array(data=data, source=f'{fft_lowpass_filter.__name__} data', accepted_ndims=(1, 2), accepted_dtypes=Formats.NUMERIC_DTYPES.value, raise_error=True)
    check_float(name=f'{fft_lowpass_filter.__name__} cut_off', value=cut_off, min_value=10e-6, max_value=1.0 - 1e-9)
    ndim = data.ndim

    data_work = data.astype(np.float64)
    results = np.zeros_like(data_work)

    if ndim == 1:
        data_work = data_work.reshape(-1, 1)
        results = results.reshape(-1, 1)

    mask = np.fft.rfftfreq(data_work.shape[0]) < cut_off
    for dim in range(data_work.shape[1]):
        column_data = data_work[:, dim].copy()
        fft_vals = np.fft.rfft(column_data)
        fft_vals[~mask] = 0
        reconstructed = np.fft.irfft(fft_vals, n=data_work.shape[0])
        results[:, dim] = reconstructed

    if ndim == 1:
        results = results.flatten()

    return results.astype(data.dtype)






# from simba.utils.read_write import read_df
#
# IN_PATH = r"C:\troubleshooting\RAT_NOR\project_folder\csv\outlier_corrected_movement_location\2022-06-20_NOB_DOT_4.csv"
# OUT_PATH = r"C:\troubleshooting\RAT_NOR\project_folder\csv\outlier_corrected_movement_location\2022-06-20_NOB_DOT_4_filtered.csv"
#
# df = read_df(file_path=IN_PATH)
# data = df.values
# x = fft_lowpass_filter(data=data, cut_off=0.1)
# df = pd.DataFrame(data=x, columns=df.columns)
# df.to_csv(OUT_PATH)