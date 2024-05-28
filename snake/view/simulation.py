import copy
import json

from core.service.anchor import Anchor
from core.ui.layout import BoxLayout
from core.view.simulation import SimulationView as CoreSimulationView
from snake.component.arena import Arena
from snake.component.brain import Brain
from snake.component.map import Map
from snake.component.snake import Snake
from snake.component.world import World
from snake.service.color import Color
from snake.settings import Settings
from snake.ui import ExitButton, PauseButton, RestartButton, SpeedButton


class SimulationView(CoreSimulationView):
    settings = Settings()
    update_rate = 1 / 10**10
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton
    speed_button: SpeedButton
    pause_button: PauseButton
    restart_button: RestartButton

    world: World
    arena: Arena = None
    snake_perform_timer: float
    snake_released: bool
    snake_brain_path = settings.CLEAN_BRAIN_PATH

    @staticmethod
    def dump_brain(path: str, brain: Brain) -> None:
        with open(path, 'w') as file:
            data = brain.dump()
            json.dump(data, file, indent = 4)

    @classmethod
    def load_brain(cls) -> Brain:
        with open(cls.snake_brain_path, 'r') as file:
            data = json.load(file)
            brain = Brain.load(data)
        return brain

    @classmethod
    def load_snake(cls, world_map: Map) -> Snake:
        brain = cls.load_brain()
        snake = Snake(brain, world_map)
        return snake

    def prepare_arena(self) -> Arena:
        world_map = copy.deepcopy(self.world.reference_map)
        snake = self.load_snake(world_map)
        arena = Arena(snake, world_map)
        self.snake_perform_timer = 0
        return arena

    def prepare_buttons(self) -> None:
        layout = BoxLayout()

        self.speed_button = SpeedButton(self)
        layout.add(self.speed_button)

        self.pause_button = PauseButton(self)
        layout.add(self.pause_button)

        self.restart_button = RestartButton(self)
        layout.add(self.restart_button)

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

        # todo: remove 2 lines
        self.arena = self.prepare_arena()
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
            if self.arena.snake.alive and self.snake_perform_timer > (period := 1 / self.speed_button.speed):
                self.snake_perform_timer -= period
                self.arena.snake.perform()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
