import math
from typing import TYPE_CHECKING

import PIL.Image
import arcade
from arcade import Sprite, SpriteList

from core.texture import Texture
from snake.component.map import Map
from snake.service.color import Color
from snake.settings import Settings


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView

Position = tuple[float, float] | list[float]


class Tile(Sprite):
    settings = Settings()

    colors: dict[bool, Color]
    default_border_color = Color.TILE_BORDER
    image_path = f"{settings.IMAGES_FOLDER}/hexagon_0.png"
    _texture: Texture = None

    overlap_distance = 1.5
    radius = 20
    default_width = float(math.sqrt(3) * radius + overlap_distance)
    default_height = float(2 * radius + overlap_distance)

    map_x: int
    map_y: int
    is_surface = False
    is_border = False

    # границы плиток должны задаваться с небольшим наслоением, так как границы не считаются их частью
    # если граница проходит по 400 координате, то 399.(9) принадлежит плитке, а 400 уже - нет
    def __init__(self, center: Position, world: "World") -> None:
        self.world = world
        self.enabled = False
        super().__init__(self.get_texture(), center_x = center[0], center_y = center[1])

        self.border_points = (
            (self.center_x - self.width / 2, self.center_y - self.height / 4),
            (self.center_x - self.width / 2, self.center_y + self.height / 4),
            (self.center_x, self.center_y + self.height / 2),
            (self.center_x + self.width / 2, self.center_y + self.height / 4),
            (self.center_x + self.width / 2, self.center_y - self.height / 4),
            (self.center_x, self.center_y - self.height / 2)
        )
        self.border = arcade.shape_list.create_line_loop(
            self.border_points,
            self.default_border_color,
            self.overlap_distance
        )

        self.neighbors: set[Tile] = set()
        self.color = self.colors[self.enabled]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{int(self.center_x), int(self.center_y)}"

    @classmethod
    def get_texture(cls) -> Texture:
        if cls._texture is None:
            image = PIL.Image.open(cls.image_path)
            cls._texture = Texture(image)
            cls._texture.width = cls.default_width
            cls._texture.height = cls.default_height
        return cls._texture

    def register(self) -> None:
        self.world.all_tiles.append(self)
        self.world.tile_borders.append(self.border)

    def unregister(self) -> None:
        self.remove_from_sprite_lists()
        self.world.tile_borders.remove(self.border)

    def update_color(self) -> None:
        arena = self.world.view.arena
        if self.world.view.snake_released and arena.world_map.snake[self.map_x][self.map_y]:
            snake = arena.snake
            color = snake.colors[snake.alive]
        elif self.world.view.snake_released and arena.world_map.food[self.map_x][self.map_y]:
            color = Color.FOOD
        else:
            color = self.colors[self.enabled]

        if color != self.color:
            self.color = color


class SurfaceTile(Tile):
    colors = {
        False: Color.SURFACE_TILE_NORMAL,
        True: Color.SURFACE_TILE_ENABLED
    }
    is_surface = True

    def __init__(self, center: Position, world: "World") -> None:
        super().__init__(center, world)

    def register(self) -> None:
        super().register()
        self.world.surface_tiles.append(self)


class BorderTile(Tile):
    colors = {
        False: Color.BORDER_TILE_NORMAL,
        True: Color.BORDER_TILE_ENABLED
    }
    is_border = True

    def register(self) -> None:
        super().register()
        self.world.border_tiles.append(self)


class World:
    def __init__(self, view: "SimulationView") -> None:
        self.view = view

        self.tiles_in_radius = 10
        self.border_thickness = 1
        self.center = (self.view.window.width * 2 / 3, self.view.window.center_y)
        self.position_to_tile_cache: dict[tuple[int, int], Tile | None] = {}

        # список плиток мира
        self.surface_tiles = SpriteList[SurfaceTile](True)
        # список плиток границы мира
        self.border_tiles = SpriteList[BorderTile](True)
        # список всех плиток
        self.all_tiles = SpriteList[Tile](True)
        self.tile_borders = arcade.shape_list.ShapeElementList()
        self.create()
        for tile in self.surface_tiles:
            self.tile_borders.append(tile.border)

        self.reference_map = Map(self)

    # мир делится на шестиугольники
    # https://www.redblobgames.com/grids/hexagons/
    def create(self) -> None:
        width = math.sqrt(3) * Tile.radius
        height = 2 * Tile.radius
        offsets = (
            [width / 2, height * 3 / 4],
            [width, 0],
            [width / 2, -height * 3 / 4],
            [-width / 2, -height * 3 / 4],
            [-width, 0],
            [-width / 2, height * 3 / 4]
        )

        tile_center = list(self.center)
        SurfaceTile(tile_center, self).register()

        for edge_size in range(1, self.tiles_in_radius + self.border_thickness):
            if edge_size < self.tiles_in_radius:
                tile_class = SurfaceTile
            else:
                tile_class = BorderTile

            tile_center[0] -= width
            for offset_x, offset_y in offsets:
                for _ in range(edge_size):
                    tile_center[0] += offset_x
                    tile_center[1] += offset_y
                    tile_class(tile_center, self).register()

        for tile in self.all_tiles:
            for offset_x, offset_y in offsets:
                neighbour = self.position_to_tile((tile.center_x + offset_x, tile.center_y + offset_y))
                if neighbour is not None:
                    tile.neighbors.add(neighbour)

    def position_to_tile(self, position: Position) -> Tile | None:
        point = (int(position[0]), int(position[1]))
        if point not in self.position_to_tile_cache:
            try:
                self.position_to_tile_cache[point] = arcade.get_sprites_at_point(point, self.all_tiles)[0]
            except IndexError:
                self.position_to_tile_cache[point] = None
        return self.position_to_tile_cache[point]
