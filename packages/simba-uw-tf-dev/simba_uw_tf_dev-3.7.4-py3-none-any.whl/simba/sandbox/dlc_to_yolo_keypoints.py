import os
from typing import Union, Tuple, Dict, List, Optional
import pandas as pd
import cv2
import numpy as np
import random

from simba.utils.read_write import find_files_of_filetypes_in_directory,create_directory, get_fn_ext
from simba.utils.checks import check_if_dir_exists, check_valid_boolean, check_valid_dataframe, check_file_exist_and_readable, check_float, check_valid_tuple, check_valid_dict, check_str, check_valid_lst
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.errors import NoFilesFoundError, InvalidInputError
from simba.utils.enums import Formats
from simba.third_party_label_appenders.converters import create_yolo_keypoint_yaml


def recursive_file_search(directory: Union[str, os.PathLike],
                          substrings: Union[str, List[str]],
                          extensions: Union[str, List[str]],
                          case_sensitive: bool = False,
                          raise_error: bool = True) -> List[str]:
    """
    Recursively search for files in a directory and all subdirectories that:
    - Contain any of the given substrings in their filename
    - Have one of the specified file extensions

    :param directory: Directory to start the search from.
    :param substrings: A substring or list of substrings to match in filenames.
    :param extensions: A file extension or list of allowed extensions (with or without dot).
    :param case_sensitive: If True, substring match is case-sensitive. Default False.
    :param raise_error: If True, raise an error if no matches are found.
    :return: List of matching file paths.
    """

    check_if_dir_exists(in_dir=directory)
    if isinstance(substrings, str):
        substrings = [substrings]
    check_valid_lst(data=substrings, valid_dtypes=(str,), min_len=1, raise_error=True)

    if isinstance(extensions, str):
        extensions = [extensions]
    check_valid_lst(data=extensions, valid_dtypes=(str,), min_len=1, raise_error=True)

    check_valid_boolean(value=case_sensitive, source=f'{recursive_file_search.__name__} case_sensitive', raise_error=True)

    extensions = [ext.lower().lstrip('.') for ext in extensions]
    if not case_sensitive:
        substrings = [s.lower() for s in substrings]

    results = []
    for root, _, files in os.walk(directory):
        for f in files:
            name, ext = os.path.splitext(f)
            ext = ext.lstrip('.').lower()
            match_substr = any(s in f if case_sensitive else s in f.lower() for s in substrings)
            if ext in extensions and match_substr:
                results.append(os.path.join(root, f))

    if not results and raise_error:
        raise NoFilesFoundError(msg=f'No files with extensions {extensions} and substrings {substrings} found in {directory}', source=recursive_file_search.__name__)

    return results





def dlc_to_yolo_keypoints(dlc_dir: Union[str, os.PathLike],
                          save_dir: Union[str, os.PathLike],
                          train_size: float = 0.7,
                          verbose: bool = False,
                          padding: float = 0.00,
                          flip_idx: Tuple[int, ...] = (1, 0, 2, 3, 5, 4, 6, 7),
                          map_dict: Dict[int, str] = {0: 'mouse'},
                          bp_id_idx: Optional[Dict[int, Union[Tuple[int], List[int]]]] = None) -> None:

    """
    Converts DLC annotations into YOLO keypoint format formatted for model training.

    .. note::
       ``dlc_dir`` can be a directory with subdirectories containing images and CSV files with the ``CollectedData`` substring filename.

    :param Union[str, os.PathLike] dlc_dir: Directory path containing DLC-generated CSV files with keypoint annotations and images.
    :param Union[str, os.PathLike] save_dir: Output directory where YOLO-formatted images, labels, and map YAML file will be saved. Subdirectories `images/train`, `images/val`, `labels/train`, `labels/val` will be created.
    :param float train_size: Proportion of frames randomly assigned to the training dataset. Value must be between 0.1 and 0.99. Default: 0.7.
    :param bool verbose: If True, prints progress. Default: True.
    :param float padding: Fractional padding to add around the bounding boxes (relative to image dimensions). Helps to slightly enlarge bounding boxes by this percentage. Default 0.05. E.g., Useful when all body-parts are along animal length.
    :param Tuple[int, ...] flip_idx: Tuple of keypoint indices used for horizontal flip augmentation during training. The tuple defines the order of keypoints after flipping.
    :param Dict[int, str] map_dict: Dictionary mapping class indices to class names. Used for creating the YAML class names mapping file.
    :return: None. Results saved in ``save_dir``.

    :example:
    >>> dlc_to_yolo_keypoints(dlc_dir=r'D:\mouse_operant_data\Operant_C57_labelled_images\labeled-data', save_dir=r"D:\mouse_operant_data\yolo", verbose=True)
    >>> dlc_to_yolo_keypoints(dlc_dir=r'D:\rat_resident_intruder\dlc_data', save_dir=r"D:\rat_resident_intruder\yolo", verbose=True, bp_id_idx={0: list(range(0, 8)), 1: list(range(8, 16))},  map_dict={0: 'resident', 1: 'intruder'})
    """

    timer = SimbaTimer(start=True)
    check_if_dir_exists(in_dir=dlc_dir, source=f'{dlc_to_yolo_keypoints.__name__} dlc_dir')
    check_valid_boolean(value=verbose, source=f'{dlc_to_yolo_keypoints.__name__} verbose')
    check_float(name=f'{dlc_to_yolo_keypoints.__name__} padding', value=padding, max_value=1.0, min_value=0.0, raise_error=True)
    check_float(name=f'{dlc_to_yolo_keypoints.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
    check_valid_dict(x=map_dict, valid_key_dtypes=(int,), valid_values_dtypes=(str,), min_len_keys=1)
    check_if_dir_exists(in_dir=save_dir)
    annotation_paths = recursive_file_search(directory=dlc_dir, substrings=['CollectedData'], extensions=['csv'], case_sensitive=False, raise_error=True)
    check_valid_tuple(x=flip_idx, source=dlc_to_yolo_keypoints.__name__, valid_dtypes=(int,), minimum_length=1)
    img_dir, lbl_dir = os.path.join(save_dir, 'images'), os.path.join(save_dir, 'labels')
    img_train_dir, img_val_dir = os.path.join(img_dir, 'train'), os.path.join(img_dir, 'val')
    lbl_train_dir, lb_val_dir = os.path.join(lbl_dir, 'train'), os.path.join(lbl_dir, 'val')
    create_directory(paths=[img_train_dir, img_val_dir, lbl_train_dir, lb_val_dir], overwrite=False)
    annotations = []
    if bp_id_idx is not None:
        bp_id_idx_ints = list(bp_id_idx.values())
        bp_id_idx_ints = [x for xs in bp_id_idx_ints for x in xs]
        check_valid_dict(x=bp_id_idx, valid_key_dtypes=(int,), valid_values_dtypes=(tuple, list,))
        missing_map_dict_keys = [x for x in bp_id_idx.keys() if x not in map_dict.keys()]
        missing_bp_id_keys = [x for x in map_dict.keys() if x not in bp_id_idx.keys()]
        if len(missing_map_dict_keys) > 0:
            raise InvalidInputError(msg=f'Keys {missing_map_dict_keys} exist in bp_id_idx but is not passed in map_dict', source=dlc_to_yolo_keypoints.__name__)
        if len(missing_bp_id_keys) > 0:
            raise InvalidInputError(msg=f'Keys {missing_bp_id_keys} exist in map_dict but is not passed in bp_id_idx', source=dlc_to_yolo_keypoints.__name__)

    map_path = os.path.join(save_dir, 'map.yaml')
    for file_cnt, annotation_path in enumerate(annotation_paths):
        annotation_data = pd.read_csv(annotation_path, header=[0, 1, 2])
        img_paths = annotation_data.pop(annotation_data.columns[0]).reset_index(drop=True).values
        body_parts = []
        body_part_headers = []
        for i in annotation_data.columns[1:]:
            if 'unnamed:' not in i[1].lower() and i[1] not in body_parts:
                body_parts.append(i[1])
        for i in body_parts:
            body_part_headers.append(f'{i}_x'); body_part_headers.append(f'{i}_y')
        annotation_data.columns = body_part_headers
        check_valid_dataframe(df=annotation_data, source=dlc_to_yolo_keypoints.__name__, valid_dtypes=Formats.NUMERIC_DTYPES.value)
        annotation_data = annotation_data.reset_index(drop=True)
        img_paths = [os.path.join(os.path.dirname(annotation_path), os.path.basename(x)) for x in img_paths]
        annotation_data['img_path'] = img_paths
        annotations.append(annotation_data)
    annotations = pd.concat(annotations, axis=0).reset_index(drop=True)
    img_paths = annotations.pop('img_path').reset_index(drop=True).values
    train_idx = random.sample(list(range(0, len(annotations))), int(len(annotations) * train_size))
    for cnt, (idx, idx_data) in enumerate(annotations.iterrows()):
        img_lbl = ''
        if verbose:
            print(f'Processing image {cnt+1}/{len(annotations)}...')
        file_name = f"{os.path.basename(os.path.dirname(img_paths[cnt]))}.{os.path.splitext(os.path.basename(img_paths[cnt]))[0]}"
        if idx in train_idx:
            img_save_path, lbl_save_path = os.path.join(img_dir, 'train', f'{file_name}.png'), os.path.join(lbl_dir, 'train', f'{file_name}.txt')
        else:
            img_save_path, lbl_save_path = os.path.join(img_dir, 'val', f'{file_name}.png'), os.path.join(lbl_dir, 'val', f'{file_name}.txt')
        check_file_exist_and_readable(img_paths[cnt])
        img = cv2.imread(img_paths[cnt])
        img_h, img_w = img.shape[0], img.shape[1]
        keypoints_with_id = {}
        if bp_id_idx is not None:
            for k, idx in bp_id_idx.items():
                keypoints_with_id[k] = idx_data.values.reshape(-1, 2)[idx, :]
        else:
            keypoints_with_id[0] = idx_data.values.reshape(-1, 2)

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
            # for kp in keypoints:
            #     if not np.isnan(kp).any():
            #         p = (int(kp[0]), int(kp[1]))
            #         img = cv2.circle(img, p, 5, (255, 255, 0), 2,)
            # cv2.imshow('saasd', img)
            # cv2.waitKey(1000)
            keypoints[:, 0] /= img_w
            keypoints[:, 1] /= img_h
            keypoints[:, 0:2] = np.clip(keypoints[:, 0:2], 0.0, 1.0)
            visability_col = np.where(np.isnan(keypoints).any(axis=1), 0, 2)
            keypoints = np.nan_to_num(np.hstack((keypoints, visability_col[:, np.newaxis])), nan=0.0)
            instance_str += f"{x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f} "
            for kp in keypoints:
                instance_str += f"{kp[0]:.6f} {kp[1]:.6f} {int(kp[2])} "
            img_lbl += instance_str.strip() + '\n'
        with open(lbl_save_path, mode='wt', encoding='utf-8') as f:
            f.write(img_lbl)
        cv2.imwrite(img_save_path, img)
    create_yolo_keypoint_yaml(path=save_dir, train_path=img_train_dir, val_path=img_val_dir, names=map_dict, save_path=map_path, kpt_shape=(len(flip_idx), 3), flip_idx=flip_idx)
    timer.stop_timer()
    stdout_success(msg=f'YOLO formated data saved in {save_dir} directory', source=dlc_to_yolo_keypoints.__name__, elapsed_time=timer.elapsed_time_str)

#
# dlc_to_yolo_keypoints(dlc_dir=r'D:\rat_resident_intruder\dlc_data',
#                       save_dir=r"D:\rat_resident_intruder\yolo",
#                       verbose=True,
#                       bp_id_idx={0: list(range(0, 8)), 1: list(range(8, 16))},
#                       map_dict={0: 'resident', 1: 'intruder'})



dlc_to_yolo_keypoints(dlc_dir=r'D:\mouse_operant_data\Operant_C57_labelled_images\labeled-data',
                      save_dir=r"D:\mouse_operant_data\yolo",
                      verbose=True,
                      bp_id_idx=None,
                      map_dict={0: 'mouse'})


#recursive_file_search(directory=r'D:\mouse_operant_data\Operant_C57_labelled_images\labeled-data\Box1-20190805T1117-1127', substrings=['CollectedData'], extensions=['csv'], case_sensitive=False)