import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import h5py
import itertools
from typing import Tuple, Union, List
from simba.utils.checks import check_if_dir_exists, check_file_exist_and_readable, check_str, check_valid_tuple, check_if_keys_exist_in_dict
from simba.utils.read_write import find_files_of_filetypes_in_directory, create_directory, read_json, get_fn_ext, copy_files_to_directory
from simba.utils.enums import Options
from simba.utils.errors import NoFilesFoundError
import yaml

class Coco2DLC:

    """
    :example:
    >>> x = Coco2DLC(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\merged\merged_08132025.json", img_dir=r'D:\cvat_annotations\frames\all_imgs_071325', project_path=r'D:\coco_dlc', verbose=False)
    >>> x.run()
    """

    def __init__(self,
                 coco_path: str,
                 img_dir: str,
                 project_path: str,
                 bp_names: Tuple[str] = ('Nose', 'Left_ear', 'Right_ear', 'Left_side', 'Center', 'Right_side', 'Tail_base', 'Tail_center', 'Tail_tip'),
                 skeleton: List[List[int]] = [[0, 1], [0, 2], [2, 1], [1, 3], [2, 4], [3, 5], [1, 5], [2, 5], [5, 4], [5, 6], [3, 6], [4, 6]],
                 experimenter_name: str = 'simon',
                 verbose: bool = True):

        check_if_dir_exists(in_dir=img_dir, source=self.__class__.__name__)
        check_file_exist_and_readable(file_path=coco_path, raise_error=True)
        check_if_dir_exists(in_dir=os.path.dirname(project_path), source=self.__class__.__name__)
        check_valid_tuple(x=bp_names, source=self.__class__.__name__, valid_dtypes=(str,))
        check_str(name=f'{self.__class__.__name__} experimenter_name', value=experimenter_name, allow_blank=False)
        self.coco_path, self.img_dir, self.project_path = coco_path, img_dir, project_path
        self.experimenter_name, self.bp_names = experimenter_name, bp_names
        self.img_paths = find_files_of_filetypes_in_directory(directory=self.img_dir, extensions=Options.ALL_IMAGE_FORMAT_OPTIONS.value, as_dict=True, raise_error=True)
        self.skeleton, self.verbose = skeleton, verbose
        self.data_cols =[f"{bp}_x" for bp in bp_names] + [f"{bp}_y" for bp in bp_names]
        self.data_cols.insert(0, 'frame')
        print(self.data_cols)



    def run(self):
        self.coco_data = read_json(x=self.coco_path)

        check_if_keys_exist_in_dict(data=self.coco_data, key=['categories', 'images', 'annotations'], name=self.coco_path)
        self.img_cnt = len(self.coco_data['images'])
        lbl_data_dir = os.path.join(self.project_path, 'labeled-data')
        train_datasets_dir = os.path.join(self.project_path, 'training-datasets')
        train_videos_dir = os.path.join(self.project_path, 'videos')
        dlc_models_dir = os.path.join(self.project_path, 'dlc-models')
        logs_dir = os.path.join(self.project_path, 'logs')
        create_directory(paths=[lbl_data_dir, train_datasets_dir, train_videos_dir, dlc_models_dir, logs_dir], overwrite=True)

        self.dfs, video_sets = {}, {}
        for cnt in range(len(self.coco_data['images']))[:300]:
            img_data = self.coco_data['images'][cnt]
            check_if_keys_exist_in_dict(data=img_data, key=['width', 'height', 'file_name', 'id'], name=self.coco_path)
            _, img_name, ext = get_fn_ext(filepath=img_data['file_name'])
            if self.verbose:
                print(f'Processing annotation {cnt + 1}/{self.img_cnt} from COCO to YOLO ({img_name})...')
            if not img_name in self.img_paths.keys():
                raise NoFilesFoundError(msg=f'The file {img_name} could not be found in the {self.img_dir} directory', source=self.__class__.__name__)
            dir_name = img_name.split('_')[0]
            dir_path = os.path.join(lbl_data_dir, dir_name)
            create_directory(paths=[dir_path], overwrite=False)
            copy_files_to_directory(file_paths=self.img_paths[img_name], dir=dir_path, verbose=True)
            video_sets[os.path.join(lbl_data_dir, dir_name)] = {'crop': ', '}
            if dir_path not in self.dfs.keys():
                self.dfs[dir_path] = pd.DataFrame(columns=self.data_cols)
            img_annotations = [x for x in self.coco_data['annotations'] if x['image_id'] == img_data['id']]
            for img_annotation in img_annotations:
                check_if_keys_exist_in_dict(data=img_annotation, key=['bbox', 'keypoints', 'id', 'image_id', 'category_id'], name=str(self.coco_path))
                kps = np.array(img_annotation['keypoints']).reshape(-1, 3).astype(np.float32)
                mask = (kps[:, -1] == 0.0) | (kps[:, -1] == 1.0)
                kps[mask, :] = np.nan
                kps = kps[:, :2].flatten()
                kps = [f'{img_name}{ext}'] + kps.tolist()
                self.dfs[dir_path].loc[len(self.dfs[dir_path])] = kps

        scorer_vals = (self.experimenter_name,) * (len(self.bp_names) * 2)
        bodyparts_vals = tuple(bp for bp in self.bp_names for _ in (0, 1))
        coords_vals = ("x", "y") * len(self.bp_names)
        headers = pd.MultiIndex.from_tuples(zip(scorer_vals, bodyparts_vals, coords_vals), names=["scorer", "bodyparts", "coords"])
        headers = headers.insert(0, (None, None, None))


        for df_path, df_data in self.dfs.items():
            csv_path = os.path.join(df_path, f'CollectedData_{self.experimenter_name}.csv')
            df_data.insert(0, os.path.basename(df_path), [os.path.basename(df_path)] * len(df_data))
            df_data.insert(0, "labeled-data", ["labeled-data"] * len(df_data))
            df_data = df_data.set_index(["labeled-data", os.path.basename(df_path)])
            df_data.columns = headers
            df_data.to_csv(csv_path)


        # Enhanced config with all required DLC 3.0 fields
        self.config = {
            'Task': os.path.basename(self.project_path),
            'scorer': self.experimenter_name,
            'date': datetime.today().strftime("%Y-%m-%d"),
            'multianimalproject': {'identity': {}},
            'project_path': self.project_path,
            'engine': 'pytorch',
            'video_sets': video_sets,
            'bodyparts': list(self.bp_names),
            'start': None,
            'stop': None,
            'numframes2pick': None,
            'skeleton': self.skeleton,
            'skeleton_color': None,
            'pcutoff': None,
            'dotsize': None,
            'alphavalue': None,
            'colormap': None,
            'TrainingFraction': [0.95],
            'iteration': 0,
            'net_type': 'hrnet_w32',
            'method': 'bu',
            'batch_size': 8,
            'snapshotindex': -1,
            'detector_snapshotindex': -1,
            'detector_batch_size': 1,

            # DLC 3.0 specific configurations
            'train_settings': {
                'batch_size': 8,
                'epochs': 200,
                'dataloader_workers': 0
            },

            'model': {
                'backbone': {
                    'type': 'HRNet',
                    'model_name': 'hrnet_w32'
                }
            },

            'runner': {
                'type': 'PoseTrainingRunner',
                'gpus': [0],  # Will auto-detect if GPU available
                'key_metric': 'test.mAP',
                'key_metric_asc': True,
                'eval_interval': 10,
                'optimizer': {
                    'type': 'AdamW',
                    'params': {'lr': 0.0005}
                },
                'scheduler': {
                    'type': 'LRListScheduler',
                    'params': {
                        'lr_list': [[0.0001], [1e-05]],
                        'milestones': [90, 120]
                    }
                },
                'snapshots': {
                    'max_snapshots': 5,
                    'save_epochs': 25,
                    'save_optimizer_state': False
                }
            },

            # SuperAnimal configuration
            'SuperAnimalConversionTables': {
                'detector_type': 'fasterrcnn_resnet50_fpn_v2',
                'labeled-data': 'labeled-data',
                'super_animal': 'superanimal_topviewmouse'
            },

            # Weight initialization paths (will be auto-updated during training)
            'weight_init': {
                'dataset': 'superanimal_topviewmouse',
                'snapshot_path': None,  # Will be set by build_weight_init
                'detector_snapshot_path': None,  # Will be set by build_weight_init
                'with_decoder': False,
                'memory_replay': False
            }
        }
        with open(os.path.join(self.project_path, 'config.yaml'), 'w') as f:
            yaml.dump(self.config , f, default_flow_style=False)


x = Coco2DLC(coco_path=r"D:\cvat_annotations\frames\coco_keypoints_1\merged\merged_08132025.json", img_dir=r'D:\cvat_annotations\frames\all_imgs_071325', project_path=r'D:\coco_dlc', verbose=False)
x.run()







