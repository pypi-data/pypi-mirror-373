import datetime
import re
import ipywidgets
import ipyleaflet

import geodesic
from geodesic.widgets import CQLFilterWidget, GeodesicHeaderWidget, AssetBandsWidget
from geodesic.mapping import BBoxSelector, calc_zoom_center

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Matplotlib backend for interaction
matplotlib.use("module://ipympl.backend_nbagg")


class DatasetExplorerWidget(ipywidgets.VBox):
    """search and get pixel data from all the datasets that this user has access to.

    The Dataset Explorer is intended to be a simple way to browse some of the datasets in
    Entanglement using
    a user interface.

    For privacy purposes, a user can choose to only show a subset of projects

    Public Attributes:
        pixels_results: a `numpy.ndarray` of the result of running a pixels request
        search_results: a `geodesic.FeatureCollection`
        dataset: the selected dataset
        selected_project: the selected project
        pixels_request: the currently active pixels request
        search_request: the currently active search request

    Args:
        figsize: the size of the figure in the raster pane. It's difficult to make this dynamic, so
        it's set to a
                sensible default.
        show_projects_matching: a list of project names or regex patterns to show in the projects
        dropdown. If `None`,
                will show all.
    """

    def __init__(self, figsize=(8, 5), show_projects_matching=None):
        self.geometry = None
        self.pixels_results = None
        self.search_results = None

        self._setup_figure(figsize)
        self._setup_map()
        self._setup_dataset_selector(show_projects_matching)
        self._setup_global_filters()
        self._setup_dataset_vbox()

        self._setup_search_vbox()
        self._setup_pixels_vbox()
        self._setup_dataset_operations_accordion()
        self._setup_lhs()
        self._setup_rhs()

        hbox = ipywidgets.HBox([self.lhs, self.rhs])
        header = GeodesicHeaderWidget("Dataset Explorer")
        super().__init__([header, hbox])

    def _setup_figure(self, figsize):
        plt.ioff()
        plt.style.use("dark_background")
        self.figure = plt.figure(figsize=figsize)
        self.figure.suptitle("Pixels Output", fontsize=16)
        self.figure.canvas.layout.min_width = "80%"
        self.figure.canvas.layout.min_height = "80%"
        self.figure.canvas.header_visible = False
        self.figure.canvas.toolbar_position = "bottom"
        self.figure.canvas.layout.align_items = "center"
        self.ax = plt.gca()

        self.rendering_bar = RenderingBar(
            layout={
                "border": "1px solid",
                "padding": "5px",
                "align_items": "flex-end",
                "min_width": "150px",
            }
        )
        self.rendering_bar.set_callback(self._redraw_imshow)

    def _setup_dataset_selector(self, show_projects_matching):
        self.projects = geodesic.get_projects()
        if show_projects_matching is None:
            show_projects_matching = [".*"]

        show_projects_re = []
        for pattern_str in show_projects_matching:
            pattern = re.compile(pattern_str)
            show_projects_re.append(pattern)

        self.project_names = [
            (project.alias, project.uid)
            for project in self.projects
            if any([pattern.match(project.name) for pattern in show_projects_re])
            or any([pattern.match(project.alias) for pattern in show_projects_re])
        ]

        self.selected_project = None
        self.project_selector = ipywidgets.Dropdown(
            description="Project",
            placeholder="select project...",
            options=self.project_names,
        )
        self.dataset_selector = ipywidgets.Dropdown(
            description="Dataset",
            placeholder="select dataset...",
            options=[],
            disabled=True,
        )
        self.project_selector.observe(self._on_select_project, names="value")
        self.dataset_selector.observe(self._on_dataset_select, names="value")
        if len(self.project_names) > 0:
            self._on_select_project({"new": self.project_names[0][1]})

    def _setup_map(self):
        self.map = BBoxSelector(
            set_geometry_on=[self],
            scroll_wheel_zoom=True,
            layout=ipywidgets.Layout(width="98%", height="600px", margin="10px"),
        )

    def _setup_global_filters(self):
        self.filter = CQLFilterWidget()
        self.start_datetime_picker = ipywidgets.DatePicker(
            description="Start Date",
            allow_none=True,
            layout=ipywidgets.Layout(width="200px"),
        )
        self.end_datetime_picker = ipywidgets.DatePicker(
            description="End Date",
            allow_none=True,
            layout=ipywidgets.Layout(width="200px"),
        )
        self.datetime_hbox = ipywidgets.HBox(
            (self.start_datetime_picker, self.end_datetime_picker),
            layout=ipywidgets.Layout(align_items="flex-start"),
        )

    def _setup_dataset_vbox(self):
        children = [
            self.project_selector,
            self.dataset_selector,
            self.filter,
            self.datetime_hbox,
        ]
        self.dataset_vbox = ipywidgets.VBox(
            children, layout=ipywidgets.Layout(align_items="flex-start")
        )

    def _setup_search_vbox(self):
        self.search_submit_button = ipywidgets.Button(
            description="submit", layout=ipywidgets.Layout(width="60px", margin="12px")
        )
        self.search_submit_button.on_click(self._on_search_submit)

        self.limit = ipywidgets.BoundedIntText(
            value=1000, min=0, max=20000, step=1, description="Feature Limit:"
        )
        self.page_size = ipywidgets.BoundedIntText(
            value=500, min=0, max=2000, step=1, description="Page Size:"
        )
        self.collections = ipywidgets.Text(
            placeholder="<comma separated collections>", description="Collections:"
        )
        self.color = ipywidgets.ColorPicker(
            concise=False, description="Color", value="#428BA9", disabled=False
        )

        self.search_vbox = ipywidgets.VBox(
            [
                self.limit,
                self.page_size,
                self.collections,
                self.color,
                self.search_submit_button,
            ]
        )

    def _setup_pixels_vbox(self):
        self.pixels_submit_button = ipywidgets.Button(
            description="submit", layout=ipywidgets.Layout(width="60px", margin="12px")
        )
        self.pixels_submit_button.on_click(self._on_pixels_submit)

        self.pixel_size_x = ipywidgets.FloatText(
            description="Pixel Size X",
            value=10.0,
            layout=ipywidgets.Layout(width="150px"),
        )
        self.pixel_size_y = ipywidgets.FloatText(
            description="Pixel Size Y",
            value=10.0,
            layout=ipywidgets.Layout(width="150px"),
        )
        self.shape_rows = ipywidgets.IntText(
            description="Rows", value=1000, layout=ipywidgets.Layout(width="150px")
        )
        self.shape_cols = ipywidgets.IntText(
            description="Columns", value=1000, layout=ipywidgets.Layout(width="150px")
        )
        self.resampling = ipywidgets.Dropdown(
            options=geodesic.boson.dataset._valid_resampling,
            value="nearest",
            description="Resampling:",
        )
        self.colormap = ipywidgets.Dropdown(
            options=plt.colormaps(), value="magma", description="Colormap:"
        )

        pixel_hbox = ipywidgets.HBox([self.pixel_size_x, self.pixel_size_y])
        shape_hbox = ipywidgets.HBox([self.shape_rows, self.shape_cols])
        self.output_spatial_ref = ipywidgets.Text(
            value="EPSG:3857",
            description="Output SRS:",
        )

        self.use_pixel_size_or_shape = ipywidgets.Dropdown(
            description="Use:",
            options=["pixel size", "shape"],
        )

        self.asset_bands_selector = AssetBandsWidget()

        self.pixels_vbox = ipywidgets.VBox(
            [
                self.asset_bands_selector,
                pixel_hbox,
                shape_hbox,
                self.use_pixel_size_or_shape,
                self.resampling,
                self.colormap,
                self.output_spatial_ref,
                self.pixels_submit_button,
            ],
        )

    def _setup_dataset_operations_accordion(self):
        self.dataset_operations_accordian = ipywidgets.Accordion(
            [self.search_vbox, self.pixels_vbox],
            layout=ipywidgets.Layout(margin="10px", width="95%"),
        )
        self.dataset_operations_accordian.set_title(0, "search/\.")
        self.dataset_operations_accordian.set_title(1, "pixels")

    def _setup_lhs(self):
        self.lhs = ipywidgets.VBox(
            [
                self.dataset_vbox,
                self.dataset_operations_accordian,
            ],
            layout=ipywidgets.Layout(align_items="center", border="1px solid #444", padding="10px"),
        )

    def _setup_rhs(self):
        raster_hbox = ipywidgets.HBox(
            layout=ipywidgets.Layout(height="600px", align_items="center", width="90%")
        )
        raster_hbox.children = [self.rendering_bar, self.figure.canvas]

        self.rhs = ipywidgets.Tab()
        self.rhs.children = [self.map, raster_hbox]
        self.rhs.set_title(0, "Map")
        self.rhs.set_title(1, "Raster")
        self.rhs.layout = ipywidgets.Layout(width="70%")

    def _on_select_project(self, event):
        value = event["new"]

        self.datasets = geodesic.list_datasets(project=value)
        self.dataset_selector.options = [
            (f"{dataset.alias} ({dataset.name})", dataset.name)
            for name, dataset in self.datasets.items()
        ]
        self.dataset_selector.disabled = False

    @property
    def search_request(self):
        limit = self.limit.value
        page_size = self.page_size.value
        collections = self.collections.value.split(",")

        req = {"limit": min(page_size, limit)}

        collections = [c for c in collections if c != ""]
        if len(collections) > 0:
            req["collections"] = collections

        if self.map.geometry is not None:
            req["intersects"] = self.map.geometry

        start = self.start_datetime_picker.value
        end = self.end_datetime_picker.value
        if start is not None:
            start = datetime.datetime(start.year, start.month, start.day)
        if end is not None:
            end = datetime.datetime(end.year, end.month, end.day)

        if not (start is None and end is None):
            req["datetime"] = (start, end)
        if self.filter.filter is not None:
            req["filter"] = self.filter.filter

        return req

    def _on_search_submit(self, event):
        limit = self.limit.value
        req = self.search_request
        fc = self.dataset.search(**req, limit=limit)

        style = dict(
            opacity=1.0,
            fillOpacity=0.5,
            color=self.color.value,
            fillColor=self.color.value,
        )

        self.map.add_feature_collection(self.dataset.name, fc, style=style)

        self.search_results = fc

    @property
    def pixels_request(self):
        req = {}
        if self.map.geometry is not None:
            req["bbox"] = self.map.geometry.bounds

        start = self.start_datetime_picker.value
        end = self.end_datetime_picker.value
        if start is not None:
            start = datetime.datetime(start.year, start.month, start.day)
        if end is not None:
            end = datetime.datetime(end.year, end.month, end.day)

        if not (start is None and end is None):
            req["datetime"] = (start, end)

        if self.filter.filter is not None:
            req["filter"] = self.filter.filter

        asset_bands = self.asset_bands_selector.asset_bands
        if asset_bands is None:
            return
        req["asset_bands"] = asset_bands
        if self.use_pixel_size_or_shape.value == "pixel size":
            req["pixel_size"] = [self.pixel_size_x.value, self.pixel_size_y.value]
        else:
            req["shape"] = [self.shape_rows.value, self.shape_cols.value]

        return req

    def _on_pixels_submit(self, event):
        pixels_request = self.pixels_request
        if pixels_request is None:
            print("invalid pixels request options")
            return

        bands = []
        for asset_bands in pixels_request["asset_bands"]:
            asset = asset_bands["asset"]
            bands.extend([f"{asset}:{band}" for band in asset_bands["bands"]])
        self.rendering_bar.set_bands_list(bands)

        self.pixels_results = self.dataset.get_pixels(**pixels_request)
        self._redraw_imshow(None)
        self.rhs.selected_index = 1

    def _redraw_imshow(self, _):
        if self.pixels_results is None:
            return

        self.ax.clear()

        renderer_props = self.rendering_bar.renderer_properties
        if renderer_props["renderer"] == "colormap":
            band_idx = renderer_props["band"]
            self.ax.imshow(self.pixels_results[band_idx], **renderer_props["imshow_kwargs"])
        else:
            rgb = self.pixels_results[renderer_props["bands"]].astype(np.float32)
            # Normalize
            for i in range(rgb.shape[0]):
                rgb[i] /= np.nanmax(rgb[i])

            rgb = np.moveaxis(rgb, 0, 2)
            self.ax.imshow(rgb, **renderer_props["imshow_kwargs"])
        self.figure.canvas.draw()

    def _on_dataset_select(self, event):
        value = event["new"]

        self.dataset = self.datasets[value]
        extent = self.dataset.item.get("extent", {})
        spatial = extent.get("spatial", {})
        bbox = spatial.get("bbox", [[-180, -90, 180, 90]])[0]

        layer_exists = False
        for layer in self.map.layers:
            if layer.name == "Dataset Extent":
                layer_exists = True
                break

        geom = [
            (bbox[1], bbox[0]),
            (bbox[1], bbox[2]),
            (bbox[3], bbox[2]),
            (bbox[3], bbox[0]),
            (bbox[1], bbox[0]),
        ]

        if not layer_exists:
            layer = ipyleaflet.Polygon(
                name="Dataset Extent", locations=geom, color="green", fill_opacity=0.0
            )
            self.map.add_layer(layer)
        else:
            layer.locations = geom

        zoom, center = calc_zoom_center(bbox)

        self.map.center = center
        self.map.zoom = zoom


class RenderingBar(ipywidgets.VBox):
    def __init__(self, **kwargs):
        self.bands_list = []
        self._setup_colormap_rendering()
        self._setup_rgb_rendering()

        self.select_renderer = ipywidgets.RadioButtons(
            description="             ", options=("colormap", "rgb")
        )
        super().__init__([self.select_renderer, self.colormap_panel, self.rgb_panel], **kwargs)

    def _setup_colormap_rendering(self):
        selector_layout = {"width": "180px"}
        self.colormap_label = ipywidgets.Label(value="Colormap:")
        self.colormap = ipywidgets.Dropdown(
            options=plt.colormaps(),
            value="magma",
            description="Colormap:",
            layout=selector_layout,
        )
        self.band = ipywidgets.Dropdown(
            options=self.bands_list, description="Band:", layout=selector_layout
        )
        vbox = ipywidgets.VBox([self.colormap, self.band])
        self.colormap_panel = ipywidgets.VBox(
            [self.colormap_label, vbox], layout={"align_items": "center"}
        )

    def _setup_rgb_rendering(self, bands_list=[]):
        selector_layout = {"width": "180px"}
        self.rgb_label = ipywidgets.Label(value="RGB:")
        self.red = ipywidgets.Dropdown(
            description="red", options=self.bands_list, layout=selector_layout
        )
        self.green = ipywidgets.Dropdown(
            description="green", options=self.bands_list, layout=selector_layout
        )
        self.blue = ipywidgets.Dropdown(
            description="blue", options=self.bands_list, layout=selector_layout
        )
        vbox = ipywidgets.VBox([self.red, self.green, self.blue])
        self.rgb_panel = ipywidgets.VBox([self.rgb_label, vbox], layout={"align_items": "center"})

    def set_bands_list(self, bands_list):
        self.bands_list = bands_list
        self.red.options = bands_list
        self.green.options = bands_list
        self.blue.options = bands_list
        self.band.options = bands_list
        if len(bands_list) > 0:
            max_index = len(bands_list) - 1
            self.red.value = bands_list[0]
            self.green.value = bands_list[min(max_index, 1)]
            self.blue.value = bands_list[min(max_index, 2)]
            self.band.value = bands_list[0]

    @property
    def renderer_properties(self):
        if self.select_renderer.value == "colormap":
            return {
                "renderer": "colormap",
                "imshow_kwargs": {
                    "cmap": self.colormap.value,
                },
                "band": self.band.index,
            }
        return {
            "renderer": "rgb",
            "imshow_kwargs": {},
            "bands": [self.red.index, self.green.index, self.blue.index],
        }

    def set_callback(self, cb):
        self.red.observe(cb, names="value")
        self.green.observe(cb, names="value")
        self.blue.observe(cb, names="value")
        self.band.observe(cb, names="value")
        self.colormap.observe(cb, names="value")
        self.select_renderer.observe(cb, names="value")
