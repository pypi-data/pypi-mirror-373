import time
import warnings
from typing import TYPE_CHECKING, Optional, Union, List, Tuple, Literal

import numpy as np
from geodesic.account.projects import _ProjectDescr, get_active_project, get_project
from geodesic.descriptors import (
    _BBoxDescr,
    _GeometryDescr,
    _IntDescr,
    _ListDescr,
    _StringDescr,
    _TypeConstrainedDescr,
)
from geodesic.service import RequestsServiceClient
from geodesic.tesseract.components import (
    JobResponse,
    Step,
    Bucket,
    Webhook,
    StepInput,
    StepOutput,
    Container,
    Alert,
    MultiscaleOptions,
    parse_container,
)
from geodesic.tesseract.regex import job_id_re
from geodesic.utils import DeferredImport, MockImport, hamming_distance
from geodesic.bases import _APIObject
from geodesic.client import raise_on_error
from geodesic import Dataset
from geodesic.stac import FeatureCollection, Item, Feature

if TYPE_CHECKING:
    import datetime
    from geodesic.account import Project
    from geodesic.tesseract import (
        AssetBands,
        OutputTimeBins,
        PixelsOptions,
        RasterizeOptions,
    )
    from shapely.geometry import (
        Point,
        Polygon,
        LineString,
        MultiPolygon,
        MultiLineString,
        MultiPoint,
    )

    Geometry = Union[
        str, dict, Point, Polygon, LineString, MultiPolygon, MultiLineString, MultiPoint
    ]

tqdm = DeferredImport("tqdm")
ipywidgets = DeferredImport("ipywidgets")
ipyleaflet = DeferredImport("ipyleaflet")
mapping = DeferredImport("geodesic.mapping")
display = DeferredImport("IPython.display")

try:
    import networkx as nx
except ImportError:
    warnings.warn(
        "networkx is not installed. topological checks on tesseract jobs will not be performed"
    )
    nx = None

try:
    import zarr
except ImportError:
    zarr = MockImport("zarr")

tesseract_client = RequestsServiceClient("tesseract", version=1)


def list_jobs(
    search: str = None,
    project=None,
    status: Literal["completed", "running", "deleted", "all"] = "all",
) -> "JobList":
    """Depreciated function, use `get_jobs()` instead."""
    warnings.warn(
        "list_jobs() is depreciated and will be removed in v1.0.0, use get_jobs() instead",
        UserWarning,
    )
    return get_jobs(search=search, project=project, status=status)


def get_jobs(
    search: str = None,
    project=None,
    status: Literal["completed", "running", "deleted", "all"] = "all",
) -> "JobList":
    """Returns a list of Tesseract Jobs.

    Args:
        search: a search string used to search within the jobs name, alias or description.
        This will do simple partial string matching.
        project: the name of the project to search jobs. Defaults to the current active project.
        status: return only jobs that have this status. this can be 'completed, 'running',
        'deleted', or 'all' (default) to return jobs in any state.

    Returns:
        a :class:`JobList` of matching Jobs

    Example:
        To list Tesseract jobs related to Hurricane Ida we could run the `list_jobs()` function
        like so:

        >>> jobs = list_jobs(
        ...    search="ida",
        ...    project="ida-demo",
        ...    status="completed"
        ... )
        >>> jobs[0].alias
            "Ida Road Model"

    """
    if project is None:
        project = get_active_project()
    else:
        if isinstance(project, str):
            project = get_project(project)
        elif not isinstance(project, Project):
            raise ValueError("project must be string or Project")

    if status.lower() not in ["completed", "running", "deleted", "all"]:
        raise ValueError("status must be one of ['completed', 'running', 'deleted', 'all']")

    params = {}

    if search is not None:
        params["search"] = search

    params["project"] = project.uid

    resp = tesseract_client.get("jobs", params=params)
    raise_on_error(resp)

    js = resp.json()
    try:
        if js["jobs"] is None:
            return JobList([])
    except KeyError:
        if js == {}:
            return JobList([])

    jl = []
    for j in js["jobs"]:
        try:
            jl.append(Job(**j))
        except Exception as e:
            warnings.warn(f"Failed to create job from json {j} \nexception: {e}")
    jobs = JobList(jl)
    if status.lower() == "all":
        return jobs

    # Since there isnt a way to filter serverside by state we need
    # to check each of the return jobs and remove ones that dont match.
    filtered_jobs = {}
    for name, job in jobs.items():
        st = job.status()["state"]
        if st == status.lower():
            filtered_jobs[name] = job

    return filtered_jobs


class Job(_APIObject):
    r"""represents a Tesseract Job.

    The class can be initialized either with a dictionary (\\*\\*spec) that represents the request
    for the particular
    type, or can be given an job ID. If a job ID is provided it will query for that job on the
    tesseract service
    and then update this class with the specifics of that job.

    Args:
        \\*\\*spec: A dictionary representing the job request.
        job_id: The job ID string. If provided the job will be initialized
            with info by making a request to tesseract.
    """

    name = _StringDescr(doc="a unique name for the dataset created by this job.")
    alias = _StringDescr(doc="a human readable name for the dataset created by this job")
    description = _StringDescr(doc="a longer description for the dataset created by this job")
    project = _ProjectDescr(doc="the project that this job will be assigned to")
    workers = _IntDescr(doc="the number of workers to use for this job")
    bbox = _BBoxDescr(
        doc="the rectangular extent of this job. Can be further filtered by a geometry"
    )
    bbox_epsg = _IntDescr(doc="the EPSG code of the bounding box spatial reference.")
    output_epsg = _IntDescr(
        doc="the EPSG code of the output spatial reference.\
            Pixel size will be with respect to this."
    )
    geometry = _GeometryDescr(
        doc="A geometry to filter the job with only assets intersecting this will be processed. \
            Inputs can be WKT, WKB, GeoJSON, or a anything that implements a __geo_interface__"
    )
    workers = _IntDescr(
        doc="Number of workers to use for each step in the job.\
            Can also be specified on each step individually."
    )
    steps = _ListDescr(
        item_type=(Step, dict),
        doc="A list of steps to execute",
        coerce_items=True,
    )
    hooks = _ListDescr(
        item_type=(Webhook, dict),
        doc="NOT YET IMPLEMENTED. A list of webhooks to execute when job is complete",
    )
    output = _TypeConstrainedDescr(
        (Bucket, dict),
        doc="the output, other than default storage",
    )

    def __init__(
        self,
        name: str = None,
        bbox: Tuple[float, float, float, float] = None,
        geometry: "Geometry" = None,
        alias: str = None,
        description: str = None,
        bbox_epsg: int = 4326,
        output_epsg: int = 3857,
        output: Union[Bucket, str] = None,
        job_id: str = None,
        **spec,
    ):
        self._service = tesseract_client
        self.project = get_active_project()

        self._submitted = False
        self._dataset = None
        self._item = None
        self._bounds = None
        self._widget = None

        # status values
        self._state = None
        self._n_quarks = None
        self._n_completed = None

        # geometries
        self._query_geom = None
        self._quark_geoms = None
        self.job_id = None

        if job_id is not None and len(spec) == 0:
            self.load(job_id=job_id)
            super().__init__()
            return

        spec["name"] = name

        if bbox is None and geometry is None:
            raise ValueError("must specify either bbox or geometry")

        if bbox is not None:
            spec["bbox"] = bbox
        spec["bbox_epsg"] = bbox_epsg
        spec["output_epsg"] = output_epsg
        if geometry is not None:
            spec["geometry"] = geometry
        if alias is not None:
            spec["alias"] = alias
        if description is not None:
            spec["description"] = description
        if output is not None:
            if isinstance(output, str):
                output = Bucket(output)
            spec["output"] = output

        super().__init__(**spec)

    def load(self, job_id: str, dry_run: bool = False) -> None:
        """Loads job information for `job_id` if the job exists.

        Args:
            job_id (str): The job ID to load
            dry_run (bool): If True, only loads the job information, not the dataset or item.
        """
        job_resp = raise_on_error(
            self._service.get(f"jobs/{job_id}", params=dict(project=self.project.uid))
        ).json()
        if "jobs" not in job_resp or len(job_resp["jobs"]) == 0:
            raise ValueError(f"job '{job_id}' not found in project '{self.project.uid}'")

        self.update(job_resp["jobs"][0])
        self.job_id = job_resp["jobs"][0].get("job_id", job_id)

        if dry_run:
            return

        # If this isn't a dry run, load the other data.
        ds = raise_on_error(
            self._service.get(f"jobs/{job_id}/dataset", params=dict(project=self.project.uid))
        ).json()
        self._dataset = Dataset(**ds)
        si = raise_on_error(
            self._service.get(f"jobs/{job_id}/item", params=dict(project=self.project.uid))
        ).json()
        self._item = Item(**si)
        self._query_geom = getattr(self._item, "geometry", None)
        self.status(return_quark_geoms=True)

    def submit(
        self,
        overwrite: bool = False,
        dry_run: bool = False,
        timeout_seconds: float = 30.0,
    ) -> JobResponse:
        """Submits a job to be processed by tesseract.

        This function will take the job defined by this class and submit it to the tesseract api for
        processing.
        Once submitted the dataset and items fields will be populated containing the SeerAI dataset
        and STAC item
        respectively. Keep in mind that even though the links to files in the STAC item will be
        populated, the job
        may not yet be completed and so some of the chunks may not be finished.

        Args:
            overwrite: if the job exists, deletes it and creates a new one
            dry_run: runs this as a dry run (no work submitted, only estimated.)
            timeout_seconds: how long to wait for the job to be submitted before timing out.
        """
        # If this job has a job_id, delete the existing job
        if self.job_id is not None:
            if overwrite:
                self.delete_and_wait()
            else:
                self.status()
                # If the current job state is "dry_run" and we're submitting a non-dry run, delete
                # the job and wait.
                if self.state == "dry_run" and not dry_run:
                    self.delete_and_wait(timeout_seconds=timeout_seconds)
                else:
                    self.load(self.job_id, dry_run=self.state == "dry_run")
                    return

        req = dict(self)
        req["dry_run"] = dry_run

        # submit the job
        response = self._service.post("submit", json=req)

        res = response.json()
        # If there's an error, get the job ID from that error
        if "error" in res:
            detail = res["error"].get("detail", "")
            job_id_match = job_id_re.search(detail)
            # If the job already exists and we don't already have the job_id set,
            # get and set the job_id
            if "exists" in detail and job_id_match and self.job_id is None:
                job_id = job_id_match.group(1)
                self.job_id = job_id

                # Recursively call this, now that we have the job_id
                return self.submit(
                    overwrite=overwrite,
                    dry_run=dry_run,
                    timeout_seconds=timeout_seconds,
                )
            else:
                raise_on_error(response)

        res = JobResponse(**res)

        job_id = res.get("job_id", None)
        if job_id is None:
            raise ValueError("no job_id was returned, something went wrong")

        self.job_id = job_id
        self.load(job_id, dry_run=dry_run)
        self._submitted = True

        res.warn()
        return res

    def delete_and_wait(self, timeout_seconds=30.0):
        self.delete(remove_data=True)
        timeout = time.time() + timeout_seconds
        timed_out = True
        while time.time() < timeout:
            self.status()
            if self._state == "deleted":
                timed_out = False
                break
            time.sleep(1.0)
        if timed_out:
            raise ValueError(
                "Job submission timed out waiting for deletion to complete. Job is still deleting,"
                " please try again later"
            )

    @property
    def dataset(self):
        return self._dataset

    @property
    def item(self):
        return self._item

    @property
    def state(self):
        return self._state

    def zarr(self, asset_name: str = None):
        """Returns the Zarr group for the corresponding asset name.

        Args:
            asset_name: name of the asset to open and return
        Returns:
            zarr file pointing to the results.
        """
        if self._item is None or self._n_completed != self._n_quarks:
            raise ValueError("computation not completed")

        try:
            assets = self._item.assets
        except AttributeError:
            raise AttributeError("item has no assets")

        try:
            asset = assets[asset_name]
        except KeyError:
            raise KeyError(f"asset {asset_name} does not exist")

        href = asset.href

        return zarr.open(href)

    def ndarray(self, asset_name: str):
        """Returns a numpy.ndarray for specified asset name.

        USE WITH CAUTION! RETURNS ALL OF WHAT COULD BE A
        HUGE ARRAY

        Args:
            asset_name: name of the asset to open and return
        Returns:
            numpy array of all the results.
        """
        return self.zarr(asset_name)["tesseract"][:]

    def status(
        self,
        return_quark_geoms: bool = False,
        return_quark_status: bool = False,
        return_alerts: bool = False,
        warn: bool = False,
    ):
        """Status queries the tesseract service for the jobs status.

        Args:
            return_quark_geoms(bool): Should the query to the service ask for all of the
                quarks geometries. If True it will populate the geometry in this class.
            return_quark_status(bool): If True will query for the status of each individual quark
                associated with the job.
            return_alerts(bool): If True, will return all alerts (planning errors, warnings, etc)
                for the job.
            warn(bool): If any alerts are returned, warns the user with a Python warning

        Returns:
            A dictionary with the response from the Tesseract service

        """
        if not self.job_id:
            raise Exception("job_id not set, cannot get status")

        q = {
            "return_quark_geoms": return_quark_geoms,
            "return_quark_status": return_quark_status,
            "return_alerts": return_alerts,
            "project": self.project.uid,
        }
        res = raise_on_error(self._service.get(f"jobs/{self.job_id}/status", params=q)).json()

        status = res.get("job_status", None)
        if status is None:
            print(res)
            raise Exception("could not get job status")

        self._n_quarks = status.get("n_quarks", None)
        self._n_completed = status.get("n_quarks_completed", 0)
        self._state = status.get("state", None)

        if return_quark_geoms:
            quark_geoms = status.get("features", None)
            if quark_geoms is None:
                raise Exception("job status returned no geometries")
            self.quark_geoms = FeatureCollection(**quark_geoms)

        self._status = status

        self.alerts = [Alert(**w) for w in status.get("alerts", [])]
        if warn:
            for alert in self.alerts:
                alert.warn()

        return status

    def add_create_assets_step(
        self,
        *,
        asset_name: str,
        name: str = None,
        workers: int = 1,
        dataset: Optional[Union["Dataset", str]] = None,
        dataset_project: Optional[Union["Project", str]] = None,
        stac_items: Optional[List[Union[dict, "Feature", "Item"]]] = None,
        asset_bands: Optional[List[Union["AssetBands", dict]]] = None,
        output_time_bins: Optional[Union["OutputTimeBins", dict]] = None,
        pixels_options: Optional[Union["PixelsOptions", dict]] = None,
        rasterize_options: Optional[Union["RasterizeOptions", dict]] = None,
        no_data: Optional[List[Union[int, float, complex, str]]] = None,
        pixel_dtype: Optional[Union[str, np.dtype]] = None,
        fill_value: Optional[Union[str, int, float, complex]] = None,
        ids: Optional[List[str]] = None,
        filter: Optional[dict] = None,
        datetime: Optional[Union[Tuple[Union["datetime.datetime", str]], str]] = None,
        chip_size: Optional[int] = 512,
        output_bands: Optional[List[str]] = None,
        compression: Optional[str] = "blosc",
        page_size: Optional[int] = 1000,
        feature_tiles: Optional[int] = 1,
    ) -> "Job":
        r"""Add a Data input to this Tesseract Job.

        This adds a data input to this Job. Although there are many arguments, many of them don't
        need to be specified. The following rules apply

        * You MUST specified either a ``dataset`` or ``stac_items``, but not both. Specifying both 
            is undefined and will raise an Exception.
        * You MUST specify ``pixels_options``, or ``rasterize_options``, or leave both as None. 
            Specifying both is undefined and will raise an exception. If you specify neither, the
            Features/Items will be added in vector/GeoJSON format
        * If pixels_options is specified, you must specify ``asset_bands`` as there is no general
            way to know what asset and band list from the dataset is desired.
        * You do not need to specify the ``dataset_project`` unless the ``dataset``'\s project is
            ambiguous based on the name alone. This will check the ``active_project`` first,
            followed by ``global``, and 
            raise an exception if the
            ``dataset`` is not in either. If you specify a ``Dataset`` object, the 
            ``dataset_project`` will be pulled from that.

        This method returns ``self`` so that it can be chained together with other methods.

        Args:
            name: the name of the step. This must be unqiue across the whole job.
            asset_name: the name of the output ``asset`` in Tesseract that this will create. This 
                name can be referenced by future ``Step``'\s in the job.
            workers: the number of workers to use for this step. (default=1)
            dataset: the name of the ``Dataset`` or a ``Dataset`` object that has been saved in 
                Entanglement.
            dataset_project: the project that the ``Dataset`` belongs to. This is to resolve
                ambiguity between ``Dataset``'\s that have the same name as each other.
            stac_items: A list of Features or STAC Items that used in lieu of a ``Dataset`` as this
                step's inputs. Do not specify more than a handful of features via this method as the
                job performance may suffer or the ``Job`` may fail to submit successfully.
            asset_bands: a list of ``asset``/``bands`` combinations. The combination of the 
                ``asset`` and the list of ``bands`` will be extracted from the dataset, if
                available. It's not always possible for Tesseract to guarantee that the asset/bands 
                are available without starting the job. Double check your arguments to avoid ``Job``
                failure after the job has been submitted.
            output_time_bins: a specification of how to create the output time bins for the job.
            pixels_options: If this is set, Tesseract will assume that this step will create a
                tensor output from either the specified ``dataset`` or the ``stac_items`` provided.
            rasterize_options: If this is set, Tesseract will assume that this step will create a
                tensor output by rasterizing either the feature outputs from querying the 
                ``dataset`` or using the provided ``stac_items``.
            no_data: For pixels jobs, this will be used as the no_data value for the input rasters.
            pixel_dtype: The data type of tensor outputs. Not needed for features.
            fill_value: The value to set as the no data value for tensor output. This will be set as
                the "fill_value" in the resulting zarr output file.
            ids: A list of IDs to filter the dataset to. Useful if you know exactly what data you
                wish for Tesseract to use.
            filter: a CQL2 JSON filter as a Python dict. This will be used to filter the data if the
                ``dataset`` supports filtering.
            datetime: The range to query for input items from the ``dataset``. This may be specified
                either as a tuple of datetimes/rfc3339 strings or as a STAC style range, \
                'YYYY-mm-ddTHH:MM:SS[Z][+-HH:MM]/YYYY-mm-ddTHH:MM:SS[Z][+-HH:MM]', 
                'YYYY-mm-ddTHH:MM:SS[Z][+-HH:MM]/..' or '../YYYY-mm-ddTHH:MM:SS[Z][+-HH:MM]'
            chip_size: for tensor outputs, what size in pixels should each of the chips be? This
                can be 256>= ``chip_size`` >= 2048
            output_bands: a list of string names of what the output bands should be called. Length
                must match the asset_bans total count of bins.
            compression: what compression algorithm to use on compressed tensor chunks. 'blosc' is
                default and usually very effective.
            page_size: how many items to query at a time from Boson. For complex features, this may
                need to be a smaller value (default 1000 is usually fine), but for simpler features
                using a large value will speed up the processing.
            feature_tiles: if the dataset is a feature dataset this will set how many tiles it will
                divide the search requests into

        Returns:
            This ``Job`` after this step has been added. This is so that these can be chained. If
            you want to suppress the output, call like so: _ = job.add_data_input(...)

        Examples:
            Add an ``asset`` from the "srtm-gl1" dataset. This will use the pixels functionality to 
            reproject/resample

            >>> job = Job()
            >>> _ = job.add_data_input(
            ...         name="add-srtm",
            ...         asset_name="elevation",
            ...         dataset="srtm-gl1",
            ...         asset_bands=[{"asset": "elevation", "bands": [0]}],
            ...         pixels_options={
            ...             "pixel_size": 30.0
            ...         },
            ...         chip_size=2048
            ...     )


            Add an ``asset`` from a feature dataset. This will use the rasterize functionality to
            rasterize the features

            >>> job = Job()
            >>> _ = job.add_data_input(
            ...         name="add-usa-counties",
            ...         asset_name="counties",
            ...         dataset="usa-counties",
            ...         rasterize_options={
            ...             "pixel_size": [500.0, 500.0],
            ...             "value": "FIPS"
            ...         },
            ...         chip_size=1024
            ...     )

            Add the same as the previous step, but do not rasterize

            >>> job = Job()
            >>> _ = job.add_data_input(
            ...         name="add-usa-counties",
            ...         asset_name="counties",
            ...         dataset="usa-counties",
            ...     )

        """
        if name is None:
            name = f"add-{asset_name}"

        # Check dataset OR stac_items is specified
        if dataset is None and stac_items is None:
            raise ValueError("must specify either 'dataset' or 'stac_items'")
        if dataset is not None and stac_items is not None:
            raise ValueError("must specify either 'dataset' or 'stac_items', but not both")

        _type = "tensor"

        # Check that pixels_options OR rasterize_options are not None or BOTH are None
        if pixels_options is not None and rasterize_options is not None:
            raise ValueError(
                "must specify only one of pixels_options or rasterize_options, but not both"
            )

        # Check pixels dependent settings
        if pixels_options is not None and asset_bands is None:
            raise ValueError("must specify 'asset_bands' for pixels requests")

        if pixels_options is None and rasterize_options is None:
            chip_size = None
            compression = None
            _type = "features"

        if pixels_options is not None:
            pixel_size = pixels_options.get("pixel_size")
            try:
                len(pixel_size)
            except TypeError:
                pixel_size = [pixel_size, pixel_size]
                pixels_options["pixel_size"] = pixel_size

        # Prepare the StepInput kwargs for everything that's not None
        input_kwargs = {
            k: v
            for k, v in [
                ("dataset", dataset),
                ("dataset_project", dataset_project),
                ("stac_items", stac_items),
                ("asset_bands", asset_bands),
                ("filter", filter),
                ("datetime", datetime),
                ("ids", ids),
                ("no_data", no_data),
                ("page_size", page_size),
            ]
            if v is not None
        }

        band_count = 0
        if asset_bands is not None:
            for ab in asset_bands:
                band_count += len(ab.get("bands", []))

        if output_bands is not None:
            if len(output_bands) != band_count:
                raise ValueError(
                    f"len(output_bands) ({len(output_bands)}) must equal the total"
                    f"band count ({band_count})"
                )

        # Prepare the StepOutput kwargs for everything that's not None
        output_kwargs = {"asset_name": asset_name}
        output_kwargs.update(
            {
                k: v
                for k, v in [
                    ("output_time_bins", output_time_bins),
                    ("pixels_options", pixels_options),
                    ("rasterize_options", rasterize_options),
                    ("chip_size", chip_size),
                    ("compression", compression),
                    ("pixel_dtype", pixel_dtype),
                    ("fill_value", fill_value),
                    ("type", _type),
                    ("output_bands", output_bands),
                ]
                if v is not None
            }
        )

        # Create the actual Step
        step = Step(
            name=name,
            type="create-assets",
            workers=workers,
            inputs=[StepInput(**input_kwargs)],
            outputs=[StepOutput(**output_kwargs)],
            feature_tiles=feature_tiles,
        )

        return self.add_step(step)

    add_data_input = add_create_assets_step

    def add_model_step(
        self,
        *,
        name: str,
        container: Union[str, Container, dict],
        inputs: List[Union[StepInput, dict]],
        outputs: List[Union[StepOutput, dict]],
        args: dict = {},
        gpu: bool = False,
        workers: int = 1,
        feature_tiles: int = 1,
    ):
        """Add a Model step to this Tesseract Job.

        This adds a model step to this Job and runs some validation.

        This method returns `self` so that it can be chained together with other methods.

        Args:
            name: the name to give this step
            container: either a Container object or the image tag of the container for the model
            inputs: a list of StepInputs. Must refer to previous steps in the model
            outputs: a list of StepOutputs detailing the output of this model
            args: an optional list of arguements for this container at runtime. These will be
                provided to the user inference func if written so-as to accept arguments
            gpu: if this model requires a GPU to run, set to True. Unless your code is specifically
                configured for an NVIDIA GPU and your image has the appropriate drivers, this will
                not be necessary or improve performance of non-GPU optimized code.
            workers: How many workers to split this step over
            feature_tiles: if the number of tiles to split the job into are not implicitly derived
                from other inputs, this will set how many tiles it will divide the search requests
                into.

        Returns:
            self - this Job

        Examples:
            Add a step that runs a harmonic regression model using a previous asset step called
            'landsat'.

            >>> from geodesic.tesseract import Job, Container, StepInput, StepOutput
            >>> job = Job()
            ... job.add_model_step(
            ...     name="run-har-reg",
            ...     container=Container(
            ...         repository="us-central1-docker.pkg.dev/double-catfish-291717/seerai-docker/images/",
            ...         image="har-reg",
            ...         tag="v0.0.7",
            ...         args={"forder": 4}
            ...     ),
            ...     inputs=[StepInput(
            ...         asset_name="landsat",
            ...         dataset_project=proj,
            ...         spatial_chunk_shape=(512, 512),
            ...         type="tensor",
            ...         time_bin_selection=T.BinSelection(all=True),
            ...     )],
            ...     outputs=[
            ...         StepOutput(
            ...             asset_name="brightness-params",
            ...             chunk_shape=(1, 10, 512, 512),
            ...             type="tensor",
            ...             pixel_dtype="<f8",
            ...             fill_value="nan",
            ...         ),
            ...         StepOutput(
            ...             asset_name="greenness-params",
            ...             chunk_shape=(1, 10, 512, 512),
            ...             type="tensor",
            ...             pixel_dtype="<f8",
            ...             fill_value="nan",
            ...         ),
            ...         StepOutput(
            ...             asset_name="wetness-params",
            ...             chunk_shape=(1, 10, 512, 512),
            ...             type="tensor",
            ...             pixel_dtype="<f8",
            ...             fill_value="nan",
            ...         )
            ...     ],
            ...     workers=10
            ... )
        """  # noqa
        if isinstance(container, str):
            ref = container
            try:
                container = parse_container(ref)
            except Exception:
                raise ValueError(f"unable to parse container image ref '{ref}'")

        container = Container(**container)

        if args:
            container.args = args

        step = Step(
            name=name,
            type="model",
            container=container,
            inputs=inputs,
            outputs=outputs,
            gpu=gpu,
            workers=workers,
            feature_tiles=feature_tiles,
        )

        return self.add_step(step)

    def add_step(self, step: Step) -> "Job":
        if nx is not None:
            if "step:" + step.name in self.dag.nodes:
                raise ValueError(
                    "this job already has a step named '{step.name}'. Step names must be unique"
                )

        step_type = step.get("type")
        if step_type is None:
            raise ValueError("must specify step type for every step")

        self.steps.append(Step(**step))

        if nx is not None:
            if not self.is_dag():
                raise ValueError("job's graph is not acyclic")

        return self

    def update_step_params(
        self, step_name: str, input_index=None, output_index=None, **params
    ) -> bool:
        """Updates the parameters for an existing step by looking up the step by name.

        This method can be used to update the info in a step that's already been added to a job.
        You can modify parameters at either the top level of the Step or in any of the inputs or
        outputs by specifying an ``input_index`` or an ``output_index``.

        Args:
            step_name: must match one of the steps in the job. This is the step that will be updated
            input_index: the index of the input you would like to modify
            output_index: the index of the output you would like to modify
            **params: key/values to set on the Step, StepInput, or StepOutput selected

        Returns:
            True if the step passes DAG validation, False otherwise

        Examples:
            Rename the step:
            >>> job.update_step_params('old_name', name='new_name')

            Change the input dataset for 0th input
            >>> job.update_step_params('step', input_index=0, dataset="new-dataset")

            Change the 3rd output's pixel_dtype
            >>> job.update_step_params('step', output_index=3, pixel_dtype=np.float32)

        """
        selected_step = None
        closest = None
        closest_distance = 256
        for step in self.steps:
            cur_name = step.name
            d = hamming_distance(cur_name, step_name)
            if d == 0:
                selected_step = step
                break
            if d < closest_distance:
                closest = cur_name
                closest_distance = d

        if selected_step is None:
            extra = ""
            if closest is not None and closest_distance < len(step_name) / 2:
                extra = f"closest to provided step name '{closest}'"
            raise ValueError(f"could not find step with name '{step_name}' ({extra})")

        if input_index is not None and output_index is not None:
            raise ValueError("can only update one input or output, not both")

        # By default, update parameters in the step
        obj = selected_step

        # if the input_index is specified, update the parameters in that input
        if input_index is not None:
            obj = selected_step.inputs[input_index]

        if output_index is not None:
            obj = selected_step.outputs[output_index]

        for key, value in params.items():
            obj[key] = value

        try:
            return self.is_dag()
        except ImportError:
            return True

    def is_dag(self) -> bool:
        if nx is None:
            raise ImportError("is_dag requires networkx to be installed")
        return nx.is_directed_acyclic_graph(self.dag)

    def delete(self, remove_data: bool = False):
        """Deletes a job in the Tesseract service.

        Unless specified, data created by this job will remain in the underlying storage. Set
        `remove_data` to True to remove created asset data.

        Args:
            remove_data: Delete underlying data created by this job
        """
        if not self.job_id:
            raise Exception("job_id not set, cannot delete")

        _ = raise_on_error(
            self._service.delete(
                f"jobs/{self.job_id}",
                params=dict(remove_data=remove_data, project=self.project.uid),
            )
        ).json()
        self._submitted = False

    @property
    def dag(self):
        graph = nx.DiGraph()

        # add asset/step nodes and asset/step and step/asset edges
        for step in self.steps:
            if step.get("type") == "rechunk" or step.get("type") == "multiscale":
                continue
            graph.add_node("step:" + step.name, type="step", color="red")
            for input in step.inputs:
                if input.get("asset_name") is not None:
                    graph.add_node("asset:" + input.asset_name, type="asset", color="green")
                    graph.add_edge(input.asset_name, step.name)
            for output in step.outputs:
                if output.asset_name not in graph.nodes:
                    graph.add_node("asset:" + output.asset_name, type="asset")
                graph.add_edge(step.name, output.asset_name)

        return graph

    def _build_widget(self):
        # Progress bar
        self._prog = ipywidgets.IntProgress(
            value=self._n_completed,
            min=0,
            max=self._n_quarks,
            step=1,
            description="Running: ",
            bar_style="",
            orientation="horizontal",
        )
        self._title = ipywidgets.HTML(value=self._get_title())
        self._ratio = ipywidgets.HTML(value=self._get_ratio())

        zoom, center = mapping.calc_zoom_center(self._item["bbox"])

        self.map = mapping.Map(center=center, zoom=zoom, scroll_wheel_zoom=True)

        self.map.add_control(ipyleaflet.LayersControl(position="topright"))

        vb = ipywidgets.VBox([self._title, self._ratio, self._prog])
        w = ipywidgets.HBox([vb, self.map])
        self._widget = w

    def _add_item_layer(self):
        if not self._item:
            return

        disp = Item(**self._item)
        disp.geometry = disp.geometry.buffer(np.sqrt(disp.geometry.area) * 0.05).envelope
        fci = {"type": "FeatureCollection", "features": [disp]}
        query_layer = ipyleaflet.GeoJSON(
            data=fci,
            style={
                "opacity": 1,
                "color": "#e2e6d5",
                "fillOpacity": 0.0,
                "weight": 1,
                "dashArray": "4 4",
            },
            hover_style={"fillOpacity": 0.75},
        )
        query_layer.name = "Requested Extent"
        self.map.add_layer(query_layer)

    def _add_quark_layer(self):
        if not self.quark_geoms:
            return

        fc = {"type": "FeatureCollection", "features": self.quark_geoms.features}
        self._quark_layer = ipyleaflet.GeoJSON(
            data=fc,
            style={
                "fillOpacity": 0.75,
            },
            hover_style={},
            style_callback=self._quark_style,
        )
        self._quark_layer.name = "Quark Extents"
        self.map.add_layer(self._quark_layer)

    def widget(self):
        try:
            ipywidgets.VBox
        except ImportError:
            raise ValueError("ipywidgets must be installed to view widget")

        if self._state == "dry_run":
            return (
                ipywidgets.HTML(
                    value='<h2 style="color: red;">Job is currently in "dry_run" state. Submit'
                    "before watching job</h2>"
                ),
                False,
            )

        if not self.job_id:
            raise Exception("job_id not set, nothing to watch")

        self.quark_geoms_lookup = {}

        # Infinite loop is fine here, this is a widget so the user can just interrupt the kernel if
        # they want to stop.
        while True:
            quark_status = self.status(return_quark_status=True)
            try:
                for q in self.quark_geoms.features:
                    self.quark_geoms_lookup[q["id"]] = q
                for k, status in quark_status["quark_status"].items():
                    self.quark_geoms_lookup[k].properties["status"] = status
            except KeyError:
                time.sleep(5.0)
                continue
            break

        self._build_widget()
        self._add_item_layer()
        self._add_quark_layer()
        return self._widget, True

    def _quark_style(self, feature):
        # Default Style
        style = {
            "opacity": 0.5,
            "color": "#888888",
            "fillColor": "#888888",
            "fillOpacity": 0.05,
        }

        sts = feature["properties"].get("status", "incomplete")
        if sts == "incomplete":
            style["fillOpacity"] = 0.0
            return style
        elif sts == "running":
            style["fillColor"] = "green"
            style["color"] = "green"
            style["opacity"] = 0.5
        elif sts == "failed":
            style["fillColor"] = "yellow"
            style["color"] = "yellow"
            style["opacity"] = 0.0
        elif sts == "fatal":
            style["fillColor"] = "red"
            style["color"] = "red"
            style["opacity"] = 0.0
        elif sts == "completed":
            style["fillColor"] = "green"
            style["color"] = "green"
            style["opacity"] = 0.0

        return style

    def watch(self):
        """Monitor the tesseract job with the SeerAI widget.

        Will create a jupyter widget that will watch the progress of this tesseract job.
        """
        have_ipywidgets = True
        try:
            ipywidgets.VBox
        except ImportError:
            have_ipywidgets = False

        if not self.job_id:
            if have_ipywidgets:
                display.display(
                    ipywidgets.HTML(
                        value='<h2 style="color: red;">No Job ID - submit job before watching</h2>'
                    )
                )
                return
            raise ValueError("no job_id: has job been submitted?")

        while self.state in ("planning"):
            time.sleep(1.0)
            self.status()

        self.status(return_quark_status=True, return_quark_geoms=True)
        if not have_ipywidgets:
            return self.watch_terminal()

        widget, valid = self.widget()
        display.display(widget)
        if not valid:
            return

        keep_watching = True
        while keep_watching:
            self._update_widget()
            time.sleep(1)
            if self._n_completed == self._n_quarks:
                break

    def watch_terminal(self):
        with tqdm.tqdm(total=self._n_quarks, initial=self._n_completed) as progress:
            last = self._n_completed
            while True:
                state = self._state
                if state == "dry_run":
                    break
                progress.set_description(f"Job State: {self._state}")
                self.status()
                progress.update(self._n_completed - last)
                last = self._n_completed

                time.sleep(1)
                if self._n_completed == self._n_quarks:
                    break
        print(f"Job State: {self._state}")

    def _update_widget(self):
        quark_status = self.status(return_quark_status=True, return_quark_geoms=True)

        for k, status in quark_status["quark_status"].items():
            self.quark_geoms_lookup[k].properties["status"] = status

        feats = {
            "type": "FeatureCollection",
            "features": [f for _, f in self.quark_geoms_lookup.items()],
        }
        self._quark_layer.data = feats

        # set numerics
        self._prog.value = self._n_completed
        # When the progress bar is first created self._n_quarks is sometimes None for some reason
        # (I think depending on when the watch function is called), so lets set it here just
        # to be safe.
        self._prog.max = self._n_quarks if self._n_quarks is not None else 100
        self._title.value = self._get_title()
        self._ratio.value = self._get_ratio()

    def _get_title(self):
        return f"<h2>Job: {self.alias} - {self._state}</h2>"

    def _get_ratio(self):
        return f"<h2>{self._n_completed} / {self._n_quarks}</h2>"

    def add_rechunk_step(
        self,
        *,
        asset_name: str,
        chunk_shape: List[int],
        step_name: str = None,
        workers: int = 1,
    ):
        """Adds a rechunk step to the job.

        A rechunk step will create a new zarr array for a given asset called "rechunk" which will
        with copy of the tesseract array with the new given chunk shape. Note it is best to not
        decrease any dimension of the chunk shape too much. For example (1,1,1,1000) to
        (1,1,1000, 1) will be an extrememly inefficent operation (not to mention impractical).

        Args:
            asset_name: output asset name from a previous step to rechunk
            chunk_shape: a list of integers of length four which will
            step_name: name for the rechunking step, defaults to 'rechunk-{asset_name}'
            workers: the number of workers to use for this step. (default=1)
            **params: key/values to set on the Step, StepInput, or StepOutput selected

        Example:
            Add rechunk an asset from (1,1,1000,1000) to (4,2,1000,1000):

            >>> job.add_rechunk_step(
            ...    step_name='rechunk-sentinel',
            ...    asset_name="sentinel-out",
            ...    chunk_shape=[4,2,1000,1000],
            ...    workers=3
            ...    )
        """
        if step_name is None:
            step_name = f"rechunk-{asset_name}"

        step = Step(
            name=step_name,
            type="rechunk",
            inputs=[{"asset_name": asset_name}],
            outputs=[{"asset_name": asset_name, "chunk_shape": chunk_shape}],
            workers=workers,
        )
        return self.add_step(step)

    def add_multiscale_step(
        self,
        *,
        asset_name: str,
        step_name: str = None,
        min_zoom: int = 0,
        workers: int = 1,
    ):
        """Adds a multiscales step to the job.

        Args:
            asset_name: output asset name from a previous step to create multiscales for
            step_name: name for the multiscale step. Defaults to 'multiscale-{asset_name}'
            min_zoom: minimum zoom level for the multiscale step to generate. This might be useful
                if the asset is large with a small pixel size and all 20 zoom
                levels are not desired.
            workers: the number of workers to use for this step. (default=1)

        Example:
            Add a multiscale step for asset sentinel

            >>> job.add_multiscale_step(
            ...    step_name='multiscale-sentinel',
            ...    asset_name="sentinel-out",
            ...    min_zoom=10,
            ...    workers=3
            ... )

        """
        if step_name is None:
            step_name = f"multiscale-{asset_name}"

        step = Step(
            name=step_name,
            type="multiscale",
            inputs=[{"asset_name": asset_name}],
            outputs=[
                StepOutput(
                    asset_name=asset_name,
                    multiscale_options=MultiscaleOptions({"min_zoom": min_zoom}),
                )
            ],
            workers=workers,
        )
        return self.add_step(step)


class JobList(_APIObject):
    def __init__(self, jobs, ids=[]):
        self.ids = ids
        if len(ids) != len(jobs):
            self.ids = [job.name for job in jobs]
        for job in jobs:
            self._set_item(job.name, job)

    def __getitem__(self, k) -> Job:
        if isinstance(k, str):
            return super().__getitem__(k)
        elif isinstance(k, int):
            jid = self.ids[k]
            return super().__getitem__(jid)
        else:
            raise KeyError("invalid job id")

    def _ipython_display_(self, **kwargs):
        raise NotImplementedError
