from arcade.gui import UIOnChangeEvent

from core.service.functions import float_range
from core.ui.slider.slider import Slider


class StepSlider(Slider):
    def __init__(self, step: float = 1, **kwargs):
        super().__init__(**kwargs)
        self.step = step
        self.values = [x for x in float_range(self.min_value, self.max_value, self.step)]
        if self.values[-1] != self.max_value:
            self.values.append(self.max_value)

    def on_change(self, event: UIOnChangeEvent) -> None:
        self.value = min(self.values, key = lambda x: abs(x - self.value))
