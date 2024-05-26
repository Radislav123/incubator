from typing import TYPE_CHECKING

from snake.component.world import Tile
from snake.service.color import Color


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView


class Segment:
    def __init__(self, tile: Tile) -> None:
        self.tile = tile
        self.color = Color.GREEN


class Snake:
    def __init__(self, view: SimulationView) -> None:
        self.view = view
        self.world = self.view.world
