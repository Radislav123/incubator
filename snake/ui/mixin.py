from arcade.gui import UISlider, UITextureButton

from core.texture import Texture
from snake.service.color import Color
from snake.settings import Settings


# noinspection DuplicatedCode
class SnakeStyleButtonMixin:
    settings = Settings()

    DEFAULT_COLORS = {
        "texture": Color.NORMAL,
        "texture_hovered": Color.HOVERED,
        "texture_pressed": Color.PRESSED,
        "texture_disabled": Color.DISABLED
    }
    normal_style = UITextureButton.UIStyle(font_size = 14, font_name = settings.FONTS, font_color = Color.TEXT)
    hovered_style = UITextureButton.UIStyle(font_size = 16, font_name = settings.FONTS, font_color = Color.TEXT)
    DEFAULT_STYLE = {
        "normal": normal_style,
        "hover": hovered_style,
        "press": hovered_style,
        "disabled": normal_style
    }
    DEFAULT_TEXTURES = {
        "normal": Texture.create_rounded_rectangle(color = Color.NORMAL),
        "hover": Texture.create_rounded_rectangle(color = Color.HOVERED),
        "press": Texture.create_rounded_rectangle(color = Color.PRESSED),
        "disabled": Texture.create_rounded_rectangle(color = Color.DISABLED)
    }
    DEFAULT_TEXTURES_INIT = {
        "texture": DEFAULT_TEXTURES["normal"],
        "texture_hovered": DEFAULT_TEXTURES["hover"],
        "texture_pressed": DEFAULT_TEXTURES["press"],
        "texture_disabled": DEFAULT_TEXTURES["disabled"]
    }


class SnakeStyleSliderMixin:
    settings = Settings()

    normal_style = UISlider.UIStyle(bg = Color.SLIDER_NORMAL, border = Color.BORDER)
    hovered_style = UISlider.UIStyle(bg = Color.SLIDER_HOVERED, border = Color.BORDER)
    DEFAULT_STYLE = {
        "normal": normal_style,
        "hover": hovered_style,
        "press": hovered_style,
        "disabled": normal_style
    }
