import ipyleaflet
import geodesic
import numpy as np
from shapely.geometry import shape
from shapely.ops import transform

DEFAULT_BASEMAP = ipyleaflet.basemaps.CartoDB.DarkMatter

_color_cycle = [
    "#428BA9",
    "#FF902B",
    "#5FAD56",
    "#966B9D",
    "#DF2935",
]


def _get_color(i: int) -> str:
    """Returns the color corresponding to the given index, cyclic on the _color_cycle."""
    return _color_cycle[i % len(_color_cycle)]


class Map(ipyleaflet.Map):
    """Light wrapper on top of an ipyleaflet.Map.

    A basic map with some basic initialization.
    """

    def __init__(
        self, basemap=DEFAULT_BASEMAP, zoom=3, center=(0.0, 0.0), scroll_wheel_zoom=True, **kwargs
    ):
        super().__init__(
            basemap=basemap, zoom=zoom, center=center, scroll_wheel_zoom=scroll_wheel_zoom, **kwargs
        )

        self._fc_layers = []
        self.add_control(ipyleaflet.LayersControl())

    def add_feature_collection(
        self,
        layer_name: str,
        feature_collection: geodesic.FeatureCollection,
        on_click: callable = None,
        style_callback: callable = None,
        **kwargs,
    ) -> None:
        """Add a feature colleciton to the map.

        Adds a geodesic.FeatureCollection to the map as a GeoJSON layer.

        Args:
            layer_name: display name of the layer
            feature_collection: the ``geodesic.FeatureCollection`` or `geopandas.GeoDataFrame`` to
                add to the map.
            on_click: a callback function that will be called when a feature is selected.
            style_callback: a function that will be called on each feature to return the style.
                Can be used to style each feature based on its properties.
            **kwargs: additional kwargs passed to the layer constructor.
        """
        index = len(self._fc_layers)

        add_layer = True
        current_layer = None
        for i, layer in enumerate(self._fc_layers):
            if layer.name == layer_name:
                index = i
                current_layer = layer
                add_layer = False
                break

        color = _get_color(index)

        if "style" not in kwargs:
            kwargs["style"] = dict(opacity=1.0, fillOpacity=0.5, color=color, fillColor=color)

        if "hover_style" not in kwargs:
            kwargs["hover_style"] = dict(fillOpacity=1.0)

        try:
            data = feature_collection.__geo_interface__
        except AttributeError:
            data = dict(feature_collection)
        if current_layer is None:
            current_layer = ipyleaflet.GeoJSON(name=layer_name, data=data, **kwargs)
        else:
            current_layer.data = data

        if on_click is not None:
            current_layer.on_click(on_click)

        current_layer.style_callback = style_callback

        if add_layer:
            self._fc_layers.append(current_layer)
            self.add_layer(current_layer)
        else:
            self._fc_layers[index] = current_layer


class BBoxSelector(Map):
    """select a geometry/aoi on the a interactive webmap.

    Lets a user draw a geometry on the map. This geometry will be accessible as this object's
    `geometry` parameter and the bounding rectangle corners as `bbox`.

    Note: Does not handle geometries that cross the datetime.

    Args:
        set_geometry_on: a list of objects such as a `geodesic.Feature`, a `geodesic.tesseract.Job`,
            or a `geodesic.entanglement.Object`. When a draw action is performed, the drawn geometry
            is set on all objects in this list.
    """

    def __init__(self, set_geometry_on=[], scroll_wheel_zoom=True, **kwargs):
        super().__init__(scroll_wheel_zoom=scroll_wheel_zoom, **kwargs)

        self.draw_control = ipyleaflet.DrawControl()
        self.draw_control.rectangle = dict(
            shapeOptions=dict(fillColor="#428BA9", color="#428BA9", fillOpacity=0.15)
        )
        self.draw_control.polygon = dict(
            shapeOptions=dict(fillColor="#428BA9", color="#428BA9", fillOpacity=0.15)
        )

        self.draw_control.circle = dict(
            shapeOptions=dict(fillColor="#428BA9", color="#428BA9", fillOpacity=0.15)
        )

        self.set_geometry_on = set_geometry_on
        self.geometry = None

        self.draw_control.on_draw(self._bbox_callback)
        self.add_control(self.draw_control)

    def _bbox_callback(self, target, action, geo_json):
        geometry = geo_json["geometry"]

        # If it's a circle, parse that into a polygon so we can use it
        if "radius" in geo_json["properties"]["style"]:
            cx, cy = geometry["coordinates"]
            radius = geo_json["properties"]["style"]["radius"] / (
                1852.0 * 60.0
            )  # rough conversion from m to deg

            angles = np.linspace(0.0, 2.0 * np.pi, 25)
            cos = np.cos(angles)
            sin = np.sin(angles)

            x = (cx + radius * cos).tolist()
            y = (cy + radius * sin).tolist()

            coordinates = [[c for c in zip(x, y)]]
            geometry = {"type": "Polygon", "coordinates": coordinates}

        def xform(x, y, z=None) -> tuple:
            while x < -180:
                x += 360
            while x > 180:
                x -= 360

            return x, y

        self.geometry = shape(geometry)
        self.geometry = transform(xform, self.geometry)

        self.action = action

        for obj in self.set_geometry_on:
            obj.geometry = self.geometry

        target.data = [geo_json]

    @property
    def bbox(self):
        """Bbox for the geometry drawn on the map."""
        if self.geometry is None:
            return None
        return self.geometry.bounds
