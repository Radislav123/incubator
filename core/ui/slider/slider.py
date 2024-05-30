from arcade.gui import UISlider

from core.mixin import MovableWidgetMixin
from core.settings import Settings


class Slider(UISlider, MovableWidgetMixin):
    settings = Settings()

    normal_style = UISlider.UIStyle()
    hovered_style = UISlider.UIStyle()
    DEFAULT_STYLE = {
        "normal": normal_style,
        "hover": hovered_style,
        "press": hovered_style,
        "disabled": normal_style
    }

    def __init__(self, **kwargs):
        super().__init__(style = self.DEFAULT_STYLE, **kwargs)
