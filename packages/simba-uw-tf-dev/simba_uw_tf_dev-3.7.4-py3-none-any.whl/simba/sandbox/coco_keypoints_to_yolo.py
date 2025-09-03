import os
from copy import copy, deepcopy
import numpy as np
import cv2
import random
import yaml

from typing import Union, Tuple, Dict, Optional
from simba.utils.read_write import read_json, find_files_of_filetypes_in_directory, get_fn_ext, read_img, create_directory, save_json
from simba.utils.checks import check_file_exist_and_readable, check_if_keys_exist_in_dict, check_if_dir_exists, check_float, check_valid_dict, check_valid_tuple
from simba.utils.enums import Options
from simba.utils.errors import NoFilesFoundError, FaultyTrainingSetError, InvalidInputError
from simba.utils.printing import SimbaTimer, stdout_success

def create_yolo_keypoint_yaml(path: Union[str, os.PathLike],
                              train_path: Union[str, os.PathLike],
                              val_path: Union[str, os.PathLike],
                              names: Dict[str, int],
                              kpt_shape: Tuple[int, int],
                              flip_idx: Tuple[int, ...],
                              save_path: Optional[Union[str, os.PathLike]] = None,
                              use_wsl_paths: bool = False) -> Union[None, dict]:
    """
    Given a set of paths to directories, create a model.yaml file for yolo pose model training though ultralytics wrappers.

    .. seealso::
       Used by :func:`simba.sandbox.coco_keypoints_to_yolo.coco_keypoints_to_yolo`

    :param Union[str, os.PathLike] path: Parent directory holding both an images and a labels directory.
    :param Union[str, os.PathLike] train_path: Directory holding training images. For example, if C:\troubleshooting\coco_data\images\train is passed, then a C:\troubleshooting\coco_data\labels\train is expected.
    :param Union[str, os.PathLike] val_path: Directory holding validation images. For example, if C:\troubleshooting\coco_data\images\test is passed, then a C:\troubleshooting\coco_data\labels\test is expected.
    :param Union[str, os.PathLike] test_path: Directory holding test images. For example, if C:\troubleshooting\coco_data\images\validation is passed, then a C:\troubleshooting\coco_data\labels\validation is expected.
    :param Dict[str, int] names: Dictionary mapping pairing object names to object integer identifiers. E.g., {'OBJECT 1': 0, 'OBJECT 2`: 2}
    :param Union[str, os.PathLike] save_path: Optional location where to save the yolo model yaml file. If None, then the dict is returned.
    :param bool use_wsl_paths: If True, use Windows WSL paths (e.g., `/mnt/...`) in the config file.
    :return None:
    """

    class InlineList(list):
        pass

    def represent_inline_list(dumper, data):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

    yaml.add_representer(InlineList, represent_inline_list)
    for p in [path, train_path, val_path]:
        check_if_dir_exists(in_dir=p, source=create_yolo_keypoint_yaml.__name__)
    check_valid_dict(x=names, valid_key_dtypes=(int,), valid_values_dtypes=(str,), min_len_keys=1)
    unique_paths = list({path, train_path, val_path})
    if len(unique_paths) < 3:
        raise InvalidInputError('The passed paths have to be unique.', source=create_yolo_keypoint_yaml.__name__)
    if save_path is not None:
        check_if_dir_exists(in_dir=os.path.dirname(save_path), source=f'{create_yolo_keypoint_yaml.__name__} save_path')
        if save_path in [path, train_path, val_path]:
            raise InvalidInputError('The save path cannot be the same as the other passed directories.', source=f'{create_yolo_keypoint_yaml.__name__} save_path')

    train_path = os.path.relpath(train_path, path)
    val_path = os.path.relpath(val_path, path)

    data = {'path': path,
            'train': train_path,  # train images (relative to 'path')
            'val': val_path,
            'kpt_shape': InlineList(list(kpt_shape)),
            'flip_idx': InlineList(list(flip_idx)),
            'names': names}

    if save_path is not None:
        with open(save_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    else:
        return data


def coco_keypoints_to_yolo(coco_path: Union[str, os.PathLike],
                           img_dir: Union[str, os.PathLike],
                           save_dir: Union[str, os.PathLike],
                           train_size: float = 0.7,
                           flip_idx: Tuple[int, ...] = (0, 2, 1, 3, 5, 4, 6),
                           verbose: bool = True):
    """
    Convert COCO Keypoints version 1.0 data format into a YOLO keypoints training set.

    :param Union[str, os.PathLike] coco_path: Path to coco keypoints 1.0 file in json format.
    :param Union[str, os.PathLike] img_dir: Directory holding img files representing the annotated entries in the ``coco_path``.
    :param Union[str, os.PathLike] save_dir: Directory where to save the yolo formatted data.
    :param Tuple[float, float, float] split: The size of the training set. Value between 0-1.0 representing the percent of training data.
    :param bool verbose: If true, prints progress. Default: True.
    :param Tuple[int, ...] flip_idx: Tuple of ints, representing the flip of body-part coordinates when the animal image flips 180 degrees.
    :return: None

    :example:
    >>> coco_path = r"D:\netholabs\imgs_vcat\batch_1\batch_1\coco_annotations\person_keypoints_default.json"
    >>> coco_keypoints_to_yolo(coco_path=coco_path, img_dir=r'D:\netholabs\imgs_vcat\batch_1', save_dir=r"D:\netholabs\imgs_vcat\batch_1\batch_1\yolo_annotations")
    """

    timer = SimbaTimer(start=True)
    check_file_exist_and_readable(file_path=coco_path)
    check_if_dir_exists(in_dir=save_dir)
    check_float(name=f'{coco_keypoints_to_yolo.__name__} train_size', value=train_size, max_value=0.99, min_value=0.1)
    train_img_dir, val_img_dir = os.path.join(save_dir, 'images', 'train'), os.path.join(save_dir, 'images', 'val')
    train_lbl_dir, val_lbl_dir = os.path.join(save_dir, 'labels', 'train'), os.path.join(save_dir, 'labels', 'val')
    for i in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        create_directory(paths=i, overwrite=True)
    map_path = os.path.join(save_dir, 'map.yaml')
    coco_data = read_json(x=coco_path)
    check_if_keys_exist_in_dict(data=coco_data, key=['categories', 'images', 'annotations'], name=coco_path)
    map_dict = {i['id']: i['name'] for i in coco_data['categories']}
    map_ids = list(map_dict.keys())
    if sorted(map_ids) != list(range(len(map_ids))):
        map_id_lk = {} # old: new
        new_map_dict = {}
        for cnt, v in enumerate(sorted(map_ids)):
            map_id_lk[v] = cnt
        for k, v in map_id_lk.items():
            new_map_dict[v] = map_dict[k]
        map_dict = copy(new_map_dict)
    else:
        map_id_lk = {k: k for k in map_dict.keys()}

    img_file_paths = find_files_of_filetypes_in_directory(directory=img_dir, extensions=Options.ALL_IMAGE_FORMAT_OPTIONS.value, raise_error=True, as_dict=True)
    img_cnt = len(coco_data['images'])
    img_idx = list(range(len(coco_data['images'])+1))
    train_idx = random.sample(img_idx, int(img_cnt * train_size))
    check_valid_tuple(x=flip_idx, source=coco_keypoints_to_yolo.__name__, valid_dtypes=(int,), minimum_length=1)
    shapes = []
    for cnt in range(len(coco_data['images'])):
    #for cnt in range(10):
        img_data = coco_data['images'][cnt]
        check_if_keys_exist_in_dict(data=img_data, key=['width', 'height', 'file_name', 'id'], name=coco_path)
        _, img_name, ext = get_fn_ext(filepath=img_data['file_name'])
        if verbose:
            print(f'Processing annotation {cnt+1}/{img_cnt} ({img_name})...')
        if not img_name in img_file_paths.keys():
            raise NoFilesFoundError(msg=f'The file {img_name} could not be found in the {img_dir} directory', source=coco_keypoints_to_yolo.__name__)
        img = read_img(img_path=img_file_paths[img_name])
        if (img.shape[0] != img_data['height']) or (img.shape[1] != img_data['width']):
            raise FaultyTrainingSetError(msg=f'Image {img_name} is of shape {img.shape[0]}x{img.shape[1]}, but the coco data has been annotated on an image of {img_data["height"]}x{img_data["width"]}.')
        img_annotations = [x for x in coco_data['annotations'] if x['image_id'] == img_data['id']]
        roi_str = ''
        if cnt in train_idx:
            label_save_path = os.path.join(train_lbl_dir, f'{img_name}.txt')
            img_save_path = os.path.join(train_img_dir, f'{img_name}.png')
        else:
            label_save_path = os.path.join(val_lbl_dir, f'{img_name}.txt')
            img_save_path = os.path.join(val_img_dir, f'{img_name}.png')
        for img_annotation in img_annotations:
            check_if_keys_exist_in_dict(data=img_annotation, key=['bbox', 'keypoints', 'id', 'image_id', 'category_id'], name=coco_path)
            x1, y1 = img_annotation['bbox'][0], img_annotation['bbox'][1]
            w, h = img_annotation['bbox'][2], img_annotation['bbox'][3]
            x_center =  (x1 + (w / 2)) / img_data['width']
            y_center = (y1 + (h / 2)) / img_data['height']
            w = img_annotation['bbox'][2] / img_data['width']
            h = img_annotation['bbox'][3] / img_data['height']
            roi_str += ' '.join([f"{map_id_lk[img_annotation['category_id']]}", str(x_center), str(y_center), str(w), str(h), ' '])
            kps = np.array(img_annotation['keypoints']).reshape(-1, 3).astype(np.int32)
            x, y, v = kps[:, 0], kps[:, 1],  kps[:, 2]
            x, y = x / img_data['width'], y / img_data['height']
            shapes.append(x.shape[0])
            kps = list(np.column_stack((x, y, v)).flatten())
            roi_str += ' '.join(str(x) for x in kps) + '\n'

        with open(label_save_path, mode='wt', encoding='utf-8') as f:
            f.write(roi_str)
        cv2.imwrite(img_save_path, img)
    if len(list(set(shapes))) > 1:
        raise InvalidInputError(msg=f'The annotation data {coco_path} contains more than one keypoint shapes: {set(shapes)}', source=coco_keypoints_to_yolo.__name__)
    if len(flip_idx) != shapes[0]:
        raise InvalidInputError(msg=f'flip_idx contains {len(flip_idx)} values but {shapes[0]} keypoints detected per image in coco data.', source=coco_keypoints_to_yolo.__name__)
    missing = [x for x in flip_idx if x not in list(range(shapes[0]))]
    if len(missing) > 0:
        raise InvalidInputError(msg=f'flip_idx contains index values not in keypoints ({missing}).', source=coco_keypoints_to_yolo.__name__)
    missing = [x for x in list(range(shapes[0])) if x not in flip_idx]
    if len(missing) > 0:
        raise InvalidInputError(msg=f'keypoints contains index values not in flip_idx ({missing}).', source=coco_keypoints_to_yolo.__name__)

    create_yolo_keypoint_yaml(path=save_dir, train_path=train_img_dir, val_path=val_img_dir, names=map_dict, save_path=map_path, kpt_shape=(int(shapes[0]), 3), flip_idx=flip_idx)
    timer.stop_timer()
    if verbose: stdout_success(msg=f'COCO keypoints to YOLO conversion complete. Data saved in directory {save_dir}.', elapsed_time=timer.elapsed_time_str)


def merge_coco_keypoints_files(data_dir: Union[str, os.PathLike],
                               save_path: Union[str, os.PathLike]):

    """
    Merges multiple COCO-format keypoints JSON files into a single file.

    .. note::
       Image and annotation entries are appended after adjusting their `id` fields to be unique.

    :param Union[str, os.PathLike] data_dir: Directory containing multiple COCO keypoints `.json` files to merge.
    :param Union[str, os.PathLike] save_path: File path to save the merged COCO keypoints JSON.
    :return: None. Results are saved in ``save_path``.
    """

    data_files = find_files_of_filetypes_in_directory(directory=data_dir, extensions=['.json'], raise_error=True, raise_warning=False, as_dict=True)
    check_if_dir_exists(in_dir=os.path.dirname(save_path))
    results, max_image_id, max_annotation_id = None, 0, 0
    data_file_cnt = len(data_files)

    for file_cnt, (file_name, file_path) in enumerate(data_files.items()):
        print(f'Processing {file_cnt + 1}/{data_file_cnt} ({file_name})...')
        coco_data = read_json(file_path)
        check_if_keys_exist_in_dict(data=coco_data, key=['licenses', 'info', 'categories', 'images', 'annotations'], name=file_name)

        if file_cnt == 0:
            results = deepcopy(coco_data)
            max_image_id = max((img['id'] for img in results['images']), default=0)
            max_annotation_id = max((ann['id'] for ann in results['annotations']), default=0)
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
            results['images'].extend(new_images)
            new_annotations = []
            for ann in coco_data['annotations']:
                ann['id'] += max_annotation_id + 1
                ann['image_id'] = id_mapping.get(ann['image_id'], ann['image_id'])
                new_annotations.append(ann)
            results['annotations'].extend(new_annotations)
            max_image_id = max((img['id'] for img in results['images']), default=max_image_id)
            max_annotation_id = max((ann['id'] for ann in results['annotations']), default=max_annotation_id)

    save_json(data=results, filepath=save_path)
    stdout_success(msg=f'COCO keypoints file saved at {save_path}', source=merge_coco_keypoints_files.__name__)

#merge_coco_keypoints_files(data_dir=r'C:\Users\sroni\Downloads\batch_2\annotations', save_path=r'C:\Users\sroni\Downloads\batch_2\data.json')


#coco_keypoints_to_yolo

#coco_path = r"D:\netholabs\imgs_vcat\batch_1\batch_1\coco_annotations\person_keypoints_default.json"
coco_keypoints_to_yolo(coco_path=r'C:\Users\sroni\Downloads\batch_2\data.json', img_dir=r'D:\netholabs\annotated_img_keypoints', save_dir=r"D:\netholabs\yolo_data_1")



