from apps.consumption.component.settlement import Settlement
from apps.consumption.service.position import Position
from apps.consumption.service.unique import Unique


class Connection(Unique):
    def __init__(self, position: Position, settlements: list[Settlement]) -> None:
        self.position = position
        self.settlements = settlements
