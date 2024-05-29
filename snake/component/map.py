import copy
import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from snake.component.world import World


class Map:
    def __init__(self, world: "World") -> None:
        self.side_length = world.tiles_in_radius + world.border_thickness
        self.square_side_length = self.side_length * 2 - 1
        default_map: list[list[bool | None]] = [[None for _ in range(self.square_side_length)]
                                                for _ in range(self.square_side_length)]
        self.surface = copy.deepcopy(default_map)
        self.borders = copy.deepcopy(default_map)
        self.snake = copy.deepcopy(default_map)
        self.food = copy.deepcopy(default_map)

        self.offsets = (
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1)
        )
        x = self.side_length - 1
        y = self.side_length - 1
        tile = world.all_tiles[0]
        self.surface[x][y] = tile.is_surface
        self.borders[x][y] = tile.is_border
        self.snake[x][y] = False
        self.food[x][y] = False
        tile.map_x = x
        tile.map_y = y

        index = 1
        for edge_size in range(1, self.side_length):
            y -= 1
            for offset_x, offset_y in self.offsets:
                for _ in range(edge_size):
                    x += offset_x
                    y += offset_y
                    self.surface[x][y] = tile.is_surface
                    self.borders[x][y] = tile.is_border
                    self.snake[x][y] = False
                    self.food[x][y] = False
                    tile = world.all_tiles[index]
                    tile.map_x = x
                    tile.map_y = y
                    index += 1

    def place_food(self) -> None:
        free_tiles = [(x, y) for x in range(self.square_side_length) for y in range(self.square_side_length)
                      if self.surface[x][y] and not self.borders[x][y] and not self.snake[x][y]]
        tile = free_tiles[random.randint(0, len(free_tiles) - 1)]

        self.food[tile[0]][tile[1]] = True
