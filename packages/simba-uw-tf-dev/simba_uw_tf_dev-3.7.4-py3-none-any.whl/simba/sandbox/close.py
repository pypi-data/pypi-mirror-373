import numpy as np
import cv2
from typing import Tuple
from typing import Union, List
from simba.utils.checks import check_if_valid_img, is_img_bw, is_img_greyscale, check_valid_tuple, check_int
from simba.utils.errors import InvalidInputError

@staticmethod
def close(x: Union[List[np.ndarray], np.ndarray],
          kernel: Tuple[int, int],
          iterations: int = 3) -> Union[List[np.ndarray], np.ndarray]:

    imgs, results = [], []
    if isinstance(x, np.ndarray):
        check_if_valid_img(data=x, source=close.__name__, raise_error=True)
        if not is_img_bw(img=x) and not is_img_greyscale(img=x):
            raise InvalidInputError(msg='The image is invalid. Greyscale or black-and-white image is requires', source=close.__name__)
        imgs.append(x)
    elif isinstance(x, list):
        for cnt, i in enumerate(x):
            check_if_valid_img(data=i, source=f'{close.__name__} {cnt}', raise_error=True)
            if not is_img_bw(img=i) and not is_img_greyscale(img=i):
                raise InvalidInputError(msg='The image is invalid. Greyscale or black-and-white image is requires', source=close.__name__)
            imgs.append(i)
    else:
        raise InvalidInputError(msg=f'x is not a valid input. Require list of arrays or array, got {type(x)}', source=close.__name__)
    check_valid_tuple(x=kernel, source=f'{close.__name__} kernel', accepted_lengths=(2,), valid_dtypes=(int,), min_integer=1)
    check_int(name=f'{close.__name__} iterations', value=iterations, min_value=1, raise_error=True)
    for img in imgs:
        results.append(cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=iterations))
    if len(results) == 1:
        return results[0]
    else:
        return results











