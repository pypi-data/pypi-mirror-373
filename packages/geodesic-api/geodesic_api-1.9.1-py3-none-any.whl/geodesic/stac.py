from __future__ import annotations
import os
import json
import pathlib
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime as pydt
from typing import TYPE_CHECKING, Any, List, Optional, Union

from dateutil.parser import ParserError, parse
from shapely.geometry import shape

try:
    from shapely.errors import GeometryTypeError
except ImportError:
    GeometryTypeError = ValueError

from geodesic.bases import _APIObject
from geodesic.client import get_requests_client, raise_on_error
from geodesic.descriptors import (
    _BBoxDescr,
    _BaseDescr,
    _DatetimeDescr,
    _DatetimeIntervalDescr,
    _DictDescr,
    _GeometryDescr,
    _ListDescr,
    _StringDescr,
    _TypeConstrainedDescr,
)
from geodesic.utils.exif import get_image_geometry
from geodesic.utils import DeferredImport, datetime_to_utc

arcgis = DeferredImport("arcgis")
pd = DeferredImport("pandas")
gpd = DeferredImport("geopandas")
shapefile = DeferredImport("shapefile")
fiona = DeferredImport("fiona")
datasets = DeferredImport("geodesic.boson.dataset")

if TYPE_CHECKING:
    try:
        import geopandas as gpd
    except ImportError:
        GeoDataFrame = object
    try:
        import pandas as pd
    except ImportError:
        DataFrame = object

    from geodesic.entanglement import Dataset


class Feature(_APIObject):
    """A Geospatial feature.

    Feature object, represented as an RFC7946 (https://datatracker.ietf.org/doc/html/rfc7946)
    GeoJSON Feature. Can be initialized using any compliant GeoJSON Feature.

    Args:
        skip_parse: If True, will not parse dict into a Feature object so no validation will
            be performed until an attribute is requested.
    """

    id = _StringDescr(coerce=True, doc="the string id for this item")
    datetime = _DatetimeDescr(nested="properties", doc="the timestamp of this item")
    start_datetime = _DatetimeDescr(nested="properties", doc="the start timestamp of this item")
    end_datetime = _DatetimeDescr(nested="properties", doc="the end timestamp of this item")
    bbox = _BBoxDescr(default=None)
    geometry = _GeometryDescr(bbox=bbox, default=None)
    properties = _DictDescr(default={})
    links = _ListDescr(dict, default=[])

    def __init__(self, skip_parse=False, **obj) -> None:
        """Initialize the Feature by setting it's attributes."""
        self._set_item("type", "Feature")
        if skip_parse:
            for key, value in obj.items():
                self._set_item(key, value)
            return
        self.update(obj)

    @property
    def type(self):
        """The type is always Feature.

        This fills in for improperly constructed GeoJSON that doesn't have the "type" field set.
        """
        return "Feature"

    @property
    def __geo_interface__(self) -> dict:
        """The Geo Interface convention (https://gist.github.com/sgillies/2217756)."""
        return dict(**self)

    def _repr_svg_(self) -> str:
        """Represent this feature as an SVG to be rendered in Jupyter or similar.

        This returns an SVG representation of the geometry of this Feature
        """
        try:
            return self.geometry._repr_svg_()
        except Exception:
            return None

    def __repr__(self) -> str:
        return f"Feature(id={self.get('id')})"

    def __str__(self) -> str:
        geom = self.geometry
        props = self.properties
        st = "Feature:\n"
        st += f"  ID: {self.get('id')}\n"
        if geom is not None:
            st += f"  Geometry: {geom.__repr__()}\n"
        st += "  Properties:\n"
        for k, v in props.items():
            st += f"    {k}: {v}\n"
        return st


class _FeatureListDescr(_BaseDescr):
    """ListDescr is a list of Feature items.

    this sets/returns a list no matter what, it doesn't raise an attribute error.

    __get__ returns the list, creating it on the base object if necessary
    __set__ sets the list after validating that it is a list
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._type = (list,)

    def _get(self, obj: object, objtype=None) -> list:
        # Try to get the private attribute by name (e.g. '_features')
        f = getattr(obj, self.private_name, None)
        if f is not None:
            # Return it if it exists
            return f

        try:
            value = self._get_object(obj)

            # If this was set by other means, make sure the data inside are features/items
            if len(value) > 0:
                if not isinstance(value[-1], Feature):
                    is_stac = False
                    if "assets" in value[0]:
                        is_stac = True
                    if is_stac:
                        self._set_object(obj, [Item(**f) for f in value])
                    else:
                        self._set_object(obj, [Feature(**f) for f in value])
        except KeyError:
            value = []
            self._set_object(obj, value)
        setattr(obj, self.private_name, value)
        return value

    def _set(self, obj: object, value: object) -> list:
        # Reset the private attribute
        setattr(obj, self.private_name, None)
        # return STAC items if a feature has an assets
        is_stac = False

        if len(value) > 0:
            f = value[0]
            if "assets" in f:
                is_stac = True

        if is_stac:
            self._set_object(obj, [Item(skip_parse=True, **f) for f in value])
        else:
            self._set_object(obj, [Feature(skip_parse=True, **f) for f in value])

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"'{self.public_name}' must be a tuple or list")
        if len(value) > 0:
            if not isinstance(value[0], dict):
                raise ValueError(f"each value must be a dict/Feature/Item, not '{type(value[0])}'")
            if "type" not in value[0]:
                raise ValueError("features are not valid GeoJSON Features")


class FeatureCollection(_APIObject):
    """A collection of Features that is represented by a GeoJSON FeatureCollection.

    in accordance with RFC7946 (https://datatracker.ietf.org/doc/html/rfc7946)

    Args:
        dataset: a `geodesic.boson.dataset` associated with the FeatureCollection.
        query: a query, if any, used to initialize this from a request to Spacetime or Boson
        **obj: the underyling JSON data of the FeatureCollection to specify
    """

    features = _FeatureListDescr(doc="this FeatureCollection's Feature/Item objects")
    links = _ListDescr(dict, doc="links associated with this collection")

    def __init__(self, dataset: "Dataset" = None, query: dict = None, **obj) -> None:
        # From GeoJSON
        if isinstance(obj, dict):
            self.update(obj)

        self._set_item("type", "FeatureCollection")

        # Cache the GeoDataframe, Dataframe, and OGR layer
        self._gdf = None
        self._sedf = None
        self._ogr = None
        self._features = None
        self._df = None

        # Query used to
        self.query = query
        self.dataset = dataset
        if self.dataset is not None:
            self._ds_type = self.dataset.data_api
            self._ds_subtype = self.dataset.item_type

    @property
    def type(self):
        """The type is always FeatureCollection.

        This fills in for improperly constructed GeoJSON that doesn't have the "type" field set.
        """
        return "FeatureCollection"

    @property
    def gdf(self) -> GeoDataFrame:
        """Return a geopandas.GeoDataFrame representation of this FeatureCollection.

        Returns:
            a Geopandas GeoDataFrame of this object
        """
        if self._gdf is not None:
            return self._gdf

        df = pd.DataFrame([f.properties for f in self.features])

        geo = [f.geometry for f in self.features]
        self._gdf = gpd.GeoDataFrame(df, geometry=geo, crs="EPSG:4326")
        return self._gdf

    @property
    def df(self) -> DataFrame:
        """Return a Pandas DataFrame representation of this FeatureCollection.

        Returns:
            a Pandas DataFrame of this object
        """
        if self._df is not None:
            return self._df

        self._df = pd.DataFrame([f.properties for f in self.features])
        return self._df

    @property
    def sedf(self) -> DataFrame:
        """Get a spatially enabled Pandas DataFrame.

        Return an ArcGIS API for Python representation of this feature collection as a spatially
        enabled Pandas DataFrame

        Returns:
            a Pandas DataFrame of this object with a arcgis.features.GeoAccessor attached.
        """
        if self._sedf is not None:
            return self._sedf

        # Patch a bug in arcgis==2.0.0
        try:
            arcgis.geometry.Geometry.from_shapely(shape({"type": "Point", "coordinates": [0, 0]}))
        except NameError:
            arcgis.geometry._types._HASSHAPELY = True

        df = pd.DataFrame([f.properties for f in self.features])
        geo = [arcgis.geometry.Geometry.from_shapely(f.geometry) for f in self.features]
        df.spatial.set_geometry(geo)
        self._sedf = df
        return self._sedf

    @property
    def __geo_interface__(self) -> dict:
        """Return this as a GeoJSON dictionary.

        Returns:
            a dictionary of this object representing GeoJSON
        """
        return dict(self)

    @property
    def _next_link(self):
        """Get the link with relation "next" if any.

        Returns:
            the link if it exists, None otherwise
        """
        for link in self.links:
            if link.get("rel", None) == "next":
                return link

    @property
    def _next_page(self) -> Union[None, dict]:
        link = self._next_link
        if link is None:
            return
        href = link.get("href")
        if href is None:
            return

        href = unquote(href)

        method = link.get("method", "GET")

        if method.lower() == "get":
            return raise_on_error(get_requests_client().get(href)).json()
        else:
            body = link.get("body", {})
            if link.get("merge", False):
                body.update(self.query)

            return raise_on_error(get_requests_client().post(href, json=body)).json()

    def next_page(self) -> "FeatureCollection":
        fc = self._next_page
        if fc is None:
            return FeatureCollection()
        return FeatureCollection(**fc)

    def get_all(self) -> None:
        # Reset derived properties
        self._gdf = None
        self._sedf = None
        self._ogr = None

        res = SearchResponse(self.query, self)
        res = res.page_through_results()

        # Set features
        self.features = res.features

    @staticmethod
    def from_geojson_file(path: Union[str, os.PathLike]) -> "FeatureCollection":
        """Loads a geojson file and returns a new FeatureCollection.

        Args:
            path: path to the file to load
        """
        path = str(pathlib.Path(path).absolute())

        with open(path, "r") as fp:
            fc = json.load(fp)
            return FeatureCollection(**fc)

    @staticmethod
    def from_shapefile(path: Union[str, os.PathLike]) -> "FeatureCollection":
        """Loads a shapefile and returns a new FeatureCollection.

        This method uses pyshp

        Args:
            path: path to the file root/prefix to load
        """
        path = str(pathlib.Path(path).absolute())

        sf = shapefile.Reader(path)
        return FeatureCollection(**sf.__geo_interface__)

    @staticmethod
    def from_file_geodatabase(
        path: Union[str, os.PathLike], layer: str, **kwargs
    ) -> "FeatureCollection":
        """Loads a layer from a file geodatabase and returns a new FeatureCollection.

        Args:
            path: path to the file geodatabase
            layer: the name of the layer to load
            **kwargs: additional keywords to pass to fiona.open
        """
        return FeatureCollection.from_file(path, layer=layer, enabled_drivers=["OpenFileGDB"])

    @staticmethod
    def from_gpx(path: Union[str, os.PathLike], layer: str, **kwargs) -> "FeatureCollection":
        """Loads a GPX file and returns a new FeatureCollection.

        Args:
            path: path to the GPX file
            layer: which layer to read. One of waypoints, routes, tracks, route_points, or
                track_points, depending on the file
            **kwargs: additional keywords to pass to fiona.open
        """
        valid_gpx_layers = [
            "waypoints",
            "routes",
            "tracks",
            "route_points",
            "track_points",
        ]

        if layer not in valid_gpx_layers:
            raise ValueError(f"'{layer}' not valid, must be one of {', '.join(valid_gpx_layers)}")

        return FeatureCollection.from_file(path, layer=layer, enabled_drivers=["GPX"], **kwargs)

    @staticmethod
    def from_file(
        path: Union[str, os.PathLike], layer: str = None, **kwargs
    ) -> "FeatureCollection":
        """Loads geospatial data using fiona and returns a new FeatureCollection.

        For more details about what can be read with fiona, see the following docs:
        https://fiona.readthedocs.io/en/latest/

        Args:
            path: path to the file
            layer: the name of the layer to load
            **kwargs: additional keywords to pass to fiona.open
        """
        path = str(pathlib.Path(path).absolute())

        fc = FeatureCollection()
        with fiona.open(path, "r", layer=layer, **kwargs) as collection:
            for f in collection:
                try:
                    f = f.__geo_interface__
                except AttributeError:
                    pass
                fc.features.append(Feature(**f))

        return fc

    def __repr__(self) -> str:
        feats = self.features
        ellipsis = False
        if len(feats) > 5:
            feats = feats[:5]
            ellipsis = True

        feats_st = "[" + (", ".join(f.__repr__() for f in feats))
        if ellipsis:
            feats_st += ", ..."
        feats_st += "]"
        return f"FeatureCollection({feats_st})"

    def __str__(self) -> str:
        st = "Feature Collection:\n"
        st += f"  Feature Count: {len(self.features)}\n"
        return st


class Spatial(_APIObject):
    """The Spatial key in a STAC Item."""

    bbox = _ListDescr(item_type=_BBoxDescr, doc="the bounding box of this item")

    def __init__(self, **obj) -> None:
        super().__init__(**obj)


class Temporal(_APIObject):
    """The Temporal key in a STAC Item."""

    interval = _ListDescr(item_type=_DatetimeIntervalDescr, doc="the interval of this item")

    def __init__(self, **obj) -> None:
        super().__init__(**obj)


class Extent(_APIObject):
    """The Extent key in a STAC Item.

    Args:
        **obj: the attributes of this Extent
    """

    spatial = _TypeConstrainedDescr(
        (Spatial, dict), coerce=True, doc="the spatial extent of this item"
    )
    temporal = _TypeConstrainedDescr(
        (Temporal, dict), coerce=True, doc="the temporal extent of this item"
    )

    def __init__(self, **obj) -> None:
        super().__init__(**obj)


class Asset(_APIObject):
    """A STAC Asset object. Basically contains links and metadata for a STAC Asset.

    Args:
        **obj: the attributes of this Asset
    """

    href = _StringDescr()
    title = _StringDescr()
    description = _StringDescr()
    type = _StringDescr()
    roles = _ListDescr(str)

    def __init__(self, **obj) -> None:
        super().__init__(**obj)
        self._local = None

    def has_role(self, role: str) -> bool:
        """Does this have a requested role?

        Returns:
            True if yes, False if no
        """
        for r in self.roles:
            if role == r:
                return True
        return False

    @property
    def local(self) -> str:
        """Get the local path to this asset, if any.

        Returns:
            a local path to this asset if downloaded, '' otherwise
        """
        if self._local is not None:
            return self._local

        self._local = self.get("local", "")
        return self._local

    @local.setter
    def local(self, local: str) -> None:
        """Set the local path to this asset after downloading.

        Args:
            local: the local path
        """
        self._local = local
        self._set_item("local", local)

    @local.deleter
    def local(self) -> None:
        """Delete the local attribute and the underlying file in the file system."""
        path = self.pop("local")
        self._local = None
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def new() -> "Asset":
        """Returns a new asset with all the fields empty."""
        return Asset(
            **{
                "href": "",
                "title": "",
                "type": "",
                "description": "",
                "roles": [],
            }
        )

    def __repr__(self) -> str:
        return f"Asset(href={self.get('href')})"

    def __str__(self) -> str:
        st = "Asset:\n"
        st += f"  HRef: {self.get('href')}\n"
        st += f"  Title: {self.get('title')}\n"
        st += f"  Description: {self.get('description')}\n"
        st += f"  Type: {self.get('type')}\n"
        st += f"  Roles: {self.get('roles')}\n"
        return st


class _AssetsDescr(_BaseDescr):
    """A dictionary of Asset objects.

    __get__ returns the dictionary, ensuring they are indeed Assets, not plain dicts
    __set__ sets the Assets, coercing to Assets if they are dicts

    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._type = (dict, Asset)

    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_assets')
        assets = getattr(obj, self.private_name, None)
        if assets is not None:
            # Return it if it exists
            return assets

        try:
            assets = self._get_object(obj)
            setattr(obj, self.private_name, assets)
        except KeyError:
            assets = {}
            self._set_object(obj, assets)
        return assets

    def _set(self, obj: object, value: object) -> None:
        self._set_object(obj, {asset_name: Asset(**asset) for asset_name, asset in value.items()})

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, dict):
            raise ValueError(f"'{self.public_name}' must be a dict of dicts/Assets")

        for asset_name, asset in value.items():
            if not isinstance(asset_name, str):
                raise ValueError("asset name must be a string")
            if not isinstance(asset, dict):
                raise ValueError("asset must be a dict/Asset")


class Item(Feature):
    """Class representing a STAC item.

    Implements additional STAC properties on top of a :class:`geodesic.stac.feature`

    Args:
        obj: A python object representing a STAC item.
        dataset: The dataset object this Item belongs to.

    """

    assets = _AssetsDescr(doc="the assets for this item")
    collection = _StringDescr(doc="what collection this item belongs to")
    stac_extensions = _ListDescr(str)

    def __init__(self, **obj) -> None:
        super().__init__(**obj)
        self.item_type = "unknown"
        dataset = obj.pop("dataset", None)

        if dataset is not None:
            dataset = datasets.Dataset(**dataset)
            self.item_type = dataset.item_type
            self.dataset = dataset

    def _repr_html_(self) -> str:
        """Represent this Item as HTML.

        Returns:
            a str of the HTML representation
        """
        if "thumbnail" in self.assets:
            href = self.assets["thumbnail"]["href"]
            width = 500
            if href == "https://seerai.space/images/Logo.svg":
                width = 100

            return f'<img src="{href}" style="width: {width}px;"></img>'
        else:
            try:
                svg = self._repr_svg_()
                if svg is None:
                    raise Exception()
            except Exception:
                href = "https://seerai.space/images/Logo.svg"
                width = 100
                return f'<img src="{href}" style="width: {width}px;"></img>'

    @staticmethod
    def new(dataset: "Dataset" = None) -> "Item":
        """Create a new Item with blank fields."""
        return Item(
            **{
                "type": "Feature",
                "id": "",
                "collection": "",
                "stac_extensions": [],
                "properties": {},
                "assets": {},
                "links": [],
            },
            dataset=dataset,
        )

    @staticmethod
    def from_image(path: str, **item):
        """Creates a new Item using the EXIF header to locate the image.

        This is useful when an asset is derived from a photolog of similar

        Args:
            path: a path to the file
            **item: any additional parameters to pass to the Item constructor
        """
        try:
            g = get_image_geometry(path)
        except Exception as e:
            raise ValueError("unable to extract geometry from image") from e

        # create a new asset
        i = Item(**item)

        # Set some basic parameters
        i.geometry = g
        i.id = item.pop("id", path)

        # Create the asset for this image
        img = Asset.new()
        img.href = path
        img.title = path
        img.description = "local image"

        # And a thumbnail asset
        thumb = Asset.new()
        thumb.href = path
        thumb.title = path
        thumb.description = "thumbnail"
        thumb.roles = ["thumbnail"]

        # Set the Assets
        i.assets["image"] = img
        i.assets["thumbnail"] = thumb

        return i

    def __repr__(self) -> str:
        return f"Item(id={self.get('id')})"

    def __str__(self) -> str:
        geom = self.geometry
        st = "Item:\n"
        st += f"  ID: {self.get('id')}\n"
        if geom is not None:
            st += f"  Geometry: {geom.__repr__()}\n"
        st += "  Properties:\n"
        for k, v in self.properties.items():
            st += f"    {k}: {v}\n"
        st += "  Assets:"
        if len(self.assets) == 0:
            st += " {}\n"
        else:
            st += "\n"
        for k, a in self.assets.items():
            st += f"  Asset: {k}\n"
            st += f"    {a.__str__()}\n"

        return st


def _parse_date(dt, index=0):
    if isinstance(dt, str):
        try:
            return datetime_to_utc(parse(dt)).isoformat()
        except ParserError as e:
            if dt == ".." or dt == "":
                if index == 0:
                    return "0001-01-01T00:00:00+00:00"
                else:
                    return "9999-01-01T00:00:00+00:00"
            else:
                raise e
    elif isinstance(dt, pydt):
        return datetime_to_utc(dt).isoformat()
    else:
        raise ValueError("could not parse datetime. unknown type.")


class Collection(_APIObject):
    """represents a STAC or OGC Collection object.

    Basic metadata about a collection of features/items.
    """

    id = _StringDescr(doc="this Collection's string id")
    title = _StringDescr(doc="human readable/display title for this Collection")
    description = _StringDescr(doc="description of this Collection")
    keywords = _ListDescr(item_type=str, doc="a list of keywords for this Collection")
    license = _StringDescr(doc="the license associated with this data")
    extent = _TypeConstrainedDescr(
        (Extent, dict), doc="the spatiotemporal extent of this Collection"
    )
    links = _ListDescr(dict, doc="list of link objects related to this Collection")
    version = _StringDescr(doc="the STAC version for this Collection")
    extensions = _ListDescr(
        item_type=str, doc="list of STAC extensions supported by this Collection"
    )
    providers = _ListDescr(
        item_type=dict, doc="a list of data provider objects for this Collection"
    )
    summaries = _DictDescr(doc="STAC summaries for this Collection")
    assets = _DictDescr(doc="dictionary of item assets for this Collection")


class SearchResponse:
    """a polymorphic response from an API returning a GeoJSON feature collection with next links.

    Args:
        query: the query used to generate this response
        response: the response from the API
    """

    def __init__(self, query: dict, response: dict) -> None:
        self.query = query
        self.response = response
        self.features = response.get("features", [])
        self.links = response.get("links", [])
        if self.links is None:
            self.links = []

    @property
    def __geo_interface__(self) -> dict:
        """Return this as a GeoJSON dictionary.

        Returns:
            a dictionary of this object representing GeoJSON
        """
        return dict(self.feature_collection())

    def feature_collection(self) -> FeatureCollection:
        """Return this as a FeatureCollection.

        Returns:
            a FeatureCollection of this object
        """
        return FeatureCollection(query=self.query, **self.response)

    def geodataframe(self) -> GeoDataFrame:
        """Return this as a GeoDataFrame.

        Returns:
            a GeoDataFrame of this object
        """
        geoms = [f.get("geometry") for f in self.features]
        geoms = [shape(g) if g is not None else None for g in geoms]
        ids = [f.get("id") for f in self.features]
        df = pd.DataFrame([f.get("properties", {}) for f in self.features])
        gdf = gpd.GeoDataFrame(df, geometry=geoms, crs="EPSG:4326")
        gdf.loc[:, "id"] = ids
        return gdf

    @property
    def _next_link(self):
        """Get the link with relation "next" if any.

        Returns:
            the link if it exists, None otherwise
        """
        for link in self.links:
            if link.get("rel", None) == "next":
                return link

    @property
    def _next_page(self) -> Union[None, dict]:
        link = self._next_link
        if link is None:
            return
        href = link.get("href")
        if href is None:
            return

        href = unquote(href)

        method = link.get("method", "GET")

        if method.lower() == "get":
            return raise_on_error(get_requests_client().get(href)).json()
        else:
            body = link.get("body", {})
            if link.get("merge", False):
                body.update(self.query)

            return raise_on_error(get_requests_client().post(href, json=body)).json()

    def page_through_results(self, limit: int = None) -> SearchResponse:
        """Pages through results in a feature collection.

        Pages using the next page links until the limit is reached.

        Args:
            limit: the number of results to return. If `limit` is None, returns all features
        """
        next_page = self._next_page

        features = self.features

        while next_page is not None and (limit is None or len(features) < limit):
            tmp_features = next_page.get("features", [])
            if tmp_features is None or len(tmp_features) == 0:
                self.features = features
                return self

            if limit and (len(features) + len(tmp_features)) > limit:
                cnt = limit - len(features)
            else:
                cnt = len(tmp_features)

            features += tmp_features[:cnt]
            self.links = next_page.get("links", [])
            if self.links is None:
                self.links = []
            next_page = self._next_page

        self.features = features
        return self


class STACAPI:
    def __init__(self, root: str):
        self.root = root
        if root.endswith("/"):
            self.root = self.root[:-1]

    def collections(self) -> dict:
        req_url = f"{self.root}/collections"

        c = get_requests_client()

        res = raise_on_error(c.get(req_url))
        return {"collections": [Collection(**c) for c in res.json().get("collections", [])]}

    def collection(self, collection_id: str) -> Collection:
        req_url = f"{self.root}/collections/{collection_id}"

        c = get_requests_client()

        res = raise_on_error(c.get(req_url))
        return Collection(**res.json())

    def search(
        self,
        bbox: Optional[list] = None,
        datetime: Union[list, tuple] = None,
        limit: Union[None, int] = 10,
        intersects: Any = None,
        collections: List[str] = None,
        ids: List[str] = None,
        query: dict = None,
        filter: dict = None,
        fields: dict = None,
        sortby: dict = None,
        method: str = "POST",
        extra_params: dict = {},
    ) -> SearchResponse:
        """Query the search endpoint for items.

        Query this service's OGC Features or STAC API.

        Args:
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            datetime: The temporal extent for the query formatted as a list: [start, end].
            limit: The maximum number of items to return in the query.
            intersects: a geometry to filter results by geospatial intersection
            collections: a list of collections to query
            ids: a list of item/feature IDs to return
            query: a STAC query in the format of the STAC query extension
            filter: a CQL2 JSON filter
            fields: a list of fields to include/exclude. Included fields should be prefixed by '+'
                and excluded fields by '-'. Alernatively, a dict with a 'include'/'exclude' lists
                may be provided
            sortby: a list of sortby objects, with are dicts containing 'field' and 'direction'
            method: GET or POST (default)
            extra_params: dictionary of extra parameters to pass to the STAC search API

        Returns:
            A :class:`geodesic.stac.SearchResponse` with all items in the dataset
                matching the query.

        Examples:
            A query on the `sentinel-2-l2a` dataset with a given bounding box and time range.
                Additionally, you can apply filters on the parameters in the items.

            >>> bbox = geom.bounds
            >>> date_range = (datetime.datetime(2020, 12,1), datetime.datetime.now())
            >>> api.search(
            ...          bbox=bbox,
            ...          collections=['sentinel-2-l2a'],
            ...          datetime=date_range,
            ...          query={'properties.eo:cloud_cover': {'lte': 10}}
            ... )
        """
        if method.lower() not in ["post", "get"]:
            raise ValueError("request method must be 'GET' or 'POST'")

        req_url = f"{self.root}/search"

        # STAC client for Spacetime or external STAC apis.
        client = get_requests_client()

        params = _search_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            intersects=intersects,
            collections=collections,
            ids=ids,
            query=query,
            filter=filter,
            fields=fields,
            sortby=sortby,
            method=method,
            extra_params=extra_params,
        )

        if method.lower() == "post":
            res = raise_on_error(client.post(req_url, json=params))
        else:
            res = raise_on_error(client.get(req_url, params=params))

        return SearchResponse(query=params, response=res.json())

    def count(
        self,
        bbox: Optional[list] = None,
        datetime: Union[list, tuple] = None,
        intersects: Any = None,
        collections: List[str] = None,
        ids: List[str] = None,
        filter: dict = None,
        method: str = "POST",
        extra_params: dict = {},
    ) -> SearchResponse:
        """Count the number of matching items in the dataset.

        Args:
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            datetime: The temporal extent for the query formatted as a list: [start, end].
            intersects: a geometry to filter results by geospatial intersection
            collections: a list of collections to query
            ids: a list of item/feature IDs to return
            filter: a CQL2 JSON filter
            method: GET or POST (default)
            extra_params: dictionary of extra parameters to pass to the STAC search API

        Returns:
            A int of the total count of items in the dataset matching the query.

        Examples:
            A query on the `sentinel-2-l2a` dataset with a given bounding box and time range.
                Additionally, you can apply filters on the parameters in the items.

            >>> bbox = geom.bounds
            >>> date_range = (datetime.datetime(2020, 12,1), datetime.datetime.now())
            >>> api.count(
            ...          bbox=bbox,
            ...          collections=['sentinel-2-l2a'],
            ...          datetime=date_range
            ... )
        """
        if method.lower() not in ["post", "get"]:
            raise ValueError("request method must be 'GET' or 'POST'")

        req_url = f"{self.root}/count"

        # STAC client for Spacetime or external STAC apis.
        client = get_requests_client()

        params = _search_params(
            bbox=bbox,
            datetime=datetime,
            intersects=intersects,
            collections=collections,
            ids=ids,
            filter=filter,
            method=method,
            limit=None,
            extra_params=extra_params,
        )

        if method.lower() == "post":
            res = raise_on_error(client.post(req_url, json=params))
        else:
            res = raise_on_error(client.get(req_url, params=params))

        return res.json().get("count", 0)

    def collection_items(
        self,
        collection_id: str,
        bbox: Optional[list] = None,
        datetime: Union[list, tuple] = None,
        limit: Union[None, int] = 10,
        extra_params: dict = {},
    ) -> FeatureCollection:
        """Query the collections/<collection_id>/items endpoint for items.

        Query this service's OGC Features or STAC API.

        Args:
            collection_id: the collection to query
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            datetime: The temporal extent for the query formatted as a list: [start, end].
            limit: The maximum number of items to return in the query.
            extra_params: extra query parameters to pass to the api
        """
        req_url = f"{self.root}/collections/{collection_id}/items"

        # STAC client for Spacetime or external STAC apis.
        client = get_requests_client()

        # Request query/body
        params = {"limit": limit}

        # Parse geospatial aspect of this query (bbox and intersects)
        params = _query_parse_geometry(params, "features", bbox, None, method="GET")

        if datetime is not None:
            if isinstance(datetime, (str, pydt)):
                params["datetime"] = _parse_date(datetime)
            else:
                params["datetime"] = "/".join(
                    [_parse_date(d, index=i) for i, d in enumerate(datetime)]
                )

        params.update(extra_params)
        res = raise_on_error(client.get(req_url, params=params))

        return SearchResponse(query=params, response=res.json())

    def collection_item(
        self, collection_id: str, feature_id: str, extra_params: dict = {}
    ) -> Feature:
        """Get a specific feature from collections/<collection_id>/items/feature_id endpoint.

        Get a specific feature

        Args:
            collection_id: the collection to get the item from
            feature_id: The id of the feature
            extra_params: extra query parameters to pass
        """
        req_url = f"{self.root}/collections/{collection_id}/items/{feature_id}"

        # STAC client for Spacetime or external STAC apis.
        client = get_requests_client()

        res = raise_on_error(client.get(req_url, params=extra_params))

        # Wrap the results in a FeatureCollection
        feature = Feature(**res.json())

        return feature


def _search_params(
    bbox: Optional[list] = None,
    datetime: Union[list, tuple] = None,
    limit: Union[None, int] = 10,
    intersects: Any = None,
    collections: List[str] = None,
    ids: List[str] = None,
    query: dict = None,
    filter: dict = None,
    fields: dict = None,
    sortby: dict = None,
    method: str = "POST",
    extra_params: dict = {},
):
    body = {}
    if limit is not None:
        # Request query/body
        body = {"limit": limit}

    if collections is not None:
        if not isinstance(collections, list):
            raise TypeError("collections must be a list of strings")
        body["collections"] = collections

    # Parse geospatial aspect of this query (bbox and intersects)
    body = _query_parse_geometry(body, "stac", bbox, intersects, method=method)

    # Parse STAC search specific query/filtering
    params = _query_parse_stac_query(
        params=body,
        ids=ids,
        filter=filter,
        query=query,
        fields=fields,
        sortby=sortby,
        method=method,
    )

    if datetime is not None:
        if isinstance(datetime, (str, pydt)):
            params["datetime"] = _parse_date(datetime)
        else:
            params["datetime"] = "/".join([_parse_date(d, index=i) for i, d in enumerate(datetime)])

    params.update(extra_params)
    return params


def _query_parse_geometry(
    params: dict,
    api: str,
    bbox: Optional[list],
    intersects: object,
    method: str = "POST",
) -> dict:
    # If the bounding box only provided.
    if bbox is not None and intersects is None:
        if len(bbox) != 4 and len(bbox) != 6:
            raise ValueError("bbox must be length 4 or 6")
        if method == "POST":
            params["bbox"] = bbox
        else:
            params["bbox"] = ",".join([str(x) for x in bbox])
        return params

    # If a intersection geometry was provided
    if intersects is not None:
        # Geojson geometry OR feature
        if isinstance(intersects, dict):
            try:
                g = shape(intersects)
            except (ValueError, AttributeError, GeometryTypeError):
                try:
                    g = shape(intersects["geometry"])
                except Exception as e:
                    raise ValueError("could not determine type of intersection geometry") from e

        elif hasattr(intersects, "__geo_interface__"):
            g = intersects

        else:
            raise ValueError(
                "intersection geometry must be either geojson or object with __geo_interface__"
            )

        # If STAC, use the geojson
        if api == "stac":
            params["intersects"] = g.__geo_interface__
        # Bounding box is all that's supported for OAFeat
        else:
            try:
                # Shapely
                params["bbox"] = ",".join([str(x) for x in g.bounds])
            except AttributeError:
                # ArcGIS
                params["bbox"] = ",".join([str(x) for x in g.extent])
    return params


def _query_parse_stac_query(
    params: dict,
    ids: list = None,
    filter: dict = None,
    query: dict = None,
    fields: dict = None,
    sortby: dict = None,
    method: str = "POST",
) -> dict:
    # Individual item ids to get
    if ids is not None:
        if not isinstance(ids, (list, tuple)):
            raise TypeError("ids must be a list or tuple of strings")
        params["ids"] = ids

    # Parse the original STAC Query object, this will go away soon now that
    # The core STAC spec adopted CQL. This is still supported by many STAC APIs
    # in the wild, including the ubiquitous sat-api.
    if query is not None:
        params["query"] = query

    if filter is not None:
        params["filter"] = filter

    # Sortby object, see STAC sort spec
    if sortby is not None:
        params["sortby"] = sortby

    # Fields to include/exclude.
    if fields is not None:
        fieldsObj = defaultdict(list)
        # fields with +/-
        if isinstance(fields, list):
            for field in fields:
                if field.startswith("+"):
                    fieldsObj["include"].append(field[1:])
                elif field.startswith("-"):
                    fieldsObj["exclude"].append(field[1:])
                else:
                    fieldsObj["include"].append(field)
        else:
            fieldsObj = fields
        params["fields"] = fieldsObj

    return params
