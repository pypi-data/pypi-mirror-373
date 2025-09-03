import pandas as pd
import numpy as np
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.image_mixin import ImageMixin
from simba.utils.read_write import read_img_batch_from_video_gpu, read_img_batch_from_video, get_video_meta_data, read_frm_of_video
import cv2

# video_path = "/mnt/c/troubleshooting/RAT_NOR/project_folder/videos/03152021_NOB_IOT_8.mp4"
# data_path = "/mnt/c/troubleshooting/RAT_NOR/project_folder/csv/outlier_corrected_movement_location/03152021_NOB_IOT_8.csv"
#
# get_video_meta_data(video_path)
# #video_path = '/mnt/c/troubleshooting/mitra/project_folder/videos/502_MA141_Gi_CNO_0514.mp4'
# #data_path = "/mnt/c/troubleshooting/mitra/project_folder/csv/outlier_corrected_movement_location/temp_3/502_MA141_Gi_CNO_0514.csv"
# #df = pd.read_csv(data_path, usecols=['Nose_x', 'Nose_y', 'Left_ear_x', 'Left_ear_y', 'Right_ear_x', 'Right_ear_y']).head(1000).fillna(0).values.astype(int)
# df = pd.read_csv(data_path, usecols=['Nose_x', 'Nose_y', 'Ear_left_x', 'Ear_left_y', 'Ear_right_x', 'Ear_right_y']).fillna(0).values.astype(int)
#
#
# data = df.reshape(len(df), -1, 2)
# #imgs = read_img_batch_from_video(video_path=video_path, start_frm=0, end_frm=999)
# #imgs = np.stack(list(imgs.values()))
# geometries = GeometryMixin().multiframe_bodyparts_to_polygon(data=data, parallel_offset=20, verbose=True)
#
#
#
# #img = GeometryMixin.view_shapes(shapes=[geometries[98]], bg_img=imgs[98])
# imgs = ImageMixin().slice_shapes_in_imgs(imgs=video_path, shapes=geometries, verbose=True)
#
# imgs = ImageMixin.pad_img_stack(image_dict=imgs, pad_value=0)
# ImageMixin().img_stack_to_video(imgs=imgs, fps=30, save_path=r'/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508/stacked.mp4')
#
#
# cv2.imshow('asdasdasd', imgs[450])
# cv2.waitKey(0)


#
#
# # imgs = ImageMixin.pad_img_stack(image_dict=imgs, pad_value=0)
# # del geometries
# #
# # #imgs = dict(sorted(imgs.items(), key=lambda item: int(item[0])))
# #
# #
# # #imgs = np.stack(list(imgs.values()))
# # ImageMixin().img_stack_to_video(imgs=imgs, fps=30, save_path=r'/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508/stacked.mp4')
# import time
#
#
# start = time.time()
#
# DATA_PATH = r"/mnt/d/netholabs/yolo_test/results/2025-05-28_19-50-23.csv"
# VIDEO_PATH = r"/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508/2025-05-28_19-50-23.mp4"
# BODY_PARTS = ['NOSE', 'EAR_LEFT', 'EAR_RIGHT']
# BP_COLS = [f'{i}_{j}' for i in BODY_PARTS for j in ['X', 'Y']]
# #
# data_df = pd.read_csv(DATA_PATH, usecols=BP_COLS)
# head_arr = data_df.values.astype(np.float32).reshape(len(data_df), len(BODY_PARTS), 2)
#
# polygons = GeometryMixin().multiframe_bodyparts_to_polygon(data=head_arr, parallel_offset=90)
# sliced_imgs = ImageMixin().slice_shapes_in_imgs(imgs=VIDEO_PATH, shapes=polygons, core_cnt=-1, verbose=True)
# img = ImageMixin.pad_img_stack(image_dict=sliced_imgs, pad_value=0)
# ImageMixin().img_stack_to_video(imgs=img, fps=30, save_path=r'/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508/stacked.mp4')
#
# elapsed = time.time() - start
# print(elapsed)
#
# frm_idx = np.array(range(0, len(data_df)))
#
# batches = np.array_split(frm_idx, 5)
#
# results = {}
# for batch_idx in batches:
#     batch_head_arr = head_arr[batch_idx[0]:batch_idx[-1], :, :]
#     #batch_head_arr = batch_head_arr.reshape(1, batch_head_arr.shape[0], batch_head_arr.shape[1], batch_head_arr.shape[2])
#     print(batch_idx[0], batch_idx[-1])
#     imgs = read_img_batch_from_video(video_path=VIDEO_PATH, start_frm=batch_idx[0], end_frm=batch_idx[-1]-1)
#     imgs = np.stack(list(imgs.values()))
#     polygons = GeometryMixin().multiframe_bodyparts_to_polygon(data=batch_head_arr, parallel_offset=75)
#     sliced_imgs = ImageMixin().slice_shapes_in_imgs(imgs=imgs, shapes=polygons, core_cnt=12, verbose=True)
#     sorted_dict = dict(sorted(sliced_imgs.items(), key=lambda item: int(item[0])))
#     print(sorted_dict.keys)
#     for cnt, (k, v) in enumerate(sorted_dict.items()):
#         results[batch_idx[cnt]] = v
#
#
#
# vals = set(list(results.values()))
#
# # print(results.keys())
#
# img = ImageMixin.pad_img_stack(image_dict=results, pad_value=0)
# #imgaes = np.stack(list(imgaes.values()))
#
# ImageMixin().img_stack_to_video(imgs=img, fps=30, save_path=r'/mnt/d/netholabs/yolo_videos/input/mp4_20250606083508/stacked.mp4')
#
#
# #
# polygons = GeometryMixin().multiframe_bodyparts_to_polygon(data=head_arr, parallel_offset=10)
# imgs = read_img_batch_from_video(video_path=VIDEO_PATH)
#
# img =read_img_batch_from_video_gpu(video_path=VIDEO_PATH)
#
#
# read_frm_of_video(video_path=VIDEO_PATH, frame_index=7000)
#
# get_video_meta_data(video_path=VIDEO_PATH)
#
#

