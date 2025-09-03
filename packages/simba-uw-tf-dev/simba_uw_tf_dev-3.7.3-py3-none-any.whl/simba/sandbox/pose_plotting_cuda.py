import os
from typing import Union, Optional
import numpy as np
from numba import cuda
import math

from simba.utils.checks import check_file_exist_and_readable, check_if_dir_exists, check_valid_array, check_int, check_valid_boolean
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import get_video_meta_data, read_df, read_img_batch_from_video_gpu
from simba.utils.errors import FrameRangeError
from simba.mixins.plotting_mixin import PlottingMixin
from simba.utils.data import create_color_palette
from simba.utils.enums import Formats
import cv2

@cuda.jit(max_registers=None)
def _pose_plot_kernel(imgs, data, circle_size, resolution, colors):
    bp_n, img_n = cuda.grid(2)
    if img_n < 0 or img_n > (imgs.shape[0] -1):
        return
    if bp_n < 0 or bp_n > (data[0].shape[0] -1):
        return

    img, bp_loc, color  = imgs[img_n], data[img_n][bp_n], colors[bp_n]
    for x1 in range(bp_loc[0]-circle_size[0], bp_loc[0]+circle_size[0]):
        for y1 in range(bp_loc[1]-circle_size[0], bp_loc[1]+circle_size[0]):
            if (x1 > 0) and (x1 < resolution[0]):
                if (y1 > 0) and (y1 < resolution[1]):
                    b = (x1 - bp_loc[0]) ** 2
                    c = (y1 - bp_loc[1]) ** 2
                    if (b + c) < (circle_size[0] ** 2):
                        imgs[img_n][y1][x1][0] = int(color[0])
                        imgs[img_n][y1][x1][1] = int(color[1])
                        imgs[img_n][y1][x1][2] = int(color[2])


def pose_plotter(data: Union[str, os.PathLike, np.ndarray],
                 video_path: Union[str, os.PathLike],
                 save_path: Union[str, os.PathLike],
                 circle_size: Optional[int] = None,
                 colors: Optional[str] = 'Set1',
                 batch_size: int = 1500,
                 verbose: bool = True) -> None:

    """
    Creates a video overlaying pose-estimation data on frames from a given video using GPU acceleration.

    :param Union[str, os.PathLike, np.ndarray] data: Path to a CSV file with pose-estimation data or a 3d numpy array (n_images, n_bodyparts, 2) with pose-estimated locations.
    :param Union[str, os.PathLike] video_path: Path to a video file where the ``data`` has been pose-estimated.
    :param Union[str, os.PathLike] save_path: Location where to store the output visualization.
    :param Optional[int] circle_size: The size of the circles representing the location of the pose-estimated locations. If None, the optimal size will be inferred as a 100th of the max(resultion_w, h).
    :param int batch_size: The number of frames to process concurrently on the GPU. Default: 1500. Increase of host and device RAM allows it to improve runtime.

    :example:
    >>> DATA_PATH = "/mnt/c/troubleshooting/mitra/project_folder/csv/outlier_corrected_movement_location/501_MA142_Gi_CNO_0514.csv"
    >>> VIDEO_PATH = "/mnt/c/troubleshooting/mitra/project_folder/videos/501_MA142_Gi_CNO_0514.mp4"
    >>> SAVE_PATH = "/mnt/c/troubleshooting/mitra/project_folder/frames/output/pose_ex/test.mp4"
    >>> pose_plotter(data=DATA_PATH, video_path=VIDEO_PATH, save_path=SAVE_PATH, circle_size=10)
    """

    THREADS_PER_BLOCK = (32, 32, 1)
    if isinstance(data, str):
        check_file_exist_and_readable(file_path=data)
        df = read_df(file_path=data, file_type='csv')
        cols = [x for x in df.columns if not x.lower().endswith('_p')]
        data = df[cols].values
        data = np.ascontiguousarray(data.reshape(data.shape[0], int(data.shape[1] / 2), 2).astype(np.int32))
    elif isinstance(data, np.ndarray):
        check_valid_array(data=data, source=pose_plotter.__name__, accepted_ndims=(3,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)

    check_int(name=f'{pose_plotter.__name__} batch_size', value=batch_size, min_value=1)
    check_int(name=f'{pose_plotter.__name__} circle_size', value=circle_size, min_value=1)
    check_valid_boolean(value=[verbose], source=f'{pose_plotter.__name__} verbose')
    video_meta_data = get_video_meta_data(video_path=video_path)
    n, w, h = video_meta_data['frame_count'], video_meta_data['width'], video_meta_data['height']
    check_if_dir_exists(in_dir=os.path.dirname(save_path))
    if data.shape[0] != video_meta_data['frame_count']:
        raise FrameRangeError(msg=f'The data contains {data.shape[0]} frames while the video contains {video_meta_data["frame_count"]} frames')

    if circle_size is None:
        circle_size = np.array([PlottingMixin().get_optimal_circle_size(frame_size=(w, h))]).astype(np.int32)
    else:
        circle_size = np.array([circle_size]).astype(np.int32)
    fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
    video_writer = cv2.VideoWriter(save_path, fourcc, video_meta_data['fps'], (w, h))

    colors = np.array(create_color_palette(pallete_name=colors, increments=data[0].shape[0])).astype(np.int32)
    circle_size_dev = cuda.to_device(circle_size)
    colors_dev = cuda.to_device(colors)
    resolution_dev = cuda.to_device(np.array([video_meta_data['width'], video_meta_data['height']]))

    img_dev = cuda.device_array((batch_size, h, w, 3), dtype=np.int32)
    data_dev = cuda.device_array((batch_size, data.shape[1], 2), dtype=np.int32)

    total_timer = SimbaTimer(start=True)
    for batch_cnt, l in enumerate(range(0, data.shape[0], batch_size)):
        r = min(data.shape[0], l + batch_size - 1)
        if verbose:
            print(f'Processing frames {l}-{r} of {data.shape[0]} frames (video: {video_meta_data["video_name"]})...')
        batch_data = data[l:r + 1]
        batch_n = batch_data.shape[0]
        batch_frms = read_img_batch_from_video_gpu(video_path=video_path, start_frm=l, end_frm=r, out_format='array').astype(np.int32)
        grid_x = math.ceil(batch_frms.shape[0] / THREADS_PER_BLOCK[0])
        grid_z = math.ceil(batch_n / THREADS_PER_BLOCK[2])
        bpg = (grid_x, grid_z)
        img_dev[:batch_n].copy_to_device(batch_frms[:batch_n])
        data_dev[:batch_n] = cuda.to_device(batch_data[:batch_n])

        _pose_plot_kernel[bpg, THREADS_PER_BLOCK](img_dev, data_dev, circle_size_dev, resolution_dev, colors_dev)
        batch_frms = img_dev.copy_to_host()
        for img_idx in range(0, batch_n):
            video_writer.write(batch_frms[img_idx].astype(np.uint8))

    video_writer.release()
    total_timer.stop_timer()
    if verbose:
        stdout_success(msg=f'Pose-estimation video saved at {save_path}.', elapsed_time=total_timer.elapsed_time_str)


DATA_PATH = "/mnt/c/troubleshooting/mitra/project_folder/csv/outlier_corrected_movement_location/501_MA142_Gi_CNO_0514.csv"
VIDEO_PATH = "/mnt/c/troubleshooting/mitra/project_folder/videos/501_MA142_Gi_CNO_0514.mp4"
SAVE_PATH = "/mnt/c/troubleshooting/mitra/project_folder/frames/output/pose_ex/test.mp4"
pose_plotter(data=DATA_PATH, video_path=VIDEO_PATH, save_path=SAVE_PATH, circle_size=20)




