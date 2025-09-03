from typing import Union, Optional, Tuple
import os
import random
import pandas as pd
import numpy as np
import cv2

from simba.utils.read_write import find_files_of_filetypes_in_directory, get_video_meta_data, read_frm_of_video, create_directory, read_sleap_h5
from simba.utils.enums import Options
from simba.utils.errors import NoFilesFoundError, InvalidInputError
from simba.utils.warnings import FrameRangeWarning
from simba.utils.checks import check_if_dir_exists, check_int, check_float, check_valid_tuple, check_valid_boolean
from simba.third_party_label_appenders.converters import create_yolo_keypoint_yaml
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.yolo import keypoint_array_to_yolo_annotation_str


def sleap_h5_to_yolo_keypoints(data_dir: Union[str, os.PathLike],
                               video_dir: Union[str, os.PathLike],
                               save_dir: Union[str, os.PathLike],
                               frms_cnt: Optional[int] = None,
                               verbose: bool = True,
                               threshold: float = 0,
                               train_size: float = 0.7,
                               flip_idx: Tuple[int, ...] = None,
                               animal_cnt: int = 2,
                               greyscale: bool = False,
                               padding: float = 0.00):
    """

    :param data_dir:
    :param video_dir:
    :param save_dir:
    :param frms_cnt:
    :param verbose:
    :param threshold:
    :param train_size:
    :param flip_idx:
    :param animal_cnt:
    :param greyscale:
    :param padding:
    :return:

    :example:
    >>> sleap_h5_to_yolo_keypoints(data_dir=r'D:\ares\data\termite_1\data', video_dir=r'D:\ares\data\termite_1\video', save_dir=r'D:\ares\data\termite_1\yolo', threshold=0.9, frms_cnt=50)
    """


    data_paths = find_files_of_filetypes_in_directory(directory=data_dir, extensions=['.H5', '.h5'], as_dict=True, raise_error=True)
    video_paths = find_files_of_filetypes_in_directory(directory=video_dir, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value, as_dict=True, raise_error=True)
    missing_video_paths = [x for x in video_paths.keys() if x not in data_paths.keys()]
    missing_data_paths = [x for x in data_paths.keys() if x not in video_paths.keys()]
    check_if_dir_exists(in_dir=save_dir)
    img_dir, lbl_dir = os.path.join(save_dir, 'images'), os.path.join(save_dir, 'labels')
    img_train_dir, img_val_dir = os.path.join(save_dir, 'images', 'train'), os.path.join(save_dir, 'images', 'val')
    lbl_train_dir, lb_val_dir = os.path.join(save_dir, 'labels', 'train'), os.path.join(save_dir, 'labels', 'val')
    if flip_idx is not None: check_valid_tuple(x=flip_idx, source=f'{sleap_h5_to_yolo_keypoints.__name__} flip_idx', valid_dtypes=(int,), minimum_length=1)
    check_int(name=f'{sleap_h5_to_yolo_keypoints.__name__} animal_cnt', value=animal_cnt, min_value=1)
    create_directory(paths=img_train_dir); create_directory(paths=img_val_dir)
    create_directory(paths=lbl_train_dir); create_directory(paths=lb_val_dir)
    check_float(name=f'{sleap_h5_to_yolo_keypoints.__name__} instance_threshold', min_value=0.0, max_value=1.0, raise_error=True, value=threshold)
    check_valid_boolean(value=verbose, source=f'{sleap_h5_to_yolo_keypoints.__name__} verbose', raise_error=True)
    check_valid_boolean(value=greyscale, source=f'{sleap_h5_to_yolo_keypoints.__name__} greyscale', raise_error=True)
    check_float(name=f'{sleap_h5_to_yolo_keypoints.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
    check_float(name=f'{sleap_h5_to_yolo_keypoints.__name__} padding', value=padding, max_value=1.0, min_value=0.0, raise_error=True)


    map_path = os.path.join(save_dir, 'map.yaml')
    timer = SimbaTimer(start=True)
    if frms_cnt is not None:
        check_int(name=f'{sleap_h5_to_yolo_keypoints.__name__} frms_cnt', value=frms_cnt, min_value=1, raise_error=True)
    if len(missing_video_paths) > 0:
        raise NoFilesFoundError(msg=f'Video(s) {missing_video_paths} could not be found in {video_dir} directory', source=sleap_h5_to_yolo_keypoints.__name__)
    if len(missing_data_paths) > 0:
        raise NoFilesFoundError(msg=f'CSV data for {missing_data_paths} could not be found in {data_dir} directory', source=sleap_h5_to_yolo_keypoints.__name__)

    map_dict = {v: f'animal_{k+1}' for k, v in enumerate(range(animal_cnt))}
    dfs = []
    for file_cnt, (file_name, file_path) in enumerate(data_paths.items()):
        df = read_sleap_h5(file_path=file_path)
        p_cols = df.iloc[:, 2::3]
        df = df.iloc[p_cols[df.gt(threshold).all(axis=1)].index]
        df['frm_idx'] = df.index
        selected_frms = random.sample(list(df['frm_idx']), frms_cnt) if frms_cnt is not None else list(df['frm_idx'].unique())
        df = df[df['frm_idx'].isin(selected_frms)]
        df['video'] = video_paths[file_name]
        dfs.append(df)

    dfs = pd.concat(dfs, axis=0)
    dfs['id'] = dfs['frm_idx'].astype(str) + dfs['video'].astype(str)
    train_idx = random.sample(list(dfs['id'].unique()), int(len(dfs['frm_idx'].unique()) * train_size))
    for frm_cnt, frm_id in enumerate(dfs['id'].unique()):
        frm_data = dfs[dfs['id'] == frm_id]
        video_path = list(frm_data['video'])[0]
        frm_idx = list(frm_data['frm_idx'])[0]
        video_meta = get_video_meta_data(video_path=video_path)
        if verbose:
            print(f'Processing frame: {frm_cnt + 1}/{len(dfs)} ...')
        if frm_idx > video_meta['frame_count']:
            FrameRangeWarning(msg=f'Frame {frm_idx} could not be read from video {video_path}. The video {video_meta["video_name"]} has {video_meta["frame_count"]} frames', source=sleap_h5_to_yolo_keypoints.__name__)
            continue
        img = read_frm_of_video(video_path=video_path, frame_index=frm_idx, greyscale=greyscale)
        img_h, img_w = img.shape[0], img.shape[1]
        if list(frm_data['id'])[0] in train_idx:
            img_save_path = os.path.join(img_dir, 'train', f'{video_meta["video_name"]}_{frm_idx}.png')
            lbl_save_path = os.path.join(lbl_dir, 'train', f'{video_meta["video_name"]}_{frm_idx}.txt')
        else:
            img_save_path  = os.path.join(img_dir, 'val', f'{video_meta["video_name"]}_{frm_idx}.png')
            lbl_save_path = os.path.join(lbl_dir, 'val', f'{video_meta["video_name"]}_{frm_idx}.txt')
        img_lbl = ''
        frm_data = frm_data.drop(['video', 'id', 'frm_idx'], axis=1).T.iloc[:, 0]
        animal_idxs = np.array_split(list(range(0, len(frm_data))), animal_cnt)
        for track_id, animal_idx in enumerate(animal_idxs):
            keypoints = frm_data[frm_data.index.isin(animal_idx)].values.reshape(-1, 3)
            keypoints[keypoints[:, 2] != 0.0, 2] = 2
            if frm_cnt == 0 and track_id == 0:
                if flip_idx is not None and keypoints.shape[0] != len(flip_idx):
                    raise InvalidInputError(msg=f'The SLEAP data contains data for {keypoints.shape[0]} body-parts, but passed flip_idx suggests {len(flip_idx)} body-parts', source=sleap_to_yolo_keypoints.__name__)
                elif flip_idx is None:
                    flip_idx = tuple(list(range(0, keypoints.shape[0])))
            instance_str = f'{track_id} '
            img_lbl += keypoint_array_to_yolo_annotation_str(x=keypoints, img_w=img_w, img_h=img_h, padding=padding)
        with open(lbl_save_path, mode='wt', encoding='utf-8') as f:
            f.write(img_lbl)
        cv2.imwrite(img_save_path, img)
    create_yolo_keypoint_yaml(path=save_dir, train_path=img_train_dir, val_path=img_val_dir, names=map_dict, save_path=map_path, kpt_shape=(len(flip_idx), 3), flip_idx=flip_idx)
    timer.stop_timer()
    stdout_success(msg=f'YOLO formated data saved in {save_dir} directory', source=sleap_h5_to_yolo_keypoints.__name__, elapsed_time=timer.elapsed_time_str)

sleap_h5_to_yolo_keypoints(data_dir=r'D:\ares\data\termite_1\data', video_dir=r'D:\ares\data\termite_1\video', save_dir=r'D:\ares\data\termite_1\yolo', threshold=0.9, frms_cnt=50)
#df = read_sleap_h5(file_path=r"D:\ares\data\termite_1\termite.h5")

