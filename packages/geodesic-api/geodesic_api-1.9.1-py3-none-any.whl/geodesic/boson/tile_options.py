from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _IntDescr,
    _TypeConstrainedDescr,
    _FloatDescr,
    _BoolDescr,
)


class VectorTileOptions(_APIObject):
    clip_extent = _IntDescr(doc="extent to clip vector tiles to")
    simplify = _FloatDescr(doc="simplification tolerance for vector tiles")
    min_area = _FloatDescr(doc="minimum area for a polygon feature in vector tiles")
    min_length = _FloatDescr(
        doc="minimum length for a line feature in vector tiles (default 1 unit)"
    )
    skip_validate = _BoolDescr(doc="skip validation of geometries when creating vector tiles")
    skip_repair = _BoolDescr(doc="skip repairing of geometries when creating vector tiles")
    feature_limit = _IntDescr(
        doc="maximum number of features to include in a vector tile (default 50000)"
    )
    deduplicate_points = _BoolDescr(
        doc="deduplicate points in vector tiles (only works for points, not all geometry types)"
    )


class RasterTileOptions(_APIObject):
    pass


class TileOptions(_APIObject):
    min_zoom = _IntDescr(doc="minimum zoom level for tile services")
    max_zoom = _IntDescr(doc="maximum zoom level for tile services")
    vector = _TypeConstrainedDescr(
        (VectorTileOptions, dict), doc="options for vector tiles services"
    )
    raster = _TypeConstrainedDescr(
        (RasterTileOptions, dict), doc="options for raster tiles services"
    )
