from pyglet.math import Vec3

from apps.consumption.component.settlement import Settlement
from apps.consumption.service.unique import Unique


class Connection(Unique):
    def __init__(self, position: Vec3, settlements: list[Settlement]) -> None:
        # расположение центральной точки
        self.position = position
        self.settlements = settlements
