import os
from datetime import datetime
from typing import Union, List
from simba.utils.read_write import get_fn_ext
from simba.utils.checks import check_file_exist_and_readable, check_str
from simba.utils.errors import InvalidFileTypeError
try:
    from typing import Literal
except:
    from typing_extensions import Literal


def get_file_creation_date(file_path: Union[str, os.PathLike], raise_error: bool = True) -> Union[str, None]:
    """
    Get the creation date of a file as a formatted string.

    :param Union[str, os.PathLike] file_path: Path to the file for which to get creation date.
    :param bool raise_error: If True, raises an error if the file cannot be read. If False, returns None.  Default is True.
    :return Union[str, None]: Creation date as a formatted string (e.g., "2024-01-15 14:30:25.123456"), or None if the file cannot be read and raise_error is False.

    :example:
    >>> creation_date = get_file_creation_date(video_path)
    >>> print(creation_date)
    >>> '2025-04-17 17:05:07.123456'
    """
    valid_path = check_file_exist_and_readable(file_path=file_path, raise_error=raise_error)
    if not valid_path:
        return None
    try:
        stat = os.stat(file_path).st_ctime
        return str(datetime.fromtimestamp(stat))
    except Exception as e:
        if raise_error:
            print(e.args)
            raise InvalidFileTypeError(msg=f'Could not read creation date for file {file_path}', source=get_file_creation_date.__name__)
        else:
            return None


def get_file_size(file_path: Union[str, os.PathLike],
                  raise_error: bool = True,
                  unit: Literal['B', 'KB', 'MB', 'GB'] = 'MB') -> Union[float, None]:
    """
    Get file size in specified unit.

    :param Union[str, os.PathLike] file_path: Path to the file
    :param bool raise_error: If True, raises error if file not found. If False, returns None.
    :param Literal['B', 'KB', 'MB', 'GB'] unit: Unit to return size in. Default 'MB'.
    :return Union[float, None]: File size in specified unit, or None if error and raise_error=False
    """

    valid_path = check_file_exist_and_readable(file_path=file_path, raise_error=raise_error)
    check_str(name=f'{get_file_size.__name__} unit', value=unit, options=('B', 'KB', 'MB', 'GB'), raise_error=True)
    if not valid_path:
        return None
    try:
        size = os.path.getsize(file_path)

        if unit == 'B':
            return float(size)
        elif unit == 'KB':
            return round(size / 1024, 4)
        elif unit == 'MB':
            return round(size / (1024 * 1024), 4)
        elif unit == 'GB':
            return round(size / (1024 * 1024 * 1024), 4)
        else:
            return round(size / (1024 * 1024), 4)

    except Exception as e:
        if raise_error:
            raise InvalidFileTypeError(msg=f'Could not read file size for file {file_path}', source=get_file_size.__name__)
        else:
            return None


get_file_size(file_path=r"D:\netholabs\videos\mp4_20250529161329\2025-04-17_17-05-07.mp4")



