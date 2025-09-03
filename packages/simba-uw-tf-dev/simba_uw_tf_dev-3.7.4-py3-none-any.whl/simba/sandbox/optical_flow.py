import os
from typing import Union

import numpy as np
import cv2
from simba.utils.read_write import read_img_batch_from_video
import time
from numba import jit, prange
from simba.mixins.image_mixin import ImageMixin
from simba.utils.enums import Formats

@jit(nopython=True)
def resize_img_stack(imgs: np.ndarray,
                     scale_factor: float = 0.25) -> np.ndarray:
    """
    Resizes a stack of images by applying a scaling factor to each image in the stack. Uses bilinear interpolation.

    .. note::
       Pass gresyscale images.

    :param np.ndarray imgs: 3D numpy array of shape (N, H, W). All images are expected to have the same shape.
    :param float scale_factor: A float that determines the scaling factor for resizing each image. A value of 0.5 will reduce the size by  half.
    :return: A 3D numpy array of the resized images, with shape (N, Nh, Nw), where Nh and Nw are the new height and width calculated by applying the `scale_factor` to the original height and width.
    :rtype: np.ndarray

    :example:
    >>> VIDEO_PATH = r"D:\EPM_2\EPM_1.mp4"
    >>> img = read_img_batch_from_video(video_path=VIDEO_PATH, greyscale=True, start_frm=0, end_frm=15, core_cnt=1)
    >>> imgs = np.stack(list(img.values()))
    >>> resized_img = resize_img_stack(imgs=imgs)
    """

    Nh, Nw = int(imgs.shape[1] * scale_factor), int(imgs.shape[2] * scale_factor)
    results = np.empty((imgs.shape[0], Nh, Nw), dtype=imgs.dtype)
    for t in prange(imgs.shape[0]):
        for i in range(Nh):
            for j in range(Nw):
                orig_x = min(int(j / scale_factor), imgs.shape[2] - 1)
                orig_y = min(int(i / scale_factor), imgs.shape[1] - 1)
                if orig_x + 1 < imgs.shape[2] and orig_y + 1 < imgs.shape[1]:
                    dx = (j / scale_factor) - orig_x
                    dy = (i / scale_factor) - orig_y
                    top_left = imgs[t, orig_y, orig_x]
                    top_right = imgs[t, orig_y, orig_x + 1]
                    bottom_left = imgs[t, orig_y + 1, orig_x]
                    bottom_right = imgs[t, orig_y + 1, orig_x + 1]
                    top = top_left + dx * (top_right - top_left)
                    bottom = bottom_left + dx * (bottom_right - bottom_left)
                    results[t, i, j] = top + dy * (bottom - top)
                else:
                    results[t, i, j] = imgs[t, orig_y, orig_x]
    return results

@jit(nopython=True)
def resize_optical_flow(flow: np.ndarray, new_h: int, new_w: int, scale_factor: float):
    """
    Resize an optical flow field while preserving the correct motion vector scale.

    Parameters:
    - flow: (T, H, W, 2) numpy array containing optical flow (X, Y components)
    - new_h: Target height after resizing
    - new_w: Target width after resizing
    - scale_factor: The factor by which the flow vectors need to be adjusted

    Returns:
    - Resized optical flow (T, new_h, new_w, 2) with correctly scaled motion vectors
    """
    T, H, W, _ = flow.shape
    resized_flow = np.zeros((T, new_h, new_w, 2), dtype=np.float32)

    for t in range(T):
        for c in range(2):  # Flow has two channels: X and Y components
            resized_flow[t, :, :, c] = cv2.resize(flow[t, :, :, c], (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Scale the flow vectors to maintain the correct motion
        resized_flow[t, :, :, 0] *= (new_w / W)  # Scale X component
        resized_flow[t, :, :, 1] *= (new_h / H)  # Scale Y component

    return resized_flow


@jit(nopython=True, parallel=True)
def resize_optical_flow(flow: np.ndarray, scale_factor: float):
    """
    Resize an optical flow field using bilinear interpolation while preserving motion vector scale.

    Parameters:
    - flow: (T, H, W, 2) numpy array containing optical flow (X, Y components)
    - scale_factor: The factor by which the flow vectors need to be adjusted

    Returns:
    - Resized optical flow (T, new_H, new_W, 2) with correctly scaled motion vectors
    """
    T, H, W, C = flow.shape
    new_H, new_W = int(H * scale_factor), int(W * scale_factor)

    resized_flow = np.zeros((T, new_H, new_W, 2), dtype=np.float32)

    for t in prange(T):  # Parallel over time frames
        for i in prange(new_H):
            for j in prange(new_W):
                # Compute corresponding source coordinates in the original image
                src_x = j / scale_factor
                src_y = i / scale_factor

                # Find the four surrounding pixels
                x0, y0 = int(src_x), int(src_y)
                x1, y1 = min(x0 + 1, W - 1), min(y0 + 1, H - 1)

                # Compute interpolation weights
                wx1, wy1 = src_x - x0, src_y - y0
                wx0, wy0 = 1.0 - wx1, 1.0 - wy1

                for c in range(C):  # X and Y components
                    # Bilinear interpolation
                    v00 = flow[t, y0, x0, c]
                    v01 = flow[t, y1, x0, c]
                    v10 = flow[t, y0, x1, c]
                    v11 = flow[t, y1, x1, c]

                    interpolated_value = (
                        wx0 * wy0 * v00 + wx0 * wy1 * v01 +
                        wx1 * wy0 * v10 + wx1 * wy1 * v11
                    )

                    # Store resized flow and scale the vectors properly
                    resized_flow[t, i, j, c] = interpolated_value * scale_factor

    return resized_flow


# Compute optical flow between consecutive frames
def get_optical_flow(frames: np.ndarray,
                     fps: int,
                     time_interval: float = 0.5) -> np.ndarray:
    """
    Compute optical flow for frames with skipping based on the provided FPS and time interval.
    Then interpolate the optical flow to generate flow for every frame.

    :param frames: A numpy array of shape (T, H, W) representing the stack of frames.
    :param fps: The frames per second of the video.
    :param time_interval: Time interval (in seconds) between optical flow computations.
    :return: A numpy array of interpolated optical flow for every frame with shape (T, H, W, 2).
    """

    T, H, W = frames.shape
    frame_interval = int(fps * time_interval)

    optical_flows, times = [], []

    # Loop over the frames with a step of frame_interval
    for i in range(0, T - frame_interval, frame_interval):
        prev_frame = frames[i]
        next_frame = frames[i + frame_interval]

        # Calculate optical flow between frames
        flow = cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        optical_flows.append(flow)
        times.append(i)  # Store the time index for the flow calculation

    # Create a 3D array for the interpolated optical flows
    interpolated_flows = np.full((T, H, W, 2), 0.0, dtype=np.float32)  # Optical flow for every frame with NaNs

    # Linear interpolation for the flow components (u and v)
    for t in range(1, T):  # Skip the first frame as it has no optical flow
        print(t)
        # Find the closest computed optical flow points
        prev_idx = max([i for i in range(len(times)) if times[i] <= t], default=None)
        next_idx = min([i for i in range(len(times)) if times[i] >= t], default=None)

        # Handle the case where no valid prev_idx or next_idx are found
        if prev_idx is None:
            # If no previous time is found, just use NaN or default value for the first frame
            interpolated_flows[t] = np.nan  # Or you can use -1 for invalid flow
        elif next_idx is None:
            # If no next time is found, just use NaN or default value for the last frame
            interpolated_flows[t] = np.nan  # Or you can use -1 for invalid flow
        else:
            prev_flow = optical_flows[prev_idx]
            next_flow = optical_flows[next_idx]

            # Get the time indices for the prev and next flow points
            t_prev = times[prev_idx]
            t_next = times[next_idx]

            # Check if the time difference is zero to avoid division by zero
            if t_prev == t_next:
                # If both time indices are the same, use the same flow (no interpolation needed)
                interpolated_flows[t] = prev_flow
            else:
                # Linear interpolation of optical flow vectors (u and v)
                ratio = (t - t_prev) / (t_next - t_prev)  # Interpolation ratio
                interpolated_flows[t] = (1 - ratio) * prev_flow + ratio * next_flow

    return interpolated_flows

# Main function to resize images, compute optical flow, and scale the result
def compute_resized_optical_flow(imgs: np.ndarray,
                                 fps: Union[float, int],
                                 time_interval: Union[float, int],
                                 scale_factor: float = 0.5):

    # Step 1: Resize the images
    resized_imgs = resize_img_stack(imgs, scale_factor)

    # Step 2: Compute optical flow on resized images
    optical_flow_resized = get_optical_flow(resized_imgs, fps=fps, time_interval=time_interval)
    results = resize_optical_flow(flow=optical_flow_resized, scale_factor=1/scale_factor)
    return results

    # # Step 3: Rescale the optical flow back to the original image size
    # # Create an empty list to store scaled optical flow results
    # optical_flow_scaled = []
    #
    # results = resize_img_stack(optical_flow_scaled, scale_factor)
    #
    # for flow in optical_flow_resized:
    #     print('s')
    #     # Scale the flow vectors (dx, dy) to the original size
    #     flow_scaled = cv2.resize(flow, (imgs.shape[2], imgs.shape[1]), interpolation=cv2.INTER_LINEAR)
    #     optical_flow_scaled.append(flow_scaled)
    #
    # return optical_flow_scaled

#



def show_optical_flow(imgs: np.ndarray, save_path: Union[str, os.PathLike]):
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video_writer = cv2.VideoWriter(save_path, fourcc, 15, (imgs.shape[2], imgs.shape[1]))

    # Iterate through the flow frames
    for frm in imgs:
        # Ensure each frame has the flow components (x, y)
        if frm.shape[-1] != 2:
            raise ValueError("Each frame in imgs should have 2 channels for flow (x, y components).")

        # Convert flow to magnitude and angle
        magnitude, angle = cv2.cartToPolar(frm[..., 0], frm[..., 1])

        # Normalize magnitude to [0, 1] for visualization
        magnitude = np.clip(magnitude / np.max(magnitude), 0, 1)

        # Create an HSV image with magnitude and angle
        hsv = cv2.merge([angle / (2 * np.pi), np.ones_like(magnitude), magnitude])

        # Convert the HSV image to BGR
        bgr_flow = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Write the frame to the video
        video_writer.write((bgr_flow * 255).astype(np.uint8))  # Multiply by 255 to scale it to [0, 255]

    # Release the video writer
    video_writer.release()

VIDEO_PATH = r"D:\EPM_2\EPM_1.mp4"
img = read_img_batch_from_video(video_path=VIDEO_PATH,
                                greyscale=True,
                                start_frm=3000,
                                end_frm=3500,
                                core_cnt=1)
imgs = np.stack(list(img.values()))

start = time.time()
results = compute_resized_optical_flow(imgs=imgs, fps=30, time_interval=2)
end = time.time() - start
print(end)
show_optical_flow(imgs=results, save_path=r'C:\Users\sroni\OneDrive\Desktop\optical_flow.mp4')

#cv2.imshow('asdasdasd', resized_img[0])
#cv2.waitKey(0)

# start = time.time()
# of = batch_optical_flow(frames=imgs)
# end = time.time() - start






#
#
# def batch_optical_flow(frames: np.ndarray,
#                        scale=0.25) -> np.ndarray:
#     """
#     Compute dense optical flow for a batch of grayscale frames using Farneback method.
#
#     :param frames: NumPy array of shape (T, H, W) representing the grayscale frames.
#     :param scale: Scaling factor for speedup (e.g., 0.5 for 50% downscaling).
#     :return: NumPy array of shape (T-1, H, W, 2) with flow vectors (dx, dy).
#     """
#     T, H, W = frames.shape
#     optical_flows = np.zeros((T - 1, H, W, 2), dtype=np.float32)
#
#     for i in range(T - 1):
#         small_prev = cv2.resize(frames[i], (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
#         small_next = cv2.resize(frames[i + 1], (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
#         flow_small = cv2.calcOpticalFlowFarneback(small_prev, small_next, None, pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
#         flow_large = cv2.resize(flow_small, (W, H), interpolation=cv2.INTER_LINEAR)
#         flow_large *= 1 / scale  # Adjust magnitude due to resizing
#
#         optical_flows[i] = flow_large
#
#     return optical_flows  # Shape (T-1, H, W, 2)