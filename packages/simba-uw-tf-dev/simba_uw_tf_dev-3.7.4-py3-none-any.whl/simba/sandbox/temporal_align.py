import os
from typing import Union, List, Optional
import numpy as np
import pandas as pd

from simba.utils.read_write import recursive_file_search, find_core_cnt
from simba.utils.checks import check_file_exist_and_readable
import multiprocessing, functools
from numba import jit, prange, njit
import time

def _read_npz_helper(path: str,
                     keys: Optional[List[str]] = None):

    data = np.load(path[0])
    data = {k: data[k] for k in data.files}
    data = {key: data[key] for key in keys if key in data} if keys is not None else data
    data['frame_times'] = np.array([int(str(x)[:11]) for x in data['frame_times']])
    return {path[0]: {'data': data['frame_times'], 'start_time': np.min(data['frame_times']), 'end_time': np.max(data['frame_times']), 'count': len(data['frame_times'])}}

def read_npz(data_paths: List[Union[str, os.PathLike]], keys: Optional[List[str]] = None, core_cnt: int = -1):
    _ = [check_file_exist_and_readable(x) for x in data_paths]
    data_paths = [[x] for x in data_paths]
    core_cnt = find_core_cnt()[0] if core_cnt == -1 else core_cnt
    results = {}
    with multiprocessing.Pool(core_cnt, maxtasksperchild=50) as pool:
        constants = functools.partial(_read_npz_helper, keys=keys)
        for batch_cnt, batch_result in enumerate(pool.imap(constants, data_paths, chunksize=1)):
            results.update(batch_result)
    pool.terminate()
    pool.join()
    return results

@njit("(int64[:, :], int64[:],)")
def map_time_stamps(time_stamps: np.ndarray, unique_time_stamps: np.ndarray):
    results = np.full(shape=(unique_time_stamps.shape[0], time_stamps.shape[0]+1), fill_value=-1, dtype=np.int64)
    for cnt, i in enumerate(unique_time_stamps):
        for j in prange(time_stamps.shape[0]):
            idx = np.argwhere(time_stamps[j] == i).flatten()
            if idx.shape[0] > 0:
                idx = idx[0]
                results[cnt][0] = i
                results[cnt][j+1] = idx
    return results

def temporal_align(data_dir: Union[str, os.PathLike], keys: Optional[List[str]] = None):
    start = time.time()
    meta_paths = recursive_file_search(directory=data_dir, extensions=['npz'])
    meta_data = read_npz(data_paths=meta_paths, keys=keys)
    max_size, min_start_time, max_end_time = -np.inf, np.inf, -np.inf
    max_size = [max(v['count'], max_size) for k, v in meta_data.items()][0]
    max_size = max(len(v['data']) for v in meta_data.values())
    #min_start_time = [min(v['start_time'], min_start_time) for k, v in meta_data.items()][0]
    #max_end_time = [max(v['end_time'], max_end_time) for k, v in meta_data.items()][0]
    time_stamps = np.array([np.pad(v['data'], (0, max_size - len(v['data'])), constant_values=-1) for k, v in meta_data.items()])
    unique_time_stamps = np.sort(np.unique(time_stamps))
    unique_time_stamps = unique_time_stamps[unique_time_stamps != -1]
    x = map_time_stamps(time_stamps=time_stamps.astype(np.int64), unique_time_stamps=unique_time_stamps.astype(np.int64))
    files_names = [x[:-13] for x in list(meta_data.keys())]
    col_names =  ['UNIX_TIME'] + files_names
    out_df = pd.DataFrame(x, columns=col_names)
    out_df['UNIX_TIME'] = pd.to_numeric(out_df['UNIX_TIME'], errors='coerce')
    out_df['DATETIME'] = pd.to_datetime(out_df['UNIX_TIME'] * 100, unit='ms')
    out_df = out_df[['DATETIME'] + [c for c in out_df.columns if c != 'DATETIME']]
    #out_df['DATETIME'] = pd.to_datetime(out_df['UNIX_TIME'], unit='ns')
    out_df.to_csv(r'D:\netholabs\temporal_stitching\test_2.csv')
    print(f'Elapsed: {time.time()-start}s')






#
#
#
# data = np.load(r"D:\netholabs\spatial_stitching\npz\npz_sample\2025-07-16_06-01-02_metadata.npz")
# print(data.files)
#
# data['frame_times'].shape[0]

if __name__ == "__main__":
    temporal_align(data_dir=r"D:\netholabs\temporal_stitching\test_2", keys=['frame_times'])