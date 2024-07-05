from arcade import SpriteList
from arcade.shape_list import ShapeElementList, create_line

from apps.consumption.component.connection import Connection
from apps.consumption.component.settlement import Settlement
from apps.consumption.service.color import Color
from apps.consumption.service.position import Position
from apps.consumption.settings import Settings
from core.service.figure import Circle
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()

    settlements: list[Settlement] | None = None
    settlement_sprites: SpriteList | None = None
    connections: list[Connection] | None = None
    connection_lines: ShapeElementList | None = None

    def __init__(self) -> None:
        super().__init__()

    def prepare_settlements(self) -> None:
        circle = Circle(200, self.window.center_x, self.window.center_y)
        self.settlements = [(Settlement(Position(int(x), int(y), 0))) for x, y in circle.get_walk_around_points(5)]
        self.settlement_sprites = SpriteList()

        for settlement in self.settlements:
            self.settlement_sprites.append(settlement.sprite)

    def prepare_connections(self) -> None:
        self.connections = []
        self.connection_lines = ShapeElementList()

        for index in range(len(self.settlements)):
            settlement_0 = self.settlements[index % len(self.settlements)]
            settlement_1 = self.settlements[(index + 1) % len(self.settlements)]
            settlements = [settlement_0, settlement_1]
            position = Position.middle([x.position for x in settlements])

            connection = Connection(position, settlements)
            self.connections.append(connection)

        connection = Connection(Position.middle([x.position for x in self.settlements]), self.settlements)
        self.connections.append(connection)

    def update_projections(self) -> None:
        for settlement in self.settlements:
            settlement.sprite.position = (settlement.position.x, settlement.position.y)

        self.connection_lines = ShapeElementList()
        for connection in self.connections:
            for settlement in connection.settlements:
                line = create_line(
                    connection.position.x,
                    connection.position.y,
                    settlement.sprite.center_x,
                    settlement.sprite.center_y,
                    Color.ROAD,
                    2
                )
                self.connection_lines.append(line)

    def on_show_view(self) -> None:
        super().on_show_view()

        self.prepare_settlements()
        self.prepare_connections()
        self.update_projections()

    def on_hide_view(self) -> None:
        super().on_hide_view()

        self.settlements = None
        self.settlement_sprites = None
        self.connections = None
        self.connection_lines = None

    def on_draw(self) -> None:
        super().on_draw()

        if self.connections is not None:
            self.connection_lines.draw()

        if self.settlements is not None:
            self.settlement_sprites.draw()

    def on_update(self, delta_time: float) -> None:
        pass
