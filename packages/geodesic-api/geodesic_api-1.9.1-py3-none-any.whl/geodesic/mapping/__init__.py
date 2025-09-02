import math

import numpy as np

try:
    import ipyleaflet  # noqa:F401
except ImportError as e:
    raise ImportError("to use mapping package, ipyleaflet must be installed") from e

from geodesic.mapping.base import Map, BBoxSelector

__all__ = ["Map", "BBoxSelector", "calc_zoom_center"]


def calc_zoom_center(bbox):
    x_min = 0
    y_min = 1
    x_max = 2
    y_max = 3

    c = bbox

    center = ((c[y_max] + c[y_min]) / 2.0, (c[x_max] + c[x_min]) / 2.0)

    scale_x = (c[x_max] - c[x_min]) / 360
    scale_y = (c[y_max] - c[y_min]) / 180
    scale = max(scale_x, scale_y)

    if scale > 0:
        zoom = math.ceil(-np.log2(scale + 1e-9))
    else:
        zoom = 21

    zoom = max(0, zoom)
    zoom = min(21, zoom)
    return zoom, center
