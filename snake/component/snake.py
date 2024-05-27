from typing import TYPE_CHECKING

from snake.component.brain import Brain
from snake.service.color import Color


if TYPE_CHECKING:
    from snake.component.world import Map, World


class Segment:
    color = Color.SNAKE_SEGMENT_ALIVE

    def __init__(self, world_mao: "Map", x: int, y: int) -> None:
        self.map = world_mao
        self.x = x
        self.y = y

    def move_to(self, x: int, y: int) -> tuple[int, int]:
        self.map.snake[self.x][self.y] = None
        previous_x = self.x
        previous_y = self.y
        self.x = x
        self.y = y
        self.map.snake[self.x][self.y] = self
        return previous_x, previous_y


class Snake:
    brain: Brain

    def __init__(self, world: "World") -> None:
        self.age = 0
        self.starvation = 0
        self.max_starvation = 100
        self.world = world
        self.map = self.world.map
        self.alive = True
        self.direction = 0
        self.directions = (
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1)
        )

        self.segments: list[Segment] = []
        self.add_segment(self.map.side_length - 1, self.map.side_length - 1)
        self.head = self.segments[0]

    def add_segment(self, x: int, y: int) -> None:
        segment = Segment(self.map, x, y)
        self.segments.append(segment)
        self.map.snake[x][y] = segment

    def move(self, offset_x: int, offset_y: int) -> None:
        x = self.segments[0].x + offset_x
        y = self.segments[0].y + offset_y
        for segment in self.segments:
            x, y = segment.move_to(x, y)

    def choose_direction(self) -> None:
        self.brain.process([0])

        directions_amount = len(self.directions)
        direction_change = self.brain.output + directions_amount
        self.direction = (self.direction + direction_change) % direction_change

    def eat(self) -> None:
        if self.map.tiles[self.head.x][self.head.y].food is not None:
            self.starvation = 0
            # todo: прописать случай, когда некуда разместить еду?
            self.world.place_food(False)
        else:
            self.starvation += 1

    def perform(self) -> None:
        self.choose_direction()
        move_x, move_y = self.directions[self.direction]

        border_collision = self.map.tiles[self.head.x + move_x][self.head.y + move_y].border_tile
        segment_collision = self.map.snake[self.head.x + move_x][self.head.y + move_y] is not None
        starvation_death = self.starvation > self.max_starvation

        self.alive = not (border_collision or segment_collision or starvation_death)
        if self.alive:
            self.move(move_x, move_y)
            self.eat()
        else:
            Segment.color = Color.SNAKE_SEGMENT_DEAD

        self.age += 1
