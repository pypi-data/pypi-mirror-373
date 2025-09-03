import os
import subprocess
import json
from simba.utils.read_write import get_fn_ext
from simba.utils.checks import check_file_exist_and_readable, check_ffmpeg_available
from typing import Union, Dict, Any
from simba. utils.errors import FFMPEGNotFoundError, InvalidVideoFileError


def get_video_info_ffmpeg(video_path: Union[str, os.PathLike]) -> Dict[str, Any]:
    """
    Extracts metadata information from a video file using FFmpeg's ffprobe.

    .. seealso::
       To use OpenCV instead of FFmpeg, see :func:`simba.utils.read_write.get_video_meta_data`

    :param Union[str, os.PathLike] video_path: The file path to the video for which metadata is to be extracted.
    :return: A dictionary containing video metadata:
    :rtype: Dict[str, Any]

    """

    if not check_ffmpeg_available(raise_error=False):
        raise FFMPEGNotFoundError(msg=f'Cannot get video meta data from video using FFMPEG: FFMPEG not found on computer.', source=get_video_info_ffmpeg.__name__)
    check_file_exist_and_readable(file_path=video_path)
    video_name = get_fn_ext(filepath=video_path)[1]
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,duration,pix_fmt", "-of", "json", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    data = json.loads(result.stdout)
    try:
        stream = data['streams'][0]
        width = int(stream['width'])
        height = int(stream['height'])
        num, denom = map(int, stream['r_frame_rate'].split('/'))
        fps = num / denom
        frame_count = int(stream.get('nb_read_frames', 0))
        duration = float(data.get('format', {}).get('duration', 0))
        if duration == 0 and frame_count and fps:
            duration = frame_count / fps
        pix_fmt = stream.get('pix_fmt', '')
        resolution_str = str(f'{width} x {height}')

        if 'gray' in pix_fmt: color_format = 'grey'
        else: color_format = 'rgb'

        return {"video_name": video_name,
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count,
                "duration_sec": duration,
                "color_format": color_format,
                'resolution_str': resolution_str}

    except (KeyError, IndexError, ValueError) as e:
        print(e.args)
        raise InvalidVideoFileError(msg=f'Cannot use FFMPEG to extract video meta data for video {video_name}, try OpenCV?', source=get_video_info_ffmpeg.__name__)

# VIDEO_PATH = r"C:\Users\sroni\Downloads\2025-04-17_17-17-14.h264"
# info = get_video_info_ffmpeg(VIDEO_PATH)
# print(info)