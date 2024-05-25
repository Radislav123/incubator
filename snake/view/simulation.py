import math

import arcade
from arcade import SpriteList

from core.service import Color
from core.view.simulation import SimulationView as CoreSimulationView
from snake.settings import Settings


Position = tuple[float, float] | list[float]


class Tile(arcade.Sprite):
    settings = Settings()

    image_path = f"{settings.IMAGES_FOLDER}/hexagon_0.png"
    default_color: tuple[int, int, int, int]
    default_border_color = Color.BORDER
    default_texture = arcade.load_texture(image_path, hit_box_algorithm = arcade.hitbox.algo_detailed)
    overlap_distance = 1.5
    radius = 20
    default_width = math.sqrt(3) * radius + overlap_distance
    default_height = 2 * radius + overlap_distance

    # границы плиток должны задаваться с небольшим наслоением, так как границы не считаются их частью
    # если граница проходит по 400 координате, то 399.(9) принадлежит плитке, а 400 уже - нет
    def __init__(self, center: Position, world: "World") -> None:
        self.world = world
        super().__init__(self.default_texture, center_x = center[0], center_y = center[1])
        self.width = self.default_width
        self.height = self.default_height
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
        self.color = self.default_color

    def __repr__(self) -> str:
        return f"{self.center_x, self.center_y}"

    def register(self) -> None:
        self.world.all_tiles.append(self)
        self.world.tile_borders.append(self.border)

    def unregister(self) -> None:
        self.remove_from_sprite_lists()
        self.world.tile_borders.remove(self.border)


class MapTile(Tile):
    default_color = Color.NORMAL

    def register(self) -> None:
        super().register()
        self.world.map_tiles.append(self)


class BorderTile(Tile):
    default_color = Color.PRESSED

    def register(self) -> None:
        super().register()
        self.world.border_tiles.append(self)


class World:
    def __init__(self, view: "SimulationView") -> None:
        self.view = view

        self.age = 0
        self.radius = min(self.view.window.size) // 2
        # соотносится с центром окна
        self.center = self.view.window.center
        self.border_thickness = 1
        self.position_to_tile_cache: dict[Position, Tile | None] = {}

        # список плиток мира
        self.map_tiles = SpriteList[MapTile](True)
        # список плиток границы мира
        self.border_tiles = SpriteList[BorderTile](True)
        # список всех плиток
        self.all_tiles = SpriteList[Tile](True)
        self.tile_borders = arcade.shape_list.ShapeElementList()
        self.create()
        for tile in self.map_tiles:
            self.tile_borders.append(tile.border)

    # мир делится на шестиугольники
    # https://www.redblobgames.com/grids/hexagons/
    def create(self) -> None:
        width = math.sqrt(3) * Tile.radius
        height = 2 * Tile.radius
        offsets = (
            (width / 2, height * 3 / 4),
            (width, 0),
            (width / 2, -height * 3 / 4),
            (-width / 2, -height * 3 / 4),
            (-width, 0),
            (-width / 2, height * 3 / 4)
        )
        tiles_in_radius = self.radius // (Tile.radius * 2) or 1

        tile_center = list(self.center)
        MapTile(tile_center, self).register()

        for edge_size in range(1, tiles_in_radius + self.border_thickness):
            if edge_size < tiles_in_radius:
                tile_class = MapTile
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


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int
    world: World

    def reset_info(self) -> None:
        self.score = 0

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.world = World(self)

    def on_draw(self) -> None:
        self.world.all_tiles.draw()
        # self.world.tile_borders.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        self.logger.debug(self.world.position_to_tile((x, y)))
