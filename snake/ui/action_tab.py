from typing import TYPE_CHECKING

from arcade.gui import UIOnChangeEvent, UIOnClickEvent

from core.service.anchor import Anchor
from core.ui.button.texture_button import TextureButton
from core.ui.layout.box_layout import BoxLayout
from core.ui.slider.step_slider import StepSlider
from snake.ui.mixin import SnakeStyleButtonMixin, SnakeStyleSliderMixin


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView


class Action(SnakeStyleButtonMixin, TextureButton):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        self.action_tab = action_tab
        self.view = self.action_tab.view
        super().__init__(**kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.action_tab)


class Release(Action):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, text = "release", **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        super().on_click(event)
        self.view.released_arena = self.view.prepare_released_arena()
        self.view.prepare_brain_map()
        self.view.snake_released = True


class Train(Action):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, text = "train", **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.action_tab)
        self.view.max_generation = self.view.reference_brain.generation + self.action_tab.generations_amount.value
        self.view.generation_size = self.action_tab.generation_size.value
        self.view.prepare_training_arenas()
        self.view.snake_training = True


class GenerationsAmount(SnakeStyleSliderMixin, StepSlider):
    def __init__(self, action_tab: "ActionTab") -> None:
        super().__init__(step = 10, value = 10)
        self.action_tab = action_tab
        self.view = self.action_tab.view

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)

class GenerationSize(SnakeStyleSliderMixin, StepSlider):
    def __init__(self, action_tab: "ActionTab") -> None:
        super().__init__(step = 10, value = 10)
        self.action_tab = action_tab
        self.view = self.action_tab.view

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)


class ActionTab(BoxLayout):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.generations_amount = GenerationsAmount(self)
        self.generation_size = GenerationSize(self)
        children = [Release(self), Train(self), self.generations_amount, self.generation_size]
        super().__init__(children = children, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
