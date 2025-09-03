from typing import Union, Optional, Tuple
import os
import numpy as np
import cv2
import platform
import multiprocessing
import functools

from simba.utils.checks import check_file_exist_and_readable, check_int, check_valid_tuple, get_fn_ext, check_if_dir_exists, check_valid_boolean, check_nvidea_gpu_available
from simba.utils.read_write import get_video_meta_data, create_directory, find_core_cnt, concatenate_videos_in_folder
from simba.utils.enums import Formats, Defaults
from simba.utils.errors import InvalidInputError, SimBAGPUError
from simba.utils.warnings import FrameRangeWarning, GPUToolsWarning
from simba.utils.printing import SimbaTimer

def _clahe_enhance_video_mp_helper(data: tuple,
                                   video_path: str,
                                   clip_limit: int,
                                   temp_dir: str,
                                   tile_grid_size: tuple):

    cap = cv2.VideoCapture(video_path)
    video_meta_data = get_video_meta_data(video_path=video_path)
    batch_id, img_idxs = data[0], data[1]
    save_path = os.path.join(temp_dir, f'{batch_id}.mp4')
    fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
    writer = cv2.VideoWriter( save_path, fourcc, video_meta_data["fps"], (video_meta_data["width"], video_meta_data["height"]), 0)
    clahe_filter = cv2.createCLAHE(clipLimit=int(clip_limit), tileGridSize=tile_grid_size)
    start_frm, current_frm, end_frm = img_idxs[0], img_idxs[0], img_idxs[-1]
    cap.set(1, start_frm)

    while current_frm <= end_frm:
        ret, img = cap.read()
        if ret:
            if img.ndim > 2:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe_frm = clahe_filter.apply(img)
            writer.write(clahe_frm)
            #print(f"CLAHE converted frame {current_frm}/{video_meta_data['frame_count']} (core batch: {batch_id}, video name: {video_meta_data['video_name']})...")
        else:
            FrameRangeWarning(msg=f'Could not read frame {current_frm} in video {video_meta_data["video_name"]}', source=_clahe_enhance_video_mp_helper.__name__)
            break
        current_frm += 1
    writer.release()
    return batch_id

def clahe_enhance_video_mp(file_path: Union[str, os.PathLike],
                           clip_limit: Optional[int] = 2,
                           tile_grid_size: Optional[Tuple[int]] = (16, 16),
                           out_path: Optional[Union[str, os.PathLike]] = None,
                           gpu: bool = False,
                           core_cnt: int = -1) -> None:

    """
    Convert a single video file to clahe-enhanced greyscale file using multiprocessing.

    .. image:: _static/img/clahe_enhance_video.gif
       :width: 800
       :align: center

    :param Union[str, os.PathLike] file_path: Path to video file.
    :param Optional[int] clip_limit: CLAHE amplification limit. Inccreased clip limit reduce noise in output. Default: 2.
    :param Optional[Tuple[int]] tile_grid_size: The histogram kernel size.
    :param Optional[Union[str, os.PathLike]] out_path:  The result is saved with prefix``CLAHE_`` in the same directory as in the input file if out_path is not passed. Else saved at the out_path.
    :param Union[str, os.PathLike] gpu: If True, try using GPU for segment concatenation.
    :param int core_cnt: Number of cores to use. Pass ``-1`` for all available cores.
    :returns: None.

    :example:
    >>> _ = clahe_enhance_video_mp(file_path: 'project_folder/videos/Video_1.mp4')
    """

    video_timer = SimbaTimer(start=True)
    check_file_exist_and_readable(file_path=file_path)
    check_int(name=f"{clahe_enhance_video_mp.__name__} clip_limit", value=clip_limit, min_value=0)
    video_meta_data = get_video_meta_data(file_path)
    check_valid_tuple(x=tile_grid_size, source=f'{clahe_enhance_video_mp.__name__} tile_grid_size', accepted_lengths=(2,), valid_dtypes=(int,),)
    check_valid_boolean(value=[gpu], source=f'{clahe_enhance_video_mp.__name__} gpu', raise_error=True)
    if gpu and not check_nvidea_gpu_available():
        GPUToolsWarning(msg='No NVIDEA GPU detected and GPU selected. Running without GPU', source=clahe_enhance_video_mp.__name__)
        gpu = False
    if (tile_grid_size[0] > video_meta_data["height"]) or ((tile_grid_size[1] > video_meta_data["width"])):
        raise InvalidInputError(msg=f'The tile grid size ({tile_grid_size}) is larger than the video size ({video_meta_data["resolution_str"]})', source=clahe_enhance_video_mp.__name__,)
    dir, file_name, file_ext = get_fn_ext(filepath=file_path)
    if out_path is None:
        save_path = os.path.join(dir, f"CLAHE_{file_name}.mp4")
    else:
        check_if_dir_exists(in_dir=os.path.dirname(out_path), source=f'{clahe_enhance_video_mp.__name__} out_path')
        save_path = out_path
    if (platform.system() == "Darwin") and (multiprocessing.get_start_method() is None):
        multiprocessing.set_start_method("spawn", force=False)
    tempdir = os.path.join(os.path.dirname(save_path), 'temp', file_name)
    create_directory(paths=tempdir, overwrite=True)
    core_cnt = find_core_cnt()[0] if core_cnt == -1 or core_cnt > find_core_cnt()[0] else core_cnt
    frm_idx = list(range(0, video_meta_data['frame_count']))
    frm_idx = np.array_split(frm_idx, core_cnt)
    frm_idx = [(i, list(j)) for i, j in enumerate(frm_idx)]
    print(frm_idx, video_meta_data['frame_count'], video_meta_data['fps'])
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.LARGE_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(_clahe_enhance_video_mp_helper,
                                      video_path=file_path,
                                      clip_limit=clip_limit,
                                      temp_dir=tempdir,
                                      tile_grid_size=tile_grid_size)
        for cnt, result in enumerate(pool.imap(constants, frm_idx, chunksize=1)):
            print(f'Batch {(result + 1)} / {core_cnt} complete...')
    pool.terminate()
    pool.join()
    print(f"Joining {video_meta_data['video_name']} multiprocessed video...")
    concatenate_videos_in_folder(in_folder=tempdir, save_path=save_path, remove_splits=False, gpu=gpu)
    video_timer.stop_timer()
    print(f"CLAHE video {video_meta_data['video_name']} complete (saved at {save_path}) (elapsed time: {video_timer.elapsed_time_str}s) ...")


# if __name__ == "__main__":
#     clahe_enhance_video_mp(file_path=r"D:\EPM_4\original\1.mp4", gpu=True)



