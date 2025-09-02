from typing import List

import geodesic
from geodesic.bases import _APIObject
from geodesic.descriptors import _StringDescr, _DatetimeDescr
import geodesic.service

krampus_client = geodesic.service.RequestsServiceClient("krampus", api="auth")


class APIKey(_APIObject):
    """API Key object for Geodesic API."""

    api_key = _StringDescr(doc="Geodesic API Key")
    created_at = _DatetimeDescr(doc="Date and time the API key was created")
    last_used_at = _DatetimeDescr(doc="Date and time the API key was last used")

    def delete(self) -> None:
        """Delete the API key."""
        c = krampus_client.delete(f"keys/{self.api_key}")
        geodesic.raise_on_error(c)


def get_api_keys() -> List[APIKey]:
    """Get all API keys associated with the authenticated account."""
    c = krampus_client.get("keys")
    geodesic.raise_on_error(c)
    return [APIKey(**key) for key in c.json().get("api_keys", [])]
