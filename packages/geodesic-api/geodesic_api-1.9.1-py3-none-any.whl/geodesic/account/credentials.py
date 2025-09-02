import base64
from typing import Union, Any
from getpass import getpass
from geodesic.bases import _APIObject
import json
import requests
from geodesic import raise_on_error
from geodesic.service import RequestsServiceClient
from geodesic.descriptors import _StringDescr
from geodesic.account.oauth2 import OAuth2Client

# Credentials client
credentials_client = RequestsServiceClient("krampus", api="credentials", version=1)

SERVICE_ACCOUNT_KEY = "SERVICE_ACCOUNT_KEY"
AWS_KEY_PAIR = "AWS_KEY_PAIR"
AZURE_ACCESS_KEY = "AZURE_ACCESS_KEY"
JWT = "JWT"
OAUTH2_CLIENT_CREDENTIALS = "OAUTH2_CLIENT_CREDENTIALS"
OAUTH2_REFRESH_TOKEN = "OAUTH2_REFRESH_TOKEN"
BASIC_AUTH = "BASIC_AUTH"
API_KEY = "API_KEY"
DOCKER_PULL = "DOCKER_PULL"

valid_types = [
    SERVICE_ACCOUNT_KEY,
    AWS_KEY_PAIR,
    AZURE_ACCESS_KEY,
    JWT,
    OAUTH2_CLIENT_CREDENTIALS,
    OAUTH2_REFRESH_TOKEN,
    BASIC_AUTH,
    API_KEY,
    DOCKER_PULL,
]


def get_credential(name_or_uid: str = None):
    """Gets the uid/name/type of requested credential, or None if it doesn't exist.

    Args:
        name_or_uid: Name or UID of the credential to access
    """
    res = raise_on_error(credentials_client.get(name_or_uid))
    c = res.json()["credential"]
    if c is None:
        return None
    return Credential(**c)


def get_credentials():
    """Returns all of your user's credentials."""
    res = raise_on_error(credentials_client.get(""))
    return [Credential(**p) for p in res.json()["credentials"]]


class Credential(_APIObject):
    """Credentials to access secure resources such as a cloud storage bucket.

    Credentials have a name, type and data. Credentials can be created or deleted but not
    accessed again except by internal services. This is for security reasons. Credentials are
    stored using symmetric PGP encryption at rest.
    """

    uid = _StringDescr(doc="the unique ID for this credential. Set automatically")
    name = _StringDescr(
        doc="the name of this credential. Unique to the user and how a user will"
        "typically reference it"
    )
    type = _StringDescr(
        one_of=valid_types,
        doc=f"the type of the credential. Supported types are {', '.join(valid_types)}",
    )

    _limit_setitem = ["name", "type", "data"]

    def __init__(self, **credential):
        self._name = None
        self._type = None
        self.__data = bytes()
        self._client = credentials_client
        for k, v in credential.items():
            setattr(self, k, v)

    def create(self, ignore_if_exists=True):
        """Creates a new Credentials. Encodes the data to be sent."""
        data = self.__data
        if isinstance(data, bytes):
            enc_data = base64.b64encode(data).decode()
        elif isinstance(data, dict):
            enc_data = base64.b64encode(json.dumps(data).encode()).decode()
        elif isinstance(data, str):
            enc_data = base64.b64encode(data.encode()).decode()

        try:
            raise_on_error(
                self._client.post("", json=dict(name=self.name, type=self.type, data=enc_data))
            )
        except requests.HTTPError as e:
            try:
                get_credential(self.name)
                if ignore_if_exists:
                    return
                raise e
            except requests.HTTPError:
                raise e

    def delete(self):
        raise_on_error(self._client.delete(self.name))

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, v: Any):
        self.__data = v

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "data":
            self.__data = value
        return super().__setattr__(name, value)

    def from_docker_registry(
        *, name: str, username: str, host: str, email: str, password: str = None
    ) -> "Credential":
        """Creates a new Docker Pull Credential for a Docker Registry.

        Creates a Credential object that allows internal resources to pull a container image from a
        registry. Most registries support this method of pulling images and specifically this is how
        this is done in Kubernetes in most cases.

        Details for GCP/GCR: https://cloud.google.com/container-registry/docs/advanced-authentication#json-key

        Arguments:
            name: the name of the Credential to create
            username: the username (varies by registry provider, username for Dockerhub, "_json_key"
                 for GCR, etc)
            host: the hostname for the registry (e.g. https://docker.io)
            email: the email address associated with this account
            password: the password or token for this account

        Returns:
            a new Credential object that can be saved to the backend. User must call `create` to
            save it
        """
        if password is None:
            password = getpass(prompt="enter password or appropriately formatted key: ")

        return Credential(
            name=name,
            type=DOCKER_PULL,
            data={
                "username": username,
                "host": host,
                "email": email,
                "password": password,
            },
        )

    @staticmethod
    def from_gcp_service_account(*, name: str, key: Union[str, dict] = None) -> "Credential":
        """Creates new GCP Service Account Credential.

        Creates a new Credential object for a GCP Service Account (e.g. Google Earth Engine,
        BigQuery, etc)

        Arguments:
            name: the name of the Credential to create
            key: the full service account, either a string or dict. If `None`, user will
                 be prompted via stdin

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if key is None:
            key = getpass(prompt="Paste Complete Google Cloud Service Account Key: ")
        if isinstance(key, str):
            key = json.loads(key)

        return Credential(name=name, type=SERVICE_ACCOUNT_KEY, data=key)

    @staticmethod
    def from_aws_key_pair(
        *, name: str, aws_access_key_id: str, aws_secret_access_key: str = None
    ) -> "Credential":
        """Creates new AWS Key Pair Credential.

        Creates a new Credential object for an AWS Key Pair (such as from an IAM User)

        Arguments:
            name: the name of the Credential to create
            aws_access_key_id: the access key id
            aws_secret_access_key: the secret key.  If `None`, user will
                 be prompted via stdin.

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if aws_secret_access_key is None:
            aws_secret_access_key = getpass(prompt="AWS Secret Access Key: ")

        return Credential(
            name=name,
            type=AWS_KEY_PAIR,
            data={
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
            },
        )

    @staticmethod
    def from_azure_storage_account(
        *, name: str, account_name: str, account_key: str = None
    ) -> "Credential":
        """Creates new Azure Storage Account Credential.

        Creates a new Credential object for an Azure Storage Account (e.g. Blob storage)

        Arguments:
            name: the name of the Credential to create
            account_name: the Azure account name
            account_key: the secret key for the account.  If `None`, user will
                 be prompted via stdin.

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if account_key is None:
            account_key = getpass(prompt="Azure Storage Account Key: ")

        return Credential(
            name=name,
            type=AZURE_ACCESS_KEY,
            data={"account_name": account_name, "account_key": account_key},
        )

    @staticmethod
    def from_azure_connection_string(*, name: str, connection_string: str = None) -> "Credential":
        """Creates new Azure Storage Account Credential.

        Creates a new Credential object for an Azure Storage Account (e.g. Blob storage)

        Arguments:
            name: the name of the Credential to create
            connection_string: the Azure account's connection string. If `None`, user will
                 be prompted via stdin.

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if connection_string is None:
            connection_string = getpass(prompt="Azure Storage Account Connection String: ")

        return Credential(
            name=name,
            type=AZURE_ACCESS_KEY,
            data={"connection_string": connection_string},
        )

    @staticmethod
    def from_jwt(
        *,
        name: str,
        jwt: str = None,
        token_url: str = None,
        api_key: str = None,
        jwt_header_name: str = "Authorization",
        api_key_header_name: str = "API-KEY",
        insecure_skip_verify: bool = False,
    ) -> "Credential":
        """Creates new JSON Web Token Credential.

        Creates a new Credential object for an arbitrary JWT or token endpoint. Note that for OAuth2
        flows, this should NOT be used. Use from_oauth2_client_credentials or
        from_oauth2_refresh_token instead.

        Arguments:
            name: the name of the Credential to create
            jwt: the string/encoded JWT. If `None`, user will
                 be prompted via stdin.
            token_url: the token url/uri to request a JWT via an API key exchange. If `jwt` is
                specified, this is ignored. If `jwt` is not specified, the API key must also be
                specified and the remaining arguments should be checked
            api_key: the API key to exchange for a JWT. If `None`, user will be prompted via stdin.
            jwt_header_name: the header name to use for the JWT. Default "Authorization"
            api_key_header_name: the header name to use for the API key. Default
            insecure_skip_verify: whether to skip verifying the SSL certificate of the token_url

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it

        Examples:
            >>> c = Credential.from_jwt(name="my-jwt")
            >>> c = Credential.from_jwt(name="my-jwt", jwt="...")
            >>> c = Credential.from_jwt(name="my-jwt", token_url="https://my-auth-service/token", api_key="...")

        """  # noqa: E501
        if token_url is not None:
            if api_key is None:
                api_key = getpass(prompt="API Key: ")

            return Credential(
                name=name,
                type=JWT,
                data={
                    "token_url": token_url,
                    "api_key": api_key,
                    "jwt_header_name": jwt_header_name,
                    "api_key_header_name": api_key_header_name,
                    "insecure_skip_verify": insecure_skip_verify,
                },
            )

        if jwt is None:
            jwt = getpass(prompt="Paste Complete JSON Web Token: ")

        data = {"token": jwt}
        return Credential(name=name, type=JWT, data=data)

    @staticmethod
    def from_oauth2_client_credentials(
        *,
        name: str,
        client_id: str,
        client_secret: str = None,
        token_url: str = None,
        authorization_url: str = None,
        audience: str = None,
        scope: str = None,
    ) -> "Credential":
        """Creates new OAuth2 Client Credentials Credential.

        Creates a new Credential object for an OAuth2 Application

        Arguments:
            name: the name of the Credential to create
            client_id: the client_id of the oauth2 app
            client_secret: the client secret of the oauth2 app. If `None`, user will
                 be prompted via stdin.
            token_url: the token url/uri to request an access token
            authorization_url: the authorization url for certain auth flows
            audience: (optional) the audience of the access_token
            scope: (optional) custom scope to be requested with the token

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if token_url is None:
            raise ValueError("must provide token_url")
        if authorization_url is None:
            raise ValueError("must provide authorization_url")
        if client_secret is None:
            client_secret = getpass(prompt="Client Secret: ")

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "token_url": token_url,
            "authorization_url": authorization_url,
        }

        if audience is not None:
            data["audience"] = audience
        if scope is not None:
            data["scope"] = scope

        return Credential(name=name, type=OAUTH2_CLIENT_CREDENTIALS, data=data)

    @staticmethod
    def from_oauth2_refresh_token(
        *,
        name: str,
        client_id: str,
        token_url: str,
        authorization_url: str,
        client_secret: str = None,
        refresh_token: str = None,
        audience: str = None,
        scope: list = [],
        redirect_uri: str = "https://seerai.space/authPage",
        insecure_skip_verify: bool = False,
    ) -> "Credential":
        if client_secret is None:
            client_secret = getpass(prompt="Client Secret: ")

        if refresh_token is None:
            client = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url,
                authorization_url=authorization_url,
                audience=audience,
                scope=scope,
                redirect_uri=redirect_uri,
                insecure_skip_verify=insecure_skip_verify,
            )

            refresh_token = client.authenticate()

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "token_url": token_url,
            "authorization_url": authorization_url,
            "token": {
                "refresh_token": refresh_token,
            },
        }

        if audience is not None:
            data["audience"] = audience
        if scope is not None:
            data["scope"] = " ".join(scope)

        return Credential(name=name, type=OAUTH2_REFRESH_TOKEN, data=data)

    @staticmethod
    def from_basic_auth(*, name: str, username: str, password: str = None) -> "Credential":
        """Creates new Basic Auth Credential.

        Creates a new Credential object for a username/password

        Arguments:
            name: the name of the Credential to create
            username: the username
            password: the password. If `None`, user will
                 be prompted via stdin.

        Returns:
            a new Credential object that can be saved to backend. User must call `create` to save it
        """
        if password is None:
            password = getpass()

        return Credential(
            name=name,
            type=BASIC_AUTH,
            data={"username": username, "password": password},
        )
