from typing import TYPE_CHECKING

import PIL.Image
from arcade.gui import UIOnClickEvent

from apps.snake.settings import Settings
from apps.snake.ui.mixin import SnakeStyleButtonMixin
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.view.simulation import ExitButton as CoreExitButton


if TYPE_CHECKING:
    from apps.snake.view.simulation import SimulationView


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
        self.view.released_arena = self.view.prepare_released_arena()
        self.view.prepare_brain_map()
