import os
import subprocess
from typing import Optional, Tuple
from simba.utils.read_write import recursive_file_search, get_video_meta_data
from simba.utils.enums import Options

#from simba.utils.checks import

import os
import subprocess
from typing import Optional, Tuple, Union
from simba.utils.read_write import recursive_file_search, get_video_meta_data, get_fn_ext
from simba.utils.enums import Options
from simba.utils.printing import SimbaTimer
#from simba.utils.checks import

def lossless_mp4_conversion(directory: Union[str, os.PathLike],
                            save_dir: Optional[Union[str, os.PathLike]] = None,
                            file_extensions: Optional[Tuple[str, ...]] = None,
                            overwrite: bool = True):

    file_extensions = Options.ALL_VIDEO_FORMAT_OPTIONS.value if file_extensions is None else file_extensions
    file_paths = recursive_file_search(directory=directory, extensions=file_extensions, as_dict=True,)

    timer = SimbaTimer(start=True)
    for file_cnt, (file_name, file_path) in enumerate(file_paths.items()):
        print(f'{file_cnt+1}/{len(file_paths.keys())}')
        video_timer = SimbaTimer(start=True)
        video_meta = get_video_meta_data(video_path=file_path)
        if save_dir is not None:
            save_path = os.path.join(save_dir, f'{file_name}.mp4')
        else:
            in_dir, _, _ = get_fn_ext(filepath=file_path)
            save_path = os.path.join(in_dir, f'{file_name}_simon.mp4')
        if os.path.isfile(save_path) and not overwrite:
            pass
        else:
            cmd = f"ffmpeg -fflags +genpts -r {video_meta['fps']} -i '{file_path}' -c copy -movflags +faststart '{save_path}' -loglevel error -stats -hide_banner -y"
            subprocess.call(cmd, shell=True)
        timer.stop_timer()
        print(f'{video_meta["video_name"]}: {video_timer.elapsed_time_str}s')
        #print(get_video_meta_data(video_path=save_path))




DIRECTORY = r'/media/netholabs/3618cb5c-2293-4eae-ae43-978810705e02/simon/test'
SAVE_DIR = r'/media/netholabs/3618cb5c-2293-4eae-ae43-978810705e02/simon/mp4'

lossless_mp4_conversion(directory=DIRECTORY, save_dir=SAVE_DIR)



