import os
from typing import Union
import numpy as np
from simba.utils.read_write import read_pickle, write_pickle
from itertools import combinations
from simba.mixins.geometry_mixin import GeometryMixin
from simba.mixins.feature_extraction_mixin import FeatureExtractionMixin
from simba.mixins.statistics_mixin import Statistics

class BboxesToGraphs():



    def __init__(self,
                 data_path: Union[str, os.PathLike]):

        self.data = read_pickle(data_path=data_path)
        node_ids = self.data.keys()
        self.frm_cnt = -np.inf
        for k, v in self.data.items(): self.frm_cnt = max(self.frm_cnt, max(list(v.keys())))
        self.track_pairs = list(combinations(list(self.data.keys()), 2))

    def run(self):
        graphs = {}
        centroid_loc, self.weights = {}, {}
        for cnt, (k, v) in enumerate(self.data.items()):
            centroid_loc[k] = GeometryMixin().get_center(shape=list(v.values()))
            #if cnt > 4: break
        for (track_1, track_2) in self.track_pairs:
            dist = FeatureExtractionMixin().framewise_euclidean_distance(location_1=centroid_loc[track_1], location_2=centroid_loc[track_2], px_per_mm=1)
            self.weights[(track_1, track_2)] = Statistics().sliding_cumulative_mean(x=dist.astype(np.float32))

            #centers = GeometryMixin().get_center(shape=list(self.data[track_1].values()))
            #print(np.unique(centers))
            # geo_1, geo_2 = list(self.data[track_1].values()), list(self.data[track_2].values())
            # overlap = GeometryMixin().multiframe_compute_shape_overlap(shape_1=geo_1, shape_2=geo_2, core_cnt=23, verbose=True)
            # print(sum(overlap), track_1, track_2)
            #break

    def save(self):
        write_pickle(data=self.weights, save_path=r'D:\ares\data\ant\ant_weights.pickle')


        #for frm_id in range(0, self.frm_cnt):
        #    geometries = {outer_k: {k: v for k, v in subdict.items() if k <= frm_id} for outer_k, subdict in self.data.items() if frm_id in subdict}
#
#
#
        #    #p = {outer_k: subdict[frm_id] for outer_k, subdict in self.data.items() if frm_id in subdict}
        #    #if len(list(p.keys())) == 0:
        #    print(geometries.keys())
        #    break


from numba import njit, prange


# @njit("(float32[:], )")
# def sliding_cumulative_mean(x: np.ndarray):
#     """
#     Compute a sliding cumulative mean over a 1D
#
#     :param np.ndarray x: A 1D NumPy array of type float32
#     :return: A 1D float32 array of the same shape as `x`, containing the cumulative mean at each index, ignoring NaNs.
#     :rtype: np.ndarray
#     """
#
#     results = np.empty(x.shape[0], dtype=np.float32)
#     total, count = 0.0,0
#     for i in prange(x.shape[0]):
#         val = x[i]
#         if not np.isnan(val):
#             total += val
#             count += 1
#         if count > 0:
#             results[i] = total / count
#         else:
#             results[i] = np.nan
#     return results
#
#
# arr = np.array([np.nan, np.nan, 5, np.nan, 10]).astype(np.float32)
# print(sliding_cumulative_mean(arr))


d = BboxesToGraphs(data_path=r"D:\ares\data\ant\ant_geometries.pickle")
d.run()
d.save()