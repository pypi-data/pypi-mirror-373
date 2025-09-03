import base64
import io
import itertools
import json
import os
import random
from copy import copy, deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple, Union, List

import pandas as pd
from PIL import Image

try:
    from typing import Literal
except:
    from typing_extensions import Literal

import cv2
import numpy as np
import yaml
#from pycocotools import mask
from shapely.geometry import Polygon

from simba.mixins.config_reader import ConfigReader
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.image_mixin import ImageMixin
from simba.utils.checks import (check_file_exist_and_readable, check_float,
                                check_if_dir_exists,
                                check_if_keys_exist_in_dict,
                                check_if_valid_img, check_int, check_str,
                                check_valid_array, check_valid_boolean,
                                check_valid_dataframe, check_valid_dict,
                                check_valid_tuple, check_instance)
from simba.utils.enums import Formats, Options
from simba.utils.errors import (FaultyTrainingSetError, InvalidInputError,
                                NoFilesFoundError)
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (copy_files_to_directory, create_directory,
                                    find_files_of_filetypes_in_directory,
                                    find_video_of_file, get_fn_ext,
                                    get_video_meta_data, read_df,
                                    read_frm_of_video, read_img, read_json,
                                    read_roi_data, save_json, write_pickle, recursive_file_search)
from simba.third_party_label_appenders.converters import arr_to_b64



def dlc_to_labelme(dlc_dir: Union[str, os.PathLike],
                   save_dir: Union[str, os.PathLike],
                   labelme_version: Optional[str] = '5.3.1',
                   flags: Optional[Dict[Any, Any]] = None,
                   verbose: Optional[bool] = True) -> None:

    """
    Convert a folder of DLC annotations into labelme json format.

    :param Union[str, os.PathLike] dlc_dir: Folder with DLC annotations. I.e., directory inside
    :param Union[str, os.PathLike] save_dir: Directory to where to save the labelme json files.
    :param Optional[str] labelme_version: Version number encoded in the json files.
    :param Optional[Dict[Any, Any] flags: Flags included in the json files.
    :param Optional[bool] verbose: If True, prints progress.
    :return: None

    :example:
    >>> dlc_to_labelme(dlc_dir="D:\TS_DLC\labeled-data\ts_annotations", save_dir="C:\troubleshooting\coco_data\labels\test")
    >>> dlc_to_labelme(dlc_dir=r'D:\rat_resident_intruder\dlc_data\WIN_20190816081353', save_dir=r'D:\rat_resident_intruder\labelme')
    """

    timer = SimbaTimer(start=True)
    check_if_dir_exists(dlc_dir, source=f'{dlc_to_labelme.__name__} dlc_dir')
    check_if_dir_exists(save_dir, source=f'{dlc_to_labelme.__name__} save_dir')
    check_valid_boolean(value=verbose, source=f'{dlc_to_labelme.__name__} verbose')
    collected_data_path = recursive_file_search(directory=dlc_dir, substrings='CollectedData', extensions='csv', raise_error=True)
    version = labelme_version
    if flags is not None:
        check_instance(source=f'{dlc_to_labelme.__name__} flags', instance=flags, accepted_types=(dict,))
    flags = {} if flags is None else {}
    body_parts_per_file, filecnt = {}, 0
    for file_cnt, file_path in enumerate(collected_data_path):
        file_dir = os.path.dirname(file_path)
        video_name = os.path.basename(os.path.dirname(file_path))
        body_part_headers = ['image']
        annotation_data = pd.read_csv(file_path, header=[0, 1, 2])
        body_parts = []
        for i in annotation_data.columns[1:]:
            if 'unnamed:' not in i[1].lower() and i[1] not in body_parts:
                body_parts.append(i[1])
        for i in body_parts:
            body_part_headers.append(f'{i}_x'); body_part_headers.append(f'{i}_y')
        body_parts_per_file[file_path] = body_part_headers
        annotation_data.columns = body_part_headers
        for cnt, (idx, idx_data) in enumerate(annotation_data.iterrows()):
            if verbose:
                print(f'Processing image {cnt + 1}/{len(annotation_data)}... (video {file_cnt+1}/{len(collected_data_path)} ({video_name}))')
            _, img_name, ext = get_fn_ext(filepath=idx_data['image'])
            video_img_name = f'{video_name}.{img_name}'
            img_path = os.path.join(file_dir, os.path.join(f'{img_name}{ext}'))
            check_file_exist_and_readable(file_path=img_path)
            img = read_img(img_path=img_path)
            idx_data = idx_data.to_dict()
            shapes = []
            for bp_name in body_parts:
                img_shapes = {'label': bp_name,
                              'points': [idx_data[f'{bp_name}_x'], idx_data[f'{bp_name}_y']],
                              'group_id': None,
                              'description': "",
                              'shape_type': 'point',
                              'flags': {}}
                shapes.append(img_shapes)
            out = {"version": version,
                   'flags': flags,
                   'shapes': shapes,
                   'imagePath': img_path,
                   'imageData': arr_to_b64(img),
                   'imageHeight': img.shape[0],
                   'imageWidth': img.shape[1]}
            save_path = os.path.join(save_dir, f'{video_img_name}.json')
            with open(save_path, "w") as f:
                json.dump(out, f)
            filecnt += 1
    timer.stop_timer()
    if verbose:
        stdout_success(f'Labelme data for {filecnt} image(s) saved in {save_dir} directory', elapsed_time=timer.elapsed_time_str)




