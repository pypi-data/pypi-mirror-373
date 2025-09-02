from geodesic.bases import _APIObject
from geodesic.descriptors import _StringDescr, _ListDescr


class AssetBands(_APIObject):
    """Specify and asset from a dataset as well as a list of bands."""

    asset = _StringDescr(doc="asset name to reference from the dataset")
    bands = _ListDescr(
        item_type=(str, int),
        doc="a list of band indices (0-indexed) or band names to reference",
    )
