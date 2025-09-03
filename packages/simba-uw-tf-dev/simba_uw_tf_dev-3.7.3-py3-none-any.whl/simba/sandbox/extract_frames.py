from simba.utils.read_write import find_files_of_filetypes_in_directory, get_fn_ext
import cv2
import os

VIDEO_DIR = r'D:\cvat_annotations\videos'
FRAMES_DIR = r'D:\cvat_annotations\frames'
video_paths = find_files_of_filetypes_in_directory(directory=VIDEO_DIR, extensions=['.mp4'], as_dict=True)



for video_name, video_path in video_paths.items():
    cap = cv2.VideoCapture(video_path)

    save_dir = os.path.join(FRAMES_DIR, video_name)
    os.makedirs(save_dir)

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_path = os.path.join(save_dir, f'{video_name}_{frame_idx:05d}.png')
        cv2.imwrite(frame_path, frame)
        frame_idx += 1
        print(video_name, frame_idx, f'{video_name}_{frame_idx:05d}.png')

    cap.release()