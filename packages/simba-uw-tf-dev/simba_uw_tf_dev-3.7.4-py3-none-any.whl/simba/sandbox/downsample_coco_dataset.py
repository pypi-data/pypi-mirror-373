import os
from typing import Union
import cv2
from copy import deepcopy

from simba.utils.read_write import find_files_of_filetypes_in_directory, read_json, get_fn_ext, read_img, copy_files_to_directory, save_json
from simba.utils.enums import Options
from simba.utils.checks import check_if_dir_exists, check_file_exist_and_readable, check_if_keys_exist_in_dict, check_int
from simba.utils.errors import NoFilesFoundError, FaultyTrainingSetError


def downsample_coco_dataset(json_path: Union[str, os.PathLike],
                            img_dir: Union[str, os.PathLike],
                            save_dir: Union[str, os.PathLike],
                            shrink_factor: int = 4,
                            verbose: bool = True):

    """
    Downsample a COCO-format dataset (images and annotations) by a fixed integer factor.

    This function resizes all images and updates annotation coordinates accordingly.
    Bounding box coordinates and keypoints (x, y only) are scaled by `shrink_factor`,
    while visibility flags in keypoints remain unchanged. The updated dataset is saved
    in COCO format to `save_dir`.

    :param Union[str, os.PathLike] json_path: Path to the input COCO JSON annotation file.
    :param Union[str, os.PathLike] img_dir: Directory containing the original images referenced in the JSON file.
    :param Union[str, os.PathLike] save_dir: Directory where resized images and updated COCO JSON will be stored.
    :param int shrink_factor: Factor by which to downsample both images and annotation coordinates. Must be >= 2. Default is 4.
    :param bool verbose: If True, prints progress information during processing. Default is True.
    :return None: Saves new images and updated COCO JSON to `save_dir`.

    :example:
    >>> downsample_coco_dataset(
    ...     json_path=r"D:\\cvat_annotations\\frames\\coco_keypoints_1\\merged\\merged_08132025.json",
    ...     img_dir=r"D:\\cvat_annotations\\frames\\all_imgs_071325",
    ...     save_dir=r"D:\\cvat_annotations\\frames\\resampled_coco_081225"
    ... )
    """

    check_file_exist_and_readable(file_path=json_path)
    check_if_dir_exists(in_dir=img_dir)
    check_if_dir_exists(in_dir=save_dir)
    check_int(name=f'{downsample_coco_dataset.__name__} shrink_factor', value=shrink_factor, min_value=2, raise_error=True)
    img_paths = find_files_of_filetypes_in_directory(directory=img_dir, extensions=Options.ALL_IMAGE_FORMAT_OPTIONS.value, raise_error=True, as_dict=True)
    coco_data = read_json(json_path)
    check_if_keys_exist_in_dict(data=coco_data, key=['licenses', 'info', 'categories', 'images', 'annotations'], name=json_path)
    out_coco = {'licenses': coco_data['licenses'], 'info': coco_data['info'], 'categories': coco_data['categories'], 'images': [], 'annotations': []}
    _, json_name, _ = get_fn_ext(filepath=json_path)
    out_coco_path = os.path.join(save_dir, f'{json_name}.json')
    img_cnt = len(coco_data['images'])

    for cnt in range(img_cnt):
        if verbose: print(f'Processing COCO image {cnt+1}/{img_cnt}...')
        img_data = coco_data['images'][cnt]
        new_img_data = deepcopy(img_data)
        check_if_keys_exist_in_dict(data=img_data, key=['width', 'height', 'file_name', 'id'], name=json_path)
        _, img_name, img_ext = get_fn_ext(filepath=img_data['file_name'])
        if not img_name in img_paths.keys():
            raise NoFilesFoundError(msg=f'The file {img_name} could not be found in the {img_dir} directory', source=downsample_coco_dataset.__name__)
        img = read_img(img_path=img_paths[img_name], greyscale=False, clahe=False)
        if (img.shape[0] != img_data['height']) or (img.shape[1] != img_data['width']):
            raise FaultyTrainingSetError(msg=f'Image {img_name} is of shape {img.shape[0]}x{img.shape[1]}, but the coco data has been annotated on an image of {img_data["height"]}x{img_data["width"]}.')
        new_img = img[::shrink_factor, ::shrink_factor, :]
        new_img_data['width'], new_img_data['height'] = new_img.shape[1], new_img.shape[0]
        out_coco['images'].append(new_img_data)
        img_annotations = [x for x in coco_data['annotations'] if x['image_id'] == img_data['id']]
        for img_annotation in img_annotations:
            check_if_keys_exist_in_dict(data=img_annotation, key=['bbox', 'keypoints', 'id', 'image_id', 'category_id'], name=json_path)
            new_img_annotation = deepcopy(img_annotation)
            new_img_annotation['bbox'] = ([int(v / shrink_factor) for v in img_annotation['bbox']])
            new_img_annotation['keypoints'] = [int(v / shrink_factor) if (i % 3 != 2) else v for i, v in enumerate(img_annotation['keypoints'])]
            out_coco['annotations'].append(new_img_annotation)
        img_save_path = os.path.join(save_dir, f'{img_name}{img_ext}')
        cv2.imwrite(filename=img_save_path, img=new_img)

    save_json(data=out_coco, filepath=out_coco_path)
    if verbose: print(f'New COCO data stored in {save_dir}.')


downsample_coco_dataset(json_path=r"D:\cvat_annotations\frames\coco_keypoints_1\merged\merged_08132025.json", img_dir=r'D:\cvat_annotations\frames\all_imgs_071325', save_dir=r'D:\cvat_annotations\frames\resampled_coco_081225')




