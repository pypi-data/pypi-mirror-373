from typing import List, Union
from shapely.geometry import Polygon, LineString
try:
    from typing import Literal
except:
    from typing_extensions import Literal

from simba.utils.checks import check_float, check_int, check_valid_lst
from simba.utils.read_write import find_core_cnt
import multiprocessing
import functools
from simba.mixins.geometry_mixin import GeometryMixin
from simba.utils.enums import Defaults

def multiframe_buffer_shapes(geometries: List[Union[Polygon, LineString]],
                             size_mm: int,
                             pixels_per_mm: float,
                             core_cnt: int = -1,
                             cap_style: Literal["round", "square", "flat"] = "round") -> List[Polygon]:

    check_valid_lst(data=geometries, source=f'{multiframe_buffer_shapes.__name__} geometries', valid_dtypes=(Polygon, LineString,), min_len=1, raise_error=True)
    check_int(name=f'{multiframe_buffer_shapes.__name__} size_mm', value=size_mm, min_value=1)
    check_float(name=f'{multiframe_buffer_shapes.__name__} pixels_per_mm', value=pixels_per_mm, min_value=10e-6)
    check_int(name=f'{multiframe_buffer_shapes.__name__} core_cnt', value=core_cnt, min_value=-1, unaccepted_vals=[0])
    core_cnt = find_core_cnt()[0] if core_cnt == -1 or core_cnt > find_core_cnt()[0] else core_cnt
    geomety_lst = lambda lst, core_cnt: [lst[i::core_cnt] for i in range(core_cnt)]

    results = []
    with multiprocessing.Pool(core_cnt, maxtasksperchild=Defaults.MAXIMUM_MAX_TASK_PER_CHILD.value) as pool:
        constants = functools.partial(GeometryMixin.buffer_shape,
                                      size_mm=size_mm,
                                      pixels_per_mm=pixels_per_mm,
                                      cap_style=cap_style)
        for cnt, mp_return in enumerate(pool.imap(constants, geomety_lst, chunksize=1)):
            results.append(mp_return)
        pool.join()
        pool.terminate()
    return [l for ll in results for l in ll]





