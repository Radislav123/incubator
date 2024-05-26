from typing import TYPE_CHECKING

from snake.service.color import Color


if TYPE_CHECKING:
    from snake.component.world import Map


class Segment:
    color = Color.SNAKE_SEGMENT

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Snake:
    def __init__(self, world_map: "Map") -> None:
        self.map = world_map
        self.segments: list[Segment] = []
        self.add_segment(self.map.side_length - 1, self.map.side_length - 1)

    def add_segment(self, x: int, y: int) -> None:
        segment = Segment(x, y)
        self.segments.append(segment)
        self.map.snake[x][y] = segment
