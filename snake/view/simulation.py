from arcade.gui import UIOnClickEvent, UITextureButton

from core.service.anchor import Anchor
from core.ui.button import TextureButton
from core.view.simulation import ExitButton as CoreExitButton, SimulationView as CoreSimulationView
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
    def __init__(self, view: "SimulationView", *args, **kwargs) -> None:
        self.base_speed = 1
        self.speed = self.base_speed
        self.speed_multiplier = 2
        self.max_speed = 64
        super().__init__(*args, text = self.get_text(), **kwargs)
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


class SimulationView(CoreSimulationView):
    settings = Settings()
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton
    speed_button: SpeedButton

    world: World
    snake: Snake
    snake_perform_timer: float

    def on_show_view(self) -> None:
        super().on_show_view()

        self.speed_button = SpeedButton(self)
        self.speed_button.move_to(self.window.width, 0, Anchor.X.RIGHT, Anchor.Y.DOWN)
        self.ui_manager.add(self.speed_button)

        self.world = World(self)
        self.snake = Snake(self.world)
        self.snake_perform_timer = 0

    def on_draw(self) -> None:
        self.speed_button.update_text()
        super().on_draw()

        for tile in self.world.all_tiles:
            tile.update_color()
        self.world.all_tiles.draw()
        self.world.food.draw()

    def on_update(self, delta_time: float) -> None:
        self.snake_perform_timer += delta_time
        if self.snake.alive and self.snake_perform_timer > (period := 1 / self.speed_button.speed):
            self.snake_perform_timer -= period
            self.snake.perform()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
