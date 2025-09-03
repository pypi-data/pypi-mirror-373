import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import pandas as pd
import numpy as np
from typing import Union,Optional, List
from simba.data_processors.cuda.utils import _is_cuda_available
try:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results
except ModuleNotFoundError:
    YOLO = None
    Results = None
try:
    from ultralytics import SAM
except ModuleNotFoundError:
    SAM = None
from copy import deepcopy

try:
    from typing import Literal
except:
    from typing_extensions import Literal

from simba.utils.data import resample_geometry_vertices
from simba.utils.yolo import load_yolo_model, check_valid_device
from simba.utils.checks import (check_file_exist_and_readable, check_float, check_if_dir_exists, check_int, check_str, check_valid_boolean, check_valid_lst, get_fn_ext)
from simba.utils.read_write import get_video_meta_data, find_core_cnt, read_frm_of_video, read_img
from simba.utils.errors import InvalidFileTypeError, SimBAGPUError, SimBAPAckageVersionError
from simba.model.yolo_inference import YoloInference
from simba.model.yolo_pose_inference import YOLOPoseInference
from simba.utils.data import detect_bouts

CONFIDENCE = ['CONFIDENCE']



def get_sam_results_from_ultralytics_obj(sam_results: Results,
                                         max_w: Optional[int] = None,
                                         max_h: Optional[int] = None,
                                         vertice_cnt: Optional[int] = 50) -> Union[None, List[np.ndarray]]:
    if sam_results.names is None:
        return None
    results = []
    max_w = np.inf if max_w is None else max_w
    max_h = np.inf if max_h is None else max_h
    for detection in sam_results.masks:
        mask = detection.xy[0].astype(np.int64)
        mask[:, 0] = np.clip(mask[:, 0], 0, max_w)
        mask[:, 1] = np.clip(mask[:, 1], 0, max_h)
        if vertice_cnt is not None: mask = resample_geometry_vertices(vertices=mask.reshape(1, len(mask), 2), vertice_cnt=vertice_cnt)[0]
        results.append(mask)
    return results

def sam_img_inference(data: Union[np.ndarray, str, os.PathLike],
                      mdl: SAM,
                      vertice_cnt: int,
                      img_idx: Optional[int] = None,
                      bboxes: np.ndarray = None,
                      points: np.ndarray = None):

    if isinstance(data, (str, os.PathLike)):
        if get_video_meta_data(video_path=data, raise_error=False) is not None:
            img = read_frm_of_video(video_path=data, frame_index=img_idx)
        else:
            img = read_img(img_path=data)
    else:
        img = deepcopy(data)

    if bboxes is not None:
        bboxes = bboxes.astype(np.int64)

    labels = np.full(shape=(1, points.shape[1]), fill_value=1, dtype=np.int8) if points is not None else None
    results = mdl(source=img, bboxes=bboxes, points=points, labels=labels)[0]
    return get_sam_results_from_ultralytics_obj(sam_results=results, vertice_cnt=vertice_cnt)


class Yolo4SamInference():

    def __init__(self,
                 yolo_mdl: Union[str, os.PathLike],
                 sam_mdl: Union[str, os.PathLike],
                 video_path: Union[Union[str, os.PathLike], List[Union[str, os.PathLike]]],
                 verbose: Optional[bool] = False,
                 save_dir: Optional[Union[str, os.PathLike]] = None,
                 half_precision: Optional[bool] = True,
                 device: Union[Literal['cpu'], int] = 0,
                 batch_size: Optional[int] = 4,
                 core_cnt: int = 8,
                 threshold: float = 0.25,
                 max_detections: int = 300,
                 imgsz: int = 640,
                 stream: Optional[bool] = True,
                 vertice_cnt: int = 100):


        if not _is_cuda_available()[0]:
            raise SimBAGPUError(msg='No GPU detected.', source=self.__class__.__name__)
        if YOLO is None:
            raise (SimBAPAckageVersionError(msg='ultralytics.YOLO package not detected.', source=self.__class__.__name__))
        if SAM is None:
            raise (SimBAPAckageVersionError(msg='ultralytics.SAM package not detected.', source=self.__class__.__name__))
        if isinstance(video_path, list):
            check_valid_lst(data=video_path, source=f'{self.__class__.__name__} video_path', valid_dtypes=(str, np.str_,), min_len=1)
        elif isinstance(video_path, str):
            check_file_exist_and_readable(file_path=video_path)
            video_path = [video_path]
        for i in video_path:
            _ = get_video_meta_data(video_path=i)
        check_file_exist_and_readable(file_path=yolo_mdl)
        check_file_exist_and_readable(file_path=sam_mdl)
        check_valid_boolean(value=[half_precision, verbose, stream], source=self.__class__.__name__)
        check_int(name=f'{self.__class__.__name__} batch_size', value=batch_size, min_value=1)
        check_int(name=f'{self.__class__.__name__} imgsz', value=imgsz, min_value=1)
        check_float(name=f'{self.__class__.__name__} threshold', value=threshold, min_value=0.0, max_value=1.0)
        check_int(name=f'{self.__class__.__name__} max_detections', value=max_detections, min_value=1)
        check_int(name=f'{self.__class__.__name__} vertice_cnt', value=vertice_cnt, min_value=1)
        check_int(name=f'{self.__class__.__name__} core_cnt', value=core_cnt, min_value=1, max_value=find_core_cnt()[0])
        check_valid_device(device=device)
        if save_dir is not None:
            check_if_dir_exists(in_dir=save_dir, source=f'{self.__class__.__name__} save_dir')
        self.model = load_yolo_model(weights_path=yolo_mdl, verbose=verbose, device=device)
        #self.sam_mdl = load_sam_model(mdl_path=sam_mdl)
        self.sam_mdl = SAM(model=sam_mdl)
        self.video_path, self.half_precision, self.stream, self.batch_size = video_path, half_precision, stream, batch_size
        self.save_dir, self.verbose, self.imgsz, self.core_cnt, self.device = save_dir, verbose, imgsz, core_cnt,device
        self.threshold, self.max_detections, self.vertice_cnt = threshold, max_detections, vertice_cnt
        if self.model.model.task not in ['pose', 'segment']:
            raise InvalidFileTypeError(msg=f'The model {yolo_mdl} is not a pose/segment model. It is a {self.model.model.task} model', source=self.__class__.__name__)
        self.vertice_col_names = ['FRAME', 'NAME']
        for i in range(self.vertice_cnt):
            self.vertice_col_names.append(f"VERTICE_{i}_x"); self.vertice_col_names.append(f"VERTICE_{i}_y")

    def run(self):
        for video_path in self.video_path:
            _, video_name, _ = get_fn_ext(filepath=video_path)
            video_save_path = os.path.join(self.save_dir, f'{video_name}.csv')
            video_meta_data = get_video_meta_data(video_path=video_path)
            if self.model.model.task == 'segment':
                yolo_inferencer = YoloInference(weights=self.model, video_path=video_path, verbose=False)
            else:
                yolo_inferencer = YOLOPoseInference(weights=self.model, video_path=video_path, verbose=False, stream=self.stream, box_threshold=self.threshold)
            results = yolo_inferencer.run()[video_name]
            results['VISIBLE'] = (results['CONFIDENCE'].astype(np.float32) != -1.0).astype(np.int8)
            bouts = detect_bouts(data_df=results, target_lst=['VISIBLE'], fps=1)
            bout_frms = [i for s, e in zip(bouts['Start_frame'], bouts['End_frame']) for i in range(s, e+1)]
            video_results = pd.DataFrame(columns=self.vertice_col_names, index=range(video_meta_data['frame_count']))
            video_results.loc[:, :] = -1
            video_results['FRAME'] = list(range(0, video_meta_data['frame_count']))
            for img_idx in bout_frms:
                frm_res = results[results['FRAME'] == img_idx]
                bbox = results[['X1', 'Y1', 'X3', 'Y3']][results['FRAME'] == img_idx].values.astype(np.int32)
                if self.model.model.task == 'pose':
                    points = frm_res[yolo_inferencer.keypoint_col_names].values.reshape(-1, 3).astype(np.float32)
                    points = points[points[:, 2] > self.threshold][:, 0:2].astype(np.int32)
                    points = points.reshape(-1, points.shape[0], 2) if points.shape[0] > 0 else None
                else:
                    points = None
                if points is None:
                    continue
                img_results = sam_img_inference(data=video_path, mdl=self.sam_mdl, img_idx=img_idx, bboxes=None, vertice_cnt=self.vertice_cnt, points=points)
                for img_result in img_results:
                    img_result = img_result.flatten()
                    img_result = np.insert(img_result, 0, 0)
                    img_result = np.insert(img_result, 0, int(img_idx))
                    video_results.loc[video_results['FRAME'] == img_idx] = img_result
                #break
                #print(img_idx)
           # break
            video_results = video_results.fillna(-1)
            video_results.to_csv(video_save_path)
           #
           #
           #













r = Yolo4SamInference(yolo_mdl=r"D:\cvat_annotations\yolo_mdl_07122025\weights\best.pt",
                      video_path=r"D:\cvat_annotations\videos\mp4_20250624155703\s34-drinking.mp4",
                      sam_mdl=r"D:\yolo_weights\sam2.1_b.pt",
                      save_dir=r'D:\cvat_annotations\sam_yolo_data',
                      threshold=0.9)
r.run()

