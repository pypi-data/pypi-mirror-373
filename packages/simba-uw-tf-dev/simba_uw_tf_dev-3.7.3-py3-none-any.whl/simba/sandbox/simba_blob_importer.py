import os
from typing import Union, Optional
from copy import copy
import numpy as np
import pandas as pd

from simba.utils.checks import check_str, check_int, check_valid_dataframe, check_valid_boolean, check_if_dir_exists
from simba.mixins.config_reader import ConfigReader
from simba.utils.read_write import find_files_of_filetypes_in_directory, read_df, get_fn_ext, write_df, read_config_entry
from simba.utils.errors import NoFilesFoundError, InvalidInputError
from simba.utils.enums import Options, Formats, ConfigKey, Dtypes
from simba.data_processors.interpolate import Interpolate
from simba.data_processors.smoothing import Smoothing
from simba.utils.printing import stdout_success, SimbaTimer

REQUIRED_FIELDS = ['nose_x', 'nose_y', 'left_x', 'left_y', 'center_x', 'center_y', 'right_x', 'right_y', 'tail_x', 'tail_y']
BP_NAMES = ['nose', 'left', 'center', 'right', 'tail']

SIMBA_BLOB = 'simba_blob'


class SimBaBlobImporter(ConfigReader):

    """
    :example:
    >>> r = SimBaBlobImporter(config_path=r"C:\troubleshooting\simba_blob_project\project_folder\project_config.ini", data_path=r'C:\troubleshooting\simba_blob_project\data')
    >>> r.run()
    """

    def __init__(self,
                 config_path: Union[str, os.PathLike],
                 data_path: Union[str, os.PathLike],
                 save_dir: Optional[Union[str, os.PathLike]] = None,
                 smoothing_setting: Optional[str] = None,
                 smoothing_time: Optional[int] = None,
                 interpolation_settings: Optional[str] = None,
                 verbose: Optional[bool] = True):


        ConfigReader.__init__(self, config_path=config_path, read_video_info=False, create_logger=False)
        pose_config_name = self.read_config_entry(config=self.config, section=ConfigKey.CREATE_ENSEMBLE_SETTINGS.value, option=ConfigKey.POSE_SETTING.value, default_value=None, data_type=Dtypes.STR.value).strip()
        if pose_config_name != SIMBA_BLOB:
            raise InvalidInputError(msg=f'The project {config_path} is not a SimBA blob project. Cannot import SimBA blob data to a non SimBA blob project ({ConfigKey.POSE_SETTING.value}: {pose_config_name}, expected: {SIMBA_BLOB})', source=self.__class__.__name__)
        if os.path.isdir(data_path):
            self.data_paths = find_files_of_filetypes_in_directory(directory=data_path, extensions=['.csv'], raise_error=True)
        elif os.path.isfile(data_path):
            self.data_paths = [data_path]
        else:
            raise NoFilesFoundError(msg=f'{data_path} is not a valid file path or valid directory path', source=self.__class__.__name__)
        if interpolation_settings is not None:
            check_str(name=f'{self.__class__.__name__} interpolation_settings', value=interpolation_settings, options=Options.INTERPOLATION_OPTIONS_W_NONE.value)
            self.interpolation_type, self.interpolation_method = interpolation_settings.split(sep=':', maxsplit=2)
            self.interpolation_type, self.interpolation_method = self.interpolation_type.strip().lower(), self.interpolation_method.strip().lower()
        if smoothing_setting is not None:
            check_str(name=f'{self.__class__.__name__} smoothing_setting', value=smoothing_setting, options=('savitzky-golay', 'gaussian'))
            check_int(name=f'{self.__class__.__name__} smoothing_time', value=smoothing_time, min_value=1)
        check_valid_boolean(value=verbose, source=f'{self.__class__.__name__} verbose', raise_error=True)
        if save_dir is not None:
            check_if_dir_exists(in_dir=save_dir, source=f'{self.__class__.__name__} save_dir', raise_error=True)
        else:
            save_dir = copy(self.outlier_corrected_dir)
        self.interpolation_settings, self.smoothing_setting, self.smoothing_time = (interpolation_settings, smoothing_setting, smoothing_time)
        self.save_dir, self.verbose = save_dir, verbose

    def run(self):
        for file_cnt, file_path in enumerate(self.data_paths):
            file_timer = SimbaTimer(start=True)
            df = read_df(file_path=file_path, file_type='csv')
            df.columns = [x.strip().lower() for x in df.columns]
            video_name = get_fn_ext(filepath=file_path)[1]
            if self.verbose:
                print(f'Importing SimBA blob data for video {video_name}...')
            save_path = os.path.join(self.save_dir, f'{video_name}.csv')
            check_valid_dataframe(df=df, source=f'{self.__class__.__name__} {file_path}', valid_dtypes=Formats.NUMERIC_DTYPES.value, required_fields=REQUIRED_FIELDS)
            df = df[REQUIRED_FIELDS].astype(np.int32)
            df_out = pd.DataFrame()
            for i in range(0, df.shape[1], 2):
                df_out = pd.concat([df_out, df.iloc[:, i:i + 2], pd.DataFrame(1, index=df.index, columns=[f'{BP_NAMES[i//2]}_p'])], axis=1)
            del df
            write_df(df=df_out, file_type=self.file_type, save_path=save_path, multi_idx_header=True)
            if self.interpolation_settings is not None:
                interpolator = Interpolate(config_path=self.config_path, data_path=save_path, type=self.interpolation_type, method=self.interpolation_method, multi_index_df_headers=False, copy_originals=False)
                interpolator.run()
            if self.smoothing_setting is not None:
                smoother = Smoothing(config_path=self.config_path, data_path=save_path, time_window=self.smoothing_time, method=self.smoothing_setting, multi_index_df_headers=True, copy_originals=False)
                smoother.run()
            file_timer.stop_timer()
            print(f'Imported data for video {video_name} (elapsed time: {file_timer.elapsed_time}s)')
        self.timer.stop_timer()
        stdout_success(msg=f"{len(self.data_paths)} SimBA blob tracking files file(s) imported to the SimBA project {self.save_dir}", source=self.__class__.__name__, elapsed_time=self.timer.elapsed_time)

#
r = SimBaBlobImporter(config_path=r"C:\troubleshooting\simba_blob_project\project_folder\project_config.ini", data_path=r'C:\troubleshooting\simba_blob_project\data')
r.run()