import datetime
from typing import List, Union
import warnings
from dateutil.parser import isoparse
from geodesic.account.projects import _ProjectDescr
from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _BoolDescr,
    _DTypeDescr,
    _DatetimeDescr,
    _DatetimeIntervalDescr,
    _DictDescr,
    _FloatDescr,
    _IntDescr,
    _ListDescr,
    _RegexDescr,
    _StringDescr,
    _TupleDescr,
    _TypeConstrainedDescr,
    _URLDescr,
)
from geodesic.boson.dataset import Dataset, _DatasetDescr, _valid_resampling
from geodesic.stac import Item, Feature
from geodesic.utils import datetime_to_utc
from geodesic.boson import AssetBands
from geodesic.tesseract.regex import bin_size_re, _parse_container

__all__ = [
    "Container",
    "Step",
    "StepInput",
    "StepOutput",
    "Webhook",
    "Bucket",
    "Equal",
    "User",
    "TemporalBinning",
    "StridedBinning",
    "OutputBand",
    "OutputTimeBins",
    "ReduceMethod",
    "NearestSelection",
    "RangeSelection",
    "BinSelection",
    "TimeBinSelection",
    "Alert",
    "PixelsOptions",
]


resample_options = _valid_resampling + [s.upper() for s in _valid_resampling]


class Equal(_APIObject):
    """Temporal binning with equal bin size (either by count or size)."""

    bin_size = _RegexDescr(bin_size_re, doc="the bin size, in time units for each bin")
    bin_count = _IntDescr(doc="the count of bins to create")


class User(_APIObject):
    """Temporal binning by user specified bins."""

    omit_empty = _BoolDescr(doc="don't create a space for empty bins in resulting output")

    def __init__(self, **spec):
        self.omit_empty = False
        self._bins = None
        super().__init__(**spec)

    @property
    def bins(self):
        if self._bins is not None:
            return self._bins
        b = self.get("bins", [])
        if not isinstance(b, list):
            raise ValueError("bins must be a list of list of datetimes")
        out = []
        for d in b:
            if d is None:
                raise ValueError("bin cannot be None")
            dates = d
            try:
                out.append([datetime_to_utc(d) for d in map(isoparse, dates)])
            except Exception as e:
                raise e
        self._bins = out
        return out

    @bins.setter
    def bins(self, v: List[List[Union[datetime.datetime, str]]]):
        b = []
        for d in v:
            if len(d) != 2:
                raise ValueError("bins must be a list of pairs of start/end datetime bin edges")

            if isinstance(d[0], str):
                for dt in d:
                    try:
                        isoparse(dt)
                    except Exception as e:
                        raise ValueError(
                            "bin edges must be datetimes or parsable rfc3339 strings"
                        ) from e
                b.append(
                    [
                        datetime_to_utc(isoparse(d[0])).isoformat(),
                        datetime_to_utc(isoparse(d[1])).isoformat(),
                    ]
                )

            elif isinstance(d[0], datetime.datetime):
                b.append([datetime_to_utc(dt).isoformat() for dt in d])
        self._set_item("bins", b)


class TemporalBinning(_APIObject):
    """Temporal binning is a class to represent the temporal binning in a series request.

    Args:
        spec(dict): The dict to initialize the class with.
    """

    equal = _TypeConstrainedDescr((Equal, dict), doc="specify Equal time binning")
    user = _TypeConstrainedDescr((User, dict), doc="specify time bins defined by User time binning")
    reference = _StringDescr(doc="reference the time bins to another asset in the Job")


class Webhook(_APIObject):
    """A webhook triggered on completion of a step in a Tesseract Job.

    NotImplemented

    A future version of Tesseract will allow webhooks when a job step has completed, which will POST
    information to a url with specified headers and credentials
    """

    url = _URLDescr(doc="url")
    headers = _DictDescr(
        doc="dictionary with string keys to string values headers to pass along: {'key': 'value'}"
    )
    credentials = _StringDescr(doc="name of the credential to use (geodesic.accounts.Credential)")


class Container(_APIObject):
    """A container that runs arbitrary code to execute a model.

    Containers can be on any image repository that docker can pull from. The container must have
    been built using the Tesseract Python SDK in order to run in Tesseract. If containers are stored
    in a private repository you must provide the pull secret to use. This needs to be a
    :class:`Credential<geodesic.account.credentials.Credential>` stored in the Geodesic platform.

    Example:
        >>> Container(
        ...    repository="docker.io",
        ...    image="seerai/my-model",
        ...    tag="latest",
        ...    pull_secret_credential="my-credential",
        ...    args={"model_arg": "argument"},
        ... )

    """

    repository = _StringDescr(doc="the docker repository to pull from", default="docker.io")
    image = _StringDescr(doc="the name of the image to use")
    tag = _StringDescr(doc="the tag of the image to use")
    pull_secret_credential = _StringDescr(doc="name of the credential to use to pull the container")
    args = _DictDescr(doc="additional arguments to pass to the inference function")


class BinSelection(_APIObject):
    """Selection of a time bin based on a datetime or index."""

    # reference asset - which time bins it'll draw from (StepOutput only)
    reference_asset = _StringDescr(doc="which asset to reference the time bins. For step outputs")

    datetime = _DatetimeDescr(doc="datetime to use for selection")
    index = _IntDescr(doc="datetime to use for selection")


class StridedBinning(_APIObject):
    """Create output time bins based on a from, duration, stride, offset, and count.

    This allows you to create a time binning with equal sized bins, but with a stride between each
    bin.  Any data whose datetimes falls into a bin will be aggregated into that bin. Everything
    else is ignored in the output dataset.

    Args:
        from_selection(:class:`BinSelection`): from where the bins begin.
        from_end(bool): use the right end of the bin if True
        duration(str): the bin size. Must be a string with a date duration (e.g. 1D, 1h, 1m, 1s)
        stride(str): the stride (step forward) between each the left edge of each bin. Must be a
            string with a date duration (e.g. 1D, 1h, 1m, 1s)
        count(int): how many bins to create
        offset(str): the offset from the first date to start the bins. Must be a string with a date
            duration (e.g. 1D, 1h, 1m, 1s)

    .. seealso:: :func:`create_strided_binning<geodesic.tesseract.utils.create_strided_binning>`
    """

    from_selection = _TypeConstrainedDescr(
        (BinSelection, dict),
        coerce=True,
        dict_name="from",
        doc="When to start the strided binning. \n" + BinSelection.__doc__,
    )
    from_end = _BoolDescr(doc="use the right end of the bin if True")
    duration = _RegexDescr(bin_size_re, doc="the bin size, in time units for each bin")
    stride = _RegexDescr(
        bin_size_re, doc="the stride (step forward), in time units between each bin"
    )
    count = _IntDescr(doc="how many bins")
    offset = _RegexDescr(bin_size_re, doc="the offset from the first date to start the bins")

    def __init__(
        self,
        from_selection=BinSelection(),
        from_end=False,
        duration=None,
        stride=None,
        count=None,
        offset=None,
        **kwargs,
    ):
        from_ = kwargs.pop("from", None)
        if from_ is not None:
            self.from_selection = from_
        else:
            self.from_selection = from_selection
        self.from_end = from_end
        self.duration = duration
        self.stride = stride
        if offset is None:
            offset = stride
        self.offset = offset
        self.count = count


class RangeSelection(_APIObject):
    """Selection of bins between a start and an end."""

    from_index = _IntDescr(dict_name="from", doc="starting point of bin selection in a range")
    to_index = _IntDescr(dict_name="to", doc="ending point of bin selection in a range")

    def __init__(self, from_index=None, to_index=None, **kwargs):
        from_ = kwargs.pop("from", None)
        to = kwargs.pop("to", None)
        if from_ is not None:
            self.from_index = from_
        else:
            self.from_index = from_index
        if to is not None:
            self.to_index = to
        else:
            self.to_index = to_index


class NearestSelection(_APIObject):
    """Selection of the nearest bin to a specified before/after point."""

    before = _DatetimeDescr(doc="select the nearest bin BEFORE this value")
    after = _DatetimeDescr(doc="select the nearest bin AFTER this value")


class ReduceMethod(_APIObject):
    """Reduce along time bin dimension into a single bin."""

    op = _StringDescr(
        one_of=["min", "max", "mean", "sum", "first", "last"],
        doc="reduction operation on time bins",
    )


class TimeBinSelection(_APIObject):
    """A description of which time bins to select from the input."""

    # Only one of the following can be set
    all = _BoolDescr(doc="select all time bins from input")
    index = _IntDescr(doc="the index of the time bin to select")
    since = _TypeConstrainedDescr(
        (BinSelection, dict), coerce=True, doc="select all bins since this selection"
    )
    until = _TypeConstrainedDescr(
        (BinSelection, dict), coerce=True, doc="select all bins before this selection"
    )
    range = _TypeConstrainedDescr(
        (RangeSelection, dict), coerce=True, doc="selection all bins in a range"
    )
    nearest = _TypeConstrainedDescr(
        (NearestSelection, dict), coerce=True, doc="select the nearest time bin"
    )

    # Reduce along time dimension with this operation
    reduce = _TypeConstrainedDescr(
        (ReduceMethod, dict),
        coerce=True,
        doc="reduce along time dimension before sending"
        " to model. This will send a single time bin (NOT IMPLEMENTED)",
        optional=True,
    )


class OutputBand(_APIObject):
    """An output bin, either a name or STAC eo band."""

    band_name = _StringDescr(doc="the name of the bin")
    eo_band = _DictDescr(doc="an eo:band object of information about this band")


class OutputTimeBins(_APIObject):
    """How to define what the output time bins are for a step output."""

    nontemporal = _BoolDescr(doc="nontemporal; there will only be one single bin created")
    user = _TypeConstrainedDescr((User, dict), coerce=True, doc="user defined bin edges")
    strided = _TypeConstrainedDescr(
        (StridedBinning, dict),
        coerce=True,
        doc="build bins by defining a from, duration," " stride, offset, and count",
    )
    equal = _TypeConstrainedDescr(
        (Equal, dict),
        coerce=True,
        doc="equal sized bins between the start and end datetime",
    )
    reference = _StringDescr(
        doc="references the asset from which this asset should use the time bins."
    )


class FeatureAggregation(_APIObject):
    """FeatureAggregation specifies how features should be handled while rasterizing."""

    value = _TypeConstrainedDescr((str, float, int, complex))
    aggregation_rules = _ListDescr(item_type=str)
    groups = _ListDescr(item_type=dict)


class PixelsOptions(_APIObject):
    shape = _TupleDescr(
        doc="the shape of the output for this asset (rows, columns)",
        min_len=2,
        max_len=2,
    )
    pixel_size = _TupleDescr(
        doc="the size of each pixel in the output SRS (x, y)", min_len=2, max_len=2
    )
    resample = _StringDescr(
        one_of=resample_options,
        doc=f"resampling method to use, one of {', '.join(resample_options)}",
    )
    defer_search = _BoolDescr(
        doc="if set to True, Tesseract won't check if the data exists at this tile and instead"
        " use Boson directly to obtain the pixel data. (default: False"
    )
    order_by = _StringDescr(
        doc="order by a field in the inputs because mosaicing/reducing the outputs"
    )
    reduce = _TypeConstrainedDescr(
        (ReduceMethod, dict),
        doc="if multiple images are used for input, `reduce` specifies"
        " how to aggregate. If this is empty, all are mosaiced in"
        " order.",
    )


class MultiscaleOptions(_APIObject):
    min_zoom = _IntDescr(doc="minimum zoom level to create for multiscales")


class RasterizeOptions(_APIObject):
    shape = _TupleDescr(
        doc="the shape of the output for this asset (rows, columns)",
        min_len=2,
        max_len=2,
    )
    pixel_size = _TupleDescr(
        doc="the size of each pixel in the output SRS (x, y)", min_len=2, max_len=2
    )
    value = _TypeConstrainedDescr((str, float, int, complex))
    aggregation_rules = _ListDescr(item_type=str)
    groups = _ListDescr(item_type=dict)
    defer_search = _BoolDescr(
        doc="if set to True, Tesseract won't check if the data exists at this tile and instead"
        " use Boson directly to obtain the feature data to rasterize. (default: False"
    )


class StepInput(_APIObject):
    """An input for a processing step."""

    asset_name = _StringDescr(
        doc="name of the asset from a previous `StepOutput` to use as input for this `Step`"
    )
    spatial_chunk_shape = _TupleDescr(
        doc="the shape of each chunk of input for this step in row/column space"
    )
    type = _RegexDescr(r"((?:tensor)|(?:features)|(?:records))", doc="the type of input")
    overlap = _IntDescr(doc="number of pixels of overlap to apply when tiling the inputs")
    bands = _ListDescr(
        item_type=(int, float),
        coerce_items=True,
        doc="band index/ID of the bands to select from input",
    )
    time_bin_selection = _TypeConstrainedDescr(
        (TimeBinSelection, dict),
        coerce=True,
        doc="which time bins should be" " selected from the input",
    )
    asset_bands = _ListDescr(
        item_type=(AssetBands, dict),
        coerce_items=True,
        doc="a list of `AssetBand` objects",
    )
    dataset_project = _ProjectDescr(
        doc="the project that the step's input belongs to. This will be set automatically"
        " when setting the dataset"
    )
    dataset = _DatasetDescr(
        project=dataset_project,
        doc="the Dataset that will be used in this step. This may only be"
        " only used if `asset_name` is empty.",
    )
    no_data = _ListDescr(
        item_type=(int, float, complex, str),
        doc="set the value to be ignored and treated as no data in the output",
    )
    ids = _ListDescr(
        item_type=(int, str),
        doc="list of item IDs to be used to query from the specified dataset",
    )
    datetime = _DatetimeIntervalDescr(
        doc="the datetime interval to be used to query for matching data"
    )
    filter = _DictDescr(
        doc="a dictionary representing a JSON CQL2 filter as defined by the OGC spec: "
        "https://github.com/opengeospatial/ogcapi-features/tree/master/cql2"
    )
    stac_items = _ListDescr(
        item_type=(dict, Feature, Item),
        doc="a list of OGC/STAC features/items to use in lieu" " of a query",
        dict_name="items",
    )
    page_size = _IntDescr(
        doc="the number of items to return per page when querying for items in ``model`` or "
        "``create_assets`` steps"
    )


class StepOutput(_APIObject):
    """An output for a processing step."""

    asset_name = _StringDescr(doc="name of an asset this step emits")
    type = _RegexDescr(r"((?:tensor)|(?:features)|(?:records))", doc="the type of output")
    chunk_shape = _TupleDescr(
        doc="the shape of the output from this asset from the container. Even if the container"
        "performs a reduction, please specify the full dimensions in the order (time, band/feature,"
        "rows, columns). (1, 1, 1, 1) for scaler output",
        min_len=4,
        max_len=4,
    )
    pixel_dtype = _DTypeDescr(doc="the dtype of this ouptut asset")
    fill_value = _TypeConstrainedDescr(
        (int, float, str, complex), doc="the fill value for this output asset"
    )
    trim = _IntDescr(
        doc="the number of border pixels to remove from output of the model. This typically"
        " should match the overlap in the step input, but for cases like models that upsample"
        " (e.g. superresolution), this should trim off a different value."
    )
    output_time_bins = _TypeConstrainedDescr(
        (OutputTimeBins, dict), coerce=True, doc="how to generate output time bins"
    )
    output_bands = _ListDescr(
        item_type=(OutputBand, dict, str),
        coerce_items=False,
        doc="band names or STAC " "eo:band objects",
    )
    compression = _StringDescr(
        one_of=["zlib", "blosc", "none"],
        doc="the compression algorithm for output data",
    )
    chip_size = _IntDescr(
        default=512, doc="size of the chips to break work into (default=512, max=2048)"
    )
    pixels_options = _TypeConstrainedDescr(
        (PixelsOptions, dict),
        coerce=True,
        doc="options that will be used to"
        " warp/reproject/resample a raster dataset into a specific grid/spatial"
        " reference before processing. If you are working with raster data from an"
        " input `Dataset`, this must be specified",
    )
    rasterize_options = _TypeConstrainedDescr(
        (RasterizeOptions, dict),
        coerce=True,
        doc="options that will be used to"
        " rasterize a vector dataset into a specific grid/spatial"
        " reference before processing. If you are working with feature data from"
        " an input `Dataset`, this must be specified",
    )
    multiscale_options = _TypeConstrainedDescr(
        (MultiscaleOptions, dict),
        coerce=True,
        doc="options used when creating multiscales for a particular asset",
    )


class Step(_APIObject):
    """A step in a Tesseract Job.

    NotImplemented
    """

    name = _StringDescr(doc="the name of this step")
    type = _StringDescr(doc="the type of this step (model, rechunk)")
    inputs = _ListDescr(
        item_type=(StepInput, dict),
        doc="a list of inputs for this step",
        coerce_items=True,
    )
    outputs = _ListDescr(
        item_type=(StepOutput, dict),
        doc="a list of outputs for this step",
        coerce_items=True,
    )
    container = _TypeConstrainedDescr((Container, dict))
    gpu = _BoolDescr(doc="make the step run on a machine with GPU resources", default=False)
    workers = _IntDescr(doc="number of workers to run for this step")
    feature_tiles = _IntDescr(doc="number of tiles to break feature datasets into")


class Bucket(_APIObject):
    url = _StringDescr(
        doc="a storage URL, (e.g. s3://bucket/prefix or gs://bucket/prefix). If this is specified,"
        " you do not need to specify prefix, platform, bucket, region, account or domain"
    )
    prefix = _StringDescr(doc="all output will be written to this prefix")
    platform = _StringDescr(doc="the platform for this bucket (aws, gcp, azure)")
    bucket = _StringDescr(doc="name of the bucket or container")
    region = _StringDescr(doc="storage region (AWS)")
    credentials = _StringDescr(doc="credentials to access this bucket")
    account = _StringDescr(doc="the azure storage account name (e.g. storageaccount)")
    domain = _StringDescr(doc="the azure storage domain (e.g. us.core.windows.net)")
    requester_pays = _BoolDescr(doc="requester pays to access bucket", default=False)


class Alert(_APIObject):
    title = _StringDescr(doc="short description of the alert")
    detail = _StringDescr(doc="detailed description of the alert")
    severity = _StringDescr(doc="severity of the alert", default="LOW")

    def warn(self):
        warnings.warn(f"{self.title} (severity={self.severity}): {self.detail}")


class JobResponse(_APIObject):
    job_id = _StringDescr(doc="id of the submitted Tesseract Job")
    dataset = _TypeConstrainedDescr(
        (Dataset, dict), doc="the generated dataset from this job", coerce=True
    )
    item = _TypeConstrainedDescr(
        (Item, Feature, dict), doc="STAC Item for this job's output", coerce=True
    )
    n_quarks = _IntDescr(doc="nubmer of quarks produced")
    n_steps = _IntDescr(doc="nubmer of steps in this job")
    n_edges = _IntDescr(doc="number of edges in the graph")
    avg_quark_size_bytes = _FloatDescr(doc="average size of a quark, in bytes")
    alerts = _ListDescr(
        item_type=(Alert, dict),
        doc="any alerts returned while planning the job",
        coerce_items=True,
    )

    def warn(self):
        """Shows all alerts that came from this job as Python warnings."""
        for alert in self.alerts:
            alert.warn()


def parse_container(ref: str) -> Container:
    """Parses a container image string into it's constituents.

    This function takes a string of the form:

    [[host[:port]/[registry/]component[:tag][@digest]

    which we parse into:
    - repository = host:port
    - image = component
    - tag = tag@digest

    and return a Container object. This function isn't exhaustive, so if
    you run into parsing errors, but know your url is correct, directly
    instatiate a Container instead.

    Args:
        ref: the container URL to be parsed

    Returns:
        a Container object for that URL

    Raises:
        a ``ValueError`` in case of a parse error.
    """
    match = _parse_container(ref)
    repo = match.get("repo")
    if repo is None or repo == "":
        repo = "docker.io"

    image = match.get("image")
    if image is None:
        raise ValueError(f"invalid image ref '{ref}'")

    tag = match.get("tag")
    if tag is None:
        tag = "latest"

    image_split = image.split("/")
    prefix = []
    if len(image_split) > 1:
        prefix = image_split[:-1]
    repo = "/".join([repo] + prefix)
    image = image_split[-1]

    return Container(repo=repo, image=image, tag=tag)
