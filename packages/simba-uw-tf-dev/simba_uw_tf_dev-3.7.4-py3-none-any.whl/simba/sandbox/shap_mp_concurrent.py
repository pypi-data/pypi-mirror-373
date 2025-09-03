__author__ = "Simon Nilsson"

import warnings

warnings.filterwarnings("ignore")
import ast
import concurrent
import configparser
import os
import pickle
import platform
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from copy import deepcopy
from datetime import datetime
from itertools import repeat
from json import loads
from subprocess import call

import cv2
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE
from numba import njit, typed, types
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.inspection import partial_dependence, permutation_importance
from sklearn.metrics import classification_report, precision_recall_curve
from sklearn.model_selection import ShuffleSplit, learning_curve
from sklearn.preprocessing import (MinMaxScaler, QuantileTransformer,
                                   StandardScaler)
from sklearn.tree import export_graphviz
from sklearn.utils import parallel_backend
from tabulate import tabulate
from simba.mixins.train_model_mixin import TrainModelMixin
from simba.mixins import cuRF

try:
    from dtreeviz.trees import dtreeviz, tree
except:
    from dtreeviz import dtreeviz
    from dtreeviz.trees import tree

import functools
import multiprocessing
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt

try:
    from typing import Literal
except:
    from typing_extensions import Literal

from simba.mixins.plotting_mixin import PlottingMixin
from simba.plotting.shap_agg_stats_visualizer import \
    ShapAggregateStatisticsCalculator
from simba.ui.tkinter_functions import TwoOptionQuestionPopUp
from simba.utils.checks import (check_all_dfs_in_list_has_same_cols,
                                check_file_exist_and_readable,
                                check_filepaths_in_iterable_exist, check_float,
                                check_if_dir_exists, check_if_valid_input,
                                check_instance, check_int, check_str,
                                check_that_column_exist, check_valid_array,
                                check_valid_boolean, check_valid_dataframe,
                                check_valid_lst)
from simba.utils.data import (detect_bouts, detect_bouts_multiclass,
                              get_library_version)
from simba.utils.enums import (OS, ConfigKey, Defaults, Dtypes, Formats,
                               Methods, MLParamKeys, Options)
from simba.utils.errors import (ClassifierInferenceError, CorruptedFileError,
                                DataHeaderError, FaultyTrainingSetError,
                                FeatureNumberMismatchError, InvalidInputError,
                                MissingColumnsError, NoDataError,
                                SamplingError, SimBAModuleNotFoundError)
from simba.utils.lookups import get_meta_data_file_headers
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (find_core_cnt, get_fn_ext,
                                    get_memory_usage_of_df, get_pkg_version,
                                    read_config_entry, read_df, read_meta_file,
                                    str_2_bool)
from simba.utils.warnings import (GPUToolsWarning, MissingUserInputWarning,
                                  MultiProcessingFailedWarning,
                                  NoModuleWarning, NotEnoughDataWarning,
                                  SamplingWarning, ShapWarning)

plt.switch_backend("agg")

CUML = 'cuml'
SKLEARN = 'sklearn'



def _create_shap_mp_helper_concurren(data: Tuple[int, pd.DataFrame],
                                     explainer: shap.TreeExplainer,
                                     clf_name: str,
                                     verbose: bool) -> Tuple[np.ndarray, int]:
    if verbose:
        print(f'Processing SHAP core batch {data[0] + 1}... ({len(data[1])} observations)')
    _ = data[1].pop(clf_name).values.reshape(-1, 1)
    shap_batch_results = np.full(shape=(len(data[1]), len(data[1].columns)), fill_value=np.nan, dtype=np.float32)
    for idx in range(len(data[1])):
        timer = SimbaTimer(start=True)
        obs = data[1].iloc[idx, :].values
        shap_batch_results[idx] = explainer.shap_values(obs, check_additivity=False)[1]
        timer.stop_timer()
        if verbose:
            print(f'SHAP frame complete (core batch: {data[0] + 1}, core batch frame: {idx+1}/{len(data[1])}, frame processing time: {timer.elapsed_time_str}s)')
    return shap_batch_results, data[0]

def create_shap_log_concurrent_mp(rf_clf: Union[RandomForestClassifier, str, os.PathLike],
                                  x: Union[pd.DataFrame, np.ndarray],
                                  y: Union[pd.DataFrame, pd.Series, np.ndarray],
                                  x_names: List[str],
                                  clf_name: str,
                                  cnt_present: int,
                                  cnt_absent: int,
                                  core_cnt: int = -1,
                                  chunk_size: int = 100,
                                  verbose: bool = True,
                                  save_dir: Optional[Union[str, os.PathLike]] = None,
                                  save_file_suffix: Optional[int] = None,
                                  plot: bool = False) -> Union[None, Tuple[pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame], np.ndarray]]:
    """
    Compute SHAP values using multiprocessing.

    .. seealso::
       `Documentation <https://github.com/sgoldenlab/simba/blob/master/docs/Scenario1.md#train-predictive-classifiers-settings>`_
        For single-core solution, see :func:`~simba.mixins.train_model_mixins.TrainModelMixin.create_shap_log`
        For GPU method, see :func:`~simba.data_processors.cuda.create_shap_log.create_shap_log`

    .. image:: _static/img/shap.png
       :width: 400
       :align: center

    :param Union[RandomForestClassifier, str, os.PathLike] rf_clf: Fitted sklearn random forest classifier, or pat to fitted, pickled sklearn random forest classifier.
    :param Union[pd.DataFrame, np.ndarray] x: Test features.
    :param Union[pd.DataFrame, pd.Series, np.ndarray] y_df: Test target.
    :param List[str] x_names: Feature names.
    :param str clf_name: Classifier name.
    :param int cnt_present: Number of behavior-present frames to calculate SHAP values for.
    :param int cnt_absent: Number of behavior-absent frames to calculate SHAP values for.
    :param int chunk_size: How many observations to process in each chunk. Increase value for faster processing if your memory allows.
    :param bool verbose: If True, prints progress.
    :param Optional[Union[str, os.PathLike]] save_dir: Optional directory where to store the results. If None, then the results are returned.
    :param Optional[int] save_file_suffix: Optional suffix to add to the shap output filenames. Useful for gridsearches and multiple shap data output files are to-be stored in the same `save_dir`.
    :param bool plot: If True, create SHAP aggregation and plots.

    :example:
    >>> CONFIG_PATH = r"C:\troubleshooting\mitra\project_folder\project_config.ini"
    >>> RF_PATH = r"C:\troubleshooting\mitra\models\validations\straub_tail_5_new\straub_tail_5.sav"
    >>> DATA_PATH = 'r"C:\troubleshooting\mitra\project_folder\csv\targets_inserted\new_straub\appended\501_MA142_Gi_CNO_0514.csv
    >>> config = ConfigReader(config_path=CONFIG_PATH)
    >>> df = read_df(file_path=DATA_PATH, file_type='csv')
    >>> y = df['straub_tail']
    >>> x = df.drop(['immobility', 'rearing', 'grooming', 'circling', 'shaking', 'lay-on-belly', 'straub_tail'], axis=1)
    >>> x = x.drop(config.bp_col_names, axis=1)
    >>> create_shap_log_mp(rf_clf=RF_PATH, x=x, y=y, x_names=list(x.columns), clf_name='straub_tail', cnt_absent=100, cnt_present=10, core_cnt=10)
    """

    check_instance(source=f'{create_shap_log_concurrent_mp.__name__} rf_clf', instance=rf_clf, accepted_types=(RandomForestClassifier, str, os.PathLike))
    if isinstance(rf_clf, str):
        rf_clf = TrainModelMixin().read_pickle(file_path=rf_clf)
    if SKLEARN in str(rf_clf.__module__).lower():
        timer = SimbaTimer(start=True)
        check_instance(source=f'{create_shap_log_concurrent_mp.__name__} x', instance=x, accepted_types=(np.ndarray, pd.DataFrame))
        if isinstance(x, pd.DataFrame):
            check_valid_dataframe(df=x, source=f'{create_shap_log_concurrent_mp.__name__} x', valid_dtypes=Formats.NUMERIC_DTYPES.value)
            x = x.values
        else:
            check_valid_array(data=x, source=f'{create_shap_log_concurrent_mp.__name__} x', accepted_ndims=(2,),  accepted_dtypes=Formats.NUMERIC_DTYPES.value)
        check_instance(source=f'{create_shap_log_concurrent_mp.__name__} y', instance=y, accepted_types=(np.ndarray, pd.Series, pd.DataFrame))
        if isinstance(y, pd.DataFrame):
            check_valid_dataframe(df=y, source=f'{create_shap_log_concurrent_mp.__name__} y', valid_dtypes=Formats.NUMERIC_DTYPES.value, max_axis_1=1)
            y = y.values
        else:
            if isinstance(y, pd.Series):
                y = y.values
        if save_dir is not None: check_if_dir_exists(in_dir=save_dir)
        if save_file_suffix is not None: check_int(name=f'{TrainModelMixin.create_shap_log_mp.__name__} save_file_no', value=save_file_suffix, min_value=0)
        check_valid_array(data=y, source=f'{create_shap_log_concurrent_mp.__name__} y', accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
        check_valid_lst(data=x_names, source=f'{create_shap_log_concurrent_mp.__name__} x_names', valid_dtypes=(str,), exact_len=x.shape[1])
        check_str(name=f'{create_shap_log_concurrent_mp.__name__} clf_name', value=clf_name)
        check_int(name=f'{create_shap_log_concurrent_mp.__name__} cnt_present', value=cnt_present, min_value=1)
        check_int(name=f'{create_shap_log_concurrent_mp.__name__} cnt_absent', value=cnt_absent, min_value=1)
        check_int(name=f'{create_shap_log_concurrent_mp.__name__} core_cnt', value=core_cnt, min_value=-1, unaccepted_vals=[0])
        check_int(name=f'{create_shap_log_concurrent_mp.__name__} chunk_size', value=chunk_size, min_value=1)
        check_int(name=f'{create_shap_log_concurrent_mp.__name__} core_cnt', value=chunk_size, min_value=-1, unaccepted_vals=[0])
        check_valid_boolean(value=[verbose], source=f'{create_shap_log_concurrent_mp.__name__} verbose')
        check_valid_boolean(value=[plot], source=f'{create_shap_log_concurrent_mp.__name__} plot')
        core_cnt = find_core_cnt()[0] if core_cnt == -1 or core_cnt > find_core_cnt()[0] else core_cnt
        df = pd.DataFrame(np.hstack((x, y.reshape(-1, 1))), columns=x_names + [clf_name])
        del x; del y
        present_df, absent_df = df[df[clf_name] == 1], df[df[clf_name] == 0]
        if len(present_df) == 0:
            raise NoDataError(msg=f'Cannot calculate SHAP values: no target PRESENT annotations detected for classifier {clf_name}.', source=create_shap_log_mp.__name__)
        elif len(absent_df) == 0:
            raise NoDataError(msg=f'Cannot calculate SHAP values: no target ABSENT annotations detected for classifier {clf_name}.', source=create_shap_log_mp.__name__)
        if len(present_df) < cnt_present:
            NotEnoughDataWarning(msg=f"Train data contains {len(present_df)} behavior-present annotations for classifier {clf_name}. This is less the number of frames you specified to calculate shap values for ({cnt_present}). SimBA will calculate shap scores for the {len(present_df)} behavior-present frames available", source=TrainModelMixin.create_shap_log_mp.__name__)
            cnt_present = len(present_df)
        if len(absent_df) < cnt_absent:
            NotEnoughDataWarning(msg=f"Train data contains {len(absent_df)} behavior-absent annotations for classifier {clf_name}. This is less the number of frames you specified to calculate shap values for ({cnt_absent}). SimBA will calculate shap scores for the {len(absent_df)} behavior-absent frames available", source=TrainModelMixin.create_shap_log_mp.__name__)
            cnt_absent = len(absent_df)
        shap_data = pd.concat([present_df.sample(cnt_present, replace=False), absent_df.sample(cnt_absent, replace=False)], axis=0).reset_index(drop=True)
        del df
        shap_data = np.array_split(shap_data, max(1, int(np.ceil(len(shap_data) / chunk_size))))
        shap_data = [(x, y) for x, y in enumerate(shap_data)]
        explainer = TrainModelMixin().define_tree_explainer(clf=rf_clf)
        expected_value = explainer.expected_value[1]
        shap_results, shap_raw = [], []
        out_shap_path, out_raw_path, img_save_path, df_save_paths, summary_dfs, img = None, None, None, None, None, None
        print(f"Computing {cnt_present + cnt_absent} SHAP values. Follow progress in OS terminal... (CORES: {core_cnt}, CHUNK SIZE: {chunk_size})")
        with concurrent.futures.ProcessPoolExecutor(max_workers=core_cnt) as executor:
            results = [executor.submit(_create_shap_mp_helper, data, explainer, clf_name,verbose) for data in shap_data]
            for result in concurrent.futures.as_completed(results):
                batch_shap, batch_id = result.result()
                batch_x, batch_y = shap_data[batch_id][1].drop(clf_name, axis=1), shap_data[batch_id][1][clf_name].values.reshape(-1, 1)
                batch_shap_sum = np.sum(batch_shap, axis=1).reshape(-1, 1)
                expected_arr = np.full((batch_shap.shape[0]), expected_value).reshape(-1, 1)
                batch_proba = TrainModelMixin().clf_predict_proba(clf=rf_clf, x_df=batch_x, model_name=clf_name).reshape(-1, 1)
                batch_shap_results = np.hstack((batch_x, expected_arr, batch_shap_sum + expected_value, batch_proba, batch_y)).astype(np.float32)
                shap_results.append(batch_shap_results)
                shap_raw.append(batch_x)
                if verbose: print(f"Completed SHAP care batch (Batch {batch_id+1 + 1}/{len(shap_data)})...")
        shap_df = pd.DataFrame(data=np.row_stack(shap_results), columns=list(x_names) + ["Expected_value", "Sum", "Prediction_probability", clf_name])
        raw_df = pd.DataFrame(data=np.row_stack(shap_raw), columns=list(x_names))
        if save_dir is not None:
            if save_file_suffix is not None:
                check_int(name=f'{TrainModelMixin.create_shap_log_mp.__name__} save_file_no', value=save_file_suffix, min_value=0)
                out_shap_path = os.path.join(save_dir, f"SHAP_values_{save_file_suffix}_{clf_name}.csv")
                out_raw_path = os.path.join(save_dir, f"RAW_SHAP_feature_values_{save_file_suffix}_{clf_name}.csv")
                df_save_paths = {'PRESENT': os.path.join(save_dir, f"SHAP_summary_{clf_name}_PRESENT_{save_file_suffix}.csv"), 'ABSENT': os.path.join(save_dir, f"SHAP_summary_{clf_name}_ABSENT_{save_file_suffix}.csv")}
                img_save_path = os.path.join(save_dir, f"SHAP_summary_line_graph_{clf_name}_{save_file_suffix}.png")
            else:
                out_shap_path = os.path.join(save_dir, f"SHAP_values_{clf_name}.csv")
                out_raw_path = os.path.join(save_dir, f"RAW_SHAP_feature_values_{clf_name}.csv")
                df_save_paths = {'PRESENT': os.path.join(save_dir, f"SHAP_summary_{clf_name}_PRESENT.csv"), 'ABSENT': os.path.join(save_dir, f"SHAP_summary_{clf_name}_ABSENT.csv")}
                img_save_path = os.path.join(save_dir, f"SHAP_summary_line_graph_{clf_name}.png")
            shap_df.to_csv(out_shap_path); raw_df.to_csv(out_raw_path)
        if plot:
            shap_computer = ShapAggregateStatisticsCalculator(classifier_name=clf_name, shap_df=shap_df, shap_baseline_value=int(expected_value * 100), save_dir=None)
            summary_dfs, img = shap_computer.run()
            if save_dir is not None:
                summary_dfs['PRESENT'].to_csv(df_save_paths['PRESENT'])
                summary_dfs['ABSENT'].to_csv(df_save_paths['ABSENT'])
                cv2.imwrite(img_save_path, img)
        timer.stop_timer()
        if save_dir and verbose:
            stdout_success(msg=f'SHAP data saved in {save_dir}', source=TrainModelMixin.create_shap_log_mp.__name__, elapsed_time=timer.elapsed_time_str)
        if not save_dir:
            return shap_df, raw_df, summary_dfs, img
    else:
        GPUToolsWarning(msg=f'Cannot compute SHAP scores using cuml random forest model. To compute SHAP scores, turn off cuda. Alternatively, for GPU solution, see simba.data_processors.cuda.create_shap_log.create_shap_log')


if __name__ == "__main__":
    from simba.utils.read_write import read_config_file
    from simba.mixins.config_reader import ConfigReader

    CONFIG_PATH = r"C:\troubleshooting\mitra\project_folder\project_config.ini"
    RF_PATH = r"C:\troubleshooting\mitra\models\validations\straub_tail_5_new\straub_tail_5.sav"
    DATA_PATH = r"C:\troubleshooting\mitra\project_folder\csv\targets_inserted\new_straub\appended\501_MA142_Gi_CNO_0514.csv"


    config = ConfigReader(config_path=CONFIG_PATH)
    df = read_df(file_path=DATA_PATH, file_type='csv')
    y = df['straub_tail']
    x = df.drop(['immobility', 'rearing', 'grooming', 'circling', 'shaking', 'lay-on-belly', 'straub_tail'], axis=1)
    x = x.drop(config.bp_col_names, axis=1)

    create_shap_log_mp(rf_clf=RF_PATH, x=x, y=y, x_names=list(x.columns), clf_name='straub_tail', cnt_absent=100, cnt_present=10, core_cnt=10)




#
# x.drop([config.])



# rf_clf: RandomForestClassifier,
#                        x: Union[pd.DataFrame, np.ndarray],
#                        y: Union[pd.DataFrame, pd.Series, np.ndarray],
#                        x_names: List[str],
#                        clf_name: str,
#                        cnt_present: int,
#                        cnt_absent: int,
#                        core_cnt: int = -1,
#                        chunk_size: int = 100,
#                        verbose: bool = True,
#                        save_dir: Optional[Union[str, os.PathLike]] = None,
#                        save_file_suffix: Optional[int] = None,
#                        plot: bool = False) -> Union[None, Tuple[pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame], np.ndarray]]: