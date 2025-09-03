import os
import numpy as np
from itertools import combinations, product
import pandas as pd

from typing import Union
from simba.utils.checks import check_file_exist_and_readable, check_if_dir_exists, check_valid_dict
from simba.utils.read_write import read_json, create_directory, get_fn_ext, read_img
class COCO2LightningPose():


    def __init__(self,
                 coco_path: Union[str, os.PathLike],
                 img_dir: Union[str, os.PathLike],
                 save_dir: Union[str, os.PathLike],
                 scorer: str = 'simon '):

        check_if_dir_exists(in_dir=save_dir, source=f'{COCO2LightningPose.__name__} save_dir', raise_error=True)
        check_file_exist_and_readable(file_path=coco_path)
        self.lbl_data_dir = os.path.join(save_dir, 'labeled-data')
        self.csv_path = os.path.join(save_dir, 'CollectedData.csv')
        create_directory(paths=self.lbl_data_dir, overwrite=False)
        self.coco_data = read_json(x=coco_path)
        self.coco_path, self.scorer, self.img_dir = coco_path, scorer, img_dir
        check_if_dir_exists(in_dir=img_dir, source=f'{COCO2LightningPose.__name__} img_dir', raise_error=True)


    def run(self):
        check_valid_dict(x=self.coco_data, required_keys=('annotations', 'categories', 'images',), source=self.coco_path)
        categories = self.coco_data['categories']
        ids = list(set([x['id'] for x in self.coco_data['categories']]))
        bps = self.coco_data['categories'][0]['keypoints']
        bps_headers = [] #('scorer', 'bodyparts', 'coords')
        for id in ids:
            for bp in bps:
                bps_headers.append((self.scorer, f'{id}_{bp}', 'x'))
                bps_headers.append((self.scorer, f'{id}_{bp}', 'y'))
        results = pd.DataFrame(columns=pd.MultiIndex.from_tuples(bps_headers))
        for cnt, annotation_data in enumerate(self.coco_data['annotations']):
            img_data = self.coco_data['images'][cnt]
            _, img_name, ext = get_fn_ext(filepath=img_data['file_name'])
            check_valid_dict(x=annotation_data, required_keys=('keypoints', 'category_id', 'image_id',), source=f'{self.coco_path} cnt')
            kp = np.array(annotation_data['keypoints']).reshape(-1, 3).astype(np.float32)
            kp_mask = kp[:, -1] == 0
            kp[kp_mask] = np.nan
            kp = kp[:, 0:2].flatten()
            results.loc[len(results), :] = list(kp)
            img = read_img(img_path=self.img_file_paths[img_name], greyscale=self.greyscale, clahe=self.clahe)



x= COCO2LightningPose(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\test\merged_2.json",
                   img_dir=r"D:\cvat_annotations\frames\zipped_all_imgs\all_imgs_071325\all_imgs_071325",
                   save_dir=r"D:\cvat_annotations\frames\lightning_pose_data")
x.run()



