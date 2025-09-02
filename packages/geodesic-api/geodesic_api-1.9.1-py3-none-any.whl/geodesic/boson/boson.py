import datetime
import re
from typing import Union, List

from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _StringDescr,
    _BoolDescr,
    _ListDescr,
    _DictDescr,
    _IntDescr,
    _BaseDescr,
    _FloatDescr,
    _TypeConstrainedDescr,
)
from geodesic.account import Project
from geodesic.service import RequestsServiceClient
from geodesic.boson.middleware import MiddlewareConfig, Middleware
from geodesic.boson.tile_options import TileOptions
from geodesic.boson.servicer_settings import ServicerSettings, TimeEnable, time_units

# Credential Keys
DEFAULT_CREDENTIAL_KEY = "default"
STORAGE_CREDENTIAL_KEY = "storage"
API_CREDENTIAL_KEY = "api"

boson_client = RequestsServiceClient("boson", api="datasets", version=1)
vertex_bsn_client = RequestsServiceClient("vertex", api="bsn", version=1)
iri_re = re.compile(r"^bsn://dataset\/(?P<project>\w+)\/(?P<hash>\w+)$")


class CacheConfig(_APIObject):
    """Cache Configuration.

    This tells Boson how it should cache data from the provider.

    There are two main options that can be controled here:

    `enabled`: whether or not to cache data in the persistent cache. This is typically configured
        to be cloud storage like S3 or GCS. Whether enabled is True or not, Boson will perform some
        level of internal caching, but the cache will not be backed by a persistent store unless
        this is set to True.
    `ttl`: time to live for cached items in seconds. For quickly changing data, this should be set
        to a low value. This defaults to 5 minutes if not set. If this value is greater than the
        default TTL of the internal cache (5 minutes), this TTL will only correspond to the
        persistent cache. If the value is less than the internal cache, the internal cache will use
        a TTL less than or equal to this value. If `enabled` is False and this value is set to a
        value greater than 5 minutes, Boson will cap the TTL at 5 minutes.

    Args:
        enabled (bool): enable/disable persistent caching for a particular provider.
        ttl (Union[datetime.timedelta, int, float]): time to live for cached items in seconds. For
            quickly changing data, this should be set to a low value. Default is 5 minutes
            if not set.

    """

    enabled = _BoolDescr(doc="enable/disable caching for a particular provider")
    ttl_seconds = _FloatDescr(doc="time to live for cached items in seconds")

    def __init__(
        self,
        enabled: bool = False,
        ttl: Union[datetime.timedelta, int, float] = None,
        **kwargs,
    ):
        ttl_seconds = None
        if isinstance(ttl, datetime.timedelta):
            ttl_seconds = int(ttl.total_seconds())
        elif isinstance(ttl, (int, float)):
            ttl_seconds = float(ttl)

        if ttl_seconds is not None:
            kwargs["ttl_seconds"] = ttl_seconds
        super().__init__(enabled=enabled, **kwargs)


class BosonConfig(_APIObject):
    """BosonConfig Provider Configuration.

    This tells Boson how it should access the underlying data.
    """

    provider_name = _StringDescr(doc="the name of the provider this Boson uses")
    url = _StringDescr(doc="the url of the service this refers to (if any)")
    thread_safe = _BoolDescr(doc="is this particular provider implementation thread safe")
    pass_headers = _ListDescr(doc="list of headers that this provider should pass to backend")
    max_page_size = _IntDescr(doc="the max number of records this provider can page through")
    properties = _DictDescr(doc="additional provider-specific properties")
    credentials = _DictDescr(doc="credentials that are needed by this provider")
    middleware = _TypeConstrainedDescr(
        (MiddlewareConfig, dict), doc="user configured middleware", default=MiddlewareConfig()
    )
    cache = _TypeConstrainedDescr(
        (CacheConfig, dict), doc="user configured cache config", default=CacheConfig()
    )
    tile_options = _TypeConstrainedDescr(
        (TileOptions, dict), doc="user configured tile options", default=TileOptions()
    )
    servicer_settings = _TypeConstrainedDescr(
        (ServicerSettings, dict),
        doc="user configured servicer settings",
        default=ServicerSettings(),
    )
    max_get_pixels_features = _IntDescr(
        doc="max number of input rasters to mosaic in a get_pixels request"
    )

    def set_middleware(self, middleware: Union[MiddlewareConfig, List[Middleware]]):
        """Sets the middleware on this BosonConfig."""
        if isinstance(middleware, (list, tuple)):
            self.middleware = MiddlewareConfig(middleware=middleware)
        elif isinstance(middleware, (MiddlewareConfig, dict)):
            self.middleware = middleware

    def append_middleware(self, middleware: Middleware):
        """Adds a middleware to the end of the middleware chain."""
        if self.middleware is None:
            self.middleware = MiddlewareConfig(middleware=[middleware])
        else:
            self.middleware.middleware.append(middleware)

    def set_time_enabled(
        self,
        interval: int,
        interval_units: str,
        datetime_field: str = None,
        start_datetime_field: str = None,
        end_datetime_field: str = None,
        track_id_field: str = None,
        time_extent: List[Union[str, datetime.datetime]] = None,
    ):
        f"""Set the datetime fields for the dataset.

        Args:
            interval: the interval increment for the dataset
            interval_units: the time units of the interval one of: [{', '.join(time_units)}]
            datetime_field: the field that is used to search by datetime in the dataset
            start_datetime_field: the field that is used to search by start datetime in the dataset
            end_datetime_field: the field that is used to search by end datetime in the dataset
            track_id_field: the field that is used to search by track id in the dataset
            time_extent: the time extent of the dataset
        """
        if self.servicer_settings is None:
            self.servicer_settings = ServicerSettings()

        if datetime_field is None and (start_datetime_field is None or end_datetime_field is None):
            raise ValueError(
                "Must set either datetime_field, or both start_datetime_field and end_datetime_field"  # noqa E501
            )

        optional_kwargs = {
            "datetime_field": datetime_field,
            "start_datetime_field": start_datetime_field,
            "end_datetime_field": end_datetime_field,
            "track_id_field": track_id_field,
            "time_extent": time_extent,
        }

        # Do not pass any optional kwargs that are None
        optional_kwargs = {k: v for k, v in optional_kwargs.items() if v is not None}

        self.servicer_settings.time_enable = TimeEnable(
            interval=interval,
            interval_units=interval_units,
            **optional_kwargs,
        )

    def _client(self):
        if self.provider_name == "vertex":
            return vertex_bsn_client
        return boson_client

    def _root_url(self, servicer: str, hash: str, project: Project) -> str:
        if self.provider_name == "vertex":
            iri = self.properties.get("iri", None)
            if iri is not None:
                m = iri_re.match(iri)
                if m is not None:
                    project = m.group("project")
                    hash = m.group("hash")
                    return f"datasets/{project}/{hash}/{servicer}"
                raise ValueError(f"invalid iri {iri}, must match bsn://dataset/<project>/<hash>")
            return f"datasets/{project.uid}/{hash}/{servicer}"
        return f"{project.uid}/{hash}/{servicer}"


class BosonDescr(_BaseDescr):
    """A Boson Provider Config.

    __get__ returns a BosonConfig object.

    __set__ sets from a dictionary or BosonConfig, coercing to a BosonConfig if needed and stores
        internally to the APIObject dict.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (BosonConfig, dict)

    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_boson_config')
        b = getattr(obj, self.private_name, None)
        if b is not None:
            # Return it if it exists
            return b

        try:
            b = self._get_object(obj)
            if isinstance(b, dict):
                b = BosonConfig(**b)
            self._set(obj, b)
            setattr(obj, self.private_name, b)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            self._set(obj, self.default)
            return self.default
        return b

    def _set(self, obj: object, value: object) -> None:
        # Reset the private attribute (e.g. "_boson_config") to None
        setattr(obj, self.private_name, None)

        if isinstance(value, BosonConfig):
            self._set_object(obj, value)
        elif isinstance(value, dict):
            self._set_object(obj, BosonConfig(**value))
        else:
            raise ValueError(f"invalid value type {type(value)}")

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (BosonConfig, dict)):
            raise ValueError(f"'{self.public_name}' must be a BosonConfig or a dict")

        try:
            BosonConfig(**value)
        except Exception as e:
            raise ValueError("boson config is invalid") from e
