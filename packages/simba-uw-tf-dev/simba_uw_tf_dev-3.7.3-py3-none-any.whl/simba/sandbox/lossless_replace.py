from typing import Union, Optional, Tuple
import os
import subprocess
from simba.utils.read_write import recursive_file_search, get_fn_ext
from simba.utils.enums import Options
from simba.utils.printing import SimbaTimer
from simba.utils.read_write import get_video_meta_data

def lossless_mp4_conversion(directory: Union[str, os.PathLike],
                            save_dir: Optional[Union[str, os.PathLike]] = None,
                            file_extensions: Optional[Tuple[str, ...]] = None,
                            overwrite: bool = True):

    file_extensions = Options.ALL_VIDEO_FORMAT_OPTIONS.value if file_extensions is None else file_extensions
    file_paths = recursive_file_search(directory=directory, extensions=file_extensions, as_dict=True)

    timer = SimbaTimer(start=True)
    for file_cnt, (file_name, file_path) in enumerate(file_paths.items()):
        print(f'{file_cnt+1}/{len(file_paths.keys())}')
        video_timer = SimbaTimer(start=True)
        video_meta = get_video_meta_data(video_path=file_path)

        in_dir, _, _ = get_fn_ext(filepath=file_path)
        output_filename = f'{file_name}_temp.mp4' if save_dir is None else f'{file_name}.mp4'
        output_path = os.path.join(save_dir or in_dir, output_filename)

        if os.path.isfile(output_path) and not overwrite:
            continue

        cmd = f'ffmpeg -fflags +genpts -r {video_meta["fps"]} -i "{file_path}" -c copy -movflags +faststart "{output_path}" -loglevel error -stats -hide_banner -y'
        subprocess.call(cmd, shell=True)

        if save_dir is None:
            os.replace(output_path, file_path)  # Replace original safely

        video_timer.stop_timer()
        print(f'{video_meta["video_name"]}: {video_timer.elapsed_time_str}s')


lossless_mp4_conversion(directory=r'D:\netholabs\temporal_stitching\test_2')

