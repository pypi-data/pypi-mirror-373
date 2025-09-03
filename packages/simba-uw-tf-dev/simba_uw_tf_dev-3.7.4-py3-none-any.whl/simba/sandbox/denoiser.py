import os

import cv2
import numpy as np
from typing import List, Optional, Union

from simba.utils.read_write import read_frm_of_video, read_img_batch_from_video, get_video_meta_data, find_core_cnt, create_directory
from simba.utils.checks import check_int, check_if_valid_img, check_float, check_valid_lst, check_valid_array, check_if_dir_exists
from simba.utils.enums import Formats, Defaults

import multiprocessing
import functools

from skimage.restoration import denoise_nl_means

def non_local_mean_denoising(img: np.ndarray,
                             sigma: int = 30,
                             template_window: float = 0.02,
                             search_window: float = 0.10) -> np.ndarray:

    """
    Applies Non-Local Means (NLM) denoising to a grayscale or color image using OpenCV.

    .. note::
       Pretty slow.

    .. image:: _static/img/non_local_mean_denoising.webp
       :width: 400
       :align: center

    :param np.ndarray img: Input image (grayscale or color) as a NumPy array.
    :param int sigma: Strength of the filter. Higher values remove more noise but may blur details. Default 30.
    :param float template_window: Size of the local patch for denoising, relative to the larger image dimension.  Must be between `1e-5` and `1.0`. Default is `0.02`.
    :param float search_window: Size of the area where similar patches are searched, relative to the larger image dimension. Must be between `1e-5` and `1.0`. Default is `0.10`.
    :return: Denoised image as a NumPy array with the same shape as the input.
    :rtype: np.ndarray
    """

    check_if_valid_img(data=img, source=f'{non_local_mean_denoising.__name__} img')
    check_int(name=f'{non_local_mean_denoising.__name__} sigma', value=sigma, min_value=1)
    check_float(f'{non_local_mean_denoising.__name__} template_window', min_value=10e-6, max_value=1.0, value=template_window)
    check_float(f'{non_local_mean_denoising.__name__} search_window', min_value=10e-6, max_value=1.0, value=search_window)
    img_h, img_w = img.shape[0], img.shape[1]
    template_window = int(max(img_h, img_w) * template_window)
    template_window = template_window if template_window % 2 == 1 else template_window + 1
    search_window_size = int(max(img_h, img_w) * search_window)
    if img.ndim == 2:
        img = cv2.fastNlMeansDenoising(img, dst=None, h=sigma, templateWindowSize=template_window, searchWindowSize=search_window_size)
    else:
        img = cv2.fastNlMeansDenoisingColored(img, None, h=sigma, templateWindowSize=template_window, searchWindowSize=search_window_size)
    return img



def non_local_mean_denoising_sequence(imgs: np.ndarray,
                                      sigma: int = 30,
                                      img_to_denoise_idx: Optional[int] = None) -> np.ndarray:

    """
    Applies Non-Local Means (NLM) denoising to a stack of images or video frames to reduce noise, using a temporal window for multi-frame denoising.

    .. note::
       Pretty slow.

    .. image:: _static/img/non_local_mean_denoising.webp
       :width: 400
       :align: center

    .. seealso::
       For single images, see :func:`simba.mixins.image_mixin.ImageMixin.non_local_mean_denoising_image`

    :param np.ndarray imgs: A 3D or 4D NumPy array of images or video frames.  If the input is a 3D array, it represents a single image stack (height, width, num_frames). If the input is a 4D array, it represents a batch of video frames (num_frames, height, width, num_channels).
    :param int sigma: The filtering strength parameter. A higher value corresponds to stronger denoising  and more smoothing of the image. The default is 30.
    :return: Denoised video or image stack.
    :rtype: np.ndarray If input is a 3D array (grayscale), the output is a 3D array. If input is a 4D array (colored), the output is a 4D arra
    """

    check_valid_array(data=imgs, source=f'{non_local_mean_denoising_sequence.__name__} imgs', accepted_ndims=(3, 4,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, min_axis_0=2)
    check_int(name=f'{non_local_mean_denoising_sequence.__name__} sigma', value=sigma, min_value=1)
    if img_to_denoise_idx is None:
        img_to_denoise_idx = int(np.floor(imgs.shape[0] / 2))
    else:
        check_int(name=f'{non_local_mean_denoising_sequence.__name__} img_to_denoise_idx', value=img_to_denoise_idx, max_value=imgs.shape[0]-1, min_value=0)
    temporal_window_size = int((imgs.shape[0] / 2))
    temporal_window_size = temporal_window_size if temporal_window_size % 2 == 1 else temporal_window_size - 1
    if imgs.shape[0] <= 2:
        temporal_window_size = 1
    if imgs.ndim == 3:
        imgs = [imgs[:, :, i] for i in range(imgs.shape[2])]
        denoised_img = cv2.fastNlMeansDenoisingMulti(imgs, imgToDenoiseIndex=img_to_denoise_idx, temporalWindowSize=temporal_window_size, h=sigma)
    else:
        imgs = [imgs[i] for i in range(imgs.shape[0])]
        denoised_img = cv2.fastNlMeansDenoisingColoredMulti(imgs, imgToDenoiseIndex=img_to_denoise_idx, temporalWindowSize=temporal_window_size, h=sigma)

    return denoised_img


def _non_local_mean_denoising_video_helper(data: tuple,
                                           video_path: Union[str, os.PathLike],
                                           temp_dir: Union[str, os.PathLike],
                                           sigma: int,
                                           time_window: int):
    cap = cv2.VideoCapture(video_path)
    video_meta_data = get_video_meta_data(video_path=video_path)
    batch_id, img_idxs = data[0], data[1]
    fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)

    save_path = os.path.join(temp_dir, f'{str(batch_id)}.mp4')
    writer = cv2.VideoWriter(save_path, fourcc, video_meta_data['fps'], (video_meta_data['width'], video_meta_data['height']))

    def read_img_batch(start: int, end: int):

        if video_meta_data["color_format"] == 'rgb':
            results = np.full(shape=(int(end-start), video_meta_data['height'], video_meta_data['width'], 3), fill_value=-1, dtype=np.uint8)
        else:
            results = np.full(shape=(int(end-start), video_meta_data['height'], video_meta_data['width'], 3), fill_value=-1, dtype=np.uint8)
        for img_cnt, img_idx in enumerate(range(start, end)):
            results[img_cnt] = read_frm_of_video(video_path=cap, frame_index=img_idx)
        return results

    for img_cnt, img_idx in enumerate(img_idxs):
        start_idx = int(max(0, (img_idx - (time_window))))
        end_idx = int(min(video_meta_data['frame_count'] - 1, (img_idx + (time_window))))
        imgs = read_img_batch(start=start_idx, end=end_idx)
        imgs = [imgs[i] for i in range(imgs.shape[0])]
        temporal_window_size = min(len(imgs), 2 * time_window + 1)
        if temporal_window_size % 2 == 0:
            temporal_window_size -= 1
        temporal_window_size = max(1, temporal_window_size)
        imgToDenoiseIndex = min(max(temporal_window_size // 2, img_cnt), len(imgs) - 1)
        denoised_img = cv2.fastNlMeansDenoisingColoredMulti(imgs, imgToDenoiseIndex=imgToDenoiseIndex, temporalWindowSize=temporal_window_size, h=sigma)
        writer.write(denoised_img.astype(np.uint8))
        print(img_idx)
    writer.release()


def non_local_mean_denoising_video(video_path: Union[str, os.PathLike],
                                   save_path: Union[str, os.PathLike],
                                   time_window: float,
                                   sigma: int = 30,
                                   core_cnt: Optional[int] = -1):


    video_meta_data = get_video_meta_data(video_path=video_path)
    check_int(name=f'{non_local_mean_denoising_video.__name__} sigma', value=sigma, min_value=1)
    check_if_dir_exists(in_dir=os.path.dirname(save_path), source=f'{non_local_mean_denoising_video.__name__} save_path')
    check_float(name=f'{non_local_mean_denoising_video.__name__} time_window', min_value=10e-6, value=time_window)
    check_int(name=f'{non_local_mean_denoising_video.__name__} core_cnt', value=core_cnt, min_value=-1, unaccepted_vals=[0])
    core_cnt = find_core_cnt()[0] if core_cnt -1 or core_cnt > find_core_cnt()[0] else core_cnt

    temp_dir = os.path.join(os.path.dirname(save_path), 'temp')
    create_directory(paths=temp_dir, overwrite=True)
    frm_time_window = int(max(2, video_meta_data['fps'] * time_window))
    frm_idx = list(range(0, video_meta_data['frame_count']))
    frm_idx = [frm_idx[i:i + frm_time_window] for i in range(0, len(frm_idx))]
    frm_idx = [(i, j) for i, j in enumerate(frm_idx)]
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(_non_local_mean_denoising_video_helper,
                                      video_path=video_path,
                                      temp_dir=temp_dir,
                                      sigma=sigma,
                                      time_window=frm_time_window)

        for cnt, result in enumerate(pool.imap(constants, frm_idx, chunksize=1)):
            pass





def denoise_nl_means_skiimage(imgs: np.ndarray,
                              sigma: int = 30,
                              img_to_denoise_idx: Optional[int] = None):


    denoise_nl_means(im)










    pass

imgs = read_img_batch_from_video(video_path=r"D:\OF_7\bg\1.mp4", start_frm=0, end_frm=2, core_cnt=1)
imgs = np.stack(imgs.values())

denoise_nl_means_skiimage(imgs=imgs)

#
# if __name__ == "__main__":
#     non_local_mean_denoising_video(video_path=r"D:\OF_7\bg\cliopped\1.mp4", save_path=r"D:\OF_7\bg\cliopped\denoised\1.mp4", time_window=0.5, core_cnt=28, sigma=10)
#


#img = read_frm_of_video(video_path=r"D:\OF_7\bg\1.mp4")
#img = non_local_mean_denoising(img=img, sigma=20, template_window=0.02, search_window=0.1)


# imgs = read_img_batch_from_video(video_path=r"D:\OF_7\bg\1.mp4", start_frm=0, end_frm=2, core_cnt=1)
# imgs = np.stack(imgs.values())


# img = non_local_mean_denoising_sequence(imgs=imgs, img_to_denoise_idx=0)
#
# cv2.imshow('asdasdasd', img)
# cv2.waitKey(10000)