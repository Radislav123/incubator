import math
from typing import TYPE_CHECKING

import PIL.Image
import arcade
from arcade import Sprite, SpriteList

from core.texture import Texture
from snake.service.color import Color
from snake.settings import Settings


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView

Position = tuple[float, float] | list[float]


class Tile(Sprite):
    settings = Settings()

    colors: dict[bool, Texture]
    default_border_color = Color.TILE_BORDER
    image_path = f"{settings.IMAGES_FOLDER}/hexagon_0.png"
    _texture: Texture = None

    overlap_distance = 1.5
    radius = 20
    default_width = float(math.sqrt(3) * radius + overlap_distance)
    default_height = float(2 * radius + overlap_distance)

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
        return f"{int(self.center_x), int(self.center_y)}"

    @classmethod
    def get_texture(cls) -> Texture:
        if cls._texture is None:
            image = PIL.Image.open(cls.image_path)
            cls._texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
            cls._texture.width = cls.default_width
            cls._texture.height = cls.default_height
        return cls._texture

    def register(self) -> None:
        self.world.all_tiles.append(self)
        self.world.tile_borders.append(self.border)

    def unregister(self) -> None:
        self.remove_from_sprite_lists()
        self.world.tile_borders.remove(self.border)


class SurfaceTile(Tile):
    colors = {
        False: Color.SURFACE_TILE_NORMAL,
        True: Color.SURFACE_TILE_ENABLED
    }

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

    def register(self) -> None:
        super().register()
        self.world.border_tiles.append(self)


# todo: write it
class Map:
    def __init__(self, world: "World") -> None:
        self.world = world
        self.side_length = self.world.tiles_in_radius + self.world.border_thickness
        square_side_length = self.side_length * 2 - 1
        self.tiles: list[list[Tile | None]] = [[None for _ in range(square_side_length)]
                                               for _ in range(square_side_length)]

        self.prepare_tiles()

    def prepare_tiles(self) -> None:
        offsets = (
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1)
        )
        x = self.side_length - 1
        y = self.side_length - 1
        self.tiles[x][y] = self.world.all_tiles[0]

        index = 1
        for edge_size in range(1, self.side_length):
            y -= 1
            for offset_x, offset_y in offsets:
                for _ in range(edge_size):
                    x += offset_x
                    y += offset_y
                    self.tiles[x][y] = self.world.all_tiles[index]
                    index += 1


class World:
    def __init__(self, view: "SimulationView") -> None:
        self.view = view

        self.age = 0
        self.radius = min(self.view.window.size) // 2
        self.tiles_in_radius = self.radius // (Tile.radius * 2) or 1
        self.border_thickness = 1
        self.center = self.view.window.center
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

        self.map = Map(self)

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
