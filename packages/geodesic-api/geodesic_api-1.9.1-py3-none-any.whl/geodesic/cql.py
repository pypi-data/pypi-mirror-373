from typing import Tuple, Any
from geodesic.bases import _APIObject
from geodesic.descriptors import _StringDescr, _ListDescr


# Most of the CQL2 operations. We support many of these, but they can be passed through to
# 3rd party providers that support ones our system currently doesn't.
# https://github.com/opengeospatial/ogcapi-features/blob/master/cql2/standard/schema/cql2.yml
_binary_comparison_predicates = ["=", "<", ">", "<=", ">=", "<>"]
_and_or_predicates = ["and", "or"]
_not_predicate = ["not"]
_comparison_predicates = ["like", "between", "in", "isNull"]
_spatial_predicates = [
    "s_contains",
    "s_crosses",
    "s_disjoint",
    "s_equals",
    "s_intersects",
    "s_overlaps",
    "s_touches",
    "s_within",
]
_temporal_predicates = [
    "t_after",
    "t_before",
    "t_contains",
    "t_disjoint",
    "t_during",
    "t_equals",
    "t_finishedBy",
    "t_finishes",
    "t_intersects",
    "t_meets",
    "t_metBy",
    "t_overlappedBy",
    "t_overlaps",
    "t_startedBy",
    "t_starts",
]
_array_predicates = ["a_containedBy", "a_contains", "a_equals", "a_overlaps"]
ops = (
    _binary_comparison_predicates
    + _and_or_predicates
    + _not_predicate
    + _comparison_predicates
    + _spatial_predicates
    + _temporal_predicates
    + _array_predicates
)


class CQLFilter(_APIObject):
    """Represents an OGC CQL2 Filter.

    The CQL2 standard is documented on the OGC's github repo for the OGC API Features:
    https://github.com/opengeospatial/ogcapi-features/blob/master/cql2/standard/schema

    CQL2 is a way to filter tabular datasets such as features and STAC items. In Geodesic,
    we use CQL2 as the universal filtering language and it's converted internally to the needed
    filtering format.

    CQLFilter has only two keyword arguments, op and args, described below.

    Args:
        op: the name/id for the operation
        args: a list of arguments for that operation

    Filters can be composed of multiple filters using the and/or ops.

    Examples:
        >>> from geodesic.cql import CQLFilter as C
        >>> # filter a dataset for all items that have a value of "ASCENDING" for the field "properties.orbit"
        >>> filter = C.eq("properties.orbit", "ASCENDING")

        >>> # filter a dataset for all items that have a value of "ASCENDING" for the field "properties.orbit"
        >>> # and a value of "properties.angle" of less than 45.0
        >>> filter = C.and(C.eq("properties.orbit", "ASCENDING"), C.lt("properties.angle", 45.0))

        >>> # Directly create a CQLFilter using CQL syntax. This is for items with a field "a" and a value equal to "b"
        >>> from geodesic.cql import CQLFilter
        >>> filter = CQLFilter(op="=", args=[{"property": "a"}, "b"])

    """  # noqa

    op = _StringDescr(one_of=ops, doc="the operation this filter implements")
    args = _ListDescr(doc="arguments to this operation")

    # Can only set op/args in this as a dictionary, everything else is invalid.
    _limit_setitem = ["op", "args"]

    @staticmethod
    def eq(property: str, value: Any) -> "CQLFilter":
        """Filter on equality between a property and a value."""
        return _binary_op(property, value, "=")

    @staticmethod
    def neq(property: str, value: Any) -> "CQLFilter":
        """Filter on no equality between a property and a value."""
        return _binary_op(property, value, "<>")

    @staticmethod
    def gt(property: str, value: Any) -> "CQLFilter":
        """Filter that a property is greater than a value."""
        return _binary_op(property, value, ">")

    @staticmethod
    def gte(property: str, value: Any) -> "CQLFilter":
        """Filter that a property is greater than or equal to a value."""
        return _binary_op(property, value, ">=")

    @staticmethod
    def lt(property: str, value: Any) -> "CQLFilter":
        """Filter that a property is less than a value."""
        return _binary_op(property, value, "<")

    @staticmethod
    def lte(property: str, value: Any) -> "CQLFilter":
        """Filter that a property is less than or equal to a value."""
        return _binary_op(property, value, "<=")

    @staticmethod
    def logical_and(*args: Tuple["CQLFilter"]) -> "CQLFilter":
        """Filter that combines multiple filters with a logical and."""
        return CQLFilter(op="and", args=[CQLFilter(**x) for x in args])

    @staticmethod
    def logical_or(*args: Tuple["CQLFilter"]) -> "CQLFilter":
        """Filter that combines multiple filters with a logical or."""
        return CQLFilter(op="or", args=[CQLFilter(**x) for x in args])

    @staticmethod
    def logical_not(filter: "CQLFilter") -> "CQLFilter":
        """Filter that negates another filter."""
        return CQLFilter(op="not", args=[CQLFilter(**filter)])

    @staticmethod
    def like(property: str, value: str) -> "CQLFilter":
        """Filter that checks for text similarity."""
        return _binary_op(property, value, "like")

    @staticmethod
    def isin(property: str, value: list) -> "CQLFilter":
        """Filter that checks for items in an array/list."""
        return _binary_op(property, value, "in")

    @staticmethod
    def isnull(property: str) -> "CQLFilter":
        """Filter that checks that a field is null."""
        return CQLFilter(op="isNull", args=[_prop(property)])

    @staticmethod
    def between(property: str, a: Any, b: Any) -> "CQLFilter":
        """Filter that checks that a property is between two values."""
        return CQLFilter(op="between", args=[_prop(property), a, b])


def _binary_op(property: str, value: Any, op: str) -> CQLFilter:
    return CQLFilter(op=op, args=[_prop(property), value])


def _prop(property: str) -> dict:
    return {"property": property}
