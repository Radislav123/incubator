import random
from collections import defaultdict
from typing import Any, TYPE_CHECKING

from arcade.gui import UIOnClickEvent


if TYPE_CHECKING:
    from morel_buttons.view import GameView


class Logic:
    def __init__(self, view: "SimulationView", period: float) -> None:
        self.enabled = False
        self.view = view
        self.period = period
        self.previous_perform = self.view.time

    def change_state(self) -> None:
        self.enabled = not self.enabled

    def perform(self) -> Any:
        if self.view.time - self.previous_perform >= self.period:
            self.previous_perform = self.view.time
            value = self.make_logic()
        else:
            value = None
        return value

    def make_logic(self) -> Any:
        raise NotImplementedError()


class AutoClicker(Logic):
    def make_logic(self) -> None:
        values = defaultdict(list)
        for button in self.view.increment_buttons:
            values[button.increment].append(button)

        max_value = max(values)
        button = random.choice(values[max_value])

        event = UIOnClickEvent(self, button.x, button.y)
        button.on_click(event)


class AutoUpgrader(Logic):
    def make_logic(self) -> Any:
        values = defaultdict(list)
        for button in self.view.auto_increment_buttons:
            value = button.auto_increment / button.upgrade_cost
            values[value].append(button)

        max_value = max(values)
        button = random.choice(values[max_value])

        event = UIOnClickEvent(self, button.x, button.y)
        button.on_click(event)
