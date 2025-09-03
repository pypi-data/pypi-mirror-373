from numba import cuda
import numpy as np
import math

from simba.utils.checks import check_valid_array

THREADS_PER_BLOCK = 1024

@cuda.jit()
def _directionality_to_static_targets_kernel(left_ear, right_ear, nose, target, results):
    i = cuda.grid(1)
    if i > left_ear.shape[0]:
        return
    else:
        LE, RE = left_ear[i], right_ear[i]
        N, Tx, Ty = nose[i], target[0], target[1]

        Px = abs(LE[0] - Tx)
        Py = abs(LE[1] - Ty)
        Qx = abs(RE[0] - Tx)
        Qy = abs(RE[1] - Ty)
        Nx = abs(N[0] - Tx)
        Ny = abs(N[1] - Ty)
        Ph = math.sqrt(Px * Px + Py * Py)
        Qh = math.sqrt(Qx * Qx + Qy * Qy)
        Nh = math.sqrt(Nx * Nx + Ny * Ny)
        if Nh < Ph and Nh < Qh and Qh < Ph:
            results[i][0] = 0
            results[i][1] = RE[0]
            results[i][2] = RE[1]
            results[i][3] = 1
        elif Nh < Ph and Nh < Qh and Ph < Qh:
            results[i][0] = 1
            results[i][1] = LE[0]
            results[i][2] = LE[1]
            results[i][3] = 1
        else:
            results[i][0] = 2
            results[i][1] = -1
            results[i][2] = -1
            results[i][3] = 0


def directionality_to_static_targets(left_ear: np.ndarray,
                                     right_ear: np.ndarray,
                                     nose: np.ndarray,
                                     target: np.ndarray) -> np.ndarray:

    """
    GPU helper to calculate if an animal is directing towards a static location (e.g., ROI centroid), given the target location and the left ear, right ear, and nose coordinates of the observer.

    .. note::
       Input left ear, right ear, and nose coordinates of the observer is returned by :func:`simba.mixins.feature_extraction_mixin.FeatureExtractionMixin.check_directionality_viable`

    .. seealso::
        For numba based CPU method, see :func:`simba.mixins.feature_extraction_mixin.FeatureExtractionMixin.jitted_line_crosses_to_static_targets`
        If the target is moving, consider :func:`simba.mixins.feature_extraction_mixin.FeatureExtractionMixin.jitted_line_crosses_to_nonstatic_targets`.


    .. csv-table::
       :header: EXPECTED RUNTIMES
       :file: ../../../docs/tables/directionality_to_static_targets.csv
       :widths: 10, 45, 45
       :align: center
       :class: simba-table
       :header-rows: 1

    :param np.ndarray left_ear: 2D array of size len(frames) x 2 with the coordinates of the observer animals left ear
    :param np.ndarray right_ear: 2D array of size len(frames) x 2 with the coordinates of the observer animals right ear
    :param np.ndarray nose: 2D array of size len(frames) x 2 with the coordinates of the observer animals nose
    :param np.ndarray target: 1D array of with x,y of target location
    :return: 2D array of size len(frames) x 4. First column represent the side of the observer that the target is in view. 0 = Left side, 1 = Right side, 2 = Not in view. Second and third column represent the x and y location of the observer animals ``eye`` (half-way between the ear and the nose). Fourth column represent if target is view (bool).
    :rtype: np.ndarray

    :example:
    >>> left_ear = np.random.randint(0, 500, (100, 2))
    >>> right_ear = np.random.randint(0, 500, (100, 2))
    >>> nose = np.random.randint(0, 500, (100, 2))
    >>> target = np.random.randint(0, 500, (2))
    >>> directionality_to_static_targets(left_ear=left_ear, right_ear=right_ear, nose=nose, target=target)
    """

    left_ear = np.ascontiguousarray(left_ear).astype(np.int32)
    right_ear = np.ascontiguousarray(right_ear).astype(np.int32)
    nose = np.ascontiguousarray(nose).astype(np.int32)
    target = np.ascontiguousarray(target).astype(np.int32)

    left_ear_dev = cuda.to_device(left_ear)
    right_ear_dev = cuda.to_device(right_ear)
    nose_dev = cuda.to_device(nose)
    target_dev = cuda.to_device(target)
    results = cuda.device_array((left_ear.shape[0], 4), dtype=np.int32)
    bpg = (left_ear.shape[0] + (THREADS_PER_BLOCK - 1)) // THREADS_PER_BLOCK
    _directionality_to_static_targets_kernel[bpg, THREADS_PER_BLOCK](left_ear_dev, right_ear_dev, nose_dev, target_dev, results)

    results = results.copy_to_host()
    return results


import time
sizes = [1000000, 5000000, 10000000, 20000000, 40000000, 80000000, 160000000, 240000000]
for size in sizes:
    x = []
    for i in range(3):
        left_ear = np.random.randint(0, 500, (size, 2), np.int32)
        right_ear = np.random.randint(0, 500, (size, 2), np.int32)
        nose = np.random.randint(0, 500, (size, 2), np.int32)
        target = np.random.randint(0, 500, (2), np.int32)
        start = time.perf_counter()
        directionality_to_static_targets(left_ear=left_ear, right_ear=right_ear, nose=nose, target=target)
        end = time.perf_counter()
        x.append(end - start)
    print(np.mean(x), np.std(x))


