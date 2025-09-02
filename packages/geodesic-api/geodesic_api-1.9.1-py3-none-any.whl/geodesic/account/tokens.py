import base64
from typing import List, Union
from collections import defaultdict
from geodesic.bases import _APIObject
from geodesic.client import raise_on_error
from geodesic.config import get_config
from geodesic.descriptors import (
    _StringDescr,
    _DictDescr,
    _DatetimeDescr,
    _GeometryDescr,
    _BoolDescr,
)
from geodesic.account.projects import _ProjectDescr, Project, get_project
from geodesic.service import RequestsServiceClient

vertex_client = RequestsServiceClient("vertex", api="share", version=1)


class Token(_APIObject):
    """Represents the share tokens created when a user shares a dataset through Vertex.

    Args:
        **token: values corresponding to the token and the dataset it shares
    """

    token = _StringDescr(
        doc="unique 32-bit token created by Vertex and used to access a shared dataset"
    )
    alias = _StringDescr(doc="the alias/nickname of the token")
    description = _StringDescr(doc="the description of the token")
    servicer_name = _StringDescr(doc="the servicer of the dataset shared by the token")
    dataset_hash = _StringDescr(doc="the hash of the dataset shared by the token")
    dataset_name = _StringDescr(
        dict_name="name", nested="qualifiers", doc="the name of the dataset shared by the token"
    )
    qualifiers = _DictDescr(doc="qualifiers of the dataset shared by the token")
    domain = _StringDescr(nested="qualifiers", doc="the domain of the dataset shared by the token")
    category = _StringDescr(
        nested="qualifiers", doc="the category of the dataset shared by the token"
    )
    type = _StringDescr(nested="qualifiers", doc="the type of the dataset shared by the token")
    project = _ProjectDescr(
        doc="the hash (uid) of the project of the dataset shared by the token",
        dict_name="project_hash",
    )
    extra_settings = _DictDescr(doc="extra settings for the token")
    geometry = _GeometryDescr(doc="the geometry of the extent shared by the token")
    ttl = _StringDescr(doc="the remaining time in seconds until the token expires")
    created_at = _DatetimeDescr(doc="the time the token was created")
    updated_at = _DatetimeDescr(doc="the time the token was last updated")
    last_used_at = _DatetimeDescr(doc="the time the token was last used")
    expires_at = _DatetimeDescr(doc="the time the token expires")
    broadcast = _BoolDescr(doc="broadcast this dataset on the Boson Network", default=False)

    def __init__(self, **token):
        super().__init__(self, **token)

    def get_url(self, url_style: str = "path") -> str:
        """Returns the URL that can be used to access a datset shared through Vertex.

        Raises:
            requests.HTTPErrror for fault

        Returns:
            the URL to access the token in question
        """
        if url_style == "header":
            return "{api_host}/vertex/api/v1/share/h".format(api_host=get_config().host)
        elif url_style == "query":
            return "{api_host}/vertex/api/v1/share/q".format(api_host=get_config().host)
        return "{api_host}/vertex/api/v1/share/{token}/".format(
            api_host=get_config().host, token=self.token
        )

    def get_vector_tile_service_url(self, service_name: str = None):
        """Gets a url to an GeoServices VectorTileService.

        Args:
            service_name: an optional service name to use in place of the dataset name

        Returns a URL pointing to a vector tile service that can be used in ArcGIS.
        """
        if self.servicer_name != "geoservices":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'geoservices'")
        if service_name is None:
            return f"{self.get_url()}rest/services/{self.dataset_name}/VectorTileServer"
        else:
            return f"{self.get_url()}rest/services/{service_name}/VectorTileServer"

    def get_image_service_url(self, service_name: str = None):
        """Gets a url to an GeoServices ImageService.

        Args:
            service_name: an optional service name to use in place of the dataset name

        Returns a URL pointing to an image service that can be used in ArcGIS.
        """
        if self.servicer_name != "geoservices":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'geoservices'")
        if service_name is None:
            return f"{self.get_url()}rest/services/{self.dataset_name}/ImageServer"
        else:
            return f"{self.get_url()}rest/services/{service_name}/ImageServer"

    def get_feature_service_url(self, service_name: str = None):
        """Gets a url to an GeoServices FeatureService.

        Args:
            service_name: an optional service name to use in place of the dataset name

        Returns a URL pointing to a feature service that can be used in ArcGIS.
        """
        if self.servicer_name != "geoservices":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'geoservices'")
        if service_name is None:
            return f"{self.get_url()}rest/services/{self.dataset_name}/FeatureServer"
        else:
            return f"{self.get_url()}rest/services/{service_name}/FeatureServer"

    def get_ogc_vector_tile_url(
        self,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        format: str = "mvt",
    ) -> str:
        """Gets a url to an OGC API: Tiles service.

        Returns a URL pointing to a vector tile service that can be used in web mapping.
        """
        if format not in ["mvt", "pbf", "vectors.pbf"]:
            raise ValueError(
                f"format '{format}' is not supported, must be 'mvt', 'pbf', or 'vectors.pbf'"
            )
        return self._get_ogc_tile_url(
            format,
            collection,
            tile_matrix_set_id,
            tile_matrix_id,
            row_name,
            col_name,
        )

    def get_ogc_raster_tile_url(
        self,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        format: str = "png",
        tile_path: str = "coverage/tiles",
    ) -> str:
        """Gets a url to an OGC API: Tiles service.

        Returns a URL pointing to a raster tile service that can be used in web mapping.
        """
        if format not in ["png", "jpg", "jpeg", "tif"]:
            raise ValueError(
                f"format '{format}' is not supported, must be 'png', 'jpg', 'jpeg', or 'tif'"
            )
        return self._get_ogc_tile_url(
            format,
            collection,
            tile_matrix_set_id,
            tile_matrix_id,
            row_name,
            col_name,
            tile_path=tile_path,
        )

    def get_tilejson_vector_tile_url(
        self,
        collection: str = None,
    ) -> str:
        """Gets a url to a TileJSON endpoint for a vector tile service.

        If the collection is left blank, it will default to the default collection.
        Otherwise, a specific collection can be specified.

        Returns:
            a URL pointing to a vector tile service that can be used in web mapping.
        """
        if self.servicer_name != "tilejson":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'tilejson'")
        if collection is None:
            collection = self.dataset_name

        return f"{self.get_url()}vector/{collection}.json"

    def get_tilejson_raster_tile_url(self) -> str:
        """Gets a url to a TileJSON endpoint for a raster tile service.

        The tile endpoint will always point to the default asset for this dataset

        Returns:
            a URL pointing to a raster tile service that can be used in web mapping.
        """
        if self.servicer_name != "tilejson":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'tilejson'")

        collection = self.dataset_name
        return f"{self.get_url()}raster/{collection}.json"

    def _get_ogc_tile_url(
        self,
        format: str,
        collection: str = None,
        tile_matrix_set_id: str = "WebMercatorQuad",
        tile_matrix_id: str = "z",
        row_name: str = "y",
        col_name: str = "x",
        tile_path: str = "tiles",
    ) -> str:
        if self.servicer_name != "tiles":
            raise ValueError(f"token is for '{self.servicer_name}', must be for 'tiles'")
        if collection is None:
            collection = self.dataset_name

        suffix = "{" + tile_matrix_id + "}/{" + row_name + "}/{" + col_name + "}" + f".{format}"
        dataset_root = f"{self.get_url()}collections/{collection}/{tile_path}/{tile_matrix_set_id}/"
        return f"{dataset_root}{suffix}"

    def get_feature_layer_url(self, layer_id: int = 0, service_name: str = None) -> str:
        """Gets a url to an GeoServices Feature Layer.

        Returns a URL pointing to a layer that can directly be used in ArcGIS.

        Args:
            layer_id: the layer ID to expose
            service_name: an optional service name to use in place of the dataset name

        Returns:
            a URL to to layer
        """
        return f"{self.get_feature_service_url(service_name=service_name)}/{layer_id}"

    def update_ttl(self, ttl: int):
        """Update the time to live of a token in redis.

        Args:
            ttl: the amount of seconds before the token should expire. Valid values are either -1,
                 representing an infinite token life, or n, where 0 < n <= 2147483647.

        Raises:
            requests.HTTPErrror for fault

        Note: If successful, nothing is returned.
        """
        raise_on_error(vertex_client.patch(str(self.token) + "/" + str(ttl)))
        return

    def unshare(self):
        """Expires an active token created by the user, revoking access from anyone using the token.

        Raises:
            requests.HTTPErrror for fault

        .. Note::
            If successful, nothing is returned. Deleting a non-existent token does
            not raise an error.
        """
        raise_on_error(vertex_client.delete(str(self.token)))
        return


def get_tokens(
    project: Union[Project, str] = None,
    servicer_name: str = None,
    dataset_name: str = None,
    dataset_hash: str = None,
    domain: str = None,
    category: str = None,
    type: str = None,
    limit: int = None,
) -> "Tokens":
    """Returns all active tokens created by a user.

    Args:
        project: the project name - returns only tokens for this project
        servicer_name: the servicer of the dataset (optional). If None, returns for all servicers
        dataset_name: the name of the dataset to find tokens for
        dataset_hash: the hash of the dataset to find tokens for
        domain: the domain of the dataset to find tokens for
        category: the category of the dataset to find tokens for
        type: the type of the dataset to find tokens for
        limit: the maximum number of tokens to return (default is None, which returns all tokens)

    Raises:
        requests.HTTPErrror for fault
    """
    params = {}
    if project is not None:
        project = _get_project(project)
        params["project"] = project.uid
    if servicer_name is not None:
        params["servicer_name"] = servicer_name
    if dataset_name is not None:
        params["dataset_name"] = dataset_name
    if dataset_hash is not None:
        params["dataset_hash"] = dataset_hash
    if domain is not None:
        params["domain"] = domain
    if category is not None:
        params["category"] = category
    if type is not None:
        params["type"] = type

    page_size = 1000
    if limit is not None:
        page_size = limit
    if page_size > 1000:
        page_size = 1000

    page_token = base64.b64encode(f"0:{page_size}".encode()).decode("utf-8")
    params["page_token"] = page_token

    res = raise_on_error(vertex_client.get("", params=params))
    js = res.json()
    if js == {}:
        return Tokens()

    tokens = js.get("tokens", [])

    if limit is None or limit > page_size:
        next_page_token = js.get("next_page_token", None)
        while next_page_token:
            params["page_token"] = next_page_token
            res = raise_on_error(vertex_client.get("", params=params))
            next_tokens = res.json().get("tokens", [])

            if limit is not None:
                next_tokens = next_tokens[: limit - len(tokens)]

            tokens.extend(next_tokens)
            if len(next_tokens) < page_size:
                break

            next_page_token = js.get("next_page_token", None)
    if limit is not None and len(tokens) > limit:
        tokens = tokens[:limit]

    return Tokens([Token(**token) for token in tokens])


class Tokens(list):
    def __init__(self, tokens: List[Token] = []):
        super().__init__(tokens)
        self.lookup = defaultdict(list)
        for token in tokens:
            self.lookup[f"{token.project.uid}:{token.dataset_name}"].append(token)

    def tokens_for(
        self,
        project: str,
        dataset: str,
        servicer: str = None,
        persistent_only: bool = False,
        broadcasted_only: bool = False,
    ) -> "Tokens":
        """Returns all active tokens created by a user for a specific project and dataset.

        Args:
            project: the project name
            dataset: the dataset name
            servicer: the servicer of the dataset (optional). If None, returns for all servicers
            persistent_only: if True, returns only tokens that do not expire
            broadcasted_only: if True, returns only tokens that are broadcasted

        Returns:
            a list of tokens
        """
        project = _get_project(project)

        tokens = self.lookup[f"{project.uid}:{dataset}"]
        if servicer is not None:
            tokens = Tokens([token for token in tokens if token.servicer == servicer])
        if persistent_only:
            tokens = Tokens([token for token in tokens if token.ttl == "-1"])
        if broadcasted_only:
            tokens = Tokens([token for token in tokens if token.broadcast])
        return Tokens(tokens)


def _get_project(p: Union[Project, str]) -> Project:
    if isinstance(p, Project):
        return p
    return get_project(p)
