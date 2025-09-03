import os
from typing import Union, Any, Tuple, Dict, Optional
try:
    from typing import Literal
except:
    from typing_extensions import Literal
from simba.utils.read_write import get_video_meta_data, find_files_of_filetypes_in_directory
from simba.utils.enums import Options, Defaults, Formats
from simba.utils.errors import NoFilesFoundError
from tabulate import tabulate
from simba.utils.checks import check_valid_dict, check_valid_tuple, check_str
from simba.utils.lookups import get_table

def print_video_meta_data(data_path: Union[str, os.PathLike]) -> None:

    """
    Print video metadata as formatted tables to the console.

    This function reads video metadata from either a single video file or all video files
    in a directory, then prints the metadata as formatted tables.

    .. seealso::

       To get video metadata as a dictionary without printing, use :func:`simba.utils.read_write.get_video_meta_data`.

    :param Union[str, os.PathLike] data_path: Path to video file or directory containing videos.
    :return: None. Video metadata is printed as formatted tables in the main console.
    """


    if os.path.isfile(data_path):
        video_meta_data = [get_video_meta_data(video_path=data_path)]
    elif os.path.isdir(data_path):
        video_paths = find_files_of_filetypes_in_directory(directory=data_path, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value, raise_error=False)
        video_meta_data = [get_video_meta_data(video_path=x) for x in video_paths]
    else:
        raise NoFilesFoundError(msg=f'{data_path} is not a valid file or directory path', source=print_video_meta_data.__name__)
    for video_meta in video_meta_data:
        table = get_table(data=video_meta, headers=('VIDEO PARAMETER', 'VALUE'), tablefmt='psql')
        print(f"{table} {Defaults.STR_SPLIT_DELIMITER.value}TABLE")




print_video_meta_data(data_path=r'C:\Users\sroni\OneDrive\Desktop\mp4s')






