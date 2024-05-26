from arcade.gui import UITextureButton

from core.view.simulation import ExitButton as CoreExitButton, SimulationView as CoreSimulationView
from snake.component.snake import Snake
from snake.component.world import World
from snake.service.color import Color
from snake.settings import Settings


# noinspection DuplicatedCode
class ExitButton(CoreExitButton):
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


class SimulationView(CoreSimulationView):
    settings = Settings()
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton

    world: World
    snake: Snake

    def on_show_view(self) -> None:
        super().on_show_view()

        self.world = World(self)
        self.snake = Snake(self.world.map)

    def on_draw(self) -> None:
        super().on_draw()

        for tile in self.world.all_tiles:
            tile.update_color()
        self.world.all_tiles.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
