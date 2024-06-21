from typing import Any
from pytermgui import Container, Widget


class AlignedContainer(Container):
    def __init__(self, align=0, *widgets: Any, **attrs: Any) -> None:
        super().__init__(*widgets, **attrs)
        self.align = align

    def set_widgets(self, widgets: list[Widget]) -> None:
        self._widgets = []
        for widget in widgets:
            if not isinstance(widget, Widget):
                widget = Widget.from_data(widget)
                if widget is None:
                    raise ValueError(
                        f"Could not convert {widget} of type {type(widget)} to a Widget!"
                    )
            widget.parent_align = (
                self.align
                if widget.__dict__.get("self_align") is None
                else widget.self_align
            )
            self._add_widget(widget)
