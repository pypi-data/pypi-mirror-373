import time
from typing import Tuple
import numpy as np
from scipy.spatial.qhull import QhullError
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist
import pandas as pd
from simba.mixins.geometry_mixin import GeometryMixin
from simba.plotting.geometry_plotter import GeometryPlotter
from hmmlearn import hmm
from scipy.signal import medfilt
import cv2
from simba.utils.read_write import read_img_batch_from_video
from scipy.signal import medfilt
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.decomposition import PCA
from scipy.spatial import distance
from scipy.signal import medfilt
from hmmlearn.hmm import GaussianHMM


 # Returns the angle in radians


def get_nose_tail_from_vertices(vertices: np.ndarray,
                                fps: float = 10,
                                smooth_factor = 0.5,
                                jump_threshold = 0.75):

    def calculate_bearing(head, tail):
        delta_y = tail[1] - head[1]
        delta_x = tail[0] - head[0]
        return np.arctan2(delta_y, delta_x)

    smooth_factor = max(2, int(fps * smooth_factor))
    T, N, _ = vertices.shape
    anterior = np.full((T, 2), -1, dtype=np.float32)
    posterior = np.full((T, 2), -1, dtype=np.float32)

    centroids = np.mean(vertices, axis=1)
    cumulative_motion = centroids - centroids[0]

    pairwise_dists = np.array([cdist(frame, frame) for frame in vertices])
    max_indices = np.array([np.unravel_index(np.argmax(dists), dists.shape) for dists in pairwise_dists])

    first_farthest_pts = vertices[0][max_indices[0]]
    anterior[0], posterior[0] = first_farthest_pts
    head_history = [anterior[0]]

    previous_head = anterior[0]
    previous_tail = posterior[0]

    mean_distances = []

    for idx in range(1, T):
        farthest_two_pts = vertices[idx][max_indices[idx]]
        motion_vector = cumulative_motion[idx]
        projections = np.dot(farthest_two_pts - centroids[idx], motion_vector)

        head_idx = np.argmax(projections)
        tail_idx = 1 - head_idx
        candidate_head = farthest_two_pts[head_idx]
        candidate_tail = farthest_two_pts[tail_idx]

        distance = np.linalg.norm(candidate_head - candidate_tail)
        mean_distances.append(distance)

        if len(mean_distances) > smooth_factor:
            mean_distances.pop(0)

        mean_distance = np.mean(mean_distances)

        if np.linalg.norm(candidate_head - previous_head) > jump_threshold * mean_distance or np.linalg.norm(candidate_tail - previous_tail) > jump_threshold * mean_distance:
            candidate_head, candidate_tail = candidate_tail, candidate_head

        bearing = calculate_bearing(candidate_head, candidate_tail)

        if np.dot(np.array([candidate_tail[0] - candidate_head[0], candidate_tail[1] - candidate_head[1]]), np.array([np.cos(bearing), np.sin(bearing)])) < 0:
            candidate_head, candidate_tail = candidate_tail, candidate_head

        anterior[idx], posterior[idx] = candidate_head, candidate_tail
        head_history.append(candidate_head)

        if len(head_history) > smooth_factor:
            head_history.pop(0)
        previous_head, previous_tail = candidate_head, candidate_tail

    return anterior, posterior

DATA_PATH = r"D:\open_field_3\sample\blob_data\1.csv"
VIDEO_PATH = r"D:\open_field_3\sample\1.mp4"


df = pd.read_csv(DATA_PATH, index_col=0)
vertice_cols = [x for x in df.columns if 'vertice' in x]
data_arr = df[vertice_cols].values.reshape(len(df), int(len(vertice_cols)/2), 2)
# data_arr = data_arr[0:500]

start = time.time()
anterior, posterior = get_nose_tail_from_vertices(data_arr, fps=10, smooth_factor=1.0)
end = time.time()
print(end - start)
#anterior, posterior = smooth_nose_tail_hmm(anterior, posterior)
anterior_points = GeometryMixin.bodyparts_to_points(data=anterior)
posterior_points = GeometryMixin.bodyparts_to_points(data=posterior)
plotter = GeometryPlotter(geometries=[anterior_points, posterior_points], video_name=VIDEO_PATH, palette='jet', save_dir=r"D:\open_field_3\sample\post_ant", shape_opacity=1.0)
plotter.run()


# VIDEO_PATH = r"D:\EPM_2\EPM_1.mp4"
#
#
# img = read_img_batch_from_video(video_path=VIDEO_PATH, greyscale=True, start_frm=0, end_frm=500)
# imgs = np.stack(list(img.values()))
#
# optical_flow = compute_optical_flow(frames=imgs)

# df = pd.read_csv(DATA_PATH, index_col=0)
# vertice_cols = [x for x in df.columns if 'vertice' in x]
# data_arr = df[vertice_cols].values.reshape(len(df), int(len(vertice_cols)/2), 2)
# anterior, posterior = find_head_tail_using_optical_flow(vertices=data_arr, optical_flow=optical_flow)
#
# anterior_points = GeometryMixin.bodyparts_to_points(data=anterior)
# posterior_points = GeometryMixin.bodyparts_to_points(data=posterior)
#
# plotter = GeometryPlotter(geometries=[anterior_points, posterior_points], video_name=VIDEO_PATH, palette='jet', save_dir=r"D:\FST_ABOVE\anterior_posterior", shape_opacity=1.0)
# plotter.run()