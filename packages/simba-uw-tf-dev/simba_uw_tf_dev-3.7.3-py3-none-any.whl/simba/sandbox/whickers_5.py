import cv2
import numpy as np
from collections import deque

# --- Settings ---
input_path = "D:/weights/2025-04-17_17-17-14/motion_blurred_sharpened.mp4"
output_path = "D:/weights/sum_sliding_output.mp4"
window_size = 5  # Number of frames to sum

# --- Setup ---
cap = cv2.VideoCapture(input_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# --- Sliding window buffer ---
buffer = deque(maxlen=window_size)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    buffer.append(frame.astype(np.float32))

    if len(buffer) == window_size:
        sum_frame = np.sum(buffer, axis=0)
        sum_frame = np.clip(sum_frame, 0, 255).astype(np.uint8)  # avoid overflow
        out.write(sum_frame)

# --- Cleanup ---
cap.release()
out.release()
print("Saved summed output to:", output_path)