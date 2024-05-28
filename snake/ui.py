from typing import TYPE_CHECKING

import PIL.Image
from arcade.gui import UIOnClickEvent, UITextureButton

from core.texture import Texture
from core.ui.button import TextureButton
from core.ui.layout import BoxLayout
from core.view.simulation import ExitButton as CoreExitButton
from snake.service.color import Color
from snake.settings import Settings


if TYPE_CHECKING:
    from snake.component.brain import Neuron
    from snake.view.simulation import SimulationView


# noinspection DuplicatedCode
class SnakeStyleButtonMixin:
    settings = Settings()

    DEFAULT_COLORS = {
        "texture": Color.NORMAL,
        "texture_hovered": Color.HOVERED,
        "texture_pressed": Color.PRESSED,
        "texture_disabled": Color.DISABLED
    }
    normal_style = UITextureButton.UIStyle(font_size = 12, font_name = settings.FONTS, font_color = Color.TEXT)
    hovered_style = UITextureButton.UIStyle(font_size = 14, font_name = settings.FONTS, font_color = Color.TEXT)
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


class ExitButton(SnakeStyleButtonMixin, CoreExitButton):
    pass


class SpeedButton(SnakeStyleButtonMixin, TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.base_speed = 1
        self.speed = self.base_speed
        self.speed_multiplier = 2
        self.max_speed = 64
        super().__init__(text = self.get_text(), **kwargs)
        self.view = view

    def get_text(self) -> str:
        return f"{self.speed}x"

    def update_text(self) -> None:
        if (text := self.get_text()) != self.text:
            self.text = text

    def on_click(self, event: UIOnClickEvent) -> None:
        self.speed *= self.speed_multiplier
        if self.speed > self.max_speed:
            self.speed = self.base_speed

        self.update_text()


class PauseButton(SnakeStyleButtonMixin, TextureButton):
    default_textures: dict[bool, dict[str, Texture]] = None

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.enabled = True
        kwargs.update(self.get_textures_init())
        super().__init__(**kwargs)

    def get_textures_init(self) -> dict[str, Texture]:
        if self.default_textures is None:
            images = {
                True: PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/play_0.png"),
                False: PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/pause_0.png")
            }
            self.__class__.default_textures = {button_state: {state: Texture.from_texture(texture).with_image(image)
                                                              for state, texture in self.DEFAULT_TEXTURES.items()}
                                               for button_state, image in images.items()}

        return {
            "texture": self.default_textures[self.enabled]["normal"],
            "texture_hovered": self.default_textures[self.enabled]["hover"],
            "texture_pressed": self.default_textures[self.enabled]["press"],
            "texture_disabled": self.default_textures[self.enabled]["disabled"]
        }

    def update_textures(self) -> None:
        self._textures = self.default_textures[self.enabled]

    def on_click(self, event: UIOnClickEvent) -> None:
        self.enabled = not self.enabled
        self.update_textures()


class RestartButton(SnakeStyleButtonMixin, TextureButton):
    settings = Settings()

    image = PIL.Image.open(f"{settings.IMAGES_FOLDER}/restart_0.png")
    default_textures: dict[str, Texture] = None

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        if self.default_textures is None:
            self.__class__.default_textures = {
                name: Texture.from_texture(SnakeStyleButtonMixin.DEFAULT_TEXTURES_INIT[name]).with_image(self.image)
                for name in ["texture", "texture_hovered", "texture_pressed", "texture_disabled"]
            }

        self.view = view
        kwargs.update(self.default_textures)
        super().__init__(**kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.arena = self.view.create_arena()


class NeuronMap(SnakeStyleButtonMixin, TextureButton):
    def __init__(self, neuron: "Neuron", **kwargs) -> None:
        radius = 20
        texture = Texture.create_circle(radius, color = Color.NEURON_SLEEP)
        super().__init__(texture = texture, width = radius * 2, height = radius * 2, **kwargs)
        self.neuron = neuron


class BrainMap(BoxLayout):
    settings = Settings()

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.brain = self.view.arena.snake.brain
        layers = [BoxLayout(children = [NeuronMap(neuron) for neuron in layer], space_between = self.gap)
                  for layer in self.brain.layers]

        super().__init__(vertical = False, children = layers, space_between = self.gap * 4, **kwargs)
        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(
            texture = Texture.create_rounded_rectangle(
                self.size,
                color = Color.NORMAL,
                border_color = Color.BORDER
            )
        )
