from arcade.gui import UIOnChangeEvent

from core.service.functions import float_range
from core.ui.slider.slider import Slider


class StepSlider(Slider):
    default_step = 1
    default_value = 1
    default_min_value = 0
    default_max_value = 10

    def __init__(
            self,
            step: float = None,
            value: float = None,
            min_value: float = None,
            max_value: float = None,
            **kwargs
    ) -> None:
        if step is None:
            step = self.default_step
        if value is None:
            value = self.default_value
        if min_value is None:
            min_value = self.default_min_value
        if max_value is None:
            max_value = self.default_max_value

        super().__init__(
            step = step,
            value = value,
            min_value = min_value,
            max_value = max_value,
            **kwargs
        )
        self.step = step
        self.values = [x for x in float_range(self.min_value, self.max_value, self.step)]
        if self.values[-1] != self.max_value:
            self.values.append(self.max_value)

    def on_change(self, event: UIOnChangeEvent) -> None:
        self.value = min(self.values, key = lambda x: abs(x - self.value))
