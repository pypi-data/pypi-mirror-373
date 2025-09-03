import os
from typing import Union, List, Tuple
import pandas as pd
import numpy as np
from simba.utils.enums import Formats
from simba.utils.checks import check_valid_boolean
from simba.utils.read_write import find_files_of_filetypes_in_directory, check_file_exist_and_readable, check_valid_dataframe, write_pickle, read_sleap_csv
from simba.mixins.geometry_mixin import GeometryMixin

TRACK = 'track'
FRAME_IDX = 'frame_idx'

class Sleap2Bbox():

    """

    :example:
    >>> bbox_transpose = Sleap2Bbox(data_dir=r'D:\ares\data\ant')
    >>> bbox_transpose.run()
    >>> bbox_transpose.save()
    """

    def __init__(self,
                 data_dir: Union[str, os.PathLike],
                 obb: bool = False):

        self.data_paths = find_files_of_filetypes_in_directory(directory=data_dir, extensions=['.csv'], raise_error=True, as_dict=True)
        check_valid_boolean(value=obb, source=f'{self.__class__.__name__} obb', raise_error=True)


    def run(self):
        for file_cnt, (file_name, file_path) in enumerate(self.data_paths.items()):
            df, bp_names, bp_headers = read_sleap_csv(file_path=file_path)
            frm_cnt = df[FRAME_IDX].max()
            dfs = [track for _, track in df.groupby(TRACK)]
            self.results = {}
            for track_cnt, track_df in enumerate(dfs):
                print(track_cnt)
                self.results[track_cnt] = {k: None for k in range(frm_cnt+1)}
                frm_idx, bp_data = list(track_df[FRAME_IDX]), track_df[bp_headers].clip(lower=0)
                bp_data = bp_data.values.reshape(len(bp_data), len(bp_names), 2)
                geometries = GeometryMixin().multiframe_bodyparts_to_polygon(data=bp_data, core_cnt=23, verbose=False, parallel_offset=40)
                geometries = GeometryMixin().multiframe_minimum_rotated_rectangle(shapes=geometries, core_cnt=10, verbose=False)
                self.results[track_cnt].update({k: v for (k, v) in zip(frm_idx, geometries)})

    def save(self):
        write_pickle(data=self.results, save_path=r'D:\ares\data\termite_2\termite_2_geometries.pickle')

bbox_transpose = Sleap2Bbox(data_dir=r"D:\ares\data\termite_2")
bbox_transpose.run()
bbox_transpose.save()