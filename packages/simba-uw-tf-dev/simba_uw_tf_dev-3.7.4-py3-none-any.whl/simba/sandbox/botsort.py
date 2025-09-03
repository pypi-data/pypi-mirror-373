from simba.bounding_box_tools.yolo.model import load_yolo_model
import numpy as np
from typing import Callable, Optional
from simba.utils.enums import Formats
from simba.utils.errors import InvalidInputError
import pandas as pd

from simba.utils.checks import check_valid_array, check_int, check_float

OUT_COLS = ['FRAME', 'CLASS_ID', 'CLASS_NAME', 'CONFIDENCE', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4', 'TRACK']
THRESHOLD = 0.9
WEIGHTS_PATH = r"/mnt/d/netholabs/yolo_mdls_1/train/weights/best.pt"
VIDEO_PATH = "/mnt/d/netholabs/videos_/mp4/2025-05-27_00-35-36.mp4"
BOTSORT_PATH = "/mnt/c/projects/simba/simba/simba/assets/botsort.yml"
keypoint_names = ('nose', 'ear_left', 'ear_right', 'lateral_left', 'center', 'lateral_right', 'tail_base')

mdl = load_yolo_model(weights_path=WEIGHTS_PATH, verbose=True, format='onnx')
keypoint_col_names = [f'{i}_{s}'.upper() for i in keypoint_names for s in ['x', 'y', 'p']]
OUT_COLS.extend(keypoint_col_names)
video_predictions = mdl.track(source=VIDEO_PATH, stream=False, tracker=BOTSORT_PATH, persist=True)
class_dict = mdl.names

#filtered = [x for x in video_predictions if x.boxes.shape[0] != 0]
filtered = video_predictions
results = {}


def filter_yolo_keypoint_data(bbox_data: np.ndarray,
                              keypoint_data: np.ndarray,
                              class_id: Optional[int] = None,
                              confidence: Optional[float] = None,
                              class_idx: int = 6,
                              confidence_idx: int = 5):
    """
    Helper to filters YOLO bounding box and keypoint data based on class ID and/or confidence threshold.

    :param np.ndarray bbox_data: A 2D array of shape (N, M) representing YOLO bounding box data, where each row corresponds to one detection and contains class and confidence values.
    :param np.ndarray bbox_data: A 3D array of shape (N, 2, 3) representing keypoints for each detection, where K is the number of keypoints per detection.
    :param Optional[int] class_id: Target class ID to filter detections. Defaults to None.
    :param Optional[float] confidence: Minimum confidence threshold to keep detections. Must be in [0, 1]. Defaults to None.
    :param int confidence_idx: Index in `bbox_data` where confidence value is stored. Defaults to 5.
    :param int class_idx: Index in `bbox_data` where class ID is stored. Defaults to 6.
    """

    if class_id is None and confidence is None:
        raise InvalidInputError(msg='Provide at least one filter condition')

    check_valid_array(data=bbox_data, source=filter_yolo_keypoint_data.__name__, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_axis_0=1)
    check_valid_array(data=keypoint_data, source=filter_yolo_keypoint_data.__name__, accepted_ndims=(3,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[bbox_data.shape[0],])
    class_id is not None and check_int(name=filter_yolo_keypoint_data.__name__, value=class_id, min_value=0, raise_error=True)
    confidence is not None and check_float(name=filter_yolo_keypoint_data.__name__, value=confidence, min_value=0, max_value=1.0, raise_error=True)
    check_int(name=filter_yolo_keypoint_data.__name__, value=class_idx, min_value=0, max_value=bbox_data.shape[1])
    check_int(name=filter_yolo_keypoint_data.__name__, value=confidence_idx, min_value=0, max_value=bbox_data.shape[1])

    if class_id is not None:
        cls_idx = np.argwhere(bbox_data[:, class_idx] == c).flatten()
        bbox_data, keypoint_data = bbox_data[cls_idx], keypoint_data[cls_idx]
    if confidence_idx is not None:
        cls_idx = np.argwhere(bbox_data[:, confidence_idx] >= THRESHOLD).flatten()
        bbox_data, keypoint_data = bbox_data[cls_idx], keypoint_data[cls_idx]

    return bbox_data, keypoint_data



        #print(bbox_data)

    pass

video_out = []
for frm_cnt, video_prediction in enumerate(filtered):
    if video_prediction.obb is not None:
        boxes = np.array(video_prediction.obb.data.cpu()).astype(np.float32)
    else:
        boxes = np.array(video_prediction.boxes.data.cpu()).astype(np.float32)
    keypoints = np.array(video_prediction.keypoints.data.cpu()).astype(np.float32)
    for c in list(class_dict.keys()):
        if boxes.shape[1] != 7: boxes = np.insert(boxes, 4, -1, axis=1)
        if boxes.shape[0] == 0:
            frm_results = np.array([frm_cnt, c, class_dict[c], -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
            frm_results = np.append(frm_results, [-1] * len(keypoint_col_names))
            video_out.append(frm_results)
        else:
            boxes, keypoints = filter_yolo_keypoint_data(bbox_data=boxes, keypoint_data=keypoints, class_id=c, confidence=THRESHOLD)
            if boxes.shape[0] == 0:
                frm_results = np.array([frm_cnt, c, class_dict[c], -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
                frm_results = np.append(frm_results, [-1] * len(keypoint_col_names))
                video_out.append(frm_results)
            else:
                for i in range(boxes.shape[0]):
                    box = np.array([boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][1], boxes[i][2], boxes[i][3], boxes[i][0], boxes[i][3]]).astype(np.int32)
                    frm_results = np.array([frm_cnt, boxes[i][-1], class_dict[boxes[i][-1]], boxes[i][-2], boxes[i][-3]] + list(box))
                    frm_results = np.append(frm_results, keypoints[i].flatten())
                    video_out.append(frm_results)


results['1'] = pd.DataFrame(video_out, columns=OUT_COLS)

results['1'].to_csv("/mnt/d/netholabs/videos_/mp4/test.csv")

        # cls_idx = np.argwhere(boxes[:, -1] == c).flatten()
        # cls_boxes, cls_keypoints = boxes[cls_idx], keypoints[cls_idx]
        #
        # if len(cls_boxes) > 0:
        #     filter_yolo_keypoint_data(bbox_data=cls_boxes, keypoint_data=cls_keypoints, class_id=c)
        #
        # #
        #
        # cls_idx = np.argwhere(cls_boxes[:, 5] >= THRESHOLD)



        #cls_boxes = cls_boxes.reshape(-1, 7)[cls_boxes.reshape(-1, 7)[:, 5] > THRESHOLD]
        # print(cls_idx)
        #filtered_cls_frm_boxes = cls_boxes.reshape(-1, 6)[cls_boxes.reshape(-1, 6)[:, 4] > THRESHOLD]


