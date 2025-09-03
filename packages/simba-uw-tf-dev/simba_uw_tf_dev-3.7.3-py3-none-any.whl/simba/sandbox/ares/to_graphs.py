from typing import Dict, Tuple, Any
import networkx as nx
from simba.utils.read_write import read_pickle, write_pickle
import numpy as np
from simba.utils.checks import check_instance, check_valid_tuple, check_valid_array
from simba.utils.enums import Formats
from simba.mixins.network_mixin import NetworkMixin


def create_graphs(data: Dict[Tuple[Any, Any], np.ndarray]) -> nx.Graph():
    check_instance(source=create_graphs.__name__, instance=data, accepted_types=dict)
    for k, v in data.items():
        check_valid_tuple(x=k, source=create_graphs.__name__, accepted_lengths=(2,))
        check_valid_array(data=v, source=create_graphs.__name__, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    size = np.unique([v.shape[0] for v in data.values()])[0]
    graphs = {}
    for cnt, i in enumerate(range(0, size)):
        print(i)
        frm_data = {k: v[i] for k, v in data.items()}
        graphs[cnt] = NetworkMixin.create_graph(data=frm_data)

    write_pickle(data=graphs, save_path=r"D:\ares\data\termite_2\termite_2_graphs.pickle")
    print('s')


    # graphs = {}
    # for track_pair, weights in data.items():
    #     for j in weights:
    #         g = NetworkMixin.create_graph(data={track_pair: j})
    #         print((g.nodes), track_pair, j)
    #         break
    #     break
    #
    #
    # pass
    #






data = read_pickle(data_path=r"D:\ares\data\termite_2\termite_2_weights.pickle")
create_graphs(data=data)

