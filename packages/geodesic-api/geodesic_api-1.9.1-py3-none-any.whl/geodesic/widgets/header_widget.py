import geodesic
import ipywidgets

round_img_style = """
border-top-left-radius: 50% 50%;
border-top-right-radius: 50% 50%;
border-bottom-right-radius: 50% 50%;
border-bottom-left-radius: 50% 50%;
"""


class GeodesicHeaderWidget(ipywidgets.HBox):
    def __init__(self, title, **kwargs):
        super().__init__(
            **kwargs,
            layout=ipywidgets.Layout(border="1px solid #444", align_items="center"),
        )
        self.user = geodesic.myself()
        self.image = ipywidgets.HTML(
            f"""
            <img src={self.user.avatar} width=30 height=30 style="{round_img_style}"></img>
            """,
            layout=ipywidgets.Layout(margin="5px"),
        )
        name = ipywidgets.Label(self.user.alias)
        self.title = ipywidgets.HTML(
            f"<h3>{title}</h3>",
            layout=ipywidgets.Layout(width="100%", margin="0px 0px 0px 10px"),
        )

        lhs = ipywidgets.HBox(
            [self.title], layout=ipywidgets.Layout(width="20%", align_items="center")
        )
        rhs = ipywidgets.HBox(
            [name, self.image],
            layout=ipywidgets.Layout(
                justify_content="flex-end",
                align_items="center",
                width="100%",
                margin="0px 0px 0px 0px",
            ),
        )
        self.children = [lhs, rhs]
