@staticmethod
@jit(nopython=True)
def jitted_line_crosses_to_static_targets(left_ear_array: np.ndarray,
                                          right_ear_array: np.ndarray,
                                          nose_array: np.ndarray,
                                          target_array: np.ndarray) -> np.ndarray:
    """
    Jitted helper to calculate if an animal is directing towards a static location (e.g., ROI centroid),
    given the target location and the left ear, right ear, and nose coordinates of the observer.


    .. image:: _static/img/directing_static_targets.png
       :width: 400
       :align: center

    .. note::
       Input left ear, right ear, and nose coordinates of the observer is returned by
       :meth:`simba.mixins.feature_extraction_mixin.FeatureExtractionMixin.check_directionality_viable`

       If the target is moving, consider :func:`simba.mixins.feature_extraction_mixin.FeatureExtractionMixin.jitted_line_crosses_to_nonstatic_targets`.

    :param np.ndarray left_ear_array: 2D array of size len(frames) x 2 with the coordinates of the observer animals left ear
    :param np.ndarray right_ear_array: 2D array of size len(frames) x 2 with the coordinates of the observer animals right ear
    :param np.ndarray nose_array: 2D array of size len(frames) x 2 with the coordinates of the observer animals nose
    :param np.ndarray target_array: 1D array of with x,y of target location

    :return: 2D array of size len(frames) x 4. First column represent the side of the observer that the target is in view. 0 = Left side, 1 = Right side, 2 = Not in view.
    Second and third column represent the x and y location of the observer animals ``eye`` (half-way between the ear and the nose).
    Fourth column represent if target is view (bool).
    :rtype: np.ndarray

    """

    results_array = np.zeros((left_ear_array.shape[0], 4))
    for frame_no in range(results_array.shape[0]):
        Px = np.abs(left_ear_array[frame_no][0] - target_array[0])
        Py = np.abs(left_ear_array[frame_no][1] - target_array[1])
        Qx = np.abs(right_ear_array[frame_no][0] - target_array[0])
        Qy = np.abs(right_ear_array[frame_no][1] - target_array[1])
        Nx = np.abs(nose_array[frame_no][0] - target_array[0])
        Ny = np.abs(nose_array[frame_no][1] - target_array[1])
        Ph = np.sqrt(Px * Px + Py * Py)
        Qh = np.sqrt(Qx * Qx + Qy * Qy)
        Nh = np.sqrt(Nx * Nx + Ny * Ny)
        if Nh < Ph and Nh < Qh and Qh < Ph:
            results_array[frame_no] = [0, right_ear_array[frame_no][0], right_ear_array[frame_no][1], True]
        elif Nh < Ph and Nh < Qh and Ph < Qh:
            results_array[frame_no] = [1, left_ear_array[frame_no][0], left_ear_array[frame_no][1], True]
        else:
            results_array[frame_no] = [2, -1, -1, False]

    return results_array