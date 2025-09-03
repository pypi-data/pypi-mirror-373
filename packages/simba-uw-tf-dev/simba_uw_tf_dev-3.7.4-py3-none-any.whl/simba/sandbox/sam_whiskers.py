import pickle
from simba.utils.read_write import get_video_meta_data, read_frm_of_video
import cv2
import numpy as np
from collections import deque

DATA_PATH = r"D:\weights\2025-04-17_17-17-14\annotations_2025-04-17_17-17-14_1.h264_nose.pkl"
VIDEO_PATH = r"D:\weights\2025-04-17_17-17-14\2025-04-17_17-17-14_1.h264.mp4"
SAVE_PATH = r"D:\weights\2025-04-17_17-17-14\2025-04-17_17-17-14.h264_out_whiskers_4.mp4"

video_meta_data = get_video_meta_data(video_path=VIDEO_PATH)
with open(DATA_PATH, 'rb') as f: data = pickle.load(f)

fourcc = cv2.VideoWriter_fourcc(*'FFV1')
video_writer = cv2.VideoWriter(SAVE_PATH, fourcc, video_meta_data["fps"], (175, 300))
N = 20 # number of frames to smooth over
rect_buffer = deque(maxlen=N)
cropped_frames = []

for frm_id in range(0, video_meta_data['frame_count'] -1):
    frm = read_frm_of_video(video_path=VIDEO_PATH, frame_index=frm_id)
    out_img = np.copy(frm)
    mask = data[frm_id][0][0]

    points = cv2.findNonZero(mask.astype(np.uint8))
    if points is None:
        continue  # skip if no foreground

    rect = cv2.minAreaRect(points)
    (center, _, angle) = rect

    # Use fixed box size (optional)
    box_size = (175, 300)
    rect_buffer.append((center, angle))

    # Wait until we have enough frames to smooth
    if len(rect_buffer) < N:
        continue

    # Smooth center and angle over last N frames
    smoothed_center = np.mean([r[0] for r in rect_buffer], axis=0)
    smoothed_angle = np.mean([r[1] for r in rect_buffer])

    smoothed_rect = (tuple(smoothed_center), box_size, smoothed_angle)
    rotation_matrix = cv2.getRotationMatrix2D(tuple(smoothed_center), float(smoothed_angle), 1.0)


    # Rotate the full frame
    rotated = cv2.warpAffine(out_img, rotation_matrix, (out_img.shape[1], out_img.shape[0]))

    # Get corner points of the rect, transform them
    box = cv2.boxPoints(smoothed_rect)
    box = cv2.transform(np.array([box]), rotation_matrix)[0].astype(int)

    # Crop bounding region
    x_coords, y_coords = zip(*box)
    x_min, x_max = max(min(x_coords), 0), min(max(x_coords), rotated.shape[1])
    y_min, y_max = max(min(y_coords), 0), min(max(y_coords), rotated.shape[0])

    cropped = rotated[y_min:y_max, x_min:x_max]
    cropped = cv2.resize(cropped, (175, 300), interpolation=cv2.INTER_LANCZOS4)

    cropped_frames.append(cropped)
    #video_writer.write(cropped.astype(np.uint8))
    cv2.imshow('sasdasd', cropped)
    cv2.waitKey(33)



    #     box = np.int0(cv2.boxPoints(rot_rect_enlarged))
    #     drawn = cv2.cvtColor(frm_masks.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
    #     out_img = cv2.drawContours(out_img, [box], 0, (0, 165, 255), 5)
    # cv2.imshow('sasdasd', out_img)
    # cv2.waitKey(33)
    # video_writer.write(out_img.astype(np.uint8))

#video_writer.release()

