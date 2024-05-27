from typing import TYPE_CHECKING

from snake.service.color import Color


if TYPE_CHECKING:
    from snake.component.world import Map


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
    def __init__(self, world_map: "Map") -> None:
        self.map = world_map
        self.segments: list[Segment] = []
        self.add_segment(self.map.side_length - 1, self.map.side_length - 1)
        self.head = self.segments[0]
        self.alive = True

    def add_segment(self, x: int, y: int) -> None:
        segment = Segment(self.map, x, y)
        self.segments.append(segment)
        self.map.snake[x][y] = segment

    def move(self, offset_x: int, offset_y: int) -> None:
        x = self.segments[0].x + offset_x
        y = self.segments[0].y + offset_y
        for segment in self.segments:
            x, y = segment.move_to(x, y)

    def perform(self) -> None:
        move_x = 0
        move_y = 1

        border_collision = self.map.tiles[self.head.x + move_x][self.head.y + move_y].border_tile
        segment_collision = self.map.snake[self.head.x + move_x][self.head.y + move_y] is not None
        self.alive = not (border_collision or segment_collision)
        if self.alive:
            self.move(move_x, move_y)
        else:
            Segment.color = Color.SNAKE_SEGMENT_DEAD
