import geodesic
import geodesic.service

vertex_client = geodesic.service.RequestsServiceClient("vertex", api="bsn", version=1)


def vertex_bootstrap() -> str:
    """Returns the bootstrap address for the Vertex service.

    This address is returned in ``multiaddr`` format can be used to bootstrap another Vertex node on
    the DHT.

    Returns:
        str: The bootstrap address for the Vertex service.

    """
    res = geodesic.raise_on_error(vertex_client.get("bootstrap"))
    return res.json()["bootstrap_address"]
