import pickle
from simba.utils.read_write import get_video_meta_data, read_frm_of_video
import cv2
import numpy as np
from collections import deque

DATA_PATH = r"D:\weights\2025-04-17_17-17-14\annotations_2025-04-17_17-17-14_1.h264_nose.pkl"
VIDEO_PATH = r"D:\weights\2025-04-17_17-17-14\2025-04-17_17-17-14_1.h264.mp4"
SAVE_PATH = r"D:\weights\2025-04-17_17-17-14\2025-04-17_17-17-14.h264_out_whiskers.mp4"

video_meta_data = get_video_meta_data(video_path=VIDEO_PATH)
with open(DATA_PATH, 'rb') as f: data = pickle.load(f)

MASK_COLORS = [(0, 255, 255), (255, 0, 0), (0, 0, 255)]
ALPHA = 0.5


fourcc = cv2.VideoWriter_fourcc(*'FFV1')
video_writer = cv2.VideoWriter(SAVE_PATH, fourcc, video_meta_data["fps"], (video_meta_data['width'], video_meta_data['height']))
for frm_id in range(0, 201):
    frm = read_frm_of_video(video_path=VIDEO_PATH, frame_index=frm_id)
    out_img = np.copy(frm)
    img_masks = data[frm_id]

    for mask_id, mask in img_masks.items():
        overlay = np.zeros_like(out_img, dtype=np.uint8)
        overlay[mask[0] > 0] = MASK_COLORS[mask_id]  # Color only where mask > 0
        mask_area = (mask[0] > 0)[..., None]  # Shape (H, W, 1) for broadcasting
        out_img = np.where(mask_area, (ALPHA * overlay + (1 - ALPHA) * out_img).astype(np.uint8), out_img)
    cv2.imshow('Masked Frame', out_img)
    cv2.waitKey(33)
    video_writer.write(out_img.astype(np.uint8))
    #cv2.destroyAllWindows()

video_writer.release()

    #break