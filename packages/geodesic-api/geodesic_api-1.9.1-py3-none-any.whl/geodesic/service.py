from geodesic import get_requests_client


class ServiceClient:
    def __init__(self, name: str, version: int = 1, api: str = None, **extra):
        self.client = RequestsServiceClient(name, version=version, api=api, **extra)

    @property
    def _stub(self):
        return self.client._stub

    def get(self, resource="", **query):
        return self.client.get(resource, params=query)

    def delete(self, resource="", **query):
        return self.client.delete(resource, params=query)

    def delete_with_body(self, resource="", **body):
        return self.client.delete(resource, json=body)

    def put(self, resource="", **body):
        return self.client.put(resource, json=body)

    def put_bytes(self, resource="", body: bytes = None):
        return self.client.put_bytes(resource, data=body)

    def post(self, resource="", **body):
        return self.client.post(resource, json=body)

    def post_bytes(self, resource="", body: bytes = None):
        return self.client.post(resource, body=body)

    def patch(self, resource="", **body):
        return self.client.patch(resource, json=body)

    def patch_with_body(self, resource="", **body):
        return self.client.patch_with_body(resource, json=body)


class RequestsServiceClient:
    def __init__(self, name: str, api: str = None, path: str = "", version: int = 1):
        self.name = name
        self.version = version
        self._stub = f"/{name}/api/v{version}"
        if api is not None:
            self._stub += "/" + api

        if path != "":
            path = path.removeprefix("/")
            path = path.removesuffix("/")
            self._stub += "/" + path

    def get(self, resource="", **params):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_requests_client().get(self._stub + resource, **params)

    def delete(self, resource="", **params):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_requests_client().delete(self._stub + resource, **params)

    def put(self, resource="", **params):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_requests_client().put(self._stub + resource, **params)

    def post(self, resource="", **params):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_requests_client().post(self._stub + resource, **params)

    def patch(self, resource="", **params):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_requests_client().patch(self._stub + resource, **params)
