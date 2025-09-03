from typing import Union, Optional, Dict, Tuple, List
import os
import random
import pandas as pd
import numpy as np
import cv2

from simba.utils.read_write import find_files_of_filetypes_in_directory, get_video_meta_data, read_frm_of_video, create_directory
from simba.utils.enums import Options
from simba.utils.errors import NoFilesFoundError, InvalidInputError
from simba.utils.checks import check_valid_dataframe, check_if_dir_exists, check_int, check_float, check_valid_tuple, check_valid_boolean
from simba.third_party_label_appenders.converters import create_yolo_keypoint_yaml
from simba.utils.printing import SimbaTimer, stdout_success


def sleap_to_yolo_keypoints(data_dir: Union[str, os.PathLike],
                            video_dir: Union[str, os.PathLike],
                            save_dir: Union[str, os.PathLike],
                            frms_cnt: Optional[int] = None,
                            verbose: bool = True,
                            instance_threshold: float = 0,
                            train_size: float = 0.7,
                            flip_idx: Tuple[int, ...] = None,
                            names: Tuple[str, ...] = None,
                            greyscale: bool = False,
                            padding: float = 0.00):

    """
    Convert SLEAP pose estimation CSV data and corresponding videos into YOLO keypoint dataset format.

    .. note::
       This converts SLEAP **inference** data to YOLO keypoints (not SLEAP annotations).

    :param Union[str, os.PathLike] data_dir: Directory path containing SLEAP-generated CSV files with inferred keypoints.
    :param Union[str, os.PathLike] video_dir: Directory path containing corresponding videos from which frames are to be extracted.
    :param Union[str, os.PathLike] save_dir: Output directory where YOLO-formatted images, labels, and map YAML file will be saved. Subdirectories `images/train`, `images/val`, `labels/train`, `labels/val` will be created.
    :param Optional[int] frms_cnt: Number of frames to randomly sample from each video for conversion. If None, all frames are used.
    :param float instance_threshold: Minimum confidence score threshold to filter out low-confidence pose instances. Only instances with `instance.score` >= this threshold are used.
    :param float train_size: Proportion of frames randomly assigned to the training dataset. Value must be between 0.1 and 0.99. Default: 0.7.
    :param bool verbose: If True, prints progress. Default: True.
    :param Tuple[int, ...] flip_idx: Tuple of keypoint indices used for horizontal flip augmentation during training. The tuple defines the order of keypoints after flipping.
    :param Dict[str, int] map_dict: Dictionary mapping class indices to class names. Used for creating the YAML class names mapping file.
    :param float padding: Fractional padding to add around the bounding boxes (relative to image dimensions). Helps to slightly enlarge bounding boxes by this percentage. Default 0.05. E.g., Useful when all body-parts are along animal length.
    :return: None. Results saved in ``save_dir``.

    :example:
    >>> sleap_to_yolo_keypoints(data_dir=r'D:\ares\data\ant\sleap_csv', video_dir=r'D:\ares\data\ant\sleap_video', frms_cnt=550, train_size=0.8, instance_threshold=0.9, save_dir=r"D:\ares\data\ant\yolo")

    """

    data_paths = find_files_of_filetypes_in_directory(directory=data_dir, extensions=['.csv'], as_dict=True, raise_error=True)
    video_paths = find_files_of_filetypes_in_directory(directory=video_dir, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value, as_dict=True, raise_error=True)
    missing_video_paths = [x for x in video_paths.keys() if x not in data_paths.keys()]
    missing_data_paths = [x for x in data_paths.keys() if x not in video_paths.keys()]
    check_if_dir_exists(in_dir=save_dir)
    img_dir, lbl_dir = os.path.join(save_dir, 'images'), os.path.join(save_dir, 'labels')
    img_train_dir, img_val_dir = os.path.join(save_dir, 'images', 'train'), os.path.join(save_dir, 'images', 'val')
    lbl_train_dir, lb_val_dir = os.path.join(save_dir, 'labels', 'train'), os.path.join(save_dir, 'labels', 'val')
    if flip_idx is not None: check_valid_tuple(x=flip_idx, source=f'{sleap_to_yolo_keypoints.__name__} flip_idx', valid_dtypes=(int,), minimum_length=1)
    if names is not None: check_valid_tuple(x=names, source=f'{sleap_to_yolo_keypoints.__name__} names', valid_dtypes=(str,), minimum_length=1)
    create_directory(paths=img_train_dir); create_directory(paths=img_val_dir)
    create_directory(paths=lbl_train_dir); create_directory(paths=lb_val_dir)
    check_float(name=f'{sleap_to_yolo_keypoints.__name__} instance_threshold', min_value=0.0, max_value=1.0, raise_error=True, value=instance_threshold)
    check_valid_boolean(value=verbose, source=f'{sleap_to_yolo_keypoints.__name__} verbose', raise_error=True)
    check_valid_boolean(value=greyscale, source=f'{sleap_to_yolo_keypoints.__name__} greyscale', raise_error=True)
    check_float(name=f'{sleap_to_yolo_keypoints.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
    check_float(name=f'{sleap_to_yolo_keypoints.__name__} padding', value=padding, max_value=1.0, min_value=0.0, raise_error=True)

    map_path = os.path.join(save_dir, 'map.yaml')
    timer = SimbaTimer(start=True)
    if frms_cnt is not None:
        check_int(name=f'{sleap_to_yolo_keypoints.__name__} frms_cnt', value=frms_cnt, min_value=1, raise_error=True)
    if len(missing_video_paths) > 0:
        raise NoFilesFoundError(msg=f'Video(s) {missing_video_paths} could not be found in {video_dir} directory', source=sleap_to_yolo_keypoints.__name__)
    if len(missing_data_paths) > 0:
        raise NoFilesFoundError(msg=f'CSV data for {missing_data_paths} could not be found in {data_dir} directory', source=sleap_to_yolo_keypoints.__name__)

    dfs = []
    for file_cnt, (file_name, file_path) in enumerate(data_paths.items()):
        df = pd.read_csv(filepath_or_buffer=file_path)
        check_valid_dataframe(df=df, source=sleap_to_yolo_keypoints.__name__, required_fields=['track', 'frame_idx', 'instance.score'])
        df = df if instance_threshold is None else df[df['instance.score'] >= instance_threshold]
        cord_cols, frame_idx = df.drop(['track', 'frame_idx', 'instance.score'], axis=1), df['frame_idx']
        selected_frms = random.sample(list(frame_idx.unique()), frms_cnt) if frms_cnt is not None else list(frame_idx.unique())
        df = df[df['frame_idx'].isin(selected_frms)]
        df['video'] = video_paths[file_name]
        dfs.append(df)

    dfs = pd.concat(dfs, axis=0)
    unique_tracks_lk = {v: k for k, v in enumerate(dfs['track'].unique())}
    if names is not None:
        check_valid_tuple(x=names, source=f'{sleap_to_yolo_keypoints.__name__} names', valid_dtypes=(str,), accepted_lengths=(len(list(unique_tracks_lk.keys())),))
    else:
        names = [f'animal_{k+1}' for k in range(len(list(unique_tracks_lk.keys())),)]
    map_dict = {k: v for k, v in enumerate(names)}
    dfs['id'] = dfs['frame_idx'].astype(str) + dfs['video'].astype(str)
    train_idx = random.sample(list(dfs['id'].unique()), int(len(dfs['frame_idx'].unique()) * train_size))
    for frm_cnt, frm_id in enumerate(dfs['id'].unique()):
        frm_data = dfs[dfs['id'] == frm_id]
        video_path = list(frm_data['video'])[0]
        frm_idx = list(frm_data['frame_idx'])[0]
        video_meta = get_video_meta_data(video_path=video_path)
        if verbose:
            print(f'Processing frame: {frm_cnt+1}/{len(dfs)} ...')
        img = read_frm_of_video(video_path=video_path, frame_index=frm_idx, greyscale=greyscale)
        img_h, img_w = img.shape[0], img.shape[1]
        if list(frm_data['id'])[0] in train_idx:
            img_save_path = os.path.join(img_dir, 'train', f'{video_meta["video_name"]}_{frm_idx}.png')
            lbl_save_path = os.path.join(lbl_dir, 'train', f'{video_meta["video_name"]}_{frm_idx}.txt')
        else:
            img_save_path  = os.path.join(img_dir, 'val', f'{video_meta["video_name"]}_{frm_idx}.png')
            lbl_save_path = os.path.join(lbl_dir, 'val', f'{video_meta["video_name"]}_{frm_idx}.txt')
        img_lbl = ''
        for track_cnt, (_, track_data) in enumerate(frm_data.iterrows()):
            track_id, keypoints = unique_tracks_lk[track_data['track']], track_data.drop(['track', 'frame_idx', 'instance.score', 'video', 'id']),
            keypoints = keypoints.values.reshape(-1, 3)
            if frms_cnt == 0 and track_cnt == 0:
                if flip_idx is not None and keypoints.shape[0] != len(flip_idx):
                    raise InvalidInputError(msg=f'The SLEAP data contains data for {keypoints.shape[0]} body-parts, but passed flip_idx suggests {len(flip_idx)} body-parts', source=sleap_to_yolo_keypoints.__name__)
                elif flip_idx is None:
                    flip_idx = tuple(list(range(0, keypoints.shape[0])))
            keypoints[keypoints[:, 2] != 0.0, 2] = 2
            instance_str = f'{track_id} '
            x_coords, y_coords = keypoints[:, 0], keypoints[:, 1]
            min_x, max_x = np.nanmin(x_coords), np.nanmax(x_coords)
            min_y, max_y = np.nanmin(y_coords), np.nanmax(y_coords)
            pad_w, pad_h = padding * img_w, padding * img_h
            min_x, max_x = max(min_x - pad_w / 2, 0), min(max_x + pad_w / 2, img_w)
            min_y, max_y = max(min_y - pad_h / 2, 0), min(max_y + pad_h / 2, img_h)
            bbox_w, bbox_h = max_x - min_x, max_y - min_y
            x_center, y_center = min_x + bbox_w / 2, min_y + bbox_h / 2
            x_center /= img_w
            y_center /= img_h
            bbox_w /= img_w
            bbox_h /= img_h
            x_center = np.clip(x_center, 0.0, 1.0)
            y_center = np.clip(y_center, 0.0, 1.0)
            bbox_w = np.clip(bbox_w, 0.0, 1.0)
            bbox_h = np.clip(bbox_h, 0.0, 1.0)
            keypoints[:, 0] /= img_w
            keypoints[:, 1] /= img_h
            keypoints[:, 0:2] = np.clip( keypoints[:, 0:2], 0.0, 1.0)
            instance_str += f"{x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f} "
            for kp in keypoints:
                instance_str += f"{kp[0]:.6f} {kp[1]:.6f} {int(kp[2])} "
            img_lbl += instance_str.strip() + '\n'
        with open(lbl_save_path, mode='wt', encoding='utf-8') as f:
            f.write(img_lbl)
        cv2.imwrite(img_save_path, img)


    create_yolo_keypoint_yaml(path=save_dir, train_path=img_train_dir, val_path=img_val_dir, names=map_dict, save_path=map_path, kpt_shape=(len(flip_idx), 3), flip_idx=flip_idx)
    timer.stop_timer()
    stdout_success(msg=f'YOLO formated data saved in {save_dir} directory', source=sleap_to_yolo_keypoints.__name__, elapsed_time=timer.elapsed_time_str)

# sleap_to_yolo_keypoints(data_dir=r'D:\ares\data\termite_2\sleap_csv',
#                         video_dir=r'D:\ares\data\termite_2\videos',
#                         frms_cnt=500,
#                         instance_threshold=0.8,
#                         save_dir=r"D:\ares\data\termite_2\yolo")


# sleap_to_yolo_keypoints(data_dir=r'D:\troubleshooting\two_animals_sleap\import_data',
#                         video_dir=r'D:\troubleshooting\two_animals_sleap\project_folder\videos',
#                         frms_cnt=550,
#                         train_size=0.8,
#                         instance_threshold=0.9,
#                         save_dir=r"D:\troubleshooting\two_animals_sleap\import_data\yolo",
#                         names=None,
#                         flip_idx=(0, 2, 1, 3, 4)) #('animal_1', 'animal_2',)