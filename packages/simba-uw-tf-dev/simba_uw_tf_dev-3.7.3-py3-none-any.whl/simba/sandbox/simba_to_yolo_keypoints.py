import os
from typing import Union, Tuple, Dict, List, Optional
import pandas as pd
import cv2
import numpy as np
import random

from simba.utils.read_write import find_files_of_filetypes_in_directory,create_directory, read_df, read_frm_of_video, get_video_meta_data
from simba.utils.checks import check_if_dir_exists, check_valid_boolean, check_valid_dataframe, check_file_exist_and_readable, check_float, check_valid_tuple, check_valid_dict, check_int, check_video_and_data_frm_count_align
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.errors import NoFilesFoundError
from simba.utils.enums import Formats, Options
from simba.mixins.config_reader import ConfigReader
from simba.utils.warnings import NoDataFoundWarning
from simba.third_party_label_appenders.converters import  simba_to_yolo_keypoints

def simba_to_yolo_keypoints(config_path: Union[str, os.PathLike],
                            save_dir: Union[str, os.PathLike],
                            data_dir: Optional[Union[str, os.PathLike]] = None,
                            train_size: float = 0.7,
                            verbose: bool = False,
                            padding: float = 0.00,
                            flip_idx: Tuple[int, ...] = (1, 0, 2, 4, 3, 5, 6, 7, 8, 9),
                            map_dict: Dict[int, str] = {0: 'mouse'},
                            sample_size: Optional[int] = None,
                            bp_id_idx: Optional[Dict[int, Union[Tuple[int], List[int]]]] = None) -> None:

    """

    :param config_path:
    :param save_dir:
    :param data_dir:
    :param train_size:
    :param verbose:
    :param padding:
    :param flip_idx:
    :param map_dict:
    :param sample_size:
    :param bp_id_idx:
    :return:

    :example:
    >>> simba_to_yolo_keypoints(config_path=r"C:\troubleshooting\mitra\project_folder\project_config.ini", save_dir=r'C:\troubleshooting\mitra\yolo', sample_size=150, verbose=True)
    """

    timer = SimbaTimer(start=True)

    check_valid_boolean(value=verbose, source=f'{simba_to_yolo_keypoints.__name__} verbose')
    check_file_exist_and_readable(file_path=config_path)
    check_float(name=f'{simba_to_yolo_keypoints.__name__} padding', value=padding, max_value=1.0, min_value=0.0, raise_error=True)
    check_float(name=f'{simba_to_yolo_keypoints.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
    check_valid_dict(x=map_dict, valid_key_dtypes=(int,), valid_values_dtypes=(str,), min_len_keys=1)
    check_if_dir_exists(in_dir=save_dir)
    check_valid_tuple(x=flip_idx, source=simba_to_yolo_keypoints.__name__, valid_dtypes=(int,), minimum_length=1)
    img_dir, lbl_dir = os.path.join(save_dir, 'images'), os.path.join(save_dir, 'labels')
    img_train_dir, img_val_dir = os.path.join(img_dir, 'train'), os.path.join(img_dir, 'val')
    lbl_train_dir, lb_val_dir = os.path.join(lbl_dir, 'train'), os.path.join(lbl_dir, 'val')
    create_directory(paths=[img_train_dir, img_val_dir, lbl_train_dir, lb_val_dir], overwrite=False)
    map_path = os.path.join(save_dir, 'map.yaml')
    if sample_size is not None:
        check_int(name=f'{simba_to_yolo_keypoints.__name__} sample', value=sample_size, min_value=1)
    config = ConfigReader(config_path=config_path)
    if data_dir is not None:
        check_if_dir_exists(in_dir=data_dir, source=f'{simba_to_yolo_keypoints.__name__} data_dir')
    else:
        data_dir = config.outlier_corrected_dir
    data_paths = find_files_of_filetypes_in_directory(directory=data_dir, extensions=[f'.{config.file_type}'], raise_error=True, as_dict=True)
    video_paths = find_files_of_filetypes_in_directory(directory=config.video_dir, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value, raise_error=True, as_dict=True)
    missing_videos = [x for x in data_paths.keys() if x not in video_paths.keys()]
    if len(missing_videos) > 0:
        NoDataFoundWarning(msg=f'Data files {missing_videos} do not have corresponding videos in the {config.video_dir} directory', source=simba_to_yolo_keypoints.__name__)
    data_w_video = [x for x in data_paths.keys() if x in video_paths.keys()]
    if len(data_w_video) == 0:
        raise NoFilesFoundError(msg=f'None of the data files in {data_dir} have matching videos in the {config.video_dir} directory', source=simba_to_yolo_keypoints.__name__)
    if bp_id_idx is not None:
        check_valid_dict(x=bp_id_idx, valid_key_dtypes=(int,), valid_values_dtypes=(tuple, list,))
        missing_map_dict_keys = [x for x in bp_id_idx.keys() if x not in map_dict.keys()]
        missing_bp_id_keys = [x for x in map_dict.keys() if x not in bp_id_idx.keys()]
        if len(missing_map_dict_keys) > 0:
            raise InvalidInputError(msg=f'Keys {missing_map_dict_keys} exist in bp_id_idx but is not passed in map_dict', source=dlc_to_yolo_keypoints.__name__)
        if len(missing_bp_id_keys) > 0:
            raise InvalidInputError(msg=f'Keys {missing_bp_id_keys} exist in map_dict but is not passed in bp_id_idx', source=dlc_to_yolo_keypoints.__name__)

    annotations = []
    for file_cnt, video_name in enumerate(data_w_video):
        data = read_df(file_path=data_paths[video_name], file_type=config.file_type)
        check_valid_dataframe(df=data, source=simba_to_yolo_keypoints.__name__, valid_dtypes=Formats.NUMERIC_DTYPES.value)
        video_path = video_paths[video_name]
        check_video_and_data_frm_count_align(video=video_path, data=data, name=video_name, raise_error=True)
        frm_cnt = len(data)
        data = data.loc[:, ~data.columns.str.endswith('_p')].reset_index(drop=True)
        data['video'] = video_name
        #data = data.values.reshape(len(data), -1, 2).astype(np.float32)
        #img_w, img_h = video_meta['width'], video_meta['height']
        if sample_size is None:
            video_sample_idx = list(range(0, frm_cnt))
        else:
            video_sample_idx = list(range(0, frm_cnt)) if sample_size > frm_cnt else random.sample(list(range(0, frm_cnt)), sample_size)
        annotations.append(data.iloc[video_sample_idx].reset_index(drop=False))


    annotations = pd.concat(annotations, axis=0).reset_index(drop=True)
    video_names = annotations.pop('video').reset_index(drop=True).values
    train_idx = random.sample(list(annotations['index']), int(len(annotations) * train_size))

    for cnt, (idx, idx_data) in enumerate(annotations.iterrows()):
        vid_path = video_paths[video_names[cnt]]
        video_meta = get_video_meta_data(video_path=vid_path)
        frm_idx, keypoints = idx_data[0], idx_data.values[1:].reshape(-1, 2)
        mask = (keypoints[:, 0] == 0.0) & (keypoints[:, 1] == 0.0)
        keypoints[mask] = np.nan
        if np.all(np.isnan(keypoints)) or np.all(keypoints == 0.0) or np.all(np.isnan(keypoints) | (keypoints == 0.0)):
            continue
        img_lbl = ''; instance_str = f'0 '
        if verbose:
            print(f'Processing image {cnt+1}/{len(annotations)}...')
        file_name = f'{video_meta["video_name"]}.{frm_idx}'
        if frm_idx in train_idx:
            img_save_path, lbl_save_path = os.path.join(img_dir, 'train', f'{file_name}.png'), os.path.join(lbl_dir, 'train', f'{file_name}.txt')
        else:
            img_save_path, lbl_save_path = os.path.join(img_dir, 'val', f'{file_name}.png'), os.path.join(lbl_dir, 'val', f'{file_name}.txt')
        img = read_frm_of_video(video_path=vid_path, frame_index=frm_idx)
        img_h, img_w = img.shape[0], img.shape[1]
        keypoints_with_id = {}
        if bp_id_idx is not None:
            for k, idx in bp_id_idx.items():
                keypoints_with_id[k] = keypoints.reshape(-1, 2)[idx, :]
        else:
            keypoints_with_id[0] = keypoints.reshape(-1, 2)

        for id, keypoints in keypoints_with_id.items():
            if np.all(np.isnan(keypoints)) or np.all(keypoints == 0.0) or np.all(np.isnan(keypoints) | (keypoints == 0.0)):
               continue
            instance_str = f'{id} '
            x_coords, y_coords = keypoints[:, 0], keypoints[:, 1]
            min_x, max_x = np.nanmin(x_coords), np.nanmax(x_coords)
            min_y, max_y = np.nanmin(y_coords), np.nanmax(y_coords)
            pad_w, pad_h = padding * img_w, padding * img_h
            min_x, max_x = max(min_x - pad_w / 2, 0), min(max_x + pad_w / 2, img_w)
            min_y, max_y = max(min_y - pad_h / 2, 0), min(max_y + pad_h / 2, img_h)
            if max_x - min_x < 1 or max_y - min_y < 1:
                continue
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
            keypoints[:, 0:2] = np.clip(keypoints[:, 0:2], 0.0, 1.0)
            visability_col = np.where(np.isnan(keypoints).any(axis=1), 0, 2)
            keypoints = np.nan_to_num(np.hstack((keypoints, visability_col[:, np.newaxis])), nan=0.0)
            mask = (keypoints[:, 0] == 0.0) & (keypoints[:, 1] == 0.0)
            keypoints[mask, 2] = 0.0
            instance_str += f"{x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f} "
            for kp in keypoints:
                instance_str += f"{kp[0]:.6f} {kp[1]:.6f} {int(kp[2])} "
            img_lbl += instance_str.strip() + '\n'
            with open(lbl_save_path, mode='wt', encoding='utf-8') as f:
                f.write(img_lbl)
                cv2.imwrite(img_save_path, img)

    create_yolo_keypoint_yaml(path=save_dir, train_path=img_train_dir, val_path=img_val_dir, names=map_dict, save_path=map_path, kpt_shape=(len(flip_idx), 3), flip_idx=flip_idx)
    timer.stop_timer()
    stdout_success(msg=f'YOLO formated data saved in {save_dir} directory', source=simba_to_yolo_keypoints.__name__, elapsed_time=timer.elapsed_time_str)

#simba_to_yolo_keypoints(config_path=r"C:\troubleshooting\mitra\project_folder\project_config.ini", save_dir=r'C:\troubleshooting\mitra\yolo', sample_size=150, verbose=True)