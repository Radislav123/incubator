import json

from snake.component.brain import Brain
from snake.component.snake import Snake
from snake.component.world import Map


class Arena:
    snake: Snake

    def __init__(self, brain: Brain | str | None, world_map: Map) -> None:
        self.brain = brain
        self.world_map = world_map
        self.load_snake()
        self.world_map.place_food()

    def dump_brain(self, path: str) -> None:
        with open(path, 'w') as file:
            json.dump(self.snake.brain.dump(), file, indent = 4)

    def load_brain(self) -> Brain:
        if self.brain is None:
            brain = Brain.get_default()
        else:
            with open(self.brain, 'r') as file:
                brain = Brain.load(json.load(file))
        return brain

    def load_snake(self) -> None:
        if isinstance(self.brain, Brain):
            self.snake = Snake(self.brain, self.world_map)
        else:
            self.snake = Snake(self.load_brain(), self.world_map)

    def perform(self) -> None:
        self.snake.perform()
