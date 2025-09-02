import datetime

from typing import List, Tuple, Union, Any

from dateutil.parser import parse

from geodesic.bases import _APIObject
from geodesic.utils import datetime_to_utc
from geodesic.descriptors import (
    _BoolDescr,
    _ListDescr,
    _StringDescr,
    _DictDescr,
)
from geodesic.boson.asset_bands import AssetBands

# Middleware types
SEARCH_FILTER_CQL2 = "cql2"
SEARCH_FILTER_SPATIAL = "spatial"
SEARCH_FILTER_DATETIME = "datetime"
SEARCH_TRANSFORM_CREATE_COLLECTION = "create-collection"
SEARCH_TRANSFORM_RENAME_FIELDS = "rename-fields"
SEARCH_TRANSFORM_GEOMETRY = "transform-geometry"
SEARCH_TRANSFORM_COMBINE_FIELDS = "combine-fields"
SEARCH_TRANSFORM_FLATTEN_FIELDS = "flatten-fields"
SEARCH_TRANSFORM_DEFAULT_DATETIME_RANGE = "default-datetime-range"
SEARCH_TRANSFORM_S2 = "s2"
SEARCH_TRANSFORM_H3 = "h3"
SEARCH_TRANSFORM_POINTS_TO_POLYLINE = "points-to-polyline"
SEARCH_TRANSFORM_CALCULATE_FIELD = "calculate-field"
SEARCH_TRANSFORM_COMPUTE_ID = "compute-id"
PIXELS_TRANSFORM_COLORMAP = "colormap"
PIXELS_TRANSFORM_CREATE_ASSET = "create-asset"
PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS = "default_asset_bands"
PIXELS_TRANSFORM_RASTERIZE = "rasterize"
PIXELS_TRANSFORM_RESCALE_SHIFT = "rescale-shift"
PIXELS_TRANSFORM_DEFAULT_DATETIME_RANGE = "default-datetime-range"
PIXELS_TRANSFORM_BAND_ARITHMETIC = "band-arithmetic"
PIXELS_TRANSFORM_INVERSE_DISTANCE_WEIGHTING = "inverse-distance-weighting"
PIXELS_TRANSFORM_DATETIME_DIFFERENCE = "datetime-difference"


def parsedate(dt):
    try:
        return parse(dt)
    except TypeError:
        return dt


class Input(_APIObject):
    asset = _StringDescr(doc="asset to use as input")
    bands = _ListDescr(item_type=(int, str), doc="bands to use as input")
    collection = _StringDescr(doc="collection to use as input")


class Output(_APIObject):
    asset = _StringDescr(doc="asset to use as output")
    bands = _ListDescr(item_type=(int, str), doc="bands to use as output")
    collection = _StringDescr(doc="collection to use as output")
    exported = _BoolDescr(doc="show collection/asset in dataset info")


class Middleware(_APIObject):
    _limit_setitem = ("type", "properties", "inputs", "outputs")
    type = _StringDescr(
        doc="type of middleware to apply to a provider",
        soft_one_of=[
            SEARCH_FILTER_DATETIME,
            SEARCH_FILTER_CQL2,
            SEARCH_FILTER_SPATIAL,
            SEARCH_TRANSFORM_CREATE_COLLECTION,
            SEARCH_TRANSFORM_RENAME_FIELDS,
            SEARCH_TRANSFORM_COMBINE_FIELDS,
            SEARCH_TRANSFORM_FLATTEN_FIELDS,
            SEARCH_TRANSFORM_GEOMETRY,
            SEARCH_TRANSFORM_DEFAULT_DATETIME_RANGE,
            SEARCH_TRANSFORM_S2,
            SEARCH_TRANSFORM_H3,
            SEARCH_TRANSFORM_POINTS_TO_POLYLINE,
            SEARCH_TRANSFORM_CALCULATE_FIELD,
            SEARCH_TRANSFORM_COMPUTE_ID,
            PIXELS_TRANSFORM_COLORMAP,
            PIXELS_TRANSFORM_CREATE_ASSET,
            PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
            PIXELS_TRANSFORM_RASTERIZE,
            PIXELS_TRANSFORM_RESCALE_SHIFT,
            PIXELS_TRANSFORM_DEFAULT_DATETIME_RANGE,
            PIXELS_TRANSFORM_BAND_ARITHMETIC,
            PIXELS_TRANSFORM_INVERSE_DISTANCE_WEIGHTING,
            PIXELS_TRANSFORM_DATETIME_DIFFERENCE,
        ],
    )
    properties = _DictDescr(doc="properties (if any) to configure the middleware")
    inputs = _ListDescr(item_type=(Input, dict), doc="inputs to the middleware")
    outputs = _ListDescr(item_type=(Output, dict), doc="outputs to the middleware")


def _collection_inputs(
    input_collection: str = None,
    output_collection: str = None,
) -> Tuple[List[Input], List[Output]]:
    inputs = []
    if input_collection:
        inputs = [Input(collection=input_collection)]

    outputs = []
    if output_collection:
        outputs = [Output(collection=output_collection, exported=True)]

    return inputs, outputs


def _asset_band_inputs(asset: str, band: Union[int, str]) -> List[Input]:
    return [Input(asset=asset, bands=[band])]


def _asset_bands_inputs(asset: str, bands: List[Union[int, str]]) -> List[Input]:
    return [Input(asset=asset, bands=bands)]


def _asset_band_outputs(asset: str, band: Union[int, str]) -> List[Output]:
    return [Output(asset=asset, bands=[band], exported=True)]


def _asset_bands_outputs(asset: str, bands: List[Union[int, str]]) -> List[Output]:
    return [Output(asset=asset, bands=bands, exported=True)]


def cql2_filter(input_collection: str = None, output_collection: str = None) -> Middleware:
    """Adds CQL filtering to a provider that may not implement it natively.

    Args:
        input_collection: name of the input collection to filter
        output_collection: name of the output collection to filter
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(type=SEARCH_FILTER_CQL2, inputs=inputs, outputs=outputs)


def spatial_filter(input_collection: str = None, output_collection: str = None) -> "Middleware":
    """Adds spatial filtering to a provider that may not implement it natively.

    Args:
        input_collection: name of the input collection to filter
        output_collection: name of the output collection to filter
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(type=SEARCH_FILTER_SPATIAL, inputs=inputs, outputs=outputs)


def datetime_filter(
    field: str, input_collection: str = None, output_collection: str = None
) -> "Middleware":
    """Adds datetime filtering to a provider that may not implement it natively.

    Args:
        field: name of the datetime field to filter on
        input_collection: name of the input collection to filter
        output_collection: name of the output collection to filter
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_FILTER_DATETIME,
        properties={"datetime_field": field},
        inputs=inputs,
        outputs=outputs,
    )


def rename_fields(
    case=None, field_map={}, input_collection: str = None, output_collection: str = None
) -> "Middleware":
    """Rename fields in the `properties` of a search response.

    Args:
        case (str, optional): case to apply to the field names. Defaults to None.
            One of ["upper", "lower"]
        field_map (dict, optional): mapping of old field names to new field names.
            Defaults to {}.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Examples:
        >>> # Rename the field "old_field" to "new_field"
        >>> transform = rename_fields(field_map={"old_field": "new_field"})

        >>> # Rename the field "old_field" to "new_field" and make it uppercase
        >>> transform = rename_fields(case="upper", field_map={"old_field": "new_field"})
    """  # noqa: E501
    properties = {"field_map": field_map}
    if case is not None and case in ["upper", "lower"]:
        properties["case"] = case
    elif case is not None:
        raise ValueError(f"case must be one of ['upper', 'lower'], got {case}")

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_TRANSFORM_RENAME_FIELDS, properties=properties, inputs=inputs, outputs=outputs
    )


def create_collection(input_collection: str = None, output_collection: str = None) -> "Middleware":
    """Create a new collection from the input collection.

    Args:
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to create a new collection from the input collection

    Examples:
        >>> # Create a new collection from the input collection
        >>> transform = create_collection()
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_TRANSFORM_CREATE_COLLECTION,
        properties={},
        inputs=inputs,
        outputs=outputs,
    )


def combine_fields(
    new_field: str,
    fields: List[str],
    separator: str = "",
    sprintf: str = "",
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Combine fields in the `properties` of a search response.

    Args:
        new_field (str): name of the new field to create
        fields (List[str]): fields to combine
        separator (str, optional): separator to use when combining fields. Defaults to " ".
        sprintf (str, optional): sprintf format to use when combining fields. This uses golang
        format strings to format the fields into one combined string field. For instance,
        "%d.2 %s" would print "2.00 dollars" if the field values were 2 and "dollars".
        For more information about the formatting see https://pkg.go.dev/fmt.
        All fields must have values for the sprintf to be executed. Defaults to "".
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Examples:
        >>> # Combine the fields STATE_FIPS and COUNTY_FIPS into a new field called FIPS
        >>> transform = combine_fields(
        ...     new_field="FIPS",
        ...     fields=["STATE_FIPS", "COUNTY_FIPS"],
        ...     separator=""
        ... )

        >>> # Combine the fields STATE_FIPS and COUNTY_FIPS into a new field called FIPS
        >>> transform = combine_fields(
        ...     new_field="FIPS",
        ...     fields=["STATE_FIPS", "COUNTY_FIPS"],
        ...     sprintf="%02d%03d"
        ... )
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="combine-fields",
        properties={
            "new_field": new_field,
            "fields": fields,
            "separator": separator,
            "sprintf": sprintf,
        },
        inputs=inputs,
        outputs=outputs,
    )


def flatten_fields(
    separator: str = "_",
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Flatten nested fields in the `properties` of a search response.

    This middleware will flatten nested fields in the properties of a search response.
    For instance, if a feature has a property called "region" with a sub-property called
    "name", this middleware will flatten it to "region_name".

    Args:
        separator (str, optional): separator to use when flattening fields. Defaults to "_".
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to flatten fields in the properties of a search response

    Examples:
        >>> # Flatten nested fields in the properties of a search response
        >>> transform = flatten_fields(separator="_")
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="flatten-fields",
        properties={
            "separator": separator,
        },
        inputs=inputs,
        outputs=outputs,
    )


def centroid(input_collection: str = None, output_collection: str = None) -> "Middleware":
    """Calculate the centroid of the queried geometry.

    This middleware will calculate the centroid of the geometry and return it in a new
    collection called "centroid". In the case of multi-geometries, the centroid of the entire
    geometry will be calculated.

    When creating this middleware, most of the time you will want to apply it after
    any filtering happens, so that the centroid is calculated on the filtered geometry.

    Args:
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to calculate the centroid of the queried geometry

    Examples:
        >>> # Add the centroid middleware to a dataset view
        >>> ds_with_centroid = ds.view(
        ...     middleware=[
        ...         centroid()
        ...     ]
        ... )
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="transform-geometry",
        properties={
            "transform": "centroid",
            "parameters": {},
        },
        inputs=inputs,
        outputs=outputs,
    )


def convex_hull(input_collection: str = None, output_collection: str = None) -> "Middleware":
    """Calculate the convex hull of the queried geometry.

    This middleware will calculate the convex hull of the geometry and return it in a new
    collection called "convex_hull". The convex hull is the smallest convex polygon that
    encloses the geometry.  In the case of multi-geometries, the convex hull of the entire
    geometry will be calculated.

    When creating this middleware, most of the time you will want to apply it after
    any filtering happens, so that the centroid is calculated on the filtered geometry.

    Args:
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to calculate the convex hull of the queried geometry

    Examples:
        >>> # Add the convex_hull middleware to a dataset view
        >>> ds_with_convex_hull = ds.view(
        ...     middleware=[
        ...         convex_hull()
        ...     ]
        ... )
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="transform-geometry",
        properties={
            "transform": "convex_hull",
            "parameters": {},
        },
        inputs=inputs,
        outputs=outputs,
    )


def bounds(input_collection: str = None, output_collection: str = None) -> "Middleware":
    """Calculate the bounds of the queried geometry.

    This middleware will calculate the bounds of the geometry and return it in a new collection
    called "bounds". The bounds in this case are a rectangle that encloses the geometry.
    In the case of multi-geometries, the bounds of the entire geometry will be calculated.

    When creating this middleware, most of the time you will want to apply it after
    any filtering happens, so that the centroid is calculated on the filtered geometry.

    Args:
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to calculate the bounds of the queried geometry

    Examples:
        >>> # Add the bounds middleware to a dataset view
        >>> ds_with_bounds = ds.view(
        ...     middleware=[
        ...         bounds()
        ...     ]
        ... )
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="transform-geometry",
        properties={
            "transform": "bounds",
            "parameters": {},
        },
        inputs=inputs,
        outputs=outputs,
    )


def simplify(
    threshold: float, stride: int = 2, input_collection: str = None, output_collection: str = None
) -> "Middleware":
    """Simplify the queried geometry.

    This middleware will simplify the geometry by removing points according to the
    `Ramer-Douglas-Peucker Algorithm<https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`_.
    This is useful for reducing the size of the geometry for visualization or other purposes.
    The threshold is approximately the scale at which points will be removed. A smaller
    threshold will cause more points of the original geometry to be kept, and larger will cause
    more to be thrown away. The stride parameter controls how many points are checked against
    the threshold when simplifying. A larger stride will simplify the geometry faster but may
    result in a less accurate simplification. If you are not familiar with this algorithm, it
    is recommended that you leave stride at the default value of 2.

    When creating this middleware, most of the time you will want to apply it after
    any filtering happens, so that the centroid is calculated on the filtered geometry.

    .. note::
        The units of the threshold are the same as the units of the spatial reference of the
        geometry. For instance, if the geometry is in EPSG:4326, the threshold will be in degrees.

    Args:
        threshold (float): distance between points that will be removed
        stride (int, optional): number of points to skip when simplifying. Defaults to 2.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to simplify the queried geometry

    Examples:
        >>> # Add the simplify middleware to a dataset view
        >>> simplified_ds = ds.view(
        ...     middleware=[
        ...         simplify(threshold=0.01, stride=3)
        ...     ]
        ... )
    """  # noqa: E501
    if threshold < 0:
        raise ValueError("threshold must be greater than or equal to 0")

    if stride < 1:
        raise ValueError("stride must be greater than or equal to 1")

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="transform-geometry",
        properties={
            "transform": "simplify",
            "parameters": {"threshold": threshold, "stride": stride},
        },
        inputs=inputs,
        outputs=outputs,
    )


def buffer(
    distance: float = None,
    distance_field: str = None,
    segments: int = 10,
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Buffer the queried geometry.

    This middleware will buffer the geometry by a given distance. The distance is the distance
    to buffer the geometry in the units of the spatial reference of the geometry. For instance,
    if the geometry is in EPSG:4326, the distance will be in degrees. The segments parameter
    controls the number of segments to use when approximating the buffer. A larger number of
    segments will result in a smoother buffer but will result in larger geometries.

    This middleware is especially useful when combined with the rasterize middleware to create
    a buffer around points. When rasterizing points with the buffer middleware, the buffer will
    ensure that the points do not become incredibly small when a high rasterization resolution
    is used.

    Args:
        distance (float): distance to buffer the geometry
        distance_field (str): field in the properties of the feature that contains the distance
            to buffer the geometry
        segments (int, optional): number of segments to use when approximating the buffer.
            Defaults to 10.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to buffer the queried geometry

    Examples:
        >>> # Add the buffer middleware to a dataset view
        >>> buffered_ds = ds.view(
        ...     name="buffered-ds",
        ...     middleware=[
        ...         buffer(distance=0.01, segments=32)
        ...     ]
        ... )
    """
    if distance is None and distance_field is None:
        raise ValueError("Must provide either a distance or a distance_field")

    if distance is not None and distance <= 0:
        raise ValueError("distance must be greater than 0")

    properties = {"type": "transform-geometry"}
    if distance is not None:
        properties["properties"] = {
            "transform": "buffer",
            "parameters": {"distance": distance, "segments": segments},
        }
    else:
        properties["properties"] = {
            "transform": "buffer",
            "parameters": {"distance_field": distance_field, "segments": segments},
        }

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(**properties, inputs=inputs, outputs=outputs)


def default_datetime_range(
    start: Union[datetime.datetime, str] = None,
    end: Union[datetime.datetime, str] = None,
    before_now: datetime.timedelta = None,
    input_collection: str = None,
    output_collection: str = None,
    asset: str = None,
) -> "Middleware":
    """Sets the default datetime range in a search request on a Dataset.

    This is useful for when you are creating a dataset that points to a very long time history,
    but by default wish to show a specific time range. This can be useful for things like
    showing the last 24 hours of data.

    Parameters:
        start: start of the default datetime range. Defaults to None.
        end: end of the default datetime range. Defaults to None.
        before_now: time delta before now to set the start of the default datetime range. If
            provided, will be used instead of start/end and will dynamically be used based on
            the current time whenever there is a new request. Defaults to None.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)
        asset (str, optional): asset to use for the default datetime range. If provided, will
            apply the default datetime range to the asset. Use instead of input/output collection.

    Example:
        >>> # Set the default datetime range to be the last 24 hours
        >>> default_datetime_transform = default_datetime_range(before_now=datetime.timedelta(days=1))

        >>> # Set the default datetime range to be from 2021-01-01 to 2021-01-02
        >>> default_datetime_transform = default_datetime_range(start="2021-01-01", end="2021-01-02")
    """  # noqa: E501
    properties = _default_datetime_range_props(start, end, before_now)
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    if asset:
        inputs = _asset_bands_inputs(asset, [])
    return Middleware(
        type="default-datetime-range", properties=properties, inputs=inputs, outputs=outputs
    )


def s2(
    level: int,
    return_all: bool = False,
    replace_geometry: bool = False,
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Adds the S2 cell to properties.

    See http://s2geometry.io/devguide/s2cell_hierarchy.html for more details.

    Defaults to returning the S2 cell of the centroid of the geometry

    If return_all is set to True, will return a list of the S2 cells that cover the geometry

    Adds a property to the feature properties called "s2_[level]" where [level] is the level of
    the S2 cell.

    If return_all is set to True, will return a list of the S2 cells that cover the geometry,
    in a property called "s2_[level]_all".

    If replace_geometry is set, the geometry of the feature will be overwritten with the geometry
    of the S2 cell(s).

    Args:
        level: S2 level. Must be between 0 and 30
        return_all: whether to return all S2 cells that cover the geometry. Defaults to False
        replace_geometry: overwrite the geometry of the feature with the S2 cell geometry.
            Defaults to False.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to add S2 cell to feature properties

    Examples:
        >>> # Add the S2 cell to the properties of the search response
        >>> transform = s2(level=10)
    """
    if level < 0 or level > 30:
        raise ValueError("S2 level must be between 0 and 30")

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_TRANSFORM_S2,
        properties={"level": level, "return_all": return_all, "replace_geometry": replace_geometry},
        inputs=inputs,
        outputs=outputs,
    )


def h3(
    resolution: int,
    return_all: bool = False,
    replace_geometry: bool = False,
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Adds the H3 cell to properties.

    See https://h3geo.org/ for more details.

    Defaults to returning the H3 cell of the centroid of the geometry

    If return_all is set to True, will return a list of the H3 that are enclosed by the geometry

    Adds a property to the feature properties called "h3_[resolution]" where [resolution] is the
    level of the H3 cell.

    If return_all is set to True, will return a list of the H3 cells that cover the geometry,
    in a property called "h3_[resolution]_all".

    If replace_geometry is set, the geometry of the feature will be overwritten with the geometry
    of the H3 cell(s).

    Args:
        resolution: H3 resolution. Must be between 0 and 15
        return_all: whether to return all H3 cells that cover the geometry. Defaults to False
        replace_geometry: overwrite the geometry of the feature with the H3 cell geometry.
            Defaults to False.
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to add H3 cell to feature properties

    Examples:
        >>> # Add the H3 cell to the properties of the search response
        >>> transform = h3(resolution=10)
    """
    if resolution < 0 or resolution > 15:
        raise ValueError("H3 resolution must be between 0 and 15")

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_TRANSFORM_H3,
        properties={
            "resolution": resolution,
            "return_all": return_all,
            "replace_geometry": replace_geometry,
        },
        inputs=inputs,
        outputs=outputs,
    )


def points_to_polyline(
    track_id_field: str,
    sort_field: str,
    point_feature_limit: int = None,
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Create polyline/linestring features from an ordered sequence of points.

    Args:
        track_id_field (str): field in the properties that contains the track ID.
            Points will be grouped together on this field.
        sort_field (str): field in the properties that contains the sort order. This field
            can be a datetime field or a numeric field.
        point_feature_limit (int, optional): maximum number of point features to use when
            creating the polylines. Defaults to None (server's default limit, 500000).
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Examples:
        >>> # Create ship tracks based on a vessel's MMSI
        >>> transform = points_to_polyline(
        ...     track_id_field="MMSI",
        ...     sort_field="timestamp"
        ... )

        >>> # Create linear pipeline geometries based on a pipeline ID
        >>> transform = points_to_polyline(
        ...     track_id_field="pipeline_id",
        ...     sort_field="mile_marker"
        ... )
    """
    properties = {
        "track_id_field": track_id_field,
        "sort_field": sort_field,
    }

    if point_feature_limit is not None:
        properties["point_feature_limit"] = point_feature_limit

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type=SEARCH_TRANSFORM_POINTS_TO_POLYLINE,
        properties=properties,
        inputs=inputs,
        outputs=outputs,
    )


def calculate_field(
    new_field: str,
    expression: str,
    skip_if_null: bool = False,
    skip_if_nan: bool = False,
    fill_value: float = None,
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Creates a new field in the search response based on an expression.

    The fields in the expression must be numeric fields.

    Args:
        new_field: name of the new field to create
        expression: expression to calculate the new field
        skip_if_null: whether to skip the calculation if any of the fields in the expression do
            not exist.  Useful when not every feature contains a property used in the
            expression. Defaults to False.
        fill_value: value to fill the new field with if the expression is not calculated.
            Defaults to None.
        skip_if_nan: skip the calculation on any field where the expression evaluates to NaN
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to calculate a new field in the search response

    Examples:
        >>> # Calculate a new field called "sum" that is the sum of "field_1" and "field_2"
        >>> transform = calculate_field(
        ...     new_field="sum",
        ...     expression="field_1 + field_2"
        ... )

        >>> # Calculate a new field called "plus_one" that is "field_1" + 1
        >>> transform = calculate_field(
        ...     new_field="plus_one",
        ...     expression="field_1 + 1"
        ... )

        >>> # Calculate a new field called "div" that is "(field_1 + 5) / field_2"
        >>> transform = calculate_field(
        ...     new_field="div",
        ...     expression="(field_1 + 5) / field_2",
        ...     skip_if_null=True
        ... )

        >>> # Calculate a new field log scale which uses the log function "10 * log10(field_1)"
        >>> transform = calculate_field(
        ...     new_field="loc_scale_field_1",
        ...     expression="10 * log10(field_1)",
        ...     skip_if_nan=True, # If log10(0) is attempted the feature will be skipped
        ... )

    Functions:

        * exp(x) - e^x
        * sqrt(x) - square root of x
        * log(x, b) - log of x with base b, if no base is provided the default is e
        * log10(x) - log base 10 of x
        * abs(x) - absolute value of x
        * sin(x) - sine of x
        * cos(x) - cosine of x
        * tan(x) - tangent of x
        * floor(x) - rounds x down to nearest integer
        * ceil(x) - rounds x up to nearest integer
        * round(x) - rounds x up or down to nearest integer
        * pow(x, y) - x to the power of y
        * min(x, y, z) - smallest value of x, y, z - takes 2 or more arguments
        * max(x, y, z) - largest value of x, y, z - takes 2 or more arguments
        * clamp(x, min, max) - returns x unless x is greater than max or less than min
    """
    properties = {
        "new_field": new_field,
        "expression": expression,
        "skip_if_null": skip_if_null,
        "skip_if_nan": skip_if_nan,
    }

    if fill_value is not None:
        properties["fill_value"] = fill_value

    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(
        type="calculate-field",
        properties=properties,
        inputs=inputs,
        outputs=outputs,
    )


def compute_id(
    input_collection: str = None,
    output_collection: str = None,
) -> "Middleware":
    """Compute an ID for each feature in the search response.

    This middleware will compute an ID for each feature in the search response. The ID is
    computed by hashing the properties and geometry of the feature. This is useful for when you
    want to uniquely identify each feature in the search response when the features do not have
    an existing ID.

    Args:
        input_collection (str, optional): name of the input collection to apply transform to.
            Defaults to None (all collections)
        output_collection (str, optional): name of the virtual collection that the transform
            will be applied to. Defaults to None (no virtual collection created)

    Returns:
        Middleware: middleware to compute an ID for each feature in the search response

    Examples:
        >>> # Compute an ID for each feature in the search response
        >>> transform = compute_id()
    """
    inputs, outputs = _collection_inputs(input_collection, output_collection)
    return Middleware(type=SEARCH_TRANSFORM_COMPUTE_ID, inputs=inputs, outputs=outputs)


def colormap(
    *,
    asset: str,
    band: Union[int, str],
    colormap_name: str = "magma",
    lookup_table: List[List[int]] = None,
    min: float = None,
    max: float = None,
    rescale: bool = False,
    no_data_value: float = None,
    no_data_after_rescale: bool = False,
    asset_name: str = "colormap",
) -> "Middleware":
    """Apply a colormap to the pixels data from an existing asset in the dataset.

    Args:
        asset: asset to apply the colormap to
        band: band to apply the colormap to
        colormap_name: name of the colormap to apply. Defaults to "magma".
        lookup_table: lookup table to apply. Defaults to None. This can be used to provide a
            custom colormap via a lookup table. In this case, this should be a list of lists
            where each sublist is a color, including the alpha channel. For instance,
            [[0, 0, 0, 255], [255, 255, 255, 255]] would create a colormap that goes from black
            to white in two steps, splitting values below 0,5 to black and above to white.
        min: minimum value of the colormap. Valid only if rescale is True. Defaults to None.
        max: maximum value of the colormap. Valid only if rescale is True. Defaults to None.
        rescale: whether to rescale the colormap to the min and max values. If min/max are None,
            statistics of the dataset (if available) will be used, otherwise the values of the
            current response will be used.  Defaults to False.
        no_data_value: value to use for pixels with no data. These values will be transparent.
            Defaults to None.
        no_data_after_rescale: whether to set the no data value on rescaled values instead of
            prior to rescaleing. Defaults to False.
        asset_name: name of the asset to create. Defaults to "colormap".

    Examples:
        >>> # Apply the magma colormap to the rasterized band of the asset "rasterized"
        >>> colormap_transform = colormap(asset="rasterized", band="rasterized", min=0, max=1000)
    """  # noqa: E501
    properties = {
        "colormap_name": colormap_name,
        "rescale": rescale,
    }
    if lookup_table is not None:
        properties.pop("colormap_name")
        properties["lookup_table"] = lookup_table
    if min is not None:
        properties["min"] = min
    if max is not None:
        properties["max"] = max
    if no_data_value is not None:
        properties["no_data_value"] = no_data_value
        properties["no_data_after_rescale"] = no_data_after_rescale

    inputs = _asset_band_inputs(asset, band)
    outputs = _asset_bands_outputs(asset_name, bands=["red", "green", "blue", "alpha"])

    return Middleware(
        type=PIXELS_TRANSFORM_COLORMAP, properties=properties, inputs=inputs, outputs=outputs
    )


def create_asset(
    new_asset_bands: AssetBands,
    input_asset_bands: List[AssetBands],
) -> "Middleware":
    """Create a new asset from existing assets in a dataset.

    Args:
        new_asset_bands: new asset bands to create
        input_asset_bands: input asset bands to use for the new asset
    """
    return Middleware(
        type=PIXELS_TRANSFORM_CREATE_ASSET,
        properties={},
        inputs=[Input(asset=asset.asset, bands=asset.bands) for asset in input_asset_bands],
        outputs=[Output(exported=True, **new_asset_bands)],
    )


def rescale_shift(
    asset: str,
    bands: List[Union[int, str]] = None,
    scale: List[float] = None,
    shift: List[float] = None,
    clamp: List[float] = None,
    asset_name: str = "rescaled",
) -> "Middleware":
    """Rescale the pixel values of an asset in a dataset.

    Rescales the pixel values of an asset in a dataset by subtracting a shift from the pixel
    values and then dividing by a scale. This is useful for things like normalizing the pixel
    values of an image to be between 0 and 1 or 0 and 255, or recalibration pixels values under
    a linear transformation.

    If scale/shift is not specified, will rescale by the local min/max of the pixel values
    across all bands. Do not use this with tiled services as each tile will be rescaled based on
    its min/max and the result will be a checkerboard pattern. Instead, use the scale/shift
    parameters to rescale the entire image tile set.

    Args:
        asset: asset to rescale/shift
        bands: bands to rescale/shift. If not specified, will use all bands for the
            specified asset.
        scale: scale values for each band. This will divide the shifted pixel values by this
            value.
        shift: shift values for each band. This will subtract this value from the pixel values
            prior to scaling.
        clamp: If specified, must be 2 numbers to clamp the values between ranges. Values less
            than clamp[0] will be set to clamp[0] and values greater than clamp[1] will be set
            to clamp[1].  Defaults to None (no clamping)
        asset_name: name of the asset to create. Defaults to "rescaled".

    Examples:
        >>> # Rescale the pixel values of an asset with values in uint8 to be between 0 and 1
        >>> transform = rescale_shift(
        ... asset="my_asset",
        ... bands=[0, 1, 2],
        ... scale=[255],
        ... shift=[0],
        ... asset_name="rescaled"
        ... )

        >>> # Rescale all bands for "my_asset" to be between 0 and 255
        >>> transform = rescale_shift(
        ... asset="my_asset",
        ... asset_name="rescaled"
        ... )

        >>> # Rescale "red", "green", and "blue" bands for "image" to be between 0 and 1
        >>> # using a known min/max
        >>> transform = rescale_shift(
        ... asset="image",
        ... bands=["red", "green", "blue"],
        ... scale=[12345, 12345, 12345],
        ... shift=[123, 456, 789],
        ... asset_name="rescaled-rgb"
        ... )
    """
    properties = {}
    if scale is not None and shift is None:
        raise ValueError("Must provide a shift if providing a scale")
    if shift is not None and scale is None:
        raise ValueError("Must provide a scale if providing a shift")
    if scale is not None and shift is not None and len(scale) != len(shift):
        raise ValueError("Scale and shift must be the same length")
    if clamp is not None and len(clamp) != 2:
        raise ValueError("Clamp must be a list of 2 numbers")
    if scale is not None:
        properties["scale"] = scale
    if shift is not None:
        properties["shift"] = shift
    if clamp is not None:
        properties["clamp"] = clamp

    inputs = _asset_band_inputs(asset, bands)
    outputs = _asset_band_outputs(asset_name, bands)

    return Middleware(
        type=PIXELS_TRANSFORM_RESCALE_SHIFT,
        properties=properties,
        inputs=inputs,
        outputs=outputs,
    )


def default_asset_bands(default_asset_bands: List[AssetBands]) -> "Middleware":
    """Sets the default value of asset_bands in a pixels request on a Dataset.

    This is useful for when you are creating a static dataset and want to set the default bands
    that will be used in the pixels request or for when you have a dataset that has multiple
    bands and you want to set the default bands that will be used in the pixels request.

    Parameters:
        default_asset_bands: list of AssetBands objects that will be used as the default bands
        in the pixels request

    Example:
        >>> # Set the default asset bands to be the first band of the rasterized asset
        >>> default_asset_transform = Middleware.default_asset_bands(
        ...     [AssetBands(asset="rasterized", bands=[0])]
        ... )
    """
    return Middleware(
        type=PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
        properties={"asset_bands": default_asset_bands},
    )


def rasterize(
    attribute_name: str = None,
    value: Any = None,
    use_z: bool = False,
    initialize_value: Any = None,
    invert: bool = False,
    all_touched: bool = False,
    add: bool = False,
    input_collection: str = None,
    asset_name: str = "rasterized",
    band_name: str = "rasterized",
    feature_limit: int = 25000,
) -> "Middleware":
    """Creates a rasterized image from a feature collection as a new raster asset.

    Rasterize middleware is useful for performing simple aggregations on a feature collection.
    This can be useful for things like creating a population density raster from a feature
    collection of population counts or creating a binary raster from a feature collection of
    labels in a segmentation task.

    Args:
        attribute_name: attribute name to rasterize. Defaults to None.
        value: value to rasterize. Defaults to None.
        use_z: whether to use the z value of the feature. Defaults to False.
        initialize_value: value to initialize the raster with. Defaults to None.
        invert: invert which pixels are rasterize. Defaults to False.
        all_touched: whether to rasterize all pixels touched by the feature. Defaults to False.
        add: whether to add the raster to the asset. Defaults to False.
        input_collection: collection to rasterize. Defaults to None (all/default collection).
        asset_name: name of the asset to create. Defaults to "rasterized".
        band_name: name of the band to create. Defaults to "rasterized".
        feature_limit: maximum number of features to rasterize. Defaults to 25000.

    Examples:
        >>> # Rasterize the population attribute by summing the values in the attribute for each pixel
        >>> transform = rasterize(
        ... attribute_name="population",
        ... add=True,
        ... asset_name="population_raster",
        ... band_name="population"
        ... )

        >>> # Rasterize by object by setting the value to 1 wherever there is an object
        >>> transform = rasterize(
        ... value=1
        ... )

        >>> # Rasterize by object by setting the value to 1 wherever there is NOT an object
        >>> transform = rasterize(
        ... value=1,
        ... invert=True
        ... )

    """  # noqa: E501
    if (value is None and attribute_name is None) and (not use_z):
        raise ValueError("Must provide either a value or an attribute_name or use_z must be True.")

    inputs, _ = _collection_inputs(input_collection=input_collection)
    outputs = _asset_band_outputs(asset=asset_name, band=band_name)
    return Middleware(
        type=PIXELS_TRANSFORM_RASTERIZE,
        properties={
            "value": value,
            "initialize_value": initialize_value,
            "attribute_name": attribute_name,
            "invert": invert,
            "all_touched": all_touched,
            "use_z": use_z,
            "add": add,
            "feature_limit": feature_limit,
        },
        inputs=inputs,
        outputs=outputs,
    )


def inverse_distance_weighting(
    attribute_name: str,
    max_distance: float,
    asset_name: str = "idw",
    input_collection: str = None,
    no_data_value: float = 0,
    power: int = 2,
    max_points: int = 25,
    feature_limit: int = 1000,
) -> "Middleware":
    """Creates an interpolated image from a feature collection using inverse distance weighting.

    Inverse distance weighting is a method for interpolating values from a set of points to a raster. This
    method is useful for interpolating values like temperature, precipitation, or other continuous variables
    from a set of point measurements.

    If the features are not points (e.g. polygons), the centroid of the feature will be used as the point
    to interpolate from.

    Inverse distance weighting takes the k nearest points to a pixel and calculates the value at that pixel
    as the weighted average of the values of the k nearest points. The weight of each point is calculated
    as 1 / distance^power, where power is a parameter that controls the rate at which the weight decreases.


    The max distance (meters) parameter controls the maximum distance to interpolate to. If there are no points within
    this distance, the pixel will be set to the `no_data_value`.

    Increasing the feature limit will increase the number of features that are interpolated, but will also increase
    the time it takes to interpolate the image. There is a hard limit of 10,000 features that can be interpolated.

    Args:
        attribute_name: attribute name to interpolate. This is the field in the properties of each feature that will be interpolated.
        asset_name: name of the asset to create.
        max_distance: maximum distance to interpolate in meters.
        input_collection: collection to interpolate. Defaults to None (all/default collection).
        no_data_value: value to use for pixels with no data. Defaults to 0.
        power: power to use in the interpolation. Defaults to 2.
        max_points: maximum number of points to use in the interpolation. Defaults to 25.
        feature_limit: maximum number of features to interpolate. Defaults to 1000.

    Examples:
        >>> # Interpolate the temperature attribute using inverse distance weighting
        >>> transform = inverse_distance_weighting(
        ...     attribute_name="temperature",
        ...     asset_name="temperature_interpolated",
        ...     max_distance=100
        ... )
    """  # noqa: E501
    if power <= 0:
        raise ValueError("power must be greater than 0")

    if max_points <= 0:
        raise ValueError("max_points must be greater than 0")

    if feature_limit <= 0:
        raise ValueError("feature_limit must be greater than 0")

    if max_distance <= 0:
        raise ValueError("max_distance must be greater than 0")

    inputs, _ = _collection_inputs(input_collection=input_collection, output_collection=None)
    outputs = _asset_bands_outputs(asset=asset_name, bands=[attribute_name])

    return Middleware(
        type=PIXELS_TRANSFORM_INVERSE_DISTANCE_WEIGHTING,
        properties={
            "power": power,
            "max_points": max_points,
            "feature_limit": feature_limit,
            "attribute_name": attribute_name,
            "max_distance": max_distance,
            "no_data_value": no_data_value,
        },
        inputs=inputs,
        outputs=outputs,
    )


def band_arithmetic(
    expression: str, asset_name: str, band_name: str = "calculated"
) -> "Middleware":
    """Creates a new asset by applying a band arithmetic expression to an existing asset.

    Asset bands are represented using the following syntax:

    - `{"band_name": band_index}`: asset band from band index
    - `{"asset_name": "band_name"}`: asset band from band name

    Addition, subtraction, multiplication, division, and functions are supported. See
    below for the full list of functions.


    Args:
        expression: band arithmetic expression to apply
        asset_name: name of the asset to create
        band_name: name of the band to create. Defaults to "calculated"

    Returns:
        Middleware: middleware to apply band arithmetic to an asset

    Examples:
        >>> # Create a new asset by adding the "red" and "nir" bands together
        >>> transform = band_arithmetic(
        ...     expression='{"red": 0} + {"nir": 0}',
        ...     asset_name="red_nir_sum"
        ... )

        >>> # Create a new asset by adding 10 to the "red" band
        >>> transform = band_arithmetic(
        ...     expression='{"image": "red"} + 10',
        ...     asset_name="red_plus_10"
        ... )

        >>> # Create a new asset with a log scale of the "VV" band "10 * log10({"image": "VV"})"
        >>> transform = band_arithmetic(
        ...     expression='10 * log10({"image": "VV"})',
                asset_name="log_scale"
        ... )

    Functions:

        * exp(x) - e^x
        * sqrt(x) - square root of x
        * log(x, b) - log of x with base b, if no base is provided the default is e
        * log10(x) - log base 10 of x
        * abs(x) - absolute value of x
        * sin(x) - sine of x
        * cos(x) - cosine of x
        * tan(x) - tangent of x
        * floor(x) - rounds x down to nearest integer
        * ceil(x) - rounds x up to nearest integer
        * round(x) - rounds x up or down to nearest integer
        * pow(x, y) - x to the power of y
        * min(x, y, z) - smallest value of x, y, z - takes 2 or more arguments
        * max(x, y, z) - largest value of x, y, z - takes 2 or more arguments
        * clamp(x, min, max) - returns x unless x is greater than max or less than min
    """
    # some validation on the expression to catch common mistakes

    expression = expression.replace("'", '"')

    if expression.count("(") != expression.count(")"):
        raise ValueError("Expression must have an equal number of opening and closing parentheses")

    if expression.count("{") != expression.count("}"):
        raise ValueError("Expression must have an equal number of opening and closing curly braces")

    if expression.count('"') % 2 != 0:
        raise ValueError("Expression must have an even number of double quotes")

    inputs = []
    outputs = _asset_band_outputs(asset_name, band_name)

    return Middleware(
        type=PIXELS_TRANSFORM_BAND_ARITHMETIC,
        properties={
            "expression": expression,
        },
        inputs=inputs,
        outputs=outputs,
    )


def normalized_difference(
    asset_band_1: AssetBands,
    asset_band_2: AssetBands,
    asset_name: str,
    band_name: str = "calculated",
) -> "Middleware":
    """Creates a new asset by calculating the normalized difference between two bands.

    The normalized difference is calculated as (band_1 - band_2) / (band_1 + band_2).

    A common index, NDVI, is calculated by: `(NIR - Red) / (NIR + Red)`

    Args:
        asset_band_1: asset band for the first band
        asset_band_2: asset band for the second band
        asset_name: name of the asset to create
        band_name: name of the band to create. Defaults to "calculated"

    Returns:
        Middleware: middleware to calculate the normalized difference between two bands

    Examples:
        >>> # Calculate NDVI using band names
        >>> transform = normalized_difference(
        ...     asset_band_1=AssetBands(asset="image", bands=["nir"]),
        ...     asset_band_2=AssetBands(asset="image", bands=["red"]),
        ...     asset_name="ndvi"
        ... )

        >>> # Calculate NDVI using band IDs
        >>> transform = normalized_difference(
        ...     asset_band_1=AssetBands(asset="nir", bands=[0]),
        ...     asset_band_2=AssetBands(asset="red", bands=[0]),
        ...     asset_name="ndvi"
        ... )
    """
    if isinstance(asset_band_1, dict):
        asset_band_1 = AssetBands(**asset_band_1)
    if isinstance(asset_band_2, dict):
        asset_band_2 = AssetBands(**asset_band_2)

    a1 = asset_band_1.asset
    if a1 is None:
        raise ValueError("Asset band 1 must have an asset")
    b1 = asset_band_1.bands
    if len(b1) != 1:
        raise ValueError("Asset band 1 must have exactly one band")
    b1 = b1[0]
    if isinstance(b1, str):
        b1 = f'"{b1}"'

    a2 = asset_band_2.asset
    if a2 is None:
        raise ValueError("Asset band 2 must have an asset")
    b2 = asset_band_2.bands
    if len(b2) != 1:
        raise ValueError("Asset band 2 must have exactly one band")
    b2 = b2[0]
    if isinstance(b2, str):
        b2 = f'"{b2}"'

    expression = f'({{"{a1}": {b1}}} - {{"{a2}": {b2}}}) / ({{"{a1}": {b1}}} + {{"{a2}": {b2}}})'

    return band_arithmetic(expression, asset_name, band_name=band_name)


def datetime_difference(
    datetime1: Union[List[Union[datetime.datetime, str]], Tuple[Union[datetime.datetime, str]]],
    datetime2: Union[List[Union[datetime.datetime, str]], Tuple[Union[datetime.datetime, str]]],
    asset: str,
    band: Union[int, str],
    asset_name: str,
    band_name: str = None,
) -> "Middleware":
    """Creates a new asset by calculating the difference between two datetime bands.

    The difference is calculated as (datetime1 - datetime2)

    Note: This middleware will override the datetime field in any request to the new asset.

    Args:
        datetime1: first datetime range
        datetime2: second datetime range
        asset: asset to apply the difference to
        band: band to apply the difference to
        asset_name: name of the asset to create
        band_name: name of the band to create. Defaults to "{band}_datetime_difference"

    Returns:
        Middleware: middleware to calculate the difference between two datetime bands

    Examples:
        >>> # Calculate the difference on the B8 (red) band between January 2021 and 2022
        >>> transform = datetime_difference(
        ...     datetime1=[datetime.datetime(2021, 1, 1), datetime.datetime(2021, 1, 31)],
        ...     datetime2=[datetime.datetime(2022, 1, 1), datetime.datetime(2022, 1, 31)],
        ...     asset="B8",
        ...     band=0,
        ...     asset_name="datetime_difference",
        ... )
    """
    if not datetime1 or not datetime2:
        raise ValueError("Must provide two datetime ranges")
    if len(datetime1) != 2 or len(datetime2) != 2:
        raise ValueError("Datetime ranges must have exactly two bounds")
    dt1 = [datetime_to_utc(parsedate(dt)).isoformat() for dt in datetime1]
    dt2 = [datetime_to_utc(parsedate(dt)).isoformat() for dt in datetime2]

    inputs = _asset_band_inputs(asset, band)

    if band_name is None:
        band_name = f"{band}_datetime_difference"
    outputs = _asset_band_outputs(asset_name, band_name)

    return Middleware(
        type=PIXELS_TRANSFORM_DATETIME_DIFFERENCE,
        properties={
            "datetime1": dt1,
            "datetime2": dt2,
        },
        inputs=inputs,
        outputs=outputs,
    )


class MiddlewareConfig(_APIObject):
    """Configures the Middleware for a Dataset.

    Middleware can be applied to a dataset to perform actions on the data before it is returned to the user, but
    without influencing the underlying data. This can be useful for things like filtering, transforming, or
    enhancing the data in some way. Middleware can be applied to the search and pixels handlers of a dataset.

    Middleware is broken into a few different pieces:

    - Search Filters: These are filters that are applied to the search results of a dataset. They can be used to
        filter the results of a search based on some criteria. These should ONLY be applied to providers that
        don't offer filtering themselves. When in doubt DON'T apply filters. Most providers have them implemented
        and this is generally not needed. If you've implemented a remote provider with a relatively small number
        of features, this can be useful since implementing filtering on the provider side can be difficult.
    - Search Transforms: These are transforms that are applied to the search results of a dataset. They can be used
        to rename fields, combine fields, or otherwise modify the results of a search. These can be applied either
        before or after search filters. In the former case, set `search_transforms_before` and in the latter case,
        set `search_transforms_after`.
    - Pixels Transforms: These are transforms that are applied to the pixels handler of a dataset. They can be used
        to apply colormaps, rescale pixel values, or otherwise modify the pixels data. Many of them can create new
        assets in the dataset while some may modifiy existing assets.

    All of these middleware types can be applied to a dataset by adding them to the `middleware` field of a
    `MiddlewareConfig` object. The order of these operations is important. The first item in `middleware`
    will be applied to the response first, and so on until the last item. Middleware that alters the request
    must be added after any middleware that alters the response. That is, the responses will be altered by the
    middleware in a first to last order, and requests will be modified in a last to first order. Filters must
    be applied AFTER any transforms that they depend on.

    """  # noqa: E501

    middleware = _ListDescr(
        item_type=(Middleware, dict),
        coerce_items=True,
        doc="Middleware to apply to a dataset. This can include search filters, search transforms, "
        "and pixels transforms.",
    )
    search_filters = _ListDescr(
        item_type=(Middleware, dict),
        coerce_items=True,
        deprecated=True,
        doc="(DEPRECATED) Which filter actions to perform applied to the result of a dataset.",
    )
    search_transforms_before = _ListDescr(
        item_type=(Middleware, dict),
        coerce_items=True,
        deprecated=True,
        doc="(DEPRECATED) transforms to be applied to each feature/item in a search response. "
        "This is applied BEFORE any filtering takes place",
    )
    search_transforms_after = _ListDescr(
        item_type=(Middleware, dict),
        coerce_items=True,
        deprecated=True,
        doc="(DEPRECATED) transforms to be applied to each feature/item in a search response. "
        "This is applied AFTER any filtering takes place",
    )
    pixels_transforms = _ListDescr(
        item_type=(Middleware, dict),
        coerce_items=True,
        deprecated=True,
        doc="(DEPRECATED) transforms the request/response of a pixels handler. Useful for "
        "things like applying colormaps or more complex transformations on the pixels data.",
    )


def _default_datetime_range_props(
    start: Union[datetime.datetime, str] = None,
    end: Union[datetime.datetime, str] = None,
    before_now: datetime.timedelta = None,
) -> dict:
    if all([start is None, end is None, before_now is None]):
        raise ValueError("Must provide at least a start, end, or before_now")

    datetime_specified = start is not None or end is not None
    before_now_specified = before_now is not None

    if datetime_specified and before_now_specified:
        raise ValueError("Cannot provide both a before_now and a start/end")

    if before_now_specified:
        return {"seconds_before_now": before_now.total_seconds()}

    start = datetime_to_utc(parsedate(start)).isoformat()
    end = datetime_to_utc(parsedate(end)).isoformat()

    return {"datetime": [start, end]}
