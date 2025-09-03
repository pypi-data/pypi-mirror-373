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

from simba.third_party_label_appenders.converters import create_yolo_keypoint_yaml


def simba_rois_to_yolo(config_path: Optional[Union[str, os.PathLike]] = None,
                       roi_path: Optional[Union[str, os.PathLike]] = None,
                       video_dir: Optional[Union[str, os.PathLike]] = None,
                       save_dir: Optional[Union[str, os.PathLike]] = None,
                       roi_frm_cnt: Optional[int] = 10,
                       train_size: Optional[float] = 0.7,
                       obb: Optional[bool] = False,
                       greyscale: Optional[bool] = True,
                       verbose: Optional[bool] = False) -> None:
    """
    Converts SimBA roi definitions into annotations and images for training yolo network.

    :param Optional[Union[str, os.PathLike]] config_path: Optional path to the project config file in SimBA project.
    :param Optional[Union[str, os.PathLike]] roi_path: Path to the SimBA roi definitions .h5 file. If None, then the ``roi_coordinates_path`` of the project.
    :param Optional[Union[str, os.PathLike]] video_dir: Directory where to find the videos. If None, then the videos folder of the project.
    :param Optional[Union[str, os.PathLike]] save_dir: Directory where to save the labels and images. If None, then the logs folder of the project.
    :param Optional[int] roi_frm_cnt: Number of frames for each video to create bounding boxes for.
    :param float train_size: Proportion of frames randomly assigned to the training dataset. Value must be between 0.1 and 0.99. Default: 0.7.
    :param Optional[bool] obb: If True, created object-oriented yolo bounding boxes. Else, axis aligned yolo bounding boxes. Default False.
    :param Optional[bool] greyscale: If True, converts the images to greyscale if rgb. Default: True.
    :param Optional[bool] verbose: If True, prints progress. Default: False.
    :return: None

    :example I:
    >>> simba_rois_to_yolo(config_path=r"C:\troubleshooting\RAT_NOR\project_folder\project_config.ini")

    :example II:
    >>> simba_rois_to_yolo(config_path=r"C:\troubleshooting\RAT_NOR\project_folder\project_config.ini", save_dir=r"C:\troubleshooting\RAT_NOR\project_folder\logs\yolo", video_dir=r"C:\troubleshooting\RAT_NOR\project_folder\videos", roi_path=r"C:\troubleshooting\RAT_NOR\project_folder\logs\measures\ROI_definitions.h5")

    :example III:
    >>> simba_rois_to_yolo(video_dir=r"C:\troubleshooting\RAT_NOR\project_folder\videos", roi_path=r"C:\troubleshooting\RAT_NOR\project_folder\logs\measures\ROI_definitions.h5", save_dir=r'C:\troubleshooting\RAT_NOR\project_folder\yolo', verbose=True, roi_frm_cnt=20, obb=True)
    """

    timer = SimbaTimer(start=True)
    if roi_path is None or video_dir is None or save_dir is None:
        config = ConfigReader(config_path=config_path)
        roi_path = config.roi_coordinates_path
        video_dir = config.video_dir
        save_dir = config.logs_path
    check_int(name=f'{simba_rois_to_yolo.__name__} roi_frm_cnt', value=roi_frm_cnt, min_value=1)
    check_valid_boolean(value=verbose, source=f'{simba_rois_to_yolo.__name__} verbose')
    check_valid_boolean(value=greyscale, source=f'{simba_rois_to_yolo.__name__} greyscale')
    check_valid_boolean(value=obb, source=f'{simba_rois_to_yolo.__name__} obb')
    check_float(name=f'{simba_rois_to_yolo.__name__} train_size', min_value=0.001, max_value=0.9999, value=train_size, raise_error=True)
    check_if_dir_exists(in_dir=video_dir)
    roi_data = read_roi_data(roi_path=roi_path)
    roi_geometries = GeometryMixin.simba_roi_to_geometries(rectangles_df=roi_data[0], circles_df=roi_data[1], polygons_df=roi_data[2])[0]
    video_files = find_files_of_filetypes_in_directory(directory=video_dir, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value, raise_error=True, raise_warning=False, as_dict=True)
    sliced_roi_geometries = {k:v for k, v in roi_geometries.items() if k in video_files.keys()}
    if len(sliced_roi_geometries.keys()) == 0:
        raise NoFilesFoundError(msg=f'No video files for in {video_dir} directory for the videos represented in the {roi_path} file: {roi_geometries.keys()}', source=simba_rois_to_yolo.__name__)
    roi_geometries_rectangles = {}
    roi_ids, roi_cnt = {}, 0
    map_path = os.path.join(save_dir, 'map.yaml')
    img_dir, lbl_dir = os.path.join(save_dir, 'images'), os.path.join(save_dir, 'labels')
    img_train_dir, img_val_dir = os.path.join(img_dir, 'train'), os.path.join(img_dir, 'val')
    lbl_train_dir, lb_val_dir = os.path.join(lbl_dir, 'train'), os.path.join(lbl_dir, 'val')
    create_directory(paths=[img_train_dir, img_val_dir, lbl_train_dir, lb_val_dir], overwrite=False)
    if verbose: print('Reading geometries...')
    for video_cnt, (video_name, roi_data) in enumerate(sliced_roi_geometries.items()):
        if verbose: print(f'Reading ROI geometries for video {video_name}... ({video_cnt +1}/{len(list(roi_geometries.keys()))})')
        roi_geometries_rectangles[video_name] = {}
        for roi_name, roi in roi_data.items():
            if obb:
                roi_geometries_rectangles[video_name][roi_name] = GeometryMixin.minimum_rotated_rectangle(shape=roi)
            else:
                keypoints = np.array(roi.exterior.coords).astype(np.int32).reshape(1, -1, 2)
                roi_geometries_rectangles[video_name][roi_name] = Polygon(GeometryMixin.keypoints_to_axis_aligned_bounding_box(keypoints=keypoints)[0])
                print(roi_geometries_rectangles[video_name][roi_name])
            if roi_name not in roi_ids.keys():
                roi_ids[roi_name] = roi_cnt
                roi_cnt += 1

    roi_results, img_results = {}, {}
    if verbose: print('Reading coordinates ...')
    for video_cnt, (video_name, roi_data) in enumerate(roi_geometries_rectangles.items()):
        if verbose: print (f'Reading ROI coordinates for video {video_name}... ({video_cnt +1}/{len(list(roi_geometries_rectangles.keys()))})')
        roi_results[video_name] = {}
        img_results[video_name] = []
        video_path = find_video_of_file(video_dir=video_dir, filename=video_name)
        video_meta_data = get_video_meta_data(video_path)
        if roi_frm_cnt > video_meta_data['frame_count']:
            roi_frm_cnt = video_meta_data['frame_count']
        cap = cv2.VideoCapture(video_path)
        frm_idx = np.sort(np.random.choice(np.arange(0, video_meta_data['frame_count']), size=roi_frm_cnt))
        for idx in frm_idx:
            img_results[video_name].append(read_frm_of_video(video_path=cap, frame_index=idx, greyscale=greyscale))
        w, h = video_meta_data['width'], video_meta_data['height']
        for roi_name, roi in roi_data.items():
            roi_id = roi_ids[roi_name]
            if not obb:
                shape_stats = GeometryMixin.get_shape_statistics(shapes=roi)
                x_center = shape_stats['centers'][0][0] / w
                y_center = shape_stats['centers'][0][1] / h
                width = shape_stats['widths'][0] / w
                height = shape_stats['lengths'][0] / h
                roi_str = ' '.join([str(roi_id), str(x_center), str(y_center), str(width), str(height)])
            else:
                img_geometry = np.array(roi.exterior.coords).astype(np.int32)[1:]
                x1, y1 = img_geometry[0][0] / w, img_geometry[0][1] / h
                x2, y2 = img_geometry[1][0] / w, img_geometry[1][1] / h
                x3, y3 = img_geometry[2][0] / w, img_geometry[2][1] / h
                x4, y4 = img_geometry[3][0] / w, img_geometry[3][1] / h
                roi_str = ' '.join ([str(roi_id), str(x1), str(y1), str(x2), str(y2), str(x3), str(y3), str(x4), str(y4), '\n'])
            roi_results[video_name][roi_name] = roi_str

    total_img_cnt = sum(len(v) for v in img_results.values())
    train_idx = random.sample(list(range(0, total_img_cnt)), int(total_img_cnt * train_size))

    if verbose: print('Reading images ...')
    cnt = 0
    for video_cnt, (video_name, imgs) in enumerate(img_results.items()):
        if verbose: print (f'Reading ROI images for video {video_name}... ({video_cnt +1}/{len(list(img_results.keys()))})')
        for img_cnt, img in enumerate(imgs):
            if cnt in train_idx:
                img_save_path = os.path.join(img_train_dir, f'{video_name}_{img_cnt}.png')
                lbl_save_path = os.path.join(lbl_train_dir, f'{video_name}_{img_cnt}.txt')
            else:
                img_save_path = os.path.join(img_val_dir, f'{video_name}_{img_cnt}.png')
                lbl_save_path = os.path.join(lb_val_dir, f'{video_name}_{img_cnt}.txt')
            cv2.imwrite(img_save_path, img)
            # circle = roi_geometries_rectangles[video_name]['circle']
            # pts = np.array(circle.exterior.coords, dtype=np.int32)
            # pts = pts.reshape((-1, 1, 2))
            # cv2.polylines(img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            # cv2.imshow('sadasdasd', img)
            x = list(roi_results[video_name].values())
            with open(lbl_save_path, mode='wt', encoding='utf-8') as f:
                f.write('\n'.join(x))
            cnt += 1

    roi_ids = {v: k for k, v in roi_ids.items()}

    create_yolo_keypoint_yaml(path=save_dir, train_path=img_train_dir, val_path=img_val_dir, names=roi_ids, save_path=map_path)
    timer.stop_timer()
    if verbose:
        stdout_success(msg=f'yolo ROI data saved in {save_dir}', elapsed_time=timer.elapsed_time_str)


simba_rois_to_yolo(video_dir=r"C:\troubleshooting\RAT_NOR\project_folder\videos",
                   roi_path=r"C:\troubleshooting\RAT_NOR\project_folder\logs\measures\ROI_definitions.h5",
                   save_dir=r'C:\troubleshooting\RAT_NOR\project_folder\yolo',
                   verbose=True, roi_frm_cnt=20,
                   obb=True)
