import cv2
import time
import os

def measure_video_read_speed(video_path, num_frames=100):
    """Measure how long it takes to read first N frames of a video"""
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {video_path}")
    
    # Get video info
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video: {total_frames} frames, {fps} FPS")
    
    # Measure read time
    start_time = time.time()
    frames_read = 0
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
        frames_read += 1
    
    total_time = time.time() - start_time
    cap.release()
    
    fps_achieved = frames_read / total_time if total_time > 0 else 0
    print(f"Read {frames_read} frames in {total_time:.3f}s = {fps_achieved:.1f} FPS")
    
    return total_time, fps_achieved

if __name__ == "__main__":
    video_path = r"D:\netholabs\temporal_stitching\videos\video1.mp4"  # Change this path
    
    if os.path.exists(video_path):
        measure_video_read_speed(video_path, num_frames=100)
    else:
        print(f"Video file not found: {video_path}") 