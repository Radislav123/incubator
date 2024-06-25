import copy
import operator
import random
from collections import deque
from typing import Callable, TYPE_CHECKING


if TYPE_CHECKING:
    from snake.component.world import World

Comparator = Callable[[float, float], bool]
SectorFunction = tuple[Comparator, float]


class Map:
    side_length: int
    square_side_length: int
    default_map: list[list[bool | None]] = None
    sector_cache: dict[tuple[int, int, int], set[tuple[int, int]]] = {}

    def __init__(self, world: "World") -> None:
        if self.default_map is None:
            self.__class__.side_length = world.tiles_in_radius + world.border_thickness
            self.__class__.square_side_length = self.side_length * 2 - 1
            self.__class__.default_map = [[None for _ in range(self.square_side_length)]
                                          for _ in range(self.square_side_length)]

        self.surface = copy.deepcopy(self.default_map)
        self.borders = copy.deepcopy(self.default_map)
        self.snake = copy.deepcopy(self.default_map)
        self.food = copy.deepcopy(self.default_map)
        self.offsets = (
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1)
        )
        self.prepare_submaps(world)

        # y = -0.5x
        # y = -2x
        # y = x
        # {direction: ((>, coeff), (>, coeff))
        # https://www.desmos.com/calculator/pswa9sn0cw?lang=ru
        self.sector_functions: tuple[tuple[SectorFunction, SectorFunction], ...] = (
            ((operator.ge, -0.5), (operator.lt, 1)),
            ((operator.ge, 1), (operator.gt, -2)),
            ((operator.le, -2), (operator.gt, -0.5)),
            ((operator.le, -0.5), (operator.gt, 1)),
            ((operator.le, 1), (operator.lt, -2)),
            ((operator.ge, -2), (operator.lt, -0.5))
        )
        self.direction_distance_correction = (1, 1, 2**(1 / 2), 1, 1, 2**(1 / 2))
        self.all_directions_amount = len(self.offsets)
        # количество направлений для движения змеи
        self.directions_amount = 3

    # noinspection DuplicatedCode
    def prepare_submaps(self, world: "World") -> None:
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
                    tile = world.all_tiles[index]
                    self.surface[x][y] = tile.is_surface
                    self.borders[x][y] = tile.is_border
                    self.snake[x][y] = False
                    self.food[x][y] = False
                    tile.map_x = x
                    tile.map_y = y
                    index += 1

    def place_food(self) -> None:
        free_tiles = [(x, y) for x in range(self.square_side_length) for y in range(self.square_side_length)
                      if self.surface[x][y] and not self.borders[x][y] and not self.snake[x][y]]
        tile = free_tiles[random.randint(0, len(free_tiles) - 1)]
        if (10, 10) in free_tiles:
            tile = (10, 10)

        self.food[tile[0]][tile[1]] = True

    def belongs_to_sector(self, head_x: int, head_y: int, direction: int, x: int, y: int) -> bool:
        satisfy = True
        for comparator, coeff in self.sector_functions[direction]:
            comparator: Comparator
            satisfy *= comparator(y, coeff * (x - head_x) + head_y)
        return bool(satisfy)

    def get_sector(self, head_x: int, head_y: int, direction: int) -> set[tuple[int, int]]:
        cache_key = (head_x, head_y, direction)
        if cache_key not in self.sector_cache:
            directions_amount = 3
            start_direction_offset = -(directions_amount // 2)
            direction_offsets = range(start_direction_offset, directions_amount + start_direction_offset, 1)
            neighbour_directions = [(direction + x + self.all_directions_amount) % self.all_directions_amount
                                    for x in direction_offsets]
            sector = set()
            offsets = self.offsets

            queue = deque[tuple[int, int]]()
            queue.append((head_x + self.offsets[direction][0], head_y + self.offsets[direction][1]))
            while len(queue) > 0:
                x, y = queue.popleft()
                on_map = (0 <= x < self.square_side_length and 0 <= y < self.square_side_length
                          and self.surface[x][y] is not None)
                if (x, y) not in sector and on_map and self.belongs_to_sector(head_x, head_y, direction, x, y):
                    sector.add((x, y))
                    neighbours = ((x + offsets[neighbour_direction][0], y + offsets[neighbour_direction][1])
                                  for neighbour_direction in neighbour_directions)
                    queue.extend(neighbours)
            self.sector_cache[cache_key] = sector

        return self.sector_cache[cache_key]
