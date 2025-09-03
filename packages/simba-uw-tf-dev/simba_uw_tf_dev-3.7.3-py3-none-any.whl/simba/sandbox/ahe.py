import cupy as cp
import numpy as np
from simba.utils.read_write import read_img_batch_from_video_gpu
from simba.utils.lookups import win_to_wsl_path


def ahe_gpu_batch_optimized(img_batch, tile_size=(8, 8), clip_limit=2.0):
    """
    Apply Adaptive Histogram Equalization (AHE) on a batch of images using GPU.

    Parameters:
        img_batch (cp.ndarray): Batch of grayscale images (B x H x W).
        tile_size (tuple): Size of the tiles (height, width).
        clip_limit (float): Clip limit for histogram equalization.

    Returns:
        cp.ndarray: Equalized image batch (B x H x W).
    """
    B, H, W = img_batch.shape
    tile_height, tile_width = tile_size

    # Create an empty array to store the processed images
    img_eq_batch = cp.zeros_like(img_batch)

    # Process all images and tiles in parallel
    for i in range(B):
        img = img_batch[i]

        # Create a 2D index grid to get tiles
        tile_indices = cp.indices((H // tile_height, W // tile_width))

        for y_idx, x_idx in zip(tile_indices[0].flatten(), tile_indices[1].flatten()):
            y_start = y_idx * tile_height
            x_start = x_idx * tile_width
            y_end = min(y_start + tile_height, H)
            x_end = min(x_start + tile_width, W)

            # Extract the tile
            tile = cp.ascontiguousarray(img[y_start:y_end, x_start:x_end])

            # Calculate histogram
            hist, bin_edges = cp.histogram(tile, bins=256, range=(0, 256))

            # Clip the histogram
            hist = cp.clip(hist, 0, clip_limit * cp.mean(hist))

            # Compute the cumulative distribution function (CDF)
            cdf = cp.cumsum(hist)
            cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())

            # Apply the histogram equalization
            tile_eq = cp.interp(tile, bin_edges[:-1], cdf)

            # Place the equalized tile back into the image
            img_eq_batch[i, y_start:y_end, x_start:x_end] = tile_eq

    # Return the result as a CuPy array (GPU memory)
    return img_eq_batch


video_path = r"/mnt/d/open_field_5/OFT_5.mp4"
import time

imgs = cp.ascontiguousarray(cp.array(read_img_batch_from_video_gpu(video_path=video_path, start_frm=0, end_frm=20, out_format='array', greyscale=True)))
start = time.perf_counter()
img_eq_batch = ahe_gpu_batch_optimized(img_batch=imgs, tile_size=(16, 16), clip_limit=2.0)
print(time.perf_counter()-start)