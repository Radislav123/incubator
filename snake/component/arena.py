from snake.component.snake import Snake


class Arena:
    def __init__(self, snake: Snake) -> None:
        self.snake = snake
        self.world_map = self.snake.world_map
        self.world_map.place_food()

    def perform(self) -> None:
        self.snake.perform()
        if self.snake.starvation == 0:
            self.world_map.place_food()
