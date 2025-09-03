
import os
from pathlib import Path
from typing import Dict, Optional, Union
import pandas as pd
import numpy as np

from simba.mixins.config_reader import ConfigReader
from simba.mixins.plotting_mixin import PlottingMixin
from simba.utils.checks import (check_instance, check_int, check_str)
from simba.utils.data import create_color_palette
from simba.utils.enums import Options
from simba.utils.errors import CountError, InvalidFilepathError
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (find_files_of_filetypes_in_directory, get_fn_ext, get_video_meta_data, read_df)
from simba.utils.warnings import FrameRangeWarning
from simba.data_processors.cuda.image import pose_plotter

class PosePlotterGPU():
    """
    Create pose-estimation visualizations from data within a SimBA project folder.

    :param str in_directory: Path to SimBA project directory containing pose-estimation data in parquet or CSV format.
    :param str out_directory: Directory to where to save the pose-estimation videos.
    :param int Size of the circles denoting the location of the pose-estimated body-parts.
    :param Optional[dict] clr_attr: Python dict where animals are keys and color attributes values. E.g., {'Animal_1':  (255, 107, 198)}. If None, random palettes will be used.

    .. image:: _static/img/pose_plotter.png
       :width: 600
       :align: center

    :example:
    >>> test = PosePlotterMultiProcess(in_dir='project_folder/csv/input_csv', out_dir='/project_folder/test_viz', circle_size=10, core_cnt=1, color_settings={'Animal_1':  'Green', 'Animal_2':  'Red'})
    >>> test.run()
    """

    def __init__(self,
                 data_path: Union[str, os.PathLike],
                 out_dir: Optional[Union[str, os.PathLike]] = None,
                 palettes: Optional[Dict[str, str]] = None,
                 circle_size: Optional[int] = None,
                 sample_time: Optional[int] = None) -> None:

        if os.path.isdir(data_path):
            config_path = os.path.join(Path(data_path).parents[1], 'project_config.ini')
        elif os.path.isfile(data_path):
            config_path = os.path.join(Path(data_path).parents[2], 'project_config.ini')
        else:
            raise InvalidFilepathError(msg=f'{data_path} not not a valid file or directory path.', source=self.__class__.__name__)
        if not os.path.isfile(config_path):
            raise InvalidFilepathError(msg=f'When visualizing pose-estimation, select an input sub-directory of the project_folder/csv folder OR file in the project_folder/csv/ANY_FOLDER directory. {data_path} does not meet these requirements and therefore SimBA cant locate the project_config.ini (expected at {config_path}', source=self.__class__.__name__)
        self.config = ConfigReader(config_path=config_path, read_video_info=False, create_logger=False)
        if os.path.isdir(data_path):
            files_found = find_files_of_filetypes_in_directory(directory=data_path, extensions=[f'.{self.config.file_type}'], raise_error=True)
        else:
            files_found = [data_path]
        self.animal_bp_dict = self.config.body_parts_lst
        if circle_size is not None:
            check_int(name='circle_size', value=circle_size, min_value=1)
        self.color_dict = {}
        if palettes is not None:
            check_instance(source=self.__class__.__name__, instance=palettes, accepted_types=(dict,))
            if len(list(palettes.keys())) != self.config.animal_cnt:
                raise CountError(msg=f'The number of color palettes ({(len(list(palettes.keys())))}) spedificed is not the same as the number of animals ({(self.config.animal_cnt)}) in the SimBA project at {self.config.project_path}')
            for cnt, (k, v) in enumerate(palettes.items()):
                check_str(name='palette', value=v, options=Options.PALETTE_OPTIONS_CATEGORICAL.value)
                self.color_dict[cnt] = create_color_palette(pallete_name=v, increments=len(self.config.body_parts_lst))
        else:
            for cnt, (k, v) in enumerate(self.config.animal_bp_dict.items()):
                self.color_dict[cnt] = self.config.animal_bp_dict[k]["colors"]
        if sample_time is not None:
            check_int(name='sample_time', value=sample_time, min_value=1)
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(files_found[0]), f'pose_videos_{self.config.datetime}')
        self.circle_size, self.out_dir, self.sample_time = (circle_size, out_dir, sample_time)
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.data = {}
        for file in files_found: self.data[file] = self.config.find_video_of_file(video_dir=self.config.video_dir, filename=get_fn_ext(file)[1])


    def run(self):
        for file_cnt, (pose_path, video_path) in enumerate(self.data.items()):
            video_timer = SimbaTimer(start=True)
            video_name = get_fn_ext(pose_path)[1]
            self.temp_folder = os.path.join(self.out_dir, video_name, "temp")
            if os.path.exists(self.temp_folder):
                self.config.remove_a_folder(self.temp_folder)
            os.makedirs(self.temp_folder, exist_ok=True)
            save_video_path = os.path.join(self.out_dir, f"{video_name}.mp4")
            pose_df = read_df(file_path=pose_path, file_type=self.config.file_type, check_multiindex=True)
            video_meta_data = get_video_meta_data(video_path=video_path)
            if self.circle_size is None:
                video_circle_size = PlottingMixin().get_optimal_circle_size(frame_size=(int(video_meta_data['width']), int(video_meta_data['height'])), circle_frame_ratio=70)
            else:
                video_circle_size = self.circle_size
            if (self.sample_time is None) and (video_meta_data["frame_count"] != len(pose_df)):
                FrameRangeWarning(
                    msg=f'The video {video_name} has pose-estimation data for {len(pose_df)} frames, but the video has {video_meta_data["frame_count"]} frames. Ensure the data and video has an equal number of frames.',
                    source=self.__class__.__name__)
            elif isinstance(self.sample_time, int):
                sample_frm_cnt = int(video_meta_data["fps"] * self.sample_time)
                if sample_frm_cnt > len(pose_df): sample_frm_cnt = len(pose_df)
                pose_df = pose_df.iloc[0:sample_frm_cnt]
            if 'input_csv' in os.path.dirname(pose_path):
                pose_df = self.config.insert_column_headers_for_outlier_correction(data_df=pose_df, new_headers=self.config.bp_headers, filepath=pose_path)
            pose_df = (pose_df.apply(pd.to_numeric, errors="coerce").fillna(0).reset_index(drop=True))
            pose_df = pose_df[[x for x in self.config.bp_col_names if not x.endswith('_p')]]
            pose_arr = pose_df.values.reshape(len(pose_df), int(len(pose_df.columns) / 2), 2).astype(np.int32)
            print(pose_arr)



            pose_plotter(data=pose_arr, video_path=video_path, save_path=save_video_path, circle_size=video_circle_size, batch_size=2000)
            #
            # def pose_plotter(data: Union[str, os.PathLike, np.ndarray],
            #                  video_path: Union[str, os.PathLike],
            #                  save_path: Union[str, os.PathLike],
            #                  circle_size: Optional[int] = None,
            #                  colors: Optional[str] = 'Set1',
            #                  batch_size: int = 750,
            #                  verbose: bool = True) -> None:


# plotter = PosePlotterGPU(data_path=r'/mnt/c/troubleshooting/mitra/project_folder/csv/input_csv/501_MA142_Gi_CNO_0521.csv')
# plotter.run()