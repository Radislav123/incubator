import copy
import json

import PIL.Image
from arcade.gui import UIOnClickEvent, UITextureButton

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.button import TextureButton
from core.ui.layout import BoxLayout
from core.view.simulation import ExitButton as CoreExitButton, SimulationView as CoreSimulationView
from snake.component.arena import Arena
from snake.component.brain import Brain
from snake.component.map import Map
from snake.component.snake import Snake
from snake.component.world import World
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
    normal_style = UITextureButton.UIStyle(font_size = 12, font_name = settings.FONTS, font_color = Color.TEXT)
    hovered_style = UITextureButton.UIStyle(font_size = 14, font_name = settings.FONTS, font_color = Color.TEXT)
    DEFAULT_STYLE = {
        "normal": normal_style,
        "hover": hovered_style,
        "press": hovered_style,
        "disabled": normal_style
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
            default_textures = {
                "normal": Texture.create_rounded_rectangle(color = Color.NORMAL),
                "hover": Texture.create_rounded_rectangle(color = Color.HOVERED),
                "press": Texture.create_rounded_rectangle(color = Color.PRESSED),
                "disabled": Texture.create_rounded_rectangle(color = Color.DISABLED)
            }
            images = {
                True: PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/play_0.png"),
                False: PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/pause_0.png")
            }
            self.__class__.default_textures = {button_state: {state: Texture.from_texture(texture).with_image(image)
                                                              for state, texture in default_textures.items()}
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


class SimulationView(CoreSimulationView):
    settings = Settings()
    update_rate = 1 / 10**10
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton
    speed_button: SpeedButton
    pause_button: PauseButton

    world: World
    arena: Arena = None
    snake_perform_timer: float
    snake_released: bool

    @staticmethod
    def load_brain(path: str) -> Brain:
        with open(path, 'r') as file:
            data = json.load(file)
            brain = Brain.load(data)
        return brain

    @staticmethod
    def dump_brain(path: str, brain: Brain) -> None:
        with open(path, 'w') as file:
            data = brain.dump()
            json.dump(data, file, indent = 4)

    @classmethod
    def load_snake(cls, path: str, world_map: Map) -> Snake:
        brain = cls.load_brain(path)
        snake = Snake(brain, world_map)
        return snake

    def create_arena(self, path: str) -> Arena:
        world_map = copy.deepcopy(self.world.reference_map)
        snake = self.load_snake(path, world_map)
        arena = Arena(snake, world_map)
        return arena

    def prepare_buttons(self) -> None:
        layout = BoxLayout()

        self.speed_button = SpeedButton(self)
        layout.add(self.speed_button)

        self.pause_button = PauseButton(self)
        layout.add(self.pause_button)

        layout.fit_content()
        layout.move_to(self.window.width, 0, Anchor.X.RIGHT, Anchor.Y.DOWN)
        self.ui_manager.add(layout)

    def prepare_world(self) -> None:
        self.world = World(self)

    def on_show_view(self) -> None:
        super().on_show_view()
        self.prepare_buttons()
        self.prepare_world()
        self.snake_released = False
        self.snake_perform_timer = 0

        # todo: remove 2 lines
        self.arena = self.create_arena(self.settings.CLEAN_BRAIN_PATH)
        self.snake_released = True

    def on_draw(self) -> None:
        self.speed_button.update_text()
        super().on_draw()

        for tile in self.world.all_tiles:
            tile.update_color()
        self.world.all_tiles.draw()

    def on_update(self, delta_time: float) -> None:
        if self.snake_released and not self.pause_button.enabled:
            self.snake_perform_timer += delta_time
            if self.arena is not None:
                self.snake_perform_timer += delta_time
                if self.arena.snake.alive and self.snake_perform_timer > (period := 1 / self.speed_button.speed):
                    self.snake_perform_timer -= period
                    self.arena.snake.perform()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
