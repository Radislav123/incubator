from snake.component.snake import Snake
from snake.component.world import Map


class Arena:
    def __init__(self, snake: Snake, world_map: Map) -> None:
        self.snake = snake
        self.world_map = world_map
        self.world_map.place_food()

    def perform(self) -> None:
        self.snake.perform()
        if self.snake.starvation == 0:
            self.world_map.place_food()
