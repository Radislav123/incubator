import copy
import datetime
import time
from pathlib import Path

from apps.snake.component.arena import Arena
from apps.snake.component.brain import Brain
from apps.snake.component.snake import Snake
from apps.snake.component.world import World
from apps.snake.service.color import Color
from apps.snake.settings import Settings
from apps.snake.ui.action_tab import ActionTab
from apps.snake.ui.brain_map import BrainMap
from apps.snake.ui.control import ExitButton, PauseButton, RestartButton, SpeedButton
from apps.snake.ui.load_tab import LoadTab
from apps.snake.ui.train_tab import TrainTab
from core.service.anchor import Anchor
from core.ui.layout.box_layout import BoxLayout
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()
    update_rate = 1 / 60
    train_update_rate = 1 / 10**10
    max_latency = 1 / 20
    background_color = Color.BACKGROUND

    exit_button_class = ExitButton
    speed_button: SpeedButton = None
    pause_button: PauseButton = None
    restart_button: RestartButton = None

    load_tab: LoadTab = None
    action_tab: ActionTab = None
    train_tab: TrainTab = None

    world: World = None
    snake_perform_timer: float
    released_arena: Arena = None
    snake_released: bool = False
    brain_map: BrainMap = None

    reference_brains_amount: int | None
    reference_brains: list[Brain] = None
    snake_training: bool
    start_generation: int | None = None
    max_generation: int | None = None
    generation_size_by_brain: int | None = None
    training_arena_index: int
    training_arenas: list[Arena] = None
    show_training = False
    show_sensored_tiles = False

    training_start_time: datetime.datetime | None
    last_generation_trained_time: datetime.datetime | None
    best_brains_amount = 3
    best_brains: list[Brain] | None
    save_best_brains = False

    def prepare_buttons(self) -> None:
        layout = BoxLayout()

        if self.speed_button is None:
            self.speed_button = SpeedButton(self)
        layout.add(self.speed_button)

        if self.pause_button is None:
            self.pause_button = PauseButton(self)
        layout.add(self.pause_button)

        if self.restart_button is None:
            self.restart_button = RestartButton(self)
        layout.add(self.restart_button)

        layout.fit_content()
        layout.move_to(self.window.width, 0, Anchor.X.RIGHT, Anchor.Y.DOWN)
        self.ui_manager.add(layout)

    def prepare_world(self) -> None:
        if self.world is None:
            self.world = World(self)

    def prepare_released_arena(self) -> Arena:
        world_map = copy.deepcopy(self.world.reference_map)
        snake = Snake(self.reference_brains[0], world_map)
        arena = Arena(snake)
        self.snake_perform_timer = 0
        return arena

    def prepare_brain_map(self) -> None:
        if self.brain_map is not None:
            self.ui_manager.remove(self.brain_map)

        self.brain_map = BrainMap(self)
        self.brain_map.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
        self.ui_manager.add(self.brain_map)

    def prepare_training_arenas(self) -> None:
        if self.training_start_time is None:
            self.training_start_time = datetime.datetime.now()
        else:
            self.last_generation_trained_time = datetime.datetime.now()

        self.training_arenas = [Arena(Snake(brain.mutate(), copy.deepcopy(self.world.reference_map))) for _ in
                                range(self.generation_size_by_brain - 1) for brain in self.reference_brains]
        self.training_arenas.extend(
            Arena(Snake(brain, copy.deepcopy(self.world.reference_map))) for brain in self.reference_brains
        )
        self.training_arena_index = 0

        if self.show_training:
            self.released_arena = self.training_arenas[self.training_arena_index]
            self.prepare_brain_map()

    def prepare_load_tab(self) -> None:
        if self.load_tab is None:
            self.load_tab = LoadTab(self)

        self.load_tab.update_loads()
        self.ui_manager.add(self.load_tab)

    def prepare_actions_tab(self) -> None:
        if self.action_tab is None:
            self.action_tab = ActionTab(self)

        self.ui_manager.add(self.action_tab)

    def prepare_train_tab(self) -> None:
        if self.train_tab is None:
            self.train_tab = TrainTab(self)

        self.ui_manager.add(self.train_tab)

    def on_show_view(self) -> None:
        super().on_show_view()
        self.prepare_buttons()
        self.prepare_world()
        self.prepare_load_tab()
        self.snake_training = False
        self.training_start_time = None
        self.last_generation_trained_time = None

    def on_hide_view(self) -> None:
        super().on_hide_view()
        self.snake_released = False

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

        if self.snake_training:
            self.train_tab.update_labels()

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
                for arena in self.training_arenas:
                    arena.snake.brain.score = arena.snake.get_score()
                    arena.snake.brain.age = arena.snake.age
                brains = [x.snake.brain for x in
                          sorted(self.training_arenas, key = lambda x: x.snake.brain.score, reverse = True)]

                if self.save_best_brains:
                    self.best_brains.extend(brains[:self.best_brains_amount])
                    self.best_brains.sort(key = lambda x: x.score, reverse = True)
                    self.best_brains = self.best_brains[:self.best_brains_amount]

                self.reference_brains = brains[:self.reference_brains_amount]
                for brain in self.reference_brains:
                    brain.generation += 1

                self.reference_brains = copy.deepcopy(self.reference_brains)
                if self.reference_brains[0].generation < self.max_generation:
                    self.prepare_training_arenas()
                else:
                    folder = Path(self.settings.BRAINS_PATH)
                    if not folder.exists():
                        folder.mkdir(parents = True)
                    if self.save_best_brains:
                        for brain in self.best_brains:
                            brain.dump_to_file(f"{folder}/{brain.save_name}")
                    for brain in self.reference_brains:
                        brain.dump_to_file(f"{folder}/{brain.save_name}")

                    self.snake_training = False
                    self.max_generation = None
                    self.ui_manager.remove(self.train_tab)
                    self.prepare_load_tab()
                    self.window.set_update_rate(self.update_rate)

    def train(self, cycles: int) -> bool:
        for _ in range(cycles):
            if self.training_arena_index < len(self.training_arenas):
                arena = self.training_arenas[self.training_arena_index]
                if arena.snake.alive:
                    arena.perform()
                else:
                    self.training_arena_index += 1
                    if self.show_training and self.training_arena_index < len(self.training_arenas):
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
        tile = self.world.position_to_tile((x, y))
        self.logger.debug(tile)
