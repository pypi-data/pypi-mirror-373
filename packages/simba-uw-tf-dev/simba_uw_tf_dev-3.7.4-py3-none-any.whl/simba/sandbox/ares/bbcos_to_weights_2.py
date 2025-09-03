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
        centroid_loc, self.weights = {}, {}
        for (track_1, track_2) in self.track_pairs:
            print((track_1, track_2))
            geo_1, geo_2 = list(self.data[track_1].values()), list(self.data[track_2].values())
            overlap = np.array(GeometryMixin().multiframe_compute_shape_overlap(shape_1=geo_1, shape_2=geo_2, core_cnt=23, verbose=True))
            overlap = np.cumsum(overlap / 30)
            self.weights[(track_1, track_2)] = overlap

    def save(self):
        write_pickle(data=self.weights, save_path=r"D:\ares\data\termite_2\termite_2_weights.pickle")

d = BboxesToGraphs(data_path=r"D:\ares\data\termite_2\termite_2_geometries.pickle")
d.run()
d.save()