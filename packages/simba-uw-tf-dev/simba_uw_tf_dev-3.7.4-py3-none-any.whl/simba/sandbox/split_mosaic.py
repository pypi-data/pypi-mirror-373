from typing import Union, Tuple
import os
import subprocess

from simba.utils.checks import check_file_exist_and_readable, check_valid_tuple, check_if_dir_exists
from simba.utils.read_write import get_video_meta_data
from simba.utils.enums import Formats

def split_mosaic(video_path: Union[str, os.PathLike],
                 tile_size: Tuple[int, int],
                 save_dir: Union[str, os.PathLike],
                 verbose: bool = True):

    check_file_exist_and_readable(file_path=video_path)
    check_valid_tuple(x=tile_size, source=f'{split_mosaic.__name__} tile_size', accepted_lengths=(2,), valid_dtypes=(int,), min_integer=1)
    check_if_dir_exists(in_dir=save_dir, source=f'{split_mosaic.__name__} save_dir', create_if_not_exist=True)
    video_meta = get_video_meta_data(video_path=video_path)
    tile_w, tile_h = tile_size
    cnt_tiles_x = video_meta['width'] // tile_w
    cnt_tiles_y = video_meta['height'] // tile_h
    for i in range(cnt_tiles_y):
        for j in range(cnt_tiles_x):
            if verbose:
                print(f'Creating tile ({i}, {j})...')
            x, y = j * tile_w, i * tile_h
            output_path = os.path.join(save_dir, f"tile_{i}_{j}.mp4")
            cmd = f'ffmpeg -i "{video_path}" -filter:v "crop={tile_w}:{tile_h}:{x}:{y}" -c:v {Formats.BATCH_CODEC.value} -crf 10 -c:a copy "{output_path}" -hide_banner -loglevel error -stats -y'
            subprocess.call(cmd, shell=True)

            #subprocess.run(cmd, check=True)



#split_mosaic(video_path=r"D:\troubleshooting\netholabs\original_videos\3.mp4", tile_size=(1280, 720), save_dir=r"D:\troubleshooting\netholabs\original_videos\3_cropped")
