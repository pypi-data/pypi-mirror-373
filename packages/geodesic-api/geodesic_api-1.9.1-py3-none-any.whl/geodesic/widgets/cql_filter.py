from typing import Union

import ipywidgets
import traitlets
from geodesic.cql import CQLFilter


class CQLFilterLineWidget(ipywidgets.HBox):
    valid = traitlets.Bool(True).tag(sync=True)

    def __init__(self, **kwargs):
        self._field = ipywidgets.Text(placeholder="<field>", layout=ipywidgets.Layout(width="90px"))
        self._op = ipywidgets.Dropdown(
            options=[
                ("=", CQLFilter.eq),
                (">", CQLFilter.gt),
                (">=", CQLFilter.gte),
                ("<", CQLFilter.lt),
                ("<=", CQLFilter.lte),
                ("!=", CQLFilter.neq),
            ],
            layout=ipywidgets.Layout(width="45px"),
        )
        self._value = ipywidgets.Text(placeholder="value", layout=ipywidgets.Layout(width="80px"))
        self._type = ipywidgets.Dropdown(
            options=[("string", str), ("float", float), ("int", int)],
            layout=ipywidgets.Layout(width="70px"),
        )

        self._field.observe(self._validate, names="value")

        children = [self._field, self._op, self._value, self._type]

        super().__init__(children)

    def _validate(self, event):
        if event["new"] == "":
            self.valid = False
        else:
            self.valid = True

    @property
    def field(self) -> str:
        return self._field.value

    @property
    def op(self) -> callable:
        return self._op.value

    @property
    def value(self) -> Union[str, float, int]:
        return self._type.value(self._value.value)


class CQLFilterWidget(ipywidgets.VBox):
    def __init__(self, **kwargs):
        self._label = ipywidgets.Valid(description="Filter:", value=True)
        self._layout = ipywidgets.Layout(margin="10px", padding="2px")

        super().__init__([self._label, self._create_row(first=True)], layout=self._layout)

    def _clear(self, event):
        self.children = [self._label, self._create_row(first=True)]
        self._label.value = True

    def _create_row(self, first=False):
        f = CQLFilterLineWidget()
        plus = ipywidgets.Button(description="+", layout=ipywidgets.Layout(width="30px"))
        plus.on_click(self._plus(len(self.children)))

        if first:
            and_or = ipywidgets.Button(description="clear", layout=ipywidgets.Layout(width="60px"))
            and_or.on_click(self._clear)
        else:
            f.valid = False
            and_or = ipywidgets.Dropdown(
                options=("and", "or"), layout=ipywidgets.Layout(width="60px")
            )

        f.observe(self._validate, names="valid")
        return ipywidgets.HBox([and_or, f, plus])

    def _plus(self, i):
        def handler(event):
            row = self._create_row()
            label, *children = self.children
            children = list(children)
            children[-1].children = children[-1].children[:-1]
            children.append(row)
            self.children = [label] + children
            self._validate(None)

        return handler

    def _validate(self, event):
        for row in self.children[1:]:
            if not row.children[1].valid:
                self._label.value = False
                return
        self._label.value = True

    @property
    def filter(self):
        first_line = True
        or_list = []
        and_list = []

        if not self._label.value:
            return None

        if len(self.children[1:]) == 1 and self.children[1].children[1].field == "":
            return None

        for row in self.children[1:]:
            fw = row.children[1]
            field = fw.field
            op = fw.op
            value = fw.value

            f = op(field, value)

            if first_line:
                first_line = False
                and_list.append(f)

            else:
                logical_op = row.children[0].value
                if logical_op == "or":
                    if len(and_list) > 1:
                        or_list.append(CQLFilter.logical_and(*and_list))
                    else:
                        or_list.append(and_list[0])
                    or_list.append(f)

                    and_list = []
                else:
                    and_list.append(f)

        if len(or_list) == 0:
            if len(and_list) == 1:
                return and_list[0]
            return CQLFilter.logical_and(*and_list)
        elif len(or_list) == 1:
            return or_list[0]
        return CQLFilter.logical_or(*or_list)
