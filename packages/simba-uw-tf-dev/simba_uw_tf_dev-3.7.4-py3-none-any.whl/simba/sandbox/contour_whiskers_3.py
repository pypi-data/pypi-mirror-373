import numpy as np
import math
import cv2
from simba.utils.read_write import read_img_batch_from_video_gpu
from simba.utils.read_write import read_frm_of_video, read_df, get_video_meta_data
from simba.mixins.feature_extraction_mixin import FeatureExtractionMixin
from simba.utils.enums import Formats
from shapely.geometry import Polygon
from simba.mixins.image_mixin import ImageMixin

VIDEO_PATH = r"D:\troubleshooting\netholabs\original_videos\whiskers\tile_1_1_cropped.mp4"
DATA_PATH = r"D:\troubleshooting\netholabs\original_videos\whiskers\results\tile_1_1_cropped.csv"
SAVE_PATH = r"D:\troubleshooting\netholabs\original_videos\whiskers\out_video\step_3.mp4"


DATA_DF = read_df(file_path=DATA_PATH, file_type='csv')

def rotated_bounding_box(center, width, height, angle):
    rect = ((center[0], center[1]), (width, height), angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return box

video_meta_data = get_video_meta_data(video_path=VIDEO_PATH)
fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
video_writer = cv2.VideoWriter(SAVE_PATH, fourcc, 30, (video_meta_data["width"], video_meta_data["height"]))



sliced_imgs = {}
for frm_cnt, frm_idx in enumerate(range(450, 800)): #450, 800
    img = read_frm_of_video(video_path=VIDEO_PATH, frame_index=frm_idx)
    data = DATA_DF.iloc[frm_idx]
    center_cord = data[['center_x', 'center_y']].values.astype(np.int64)
    nose_cord = data[['nose_x', 'nose_y']].values.astype(np.int64)
    nape_cord = FeatureExtractionMixin.find_midpoints(bp_1=nose_cord.reshape(1, 2), bp_2=center_cord.reshape(1, 2), percentile=0.15)[0]
    bb_angle = math.degrees(math.atan2(center_cord[1] - nose_cord[1], center_cord[0] - nose_cord[0]))
    whisker_box = rotated_bounding_box(center=nape_cord, height=300, width=200, angle=bb_angle)
    whisker_polygon = Polygon(whisker_box)

    sliced_imgs[frm_cnt] = ImageMixin.slice_shapes_in_img(img=img, geometries=[whisker_polygon])[0]
    cv2.imshow('sasdasd', sliced_imgs[frm_cnt])
    cv2.waitKey(33)

sliced_imgs = ImageMixin.resize_img_dict(imgs=sliced_imgs, size='max')

imgs = np.stack(list(sliced_imgs.values()), axis=0)
ImageMixin.img_stack_to_video(imgs=sliced_imgs, fps=30, save_path=SAVE_PATH)

    #img = cv2.polylines(img, [whisker_box], isClosed=True, color=(0, 0, 255), thickness=15)



    #img = cv2.circle(img, tuple(center_cord), 30, (0, 0, 255), -1)
    #img = cv2.circle(img, tuple(nape_cord), 30, (255, 255, 255), -1)
    #img = cv2.circle(img, tuple(nose_cord), 30, (0, 0, 255), -1)
    #cv2.imshow('sasdasd', img)
    #cv2.waitKey(33)
    #video_writer.write(img.astype(np.uint8))

video_writer.release()

