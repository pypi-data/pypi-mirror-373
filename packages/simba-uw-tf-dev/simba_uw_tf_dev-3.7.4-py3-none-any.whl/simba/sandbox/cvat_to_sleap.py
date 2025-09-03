import os

import sleap_io as sio
from pathlib import Path
import json
import numpy as np
from simba.utils.read_write import recursive_file_search, get_fn_ext, copy_files_to_directory, read_json
from simba.utils.checks import check_instance, check_if_keys_exist_in_dict
from simba.utils.enums import Options, Formats

IMG_DIR = r"D:\cvat_annotations\frames\to_annotate"
SAVE_DIR = r"D:\cvat_annotations\frames\all_imgs"

img_filenames = recursive_file_search(directory=IMG_DIR, extensions=['png'])
copy_files_to_directory(file_paths=img_filenames, dir=SAVE_DIR, verbose=True)

for filename in img_filenames:
    save_path = os.path.join(SAVE_DIR, get_fn_ext(filename)[1] + '.png')
    copy_files_to_directory(file_paths=img_filenames, dir=SAVE_DIR, verbose=True)






from typing import Union

from simba.utils.checks import check_if_dir_exists, check_file_exist_and_readable

def coco_keypoints_to_sleap_annotations(coco_path: Union[str, os.PathLike],
                                        img_dir: Union[str, os.PathLike],
                                        save_path: Union[str, os.PathLike]) -> None:

    check_file_exist_and_readable(file_path=coco_path, raise_error=True)
    check_if_dir_exists(in_dir=img_dir, source=f'{coco_keypoints_to_sleap_annotations} img_dir')
    check_if_dir_exists(in_dir=os.path.dirname(save_path), source=f'{coco_keypoints_to_sleap_annotations} save_path')
    annotations = read_json(x=coco_path)
    check_if_keys_exist_in_dict(data=annotations, key=('licenses', 'info', 'categories', 'images', 'annotations'), name=coco_path, raise_error=True)
    img_filenames = recursive_file_search(directory=img_dir, extensions=Options.ALL_IMAGE_FORMAT_OPTIONS.value, raise_error=True)

    node_names = annotations["categories"][0]["keypoints"]

    edges = annotations["categories"][0]["skeleton"]

    edge_inds = [(int(x[1]) - 1, int(x[0]) - 1) for x in edge_inds]
    edge_inds = [(int(x[1]) - 1, int(x[0]) - 1) for x in edge_inds]




ANNOTATION_PATH = r"D:\cvat_annotations\frames\coco_keypoints_1\merged.json"
IMG_DIR = r"D:\cvat_annotations\frames\to_annotate"
SAVE_DIR = r'D:\cvat_annotations\frames\slp\merged.v001.slp'

with open(ANNOTATION_PATH, "r") as f:
    annotations = json.load(f)

node_names = annotations["categories"][0]["keypoints"]
edge_inds = annotations["categories"][0]["skeleton"]

node_names = [str(x) for x in list(range(0, 9))]
edge_inds = [(int(x[1])-1, int(x[0])-1) for x in edge_inds]
skeleton = sio.Skeleton(nodes=node_names, edges=edge_inds)


img_filenames = recursive_file_search(directory=IMG_DIR, extensions=['png'])

fidx_by_id = {img["id"]: ind for ind, img in enumerate(annotations["images"])}

video = sio.load_video(img_filenames)


lfs_by_img_id = {}

for ann in annotations["annotations"]:

    img_id = ann["image_id"]
    fidx = fidx_by_id[img_id]

    kps = np.array(ann["keypoints"]).reshape(-1, 3)
    kps, vis = kps[:, :2], kps[:, 2]
    kps[vis == 0] = np.nan
    assert len(kps) == len(skeleton)

    if img_id not in lfs_by_img_id:
        lfs_by_img_id[img_id] = sio.LabeledFrame(video=video, frame_idx=fidx)

    lf = lfs_by_img_id[img_id]
    lf.instances.append(sio.Instance.from_numpy(kps, skeleton=skeleton))

labels = sio.Labels(list(lfs_by_img_id.values()))


labels.save(SAVE_DIR)
print("Saved:", SAVE_DIR)