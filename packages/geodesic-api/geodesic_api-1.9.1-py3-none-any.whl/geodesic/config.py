import json
import os
from enum import Enum
from typing import List, Optional, Tuple, Union, Any


class SearchReturnType(Enum):
    """Return type for search queries."""

    GEODATAFRAME = 1
    FEATURE_COLLECTION = 2


# The path to where the config file is stored
_default_path = os.path.expanduser("~/.config/geodesic")
_config_dir = os.getenv("GEODESIC_CONFIG_DIR", _default_path)
_config_path = os.path.join(_config_dir, "config.json")

_config_manager = None


def get_config_manager():
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def _default_config(name: str = None, host: str = None) -> dict:
    """Returns the default configuration file as a dict."""
    if not name:
        name = "seerai"
    if not host:
        host = "https://api.geodesic.seerai.space"

    cfg = {
        "clusters": [
            {
                "name": name,
                "host": host,
            }
        ],
        "active": name,
        "search_return_type": SearchReturnType.GEODATAFRAME.name,
        "default_active_project": "global",
    }

    return cfg


def _default_scopes() -> list:
    """Returns the default oauth cluster scopes."""
    return [
        "email",
        "openid",
        "profile",
        "picture",
        "offline_access",
        "geodesic:admin",
        "entanglement:read",
        "entanglement:write",
        "entanglement:schema",
        "spacetime:read",
        "spacetime:write",
        "tesseract:read",
        "tesseract:write",
        "boson:read",
        "boson:write",
        "krampus:read",
        "krampus:write",
        "ted:write",
        "flock:write",
    ]


def _write_default_config():
    os.makedirs(_config_dir, exist_ok=True)

    with open(_config_path, "w") as fp:
        json.dump(_default_config(), fp, indent=4, sort_keys=True)


class ClusterConfig:
    """ClusterConfig points the geodesic API at a configured Geodesic cluster.

    Args:
        cfg(dict): The configuration dictionary containing server information.
    """

    def __init__(self, cfg: dict) -> None:
        self.name = cfg["name"]
        self.host = cfg["host"]
        if os.environ.get("GEODESIC_HOST"):
            self.host = os.environ.get("GEODESIC_HOST")
        self.api_key = cfg.get("api_key")
        self.oauth2 = OAuth2Config(cfg.get("oauth2", None))
        self.services = {s["name"]: ServiceConfig(s) for s in cfg.get("services", [])}

    def to_dict(self) -> dict:
        """Converts this cluster config into a JSON exportable dictionary.

        The dictionary will be exported as would be listed in the "clusters" field of the config
        object.
        """
        d = dict(
            name=self.name,
            host=self.host,
        )
        if self.oauth2.client_id:
            d["oauth2"] = self.oauth2.to_dict()

        if self.api_key:
            d["api_key"] = self.api_key

        if len(self.services) > 0:
            d["services"] = [s.to_dict() for k, s in self.services.items()]
        return d

    def service_host(self, service: str) -> str:
        """Given a service, returns the host configured for that service.

        Examples of services are 'spacetime', 'krampus', etc.

        Arguments:
            service: the service we want the host for (example: 'spacetime')

        Returns:
            the host for that service

        """
        # Get the default host, trim trailing forward slash if present
        default_host = self.host
        if self.host.endswith("/"):
            default_host = self.host[:-1]

        # Is the service host overridden? If so, return that
        if service in self.services:
            host = self.services[service].host
            if host.endswith("/"):
                host = host[:-1]
            return host
        return f"{default_host}/{service}"

    def send_headers(self, url: str) -> bool:
        """Given a url determine whether to send auth headers.

        It returns true if the url contains the configured host, or a host in the overrides.
        """
        if self.host in url:
            return True

        for service in self.services.values():
            if service.host in url:
                return True
        return False

    def token_url(self) -> str:
        """Returns the token url for this cluster."""
        return f"{self.service_host('krampus')}/api/v1/auth/token"

    def authorize_url(self) -> str:
        """Returns the authorize url for this cluster."""
        return f"{self.service_host('krampus')}/api/v1/auth/authorize"


def get_config() -> ClusterConfig:
    """Utility to get the configuration for the active cluster.

    This is the primary way that a user should get the cluster configuration if needed.
    In general except for development usage, the user should not create a :class:`ConfigManager`
    or :class:`ClusterConfig` manually.

    In most cases users will not need to change the active cluster, however it can be done using the
    Geodesic CLI.

    Returns:
        :class:`ClusterConfig` for the current active cluster.
    """
    os.makedirs(_config_dir, exist_ok=True)
    return ConfigManager().get_active_config()


class OAuth2Config:
    """Configuration for an OAuth2 Provider."""

    def __init__(self, cfg: Optional[dict]) -> None:
        self.client_id = None
        if not cfg:
            return
        self.client_id = cfg["client_id"]
        self.client_secret = cfg.get("client_secret")
        self.audience = cfg["audience"]
        self.redirect_uri = cfg["redirect_uri"]
        self.token_uri = cfg["token_uri"]
        self.authorization_uri = cfg["authorization_uri"]
        self.scopes = cfg.get("scopes", _default_scopes())

    def to_dict(self) -> dict:
        if self.client_id is None:
            return {}
        return dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            audience=self.audience,
            redirect_uri=self.redirect_uri,
            token_uri=self.token_uri,
            authorization_uri=self.authorization_uri,
            scopes=self.scopes,
        )


class ServiceConfig:
    """ADVANCED/DEV usage.

    Individual service level configuration. Used for machine-to-machine comms,
    or to point to replacement services as needed.
    """

    def __init__(self, cfg: dict) -> None:
        self.name = cfg["name"]
        self.host = cfg["host"]

    def to_dict(self) -> dict:
        return dict(name=self.name, host=self.host)


class ConfigManager:
    """Manages the active config.

    Mostly just used by the CLI, but if you needed to programatically change config,
    that's also an option.
    """

    def __init__(self) -> None:
        self._active_config = None

    def list_configs(self) -> Tuple[List[str], str]:
        """Return a list of clusters in this config and the active cluster."""
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}
        with open(_config_path, "r") as fp:
            cfg = json.load(fp)

        clusters = []
        for cluster in cfg["clusters"]:
            clusters.append(cluster["name"])

        return clusters, cfg["active"]

    def get_config(self, name: str) -> ClusterConfig:
        """Returns the cluster config for the given name.

        Useful for when the user needs to hop between
        clusters at runtime, also used internally in the CLI.

        Arguments:
            name: the name of the cluster to get the config for

        Returns:
            the requests cluster config
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # Read and parse
        cfg = {}
        with open(_config_path, "r") as fp:
            cfg = json.load(fp)

        if name is None:
            name = cfg["active"]

        for cluster in cfg["clusters"]:
            if cluster["name"] == name:
                return ClusterConfig(cluster)

        raise KeyError(f"cluster config '{name}' not found in the config")

    def get_active_config(self) -> ClusterConfig:
        """Gets whichever cluster config is active in the config file.

        Returns:
            the active cluster config
        """
        if self._active_config is not None:
            return self._active_config
        self._active_config = self.get_config(name=None)
        return self._active_config

    def set_active_config(
        self,
        name: str,
        add_cluster: Optional[Union[ClusterConfig, dict]] = None,
        overwrite: bool = False,
    ) -> ClusterConfig:
        """Set the active cluster config.

        This can either be a config that's already in the file or a new one.

        Arguments:
            name: the name of the cluster to make active
            add_cluster: a ClusterConfig (or dict) to add. Name in the config must match the
                name argument
            overwrite: overwrite an existing config, if present

        Returns:
            the new active cluster config
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}

        with open(_config_path, "r") as fp:
            cfg = json.load(fp)

        # If a config was passed in...
        if add_cluster is not None:
            if isinstance(add_cluster, dict):
                add_cluster = ClusterConfig(add_cluster)
            # Validate if the name matches
            if add_cluster.name != name:
                raise ValueError("provided ClusterConfig's name does not match provided name")

            # Where to add this new config
            clusterIdx = -1
            for i, cluster in enumerate(cfg["clusters"]):
                if cluster["name"] == add_cluster.name:
                    if not overwrite:
                        raise ValueError(
                            "cluster of this name already exists. Set overwrite"
                            " to True if you want to overwrite existing config"
                        )

                    clusterIdx = i
            # Write in the new config
            if clusterIdx >= 0:
                cfg["clusters"][clusterIdx] = add_cluster.to_dict()
            else:
                cfg["clusters"].append(add_cluster.to_dict())

        else:
            found = False
            for cluster in cfg["clusters"]:
                if cluster["name"] == name:
                    found = True
            if not found:
                raise ValueError(
                    f"specified cluster name was not found in your config ({_config_path})"
                )

        # Set this as active
        cfg["active"] = name

        # Save the confg
        with open(_config_path, "w") as fp:
            json.dump(cfg, fp, indent=4, sort_keys=True)

        self.get_active_config()

    def set_user_option(self, key: str, value: Any) -> None:
        """Set a user option in the active cluster config.

        Arguments:
            key: the key to set
            value: the value to set
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}
        with open(_config_path, "r") as fp:
            cfg = json.load(fp)

        # Set the value
        cfg[key] = value

        # Save the confg
        with open(_config_path, "w") as fp:
            json.dump(cfg, fp, indent=4, sort_keys=True)

        self.get_active_config()

    def get_user_option(self, key: str) -> Any:
        """Get a user option in the active cluster config.

        Arguments:
            key: the key to get

        Returns:
            the value
        """
        # If the config doesn't exist, create the default one.
        if not os.path.exists(_config_path):
            _write_default_config()

        # read the config file
        cfg = {}
        with open(_config_path, "r") as fp:
            cfg = json.load(fp)

        return cfg.get(key)
