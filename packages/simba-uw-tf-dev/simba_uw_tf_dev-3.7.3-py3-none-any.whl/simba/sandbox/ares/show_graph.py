import os
from typing import Union
from simba.utils.read_write import read_pickle
from simba.mixins.network_mixin import NetworkMixin
import networkx as nx
def graphs_to_html(data_path: Union[str, os.PathLike], save_dir: Union[str, os.PathLike]):
    data = read_pickle(data_path=data_path)
    for graph_id, graph in data.items():
        save_path = os.path.join(save_dir, f'{graph_id}.html')
        #graph = nx.spring_layout(graph, seed=42)
        img = NetworkMixin().visualize(graph=graph, img_size=(500, 500), seed=98, node_size=25, node_shape='circle')
        img.write_html(save_path)
        # if graph_id > 10:
        #     break




graphs_to_html(data_path=r"D:\ares\data\termite_2\termite_2_graphs.pickle", save_dir=r"D:\ares\data\termite_2\htmls")
#
# def visualize_graph(data):
#     pass
#
#
# from playwright.sync_api import sync_playwright
# from pathlib import Path
#
# #
# #
# # data = read_pickle()
# # # for u, v, x in data[900].edges(data=True):
# # #     print(f"Edge: ({u}, {v}), Weight: {x['weight']}")
# #
# # img = NetworkMixin().visualize(graph=data[900], img_size=(1000, 1000))
# #
#
# import webview
#
# # Replace with your PyVis HTML file path
# #file_path = "my_network.html"
#
# html_path = pathlib.Path(r"C:\projects\simba\simba\my_network.html").absolute()
#
# # Convert path to a file URI (works on Windows, macOS, Linux)
# file_url = html_path.as_uri()
#
# # Create and show a window with the HTML file loaded
# webview.create_window('Network Graph Viewer', file_url)
# webview.start()
#
#
#
#
# #
# #
# #
# #
# #
# # # Example: create timeseries of simple graphs with 5 nodes moving randomly
# # timeseries = []
# # num_frames = 20
# # num_nodes = 5
# #
# # for t in range(num_frames):
# #     G = nx.cycle_graph(num_nodes)
# #     # Assign random 3D positions (change over time)
# #     pos = {n: (np.cos(t / 5 + n), np.sin(t / 5 + n), np.sin(t / 10 + n)) for n in G.nodes()}
# #     nx.set_node_attributes(G, pos, 'pos')
# #     timeseries.append(G)
# #
# # # Initialize PyVista plotter
# # plotter = pv.Plotter()
# # plotter.open_gif("network_animation.gif")  # Optional: save gif
# #
# #
# # # Helper to build PyVista PolyData from networkx graph at time t
# # def graph_to_pyvista(G):
# #     # Extract node positions as array
# #     nodes = np.array([G.nodes[n]['pos'] for n in G.nodes()])
# #     # Create points cloud
# #     point_cloud = pv.PolyData(nodes)
# #
# #     # Create lines for edges
# #     lines = []
# #     for edge in G.edges():
# #         start_idx = list(G.nodes()).index(edge[0])
# #         end_idx = list(G.nodes()).index(edge[1])
# #         lines.append(pv.Line(nodes[start_idx], nodes[end_idx]))
# #
# #     return point_cloud, lines
# #
# #
# # # Initialize plot with first frame
# # points, edges = graph_to_pyvista(timeseries[0])
# # node_actor = plotter.add_points(points, color='red', point_size=15, render_points_as_spheres=True)
# # edge_actors = [plotter.add_mesh(line, color='black', line_width=2) for line in edges]
# #
# # plotter.show(auto_close=False)  # Keep plotter open for animation
# #
# # for t in range(1, num_frames):
# #     G = timeseries[t]
# #     nodes = np.array([G.nodes[n]['pos'] for n in G.nodes()])
# #
# #     # Update node positions
# #     node_actor.points = nodes
# #     # Update edges
# #     for line_actor, (u, v) in zip(edge_actors, G.edges()):
# #         start_idx = list(G.nodes()).index(u)
# #         end_idx = list(G.nodes()).index(v)
# #         line_actor.points = np.array([nodes[start_idx], nodes[end_idx]])
# #
# #     plotter.update()
# #     plotter.write_frame()  # For GIF
# #     time.sleep(0.1)  # Control animation speed
# #
# # plotter.close()
