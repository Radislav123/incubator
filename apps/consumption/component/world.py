from arcade import SpriteList
from arcade.shape_list import ShapeElementList, create_line
from pyglet.math import Vec2, Vec3

from apps.consumption.component.connection import Connection
from apps.consumption.component.settlement import Settlement
from apps.consumption.service.color import Color
from core.service.figure import Circle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.window import Window


class WorldProjection:
    def __init__(self) -> None:
        # линейное смещение вдоль x и y
        self.offset = Vec2()
        # поворот вокруг z
        self.rotation = 0
        self.scale = 1

        self.valid = False

    def prepare(self, window: "Window") -> None:
        self.offset = Vec2(window.width // 2, window.height // 2)


class World:
    def __init__(self, size: Vec3) -> None:
        self.size = size
        self.center = Vec3()
        self.projection = WorldProjection()

        self.settlements: list[Settlement] | None = None
        self.settlement_projections: SpriteList | None = None
        self.connections: list[Connection] | None = None
        self.connection_projections: ShapeElementList | None = None
        self.prepare_settlements()
        self.prepare_connections()

    # todo: изменить систему размещения поселений
    def prepare_settlements(self) -> None:
        radius = sum(x for x in self.size) // 12
        circle = Circle(radius, self.center.x, self.center.y)
        self.settlements = [(Settlement(Vec3(int(x), int(y), 0))) for x, y in circle.get_walk_around_points(5)]
        self.settlement_projections = SpriteList()

        for settlement in self.settlements:
            self.settlement_projections.append(settlement.projection)

    def prepare_connections(self) -> None:
        self.connections = []
        self.connection_projections = ShapeElementList()

        for index in range(len(self.settlements)):
            settlement_0 = self.settlements[index % len(self.settlements)]
            settlement_1 = self.settlements[(index + 1) % len(self.settlements)]
            settlements = [settlement_0, settlement_1]

            position = sum((x.position for x in settlements), Vec3()) / len(settlements)
            connection = Connection(position, settlements)
            self.connections.append(connection)

        position = sum((x.position for x in self.settlements), Vec3()) / len(self.settlements)
        connection = Connection(position, self.settlements)
        self.connections.append(connection)

    def update_projections(self) -> None:
        for settlement in self.settlements:
            settlement.projection.position = (
                settlement.position.x + self.projection.offset.x,
                settlement.position.y + self.projection.offset.y
            )

        self.connection_projections = ShapeElementList()
        for connection in self.connections:
            for settlement in connection.settlements:
                line = create_line(
                    connection.position.x + self.projection.offset.x,
                    connection.position.y + self.projection.offset.y,
                    settlement.projection.center_x,
                    settlement.projection.center_y,
                    Color.ROAD,
                    2
                )
                self.connection_projections.append(line)

        self.projection.valid = True

    def on_draw(self) -> None:
        if not self.projection.valid:
            self.update_projections()

        if self.connections is not None:
            self.connection_projections.draw()

        if self.settlements is not None:
            self.settlement_projections.draw()
