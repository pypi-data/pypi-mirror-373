from typing import Tuple, List
from geodesic.utils import DeferredImport
from geodesic.client import raise_on_error
from geodesic.bases import _APIObject
from geodesic.service import RequestsServiceClient
from geodesic.entanglement.object import Object, Connection, Predicate
from geodesic.entanglement.graph import Graph

graphql_client = RequestsServiceClient("entanglement", api="graphql", version=1)

nx = DeferredImport("networkx")

OBJECT_FRAGMENT = """
fragment objectParts on Object {
    uid
    name
    project
    alias
    description
    xid
    class
    domain
    category
    type
    item
    geometry
}
"""

PROJECT_FRAGMENT = """
fragment projectParts on Project {
    uid
    name
    alias
    description
    owner
    keywords
}
"""

CONNECTION_FRAGMENT = """
fragment connectionParts on Connection {
    subject {
        ...objectParts
    }
    predicate
    object {
        ...objectParts
    }
    attributes
}
"""

FRAGMENTS = {
    "objectParts": OBJECT_FRAGMENT,
    "projectParts": PROJECT_FRAGMENT,
    "connectionParts": CONNECTION_FRAGMENT,
}


class GraphResponse(_APIObject):
    """The response from a `graph` query on the Entanglement GraphQL API."""

    def __init__(
        self,
        uses_object_parts_fragment: bool = False,
        uses_connection_parts_fragment: bool = True,
        **kwargs,
    ):
        self.uses_object_parts_fragment = uses_object_parts_fragment
        self.uses_connection_parts_fragment = uses_connection_parts_fragment
        super().__init__(**kwargs)

    def as_networkx_graph(self) -> Graph:
        """Returns the response as a networkx graph."""
        nodes, edges = self.as_objects_and_connections()
        return Graph(nodes=nodes, edges=edges)

    def as_objects_and_connections(self) -> Tuple[List[Object], List[Connection]]:
        """Returns the response as a dictionary of objects and connections."""
        if not self.uses_object_parts_fragment:
            raise ValueError(
                "in order to use this method, query must use the 'objectParts' fragment"
            )

        objects = {}
        connections = []
        for obj in self["graph"]:
            if "connections" in obj:
                if not self.uses_connection_parts_fragment:
                    raise ValueError(
                        "in order to use this method, query must use the 'connectionParts' fragment"
                    )

                objs, conns = _parse_connections(obj)
                connections.extend(conns)
                for o in objs.values():
                    if o["uid"] in objects or o.get("name", "") == "":
                        continue
                    objects[o["uid"]] = Object(**o)
                obj.pop("connections")
            objects[obj["uid"]] = Object(**obj)

        return objects, connections

    def raw_response(self) -> dict:
        """Returns the 'data' from the raw graphql response."""
        return dict(**self)


def graph(query: str) -> GraphResponse:
    """Runs a `graph` query to the GraphQL API for Entanglement.

    This function executes a GraphQL query to the `graph` top level query in
    `Entanglement`. This enables your queries to return arbitrary subgraphs, by
    providing a single GraphQL query.

    Any query from the API can be specified and customer fragments can be added as well,
    but because the structure of the response depends on how the request is built. If the
    user wants to get usable Object/Connections back, the objectParts and connectionParts
    fragments should be used accordingly.

    When querying with GraphQL, the projects argument must be a list of project UIDs. The UID for
    a project can be found in the `uid` property of a project object.

    Args:
        query: a GraphQL query string

    Returns:
        a GraphResponse object that can access the raw response, a list of objects/connections,
        or a networkx graph.

    Examples:
        >>> res = graph('''
        {
            graph(projects: ["abc123"], search: "sentinel") {
                ...objectParts
                connections(predicate: "can-observe") {
                    ...connectionParts
                }
            }
        }
        ''')
    """
    if "graph(" not in query:
        raise ValueError("All calls to this function must include a request to the `graph` query")

    uses_object_parts_fragment = False
    uses_connection_parts_fragment = False
    # Add standard fragments to the query, if not present
    for key, fragment in FRAGMENTS.items():
        if f"...{key}" in query:
            if f"fragment {key} on" not in query:
                if key == "objectParts":
                    uses_object_parts_fragment = True
                if key == "connectionParts":
                    uses_connection_parts_fragment = True
                query = query + f"\n\n{fragment}"

    res = raise_on_error(graphql_client.post("query", json=dict(query=query)))
    return GraphResponse(
        uses_object_parts_fragment=uses_object_parts_fragment,
        uses_connection_parts_fragment=uses_connection_parts_fragment,
        **(res.json().get("data", {})),
    )


def _parse_connections(root: dict) -> List[Connection]:
    connections = []
    objects = {}

    conn_dicts = root.get("connections", [])
    for conn_dict in conn_dicts:
        sub = conn_dict["subject"]
        pred = conn_dict["predicate"]
        obj = conn_dict["object"]
        attrs = conn_dict["attributes"]

        objects[sub["uid"]] = sub
        objects[obj["uid"]] = obj
        if "connections" in sub:
            objs, conns = _parse_connections(sub)
            connections.extend(conns)
            objects.update(objs)
        if "connections" in obj:
            objs, conns = _parse_connections(obj)
            connections.extend(conns)
            objects.update(objs)

        if sub["uid"] == root["uid"]:
            sub = dict(**root)
            sub.pop("connections", None)
        if obj["uid"] == root["uid"]:
            obj = dict(**root)
            obj.pop("connections", None)

        conn = Connection(
            subject=_conn_object_parts(sub),
            predicate=Predicate(name=pred, **_conn_attrs_to_dict(attrs)),
            object=_conn_object_parts(obj),
        )

        connections.append(conn)

    return objects, connections


def _conn_attrs_to_dict(attrs: list) -> dict:
    attrs_dict = {}
    edge_attributes = {}
    for attr in attrs:
        if attr["key"] in ("domain", "category", "type"):
            attrs_dict[attr["key"]] = attr["value"]
        else:
            edge_attributes[attr["key"]] = attr["value"]
    attrs_dict["edge_attributes"] = edge_attributes
    return attrs_dict


def _conn_object_parts(o: dict) -> dict:
    obj = dict(
        uid=o["uid"],
        name=o["name"],
        object_class=o["class"],
    )
    domain = o.get("domain")
    category = o.get("category")
    type_ = o.get("type")

    if domain is not None:
        obj["domain"] = domain
    if category is not None:
        obj["category"] = category
    if type_ is not None:
        obj["type"] = type_

    return obj
