# If this was checked out from a git tag, this version number may not match.
# Refer to the git tag for the correct version number
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("geodesic-api")
except ModuleNotFoundError:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("geodesic-api").version

from geodesic.config import get_config_manager, SearchReturnType
from geodesic.auth import authenticate
from geodesic.stac import Item, Feature, FeatureCollection, Asset, STACAPI
from geodesic.client import Client, get_client, get_requests_client, raise_on_error

import geodesic.boson.dataset as dataset
from geodesic.boson.dataset import (
    Dataset,
    DatasetList,
    get_dataset,
    get_datasets,
)
from geodesic.entanglement.object import (
    get_objects,
    Object,
    Observable,
    Connection,
    Entity,
    Event,
    Link,
    Model,
    Concept,
    Predicate,
)
from geodesic.boson.boson import BosonConfig
from geodesic.account.projects import (
    create_project,
    get_project,
    get_projects,
    set_active_project,
    get_active_project,
    Project,
)
from geodesic.account.user import myself
from geodesic.account.credentials import Credential, get_credential, get_credentials

config_manager = get_config_manager()

search_return_type = config_manager.get_user_option("search_return_type")
if search_return_type in SearchReturnType.__members__:
    dataset.SEARCH_RETURN_TYPE = SearchReturnType[search_return_type]

default_active_project = config_manager.get_user_option("default_active_project")
if (
    default_active_project is not None
    and default_active_project != ""
    and default_active_project != "global"
):
    set_active_project(default_active_project)


def set_search_return_type(search_return_type: SearchReturnType):
    dataset.SEARCH_RETURN_TYPE = search_return_type
    config_manager.set_user_option("search_return_type", search_return_type.name)


def get_search_return_type():
    return dataset.SEARCH_RETURN_TYPE


def get_default_active_project():
    return default_active_project


def set_default_active_project(project: str):
    project_uid = project
    if isinstance(project, Project):
        project_uid = project.uid
    elif isinstance(project, str):
        project = get_project(project)
        project_uid = project.uid

    config_manager.set_user_option("default_active_project", project_uid)


__all__ = [
    "authenticate",
    "Item",
    "Feature",
    "FeatureCollection",
    "Asset",
    "BosonConfig",
    "Client",
    "get_client",
    "get_requests_client",
    "raise_on_error",
    "Raster",
    "RasterCollection",
    "Dataset",
    "DatasetList",
    "get_dataset",
    "get_datasets",
    "get_objects",
    "Object",
    "Entity",
    "Event",
    "Observable",
    "Property",
    "Link",
    "Model",
    "Concept",
    "Predicate",
    "Connection",
    "Project",
    "Credential",
    "get_credential",
    "get_credentials",
    "create_project",
    "get_project",
    "get_projects",
    "set_active_project",
    "get_active_project",
    "myself",
    "STACAPI",
    "SearchReturnType",
    "set_search_return_type",
    "get_search_return_type",
    "get_default_active_project",
    "set_default_active_project",
]
