import ipywidgets
import traitlets


class AssetBandsLineWidget(ipywidgets.VBox):
    valid = traitlets.Bool(False).tag(sync=True)

    def __init__(self, **kwargs):
        self.asset_text = ipywidgets.Text(placeholder="asset name", description="Asset:")
        self.bands_text = ipywidgets.Text(placeholder="0,1,2...", description="Bands:")
        self.asset_text.observe(self._validate, names="value")
        self.bands_text.observe(self._validate, names="value")
        super().__init__(
            [self.asset_text, self.bands_text],
            **kwargs,
            layout=ipywidgets.Layout(align_items="flex-start"),
        )

    def _validate(self, event):
        if self.asset_text.value == "" or self.bands_text.value == "":
            self.valid = False
        else:
            self.valid = True

    @property
    def asset(self) -> str:
        return self.asset_text.value

    @property
    def bands(self) -> list:
        bands = self.bands_text.value.split(",")
        try:
            bands = list(map(int, bands))
        except ValueError:
            return bands
        return bands


class AssetBandsWidget(ipywidgets.VBox):
    def __init__(self, **kwargs):
        self._label = ipywidgets.Valid(description="Asset/Bands:", value=False)
        self._clear_button = ipywidgets.Button(description="Clear", layout={"width": "70px"})
        self._clear_button.on_click(self._clear)

        self.header = ipywidgets.HBox(
            [
                self._clear_button,
                self._label,
            ]
        )

        super().__init__([self.header, self._create_row(first=True)])

    def _clear(self, event):
        self.children = [self.header, self._create_row(first=True)]

    def _create_row(self, first=False):
        f = AssetBandsLineWidget()
        plus = ipywidgets.Button(description="+", layout=ipywidgets.Layout(width="30px"))
        plus.on_click(self._plus)
        f.observe(self._validate, names="valid")

        return ipywidgets.HBox([f, plus])

    @property
    def asset_bands(self):
        if not self._label.value:
            return

        asset_bands = []
        for row in self.children[1:]:
            asset_bands_line = row.children[0]
            asset_bands.append({"asset": asset_bands_line.asset, "bands": asset_bands_line.bands})
        return asset_bands

    def _validate(self, event):
        for row in self.children[1:]:
            if not row.children[0].valid:
                self._label.value = False
                return
        self._label.value = True

    def _plus(self, event):
        children = []
        for i, child in enumerate(self.children[1:]):
            child.children = [child.children[0]]
            children.append(child)
        children.append(self._create_row(len(self.children) == 1))
        self.children = [self.children[0]] + children
