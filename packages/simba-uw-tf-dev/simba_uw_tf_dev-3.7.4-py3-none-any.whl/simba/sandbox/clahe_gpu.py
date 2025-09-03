import numpy as np
import cv2




def clahe_enhance_video(file_path: Union[str, os.PathLike],
                         clip_limit: Optional[int] = 2,
                         tile_grid_size: Optional[Tuple[int]] = (16, 16),
                         out_path: Optional[Union[str, os.PathLike]] = None) -> None:

    """
    Convert a single video file to clahe-enhanced greyscale .avi file.

    .. image:: _static/img/clahe_enhance_video.gif
       :width: 800
       :align: center

    :param Union[str, os.PathLike] file_path: Path to video file.
    :param Optional[int] clip_limit: CLAHE amplification limit. Inccreased clip limit reduce noise in output. Default: 2.
    :param Optional[Tuple[int]] tile_grid_size: The histogram kernel size.
    :param Optional[Union[str, os.PathLike]] out_path:  The result is saved with prefix``CLAHE_`` in the same directory as in the input file if out_path is not passed. Else saved at the out_path.
    :returns: None.

    :example:
    >>> _ = clahe_enhance_video(file_path: 'project_folder/videos/Video_1.mp4')
    """

    check_file_exist_and_readable(file_path=file_path)
    check_int(name=f"{clahe_enhance_video.__name__} clip_limit", value=clip_limit, min_value=0)
    video_meta_data = get_video_meta_data(file_path)
    check_valid_tuple(x=tile_grid_size, source=f'{clahe_enhance_video.__name__} tile_grid_size', accepted_lengths=(2,), valid_dtypes=(int,),)
    if (tile_grid_size[0] > video_meta_data["height"]) or ((tile_grid_size[1] > video_meta_data["width"])):
        raise InvalidInputError(msg=f'The tile grid size ({tile_grid_size}) is larger than the video size ({video_meta_data["resolution_str"]})', source=clahe_enhance_video.__name__,)
    dir, file_name, file_ext = get_fn_ext(filepath=file_path)
    if out_path is None:
        save_path = os.path.join(dir, f"CLAHE_{file_name}.avi")
    else:
        check_if_dir_exists(in_dir=os.path.dirname(out_path), source=f'{clahe_enhance_video.__name__} out_path')
        save_path = out_path
    fourcc = cv2.VideoWriter_fourcc(*Formats.AVI_CODEC.value)
    print(f"Applying CLAHE on video {file_name}, this might take awhile...")
    cap = cv2.VideoCapture(file_path)
    writer = cv2.VideoWriter( save_path, fourcc, video_meta_data["fps"], (video_meta_data["width"], video_meta_data["height"]), 0)
    clahe_filter = cv2.createCLAHE(clipLimit=int(clip_limit), tileGridSize=tile_grid_size)
    frm_cnt = 0
    try:
        while True:
            ret, img = cap.read()
            if ret:
                frm_cnt += 1
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                clahe_frm = clahe_filter.apply(img)
                writer.write(clahe_frm)
                print(f"CLAHE converted frame {frm_cnt}/{video_meta_data['frame_count']} ({file_name})...")
            else:
                break
        cap.release()
        writer.release()
        print(f"CLAHE video created: {save_path}.")
    except Exception as se:
        print(se.args)
        print(f"CLAHE conversion failed for video {file_name}.")
        cap.release()
        writer.release()
        raise InvalidVideoFileError(msg=f"Could not convert file {file_path} to CLAHE enhanced video", source=clahe_enhance_video.__name__,)

