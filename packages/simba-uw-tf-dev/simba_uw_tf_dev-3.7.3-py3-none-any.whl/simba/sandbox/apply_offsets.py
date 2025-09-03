import os
import numpy as np
from typing import Union, Tuple
from simba.utils.read_write import recursive_file_search, find_core_cnt, read_df, get_fn_ext
import multiprocessing
import functools
import pandas as pd

X_BBOX = ['X1', 'X2', 'X3', 'X4']
Y_BBOX = ['Y1', 'Y2', 'Y3', 'Y4']
X_BPS = ['NOSE_X','LEFT_EAR_X', 'RIGHT_EAR_X', 'LEFT_SIDE_X',  'CENTER_X','RIGHT_SIDE_X', 'TAIL_BASE_X', 'TAIL_CENTER_X', 'TAIL_TIP_X']
Y_BPS = ['NOSE_Y', 'LEFT_EAR_Y', 'RIGHT_EAR_Y', 'LEFT_SIDE_Y',  'CENTER_Y', 'RIGHT_SIDE_Y', 'TAIL_BASE_Y', 'TAIL_CENTER_Y', 'TAIL_TIP_Y']

def _apply_offset_helper(data_path: str,
                         id_grid: np.ndarray,
                         vertical_grid: np.ndarray,
                         horizontal_grid: np.ndarray):

    video_id = int(os.path.basename(os.path.dirname(data_path[0])))
    video_id_idx = np.argwhere(id_grid == video_id).flatten()
    video_vertical_offset = vertical_grid[video_id_idx[0]][[video_id_idx[1]]][0]
    video_horizontal_offset = horizontal_grid[video_id_idx[0]][[video_id_idx[1]]][0]
    df = pd.read_csv(data_path[0], index_col=0)
    x_bbox, y_bbox = df[X_BBOX].astype(np.int32), df[Y_BBOX].astype(np.int32)
    x_bps, y_bps = df[X_BPS].astype(np.int32), df[Y_BPS].astype(np.int32)
    df[X_BBOX] = x_bbox.where(x_bbox.isin([-1]), x_bbox + video_horizontal_offset)
    df[Y_BBOX] = y_bbox.where(y_bbox.isin([-1]), y_bbox + video_vertical_offset)
    df[X_BPS] = x_bps.where(x_bps.isin([-1, 0]), x_bps + video_horizontal_offset)
    df[Y_BPS] = y_bps.where(y_bps.isin([-1, 0]), y_bps + video_vertical_offset)
    dir, filename, _ = get_fn_ext(filepath=data_path[0])
    save_path = os.path.join(dir, f'{filename}_spatial_offset.csv')
    df.to_csv(save_path)
    return save_path

def grid_spatial_offsets(data_dir: Union[str, os.PathLike],
                         grid_size: Tuple[int, int] =  (3, 6),
                         resolution: Tuple[int, int] = (1024, 768), # WxH
                         bottom_to_top_left_to_right: bool = True,
                         core_cnt: int = -1):

    data_paths = recursive_file_search(directory=data_dir, extensions=['csv'], skip_substrings='spatial_offset')
    #unique_dirs = [int(x) for x in sorted(set(os.path.basename(os.path.dirname(path)) for path in data_paths))]
    video_id_grid, vertical_add_grid, horizontal_add_grid = None, None, None
    core_cnt = find_core_cnt()[0] if core_cnt == -1 else core_cnt
    if bottom_to_top_left_to_right:
        video_id_grid = np.flipud(np.arange(0 + 1, grid_size[1] * grid_size[0] + 1).reshape(grid_size[1], grid_size[0]).T)
        vertical_add_grid = np.repeat(np.arange(grid_size[0])[:, None] * resolution[1], grid_size[1], axis=1)
        horizontal_add_grid = np.tile(np.arange(grid_size[1]) * resolution[0], (grid_size[0], 1))
    print(vertical_add_grid)
    print(horizontal_add_grid)


    # data_paths = [[x] for x in data_paths]
    #
    # with multiprocessing.Pool(core_cnt, maxtasksperchild=50) as pool:
    #     constants = functools.partial(_apply_offset_helper,
    #                                   id_grid=video_id_grid,
    #                                   vertical_grid=vertical_add_grid,
    #                                   horizontal_grid=horizontal_add_grid)
    #     for cnt, save_path in enumerate(pool.imap(constants, data_paths, chunksize=1)):
    #         print(save_path)
    #     pool.terminate()
    #     pool.join()

    pass

#if __name__ == "__main__":
grid_spatial_offsets(data_dir=r'D:\netholabs\spatial_stitching\test')
