from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
from typing import Union, List
from simba.utils.checks import check_int, check_instance, check_float, check_valid_array
from simba.utils.enums import Formats

def smooth_geometry_bspline(data: Union[np.ndarray, Polygon, List[Polygon]], smooth_factor: float= 1.0, points: int = 50) -> List[Polygon]:
    """
    Smooths the geometry of polygons or coordinate arrays using B-spline interpolation.

    Accepts an input geometry, which can be a NumPy array, a single Polygon,
    or a list of Polygons, and applies a B-spline smoothing operation. The degree of
    smoothing is controlled by `smooth_factor`, and the number of interpolated points
    along the new smoothed boundary is determined by `points`.

    :param Union[np.ndarray, Polygon, List[Polygon]] data: The input geometry to be smoothed. This can be: A NumPy array of shape (N, 2) representing a single polygon. A NumPy array of shape (M, N, 2) representing multiple polygons. A `Polygon` object from Shapely. A list of `Polygon` objects.
    :param float smooth_factor: The smoothing factor for the B-spline. Higher values  result in smoother curves. Must be >= 0.1.
    :param int points: The number of interpolated points used to redefine the smoothed polygon boundary. Must be >= 3.
    :return: A list of smoothed polygons obtained by applying B-spline interpolation to the input geometry.
    :rtype: List[Polygon]

    :example:
    >>> polygon = np.array([[0, 0], [2, 1], [3, 3], [1, 4], [0, 3], [0, 0]])
    >>> polygon = Polygon(polygon)
    >>> smoothed_polygon = smooth_geometry_bspline(polygon)
    """


    check_float(name=f'{smooth_geometry_bspline.__name__} smooth_factor', min_value=0.1, raise_error=True, value=smooth_factor)
    check_int(name=f'{smooth_geometry_bspline.__name__} points', min_value=3, raise_error=True, value=points)
    check_instance(source=f'{smooth_geometry_bspline.__name__} data', instance=data, accepted_types=(np.ndarray, Polygon, list), raise_error=True)
    if isinstance(data, Polygon):
        coords = [np.array(data.exterior.coords)]
    elif isinstance(data, np.ndarray):
        check_valid_array(data=data, source=f'{smooth_geometry_bspline.__name__} data', accepted_ndims=(2, 3,), min_axis_0=3, accepted_dtypes=Formats.NUMERIC_DTYPES.value)
        if data.ndim == 2:
            coords = [np.copy(data)]
        else:
            coords = np.copy(data)
    else:
        coords = []
        for i in range(len(data)):
            coords.append(np.array(data[i].exterior.coords))
    u = np.linspace(0, 1, points)  # Number of interpolated points
    results = []
    for i in range(len(coords)):
        tck, _ = splprep(coords[i].T, s=smooth_factor, per=True)
        results.append(Polygon(np.array(splev(u, tck)).T))
    return results




















    #
    #
    #
    #
    # return smooth_points

# Example polygon
# polygon = np.array([[0, 0], [2, 1], [3, 3], [1, 4], [0, 3], [0, 0]])
# polygon = Polygon(polygon)
# smoothed_polygon = smooth_geometry_bspline(polygon)
#
# # Plot
# plt.plot(polygon[:, 0], polygon[:, 1], 'bo-', label="Original")
# plt.plot(smoothed_polygon[:, 0], smoothed_polygon[:, 1], 'r-', label="Smoothed")
# plt.legend()
# plt.show()