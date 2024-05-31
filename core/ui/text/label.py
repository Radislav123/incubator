from core.service.color import Color
from core.texture import Texture
from core.ui.button.texture_button import TextureButton


class Label(TextureButton):
    def __init__(self, **kwargs):
        if "width" not in kwargs:
            kwargs["width"] = 100
        if "height" not in kwargs:
            kwargs["height"] = 50
        if "texture" not in kwargs:
            kwargs["texture"] = Texture.create_empty(
                f"{self.__class__}_{kwargs}",
                (kwargs["width"], kwargs["height"]),
                kwargs["color"] if "color" in kwargs else Color.TRANSPARENT_WHITE
            )
        super().__init__(**kwargs)
