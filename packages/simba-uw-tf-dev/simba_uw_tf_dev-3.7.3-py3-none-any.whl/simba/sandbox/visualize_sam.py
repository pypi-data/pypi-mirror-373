import pickle
from simba.utils.read_write import get_video_meta_data, read_frm_of_video
import cv2
import numpy as np

DATA_PATH = r"D:\weights\annotations.pkl"
VIDEO_PATH = r"D:\weights\whisking_example.mp4"
SAVE_PATH = r"D:\weights\whisking_example_sam.mp4"

video_meta_data = get_video_meta_data(video_path=VIDEO_PATH)
with open(DATA_PATH, 'rb') as f: data = pickle.load(f)
cv2.VideoWriter()
video_writer = cv2.VideoWriter(SAVE_PATH, cv2.VideoWriter_fourcc(*"mp4v"), video_meta_data["fps"], (video_meta_data["width"], video_meta_data["height"]))

ALPHA = 0.7
COLORS = {0: (0, 255, 255), 1: (0, 255, 0), 2: (255, 255, 0)}

for frm_id in range(video_meta_data['frame_count']-1):
    frm = read_frm_of_video(video_path=VIDEO_PATH, frame_index=frm_id)
    overlay = frm.copy()
    for mask_id, mask in data[frm_id].items():
        #if mask_id == 0:
        overlay[mask[0]] = COLORS[mask_id]
    overlay = cv2.addWeighted(frm, 1-ALPHA, overlay, ALPHA, 0)
    cv2.imshow('Orange Mask Overlay', overlay)
    cv2.waitKey(33)
    video_writer.write(overlay.astype(np.uint8))

video_writer.release()



#
# overlay = frm.copy()
#
#
# blended = cv2.addWeighted(frm, 1 - 0.5, overlay, 0.5, 0)
#
# cv2.imshow('Orange Mask Overlay', blended)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
# #


