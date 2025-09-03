from typing import Dict, Iterable, List, Optional, Tuple, Union

try:
    from typing import Literal
except:
    from typing_extensions import Literal

import base64
import io
import os
import math
from collections import Counter
from copy import deepcopy

import cv2
import numpy as np
import yaml
from PIL import Image


from simba.utils.checks import (check_file_exist_and_readable,
                                check_if_dir_exists,
                                check_if_keys_exist_in_dict,
                                check_if_valid_img, check_int,
                                check_valid_array, check_valid_dict,
                                check_valid_lst, check_valid_tuple)
from simba.utils.enums import Formats, Options
from simba.utils.errors import InvalidInputError
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (find_files_of_filetypes_in_directory, read_json, save_json)
from simba.utils.warnings import DuplicateNamesWarning
from simba.mixins.geometry_mixin import GeometryMixin



def merge_coco_keypoints_files(data_dir: Union[str, os.PathLike],
                               save_path: Union[str, os.PathLike],
                               max_width: Optional[int] = None,
                               max_height: Optional[int] = None,):
    """
    Merges multiple annotation COCO-format keypoint JSON files into a single file.

    .. note::
       Image and annotation entries are appended after adjusting their `id` fields to be unique.

       COCO-format keypoint JSON files can be created using `https://www.cvat.ai/ <https://www.cvat.ai/>`__.

    .. seealso::
       To convert COCO-format keypoint JSON to YOLO training set, see :func:`simba.third_party_label_appenders.transform.coco_keypoints_to_yolo.COCOKeypoints2Yolo`

    :param Union[str, os.PathLike] data_dir: Directory containing multiple COCO keypoints `.json` files to merge.
    :param Union[str, os.PathLike] save_path: File path to save the merged COCO keypoints JSON.
    :param int max_width: Optional max width keypoint coordinate annotation. If above max, the annotation will be set to "not visible"
    :param int max_height: Optional max height keypoint coordinate annotation. If above max, the annotation will be set to "not visible"
    :return: None. Results are saved in ``save_path``.

    :example:
    >>> DATA_DIR = r'D:\cvat_annotations\frames\coco_keypoints_1\TEST'
    >>> SAVE_PATH = r"D:\cvat_annotations\frames\coco_keypoints_1\TEST\merged.json"
    >>> merge_coco_keypoints_files(data_dir=DATA_DIR, save_path=SAVE_PATH)
    """

    timer = SimbaTimer(start=True)
    data_files = find_files_of_filetypes_in_directory(directory=data_dir, extensions=['.json'], raise_error=True, raise_warning=False, as_dict=True)
    if os.path.isdir(save_path):
        raise InvalidInputError(msg=f'save_path has to be a filepath, not a directory.', source=f'{merge_coco_keypoints_files.__name__} save_path')
    check_if_dir_exists(in_dir=os.path.dirname(save_path))
    if max_width is not None:
        check_int(name=f'{merge_coco_keypoints_files.__name__} max_width', value=max_width, min_value=1, raise_error=True)
    else:
        max_width = math.inf
    if max_height is not None:
        check_int(name=f'{merge_coco_keypoints_files.__name__} max_height', value=max_height, min_value=1, raise_error=True)
    else:
        max_height = math.inf
    results, max_image_id, max_annotation_id = None, 0, 0
    data_file_cnt, img_names = len(data_files), []
    if data_file_cnt == 1:
        raise InvalidInputError(msg=f'Only 1 JSON file found in {data_dir} directory. Cannot merge a single file.', source=merge_coco_keypoints_files.__name__)

    for file_cnt, (file_name, file_path) in enumerate(data_files.items()):
        print(f'Processing {file_cnt + 1}/{data_file_cnt} ({file_name})...')
        coco_data = read_json(file_path)
        check_if_keys_exist_in_dict(data=coco_data, key=['licenses', 'info', 'categories', 'images', 'annotations'], name=file_name)
        if file_cnt == 0:
            results = deepcopy(coco_data)
            max_image_id = max((img['id'] for img in results['images']), default=0)
            max_annotation_id = max((ann['id'] for ann in results['annotations']), default=0)
            for img in coco_data['images']:
                img_names.append(img['file_name'])
        else:
            if coco_data.get('licenses'):
                for lic in coco_data['licenses']:
                    if lic not in results['licenses']:
                        results['licenses'].append(lic)

            if coco_data.get('categories'):
                for cat in coco_data['categories']:
                    if cat not in results['categories']:
                        results['categories'].append(cat)

            id_mapping = {}
            new_images = []
            for img in coco_data['images']:
                new_id = img['id'] + max_image_id + 1
                id_mapping[img['id']] = new_id
                img['id'] = new_id
                new_images.append(img)
                img_names.append(img['file_name'])
            results['images'].extend(new_images)
            new_annotations = []
            for ann in coco_data['annotations']:
                ann['id'] += max_annotation_id + 1
                ann['image_id'] = id_mapping.get(ann['image_id'], ann['image_id'])
                new_annotations.append(ann)
            results['annotations'].extend(new_annotations)
            for annotation_cnt, annotation in enumerate(results['annotations']):
                x_kp, y_kp, p_kp = annotation['keypoints'][::3], annotation['keypoints'][1::3], annotation['keypoints'][2::3]
                x_kp = [min(max(x, 0), max_width) for x in x_kp]
                y_kp = [min(max(x, 0), max_height) for x in y_kp]
                new_keypoints = [int(item) for trio in zip(x_kp, y_kp, p_kp) for item in trio]
                bps = np.stack([x_kp, y_kp], axis=1).reshape(1, -1, 2).astype(np.int32)
                bps = GeometryMixin().keypoints_to_axis_aligned_bounding_box(keypoints=bps)
                x_bbox, y_bbox = bps[:, 0].flatten(), bps[:, 1].flatten()
                x_min, y_min = int(min(x_bbox)), int(min(y_bbox))
                x_max, y_max = max(x_bbox), max(y_bbox)
                width, height = int(x_max - x_min), int(y_max - y_min)
                new_bbox= [x_min, y_min, width, height]
                results['annotations'][annotation_cnt]['keypoints'] = new_keypoints
                results['annotations'][annotation_cnt]['bbox'] = new_bbox
            max_image_id = max((img['id'] for img in results['images']), default=max_image_id)
            max_annotation_id = max((ann['id'] for ann in results['annotations']), default=max_annotation_id)

    duplicates = [item for item, count in Counter(img_names).items() if count > 1]
    if len(duplicates) > 0:
        DuplicateNamesWarning(msg=f'{len(duplicates)} annotated file names have the same name: {duplicates}', source=merge_coco_keypoints_files.__name__)

    timer.stop_timer()
    save_json(data=results, filepath=save_path)
    stdout_success(msg=f'Merged COCO key-points file (from {data_file_cnt} input files) saved at {save_path}', source=merge_coco_keypoints_files.__name__, elapsed_time=timer.elapsed_time_str)


DATA_DIR = r'D:\cvat_annotations\frames\coco_keypoints_1'
SAVE_PATH = r"D:\cvat_annotations\frames\coco_keypoints_1\TEST\merged_2.json"
merge_coco_keypoints_files(data_dir=DATA_DIR, save_path=SAVE_PATH, max_width=1280, max_height=720)