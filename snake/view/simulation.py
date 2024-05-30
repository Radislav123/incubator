import copy
import time
from pathlib import Path

from core.service.anchor import Anchor
from core.ui.layout.box_layout import BoxLayout
from core.view.simulation import SimulationView as CoreSimulationView
from snake.component.arena import Arena
from snake.component.brain import Brain
from snake.component.world import World
from snake.service.color import Color
from snake.settings import Settings
from snake.ui.brain_map import BrainMap
from snake.ui.control import ExitButton, PauseButton, RestartButton, SpeedButton


class SimulationView(CoreSimulationView):
    settings = Settings()
    update_rate = 1 / 10**10
    max_latency = 1 / 100
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton
    speed_button: SpeedButton
    pause_button: PauseButton
    restart_button: RestartButton

    world: World
    snake_perform_timer: float
    released_arena: Arena = None
    snake_released: bool = False
    brain_map: BrainMap = None

    brain: Brain | str | None = None
    reference_brain: Brain
    snake_training: bool = False
    max_generation: int = 10
    generation_size: int = 10
    training_arena_index: int
    training_arenas: list[Arena] = None
    show_training = False

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

    def create_arena(self) -> Arena:
        world_map = copy.deepcopy(self.world.reference_map)
        arena = Arena(self.brain, world_map)
        self.snake_perform_timer = 0
        return arena

    def prepare_brain_map(self) -> None:
        if self.brain_map is not None:
            self.ui_manager.remove(self.brain_map)

        self.brain_map = BrainMap(self)
        self.brain_map.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
        self.ui_manager.add(self.brain_map)

    def prepare_training_arenas(self) -> None:
        self.reference_brain.generation += 1
        self.training_arenas = [Arena(self.reference_brain.mutate(), copy.deepcopy(self.world.reference_map))
                                for _ in range(self.generation_size - 1)]
        self.training_arenas.append(Arena(self.reference_brain, copy.deepcopy(self.world.reference_map)))
        self.training_arena_index = 0

        if self.show_training:
            self.released_arena = self.training_arenas[self.training_arena_index]
            self.prepare_brain_map()

    def on_show_view(self) -> None:
        super().on_show_view()
        self.prepare_buttons()
        self.prepare_world()

        # todo: rewrite this lines
        self.reference_brain = Brain.get_default()
        self.prepare_training_arenas()
        self.snake_training = True

        # todo: remove 3 lines
        # self.released_arena = self.create_arena()
        # self.prepare_brain_map()
        # self.snake_released = True

    def on_draw(self) -> None:
        self.speed_button.update_text()
        super().on_draw()

        for tile in self.world.all_tiles:
            tile.update_color()
        self.world.all_tiles.draw()

        if (self.snake_released or self.show_training) and self.brain_map is not None:
            self.brain_map.synapses.draw()
            for neuron_map in self.brain_map.all_neuron_maps:
                neuron_map.update_texture()

    def on_update(self, delta_time: float) -> None:
        if self.snake_released and not self.pause_button.enabled:
            self.snake_perform_timer += delta_time
            if self.released_arena.snake.alive and self.snake_perform_timer > (period := 1 / self.speed_button.speed):
                self.snake_perform_timer -= period
                self.released_arena.perform()
        elif self.snake_training:
            latency = 0
            cycles = 100
            generation_trained = False

            while latency < self.max_latency and not generation_trained:
                start = time.time()
                generation_trained = self.train(cycles)
                finish = time.time()
                latency += finish - start

            if generation_trained:
                scores = {arena.snake.get_score(): arena for arena in self.training_arenas}
                arena = scores[max(scores)]
                self.reference_brain = arena.snake.brain
                if self.reference_brain.generation < self.max_generation:
                    self.prepare_training_arenas()
                else:
                    folder = Path(self.settings.BRAINS_PATH)
                    if not folder.exists():
                        folder.mkdir(parents = True)
                    arena.dump_brain(f"{folder}/{arena.snake.brain.save_name}")
                    self.snake_training = False

    def train(self, cycles: int) -> bool:
        for _ in range(cycles):
            if self.training_arena_index < self.generation_size:
                arena = self.training_arenas[self.training_arena_index]
                if arena.snake.alive:
                    arena.perform()
                else:
                    self.training_arena_index += 1
                    if self.show_training and self.training_arena_index < self.generation_size:
                        self.released_arena = self.training_arenas[self.training_arena_index]
                        self.prepare_brain_map()
            else:
                generation_trained = True
                break
        else:
            generation_trained = False
        return generation_trained

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
