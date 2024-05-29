import json

from snake.component.brain import Brain
from snake.component.snake import Snake
from snake.component.world import Map


class Arena:
    snake: Snake

    def __init__(self, brain_path: str, world_map: Map) -> None:
        self.brain_path = brain_path
        self.world_map = world_map
        self.load_snake()
        self.world_map.place_food()

    def dump_brain(self) -> None:
        with open(self.brain_path, 'w') as file:
            data = self.snake.brain.dump()
            json.dump(data, file, indent = 4)

    def load_brain(self) -> Brain:
        with open(self.brain_path, 'r') as file:
            data = json.load(file)
            brain = Brain.load(data)
        return brain

    def load_snake(self) -> None:
        # todo: return line
        # brain = self.load_brain()
        brain = Brain.get_default()
        self.snake = Snake(brain, self.world_map)

    def perform(self) -> None:
        self.snake.perform()
        if self.snake.starvation == 0:
            self.world_map.place_food()
