import cv2
import numpy as np
import os

# Video path
video_path = r"D:\weights\2025-04-17_17-17-14\output_combined.mp4"
cap = cv2.VideoCapture(video_path)

# Frame size and smoothing
frame_width = 640
frame_height = 480
smooth_factor = 0.1

# Frame buffer for sliding sum (N=1 for now)
N = 1
frame_buffer = []

# For stabilization
prev_offset_x = 0
prev_offset_y = 0

# Rectangle size
rect_w, rect_h = 225, 175

# Offsets to form 3x3 grid
grid_offsets = [(-rect_w, -rect_h), (0, -rect_h), (rect_w, -rect_h),
                (-rect_w, 0),     (0, 0),       (rect_w, 0),
                (-rect_w, rect_h), (0, rect_h), (rect_w, rect_h)]

# Setup output writers
output_writers = None
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
os.makedirs("grid_outputs", exist_ok=True)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    original = frame.copy()

    # Convert to HSV and create red mask
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Invert red mask to find non-red blobs
    non_red_mask = cv2.bitwise_not(red_mask)

    # Find contours
    contours = cv2.findContours(non_red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        northern_point = min(largest_contour, key=lambda point: point[0][1])  # y-min

        # Optional shift for better centering
        northern_point[0] = np.array([northern_point[0][0] + 20, northern_point[0][1]]).astype(np.int32)

        # Draw northern point
        cv2.circle(frame, tuple(northern_point[0]), 10, (0, 255, 0), -1)

        # Stabilize around that point
        offset_x = frame_width // 2 - northern_point[0][0]
        offset_y = frame_height // 2 - northern_point[0][1]
        offset_x = int(prev_offset_x + smooth_factor * (offset_x - prev_offset_x))
        offset_y = int(prev_offset_y + smooth_factor * (offset_y - prev_offset_y))
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        stabilized_frame = cv2.warpAffine(frame, M, (frame_width, frame_height), borderValue=(255, 255, 255))

        prev_offset_x, prev_offset_y = offset_x, offset_y

        # Create writers if first time
        if output_writers is None:
            output_writers = []
            for i in range(9):
                out_path = os.path.join("grid_outputs", f"roi_{i}.mp4")
                writer = cv2.VideoWriter(out_path, fourcc, fps, (rect_w, rect_h))
                output_writers.append(writer)

        # Extract and save grid regions
        for i, (dx, dy) in enumerate(grid_offsets):
            x1 = max(0, northern_point[0][0] + dx)
            y1 = max(0, northern_point[0][1] + dy)
            x2 = min(stabilized_frame.shape[1], x1 + rect_w)
            y2 = min(stabilized_frame.shape[0], y1 + rect_h)
            roi = stabilized_frame[y1:y2, x1:x2]

            if roi.shape[0] != rect_h or roi.shape[1] != rect_w:
                roi = cv2.resize(roi, (rect_w, rect_h))

            output_writers[i].write(roi)

    else:
        stabilized_frame = frame

    # Frame buffer
    frame_buffer.append(stabilized_frame)
    if len(frame_buffer) > N:
        frame_buffer.pop(0)

    if len(frame_buffer) == N:
        sliding_sum_frame = np.sum(frame_buffer, axis=0).astype(np.uint8)
    else:
        sliding_sum_frame = stabilized_frame

    # Show
    cv2.imshow("Stabilized Frame with Sliding Sum", sliding_sum_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
if output_writers:
    for writer in output_writers:
        writer.release()
cv2.destroyAllWindows()
