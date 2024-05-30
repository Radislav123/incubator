from typing import TYPE_CHECKING

from arcade.gui import UIOnChangeEvent, UIOnClickEvent

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.ui.layout.box_layout import BoxLayout
from core.ui.slider.step_slider import StepSlider
from core.ui.text.label import Label
from snake.service.color import Color
from snake.ui.mixin import SnakeStyleButtonMixin, SnakeStyleSliderMixin


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView


class ActionButton(SnakeStyleButtonMixin, TextureButton):
    default_width = 300
    default_height = 50

    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        self.action_tab = action_tab
        self.view = self.action_tab.view
        super().__init__(width = self.default_width, height = self.default_height, **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.action_tab)


class Release(ActionButton):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, text = "Выпустить", **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        super().on_click(event)
        self.view.released_arena = self.view.prepare_released_arena()
        self.view.prepare_brain_map()
        self.view.snake_released = True


class Train(ActionButton):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, text = "Тренировать", **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.action_tab)
        self.view.max_generation = self.view.reference_brain.generation + self.action_tab.generations_amount.value
        self.view.generation_size = self.action_tab.generation_size.value
        self.view.prepare_training_arenas()
        self.view.snake_training = True


class Back(ActionButton):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, text = "Назад", **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.action_tab)
        self.view.reference_brain = None
        self.view.prepare_load_tab()


class ActionTabSlider(SnakeStyleSliderMixin, StepSlider):
    def __init__(self, action_tab: "ActionTab") -> None:
        super().__init__(step = 10, value = 10, max_value = 200, width = ActionButton.default_width)
        self.action_tab = action_tab
        self.view = self.action_tab.view


class GenerationsAmount(ActionTabSlider):
    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.action_tab.generations_amount_label.update_text()


class GenerationSize(ActionTabSlider):
    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.action_tab.generation_size_label.update_text()


class ActionTabLabel(SnakeStyleButtonMixin, Label):
    def __init__(self, actions_tab: "ActionTab", **kwargs) -> None:
        self.actions_tab = actions_tab
        texture = Texture.create_empty("action tab label", (ActionButton.default_width, ActionButton.default_height))
        super().__init__(
            texture = texture,
            width = ActionButton.default_width,
            height = ActionButton.default_height,
            **kwargs
        )


class GenerationsAmountLabel(ActionTabLabel):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, **kwargs)
        self.update_text()

    def update_text(self) -> None:
        self.text = f"Количество поколений: {self.actions_tab.generations_amount.value}"


class GenerationSizeLabel(ActionTabLabel):
    def __init__(self, action_tab: "ActionTab", **kwargs) -> None:
        super().__init__(action_tab, **kwargs)
        self.update_text()

    def update_text(self) -> None:
        self.text = f"Размер поколения: {self.actions_tab.generation_size.value}"


class ActionTab(BoxLayout):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.generations_amount = GenerationsAmount(self)
        self.generations_amount_label = GenerationsAmountLabel(self)
        self.generation_size = GenerationSize(self)
        self.generation_size_label = GenerationSizeLabel(self)
        children = [
            Back(self),
            Release(self),
            Train(self),
            self.generations_amount_label,
            self.generations_amount,
            self.generation_size_label,
            self.generation_size
        ]
        super().__init__(children = children, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(
            texture = Texture.create_rounded_rectangle(
                self.size,
                5,
                color = Color.NORMAL,
                border_color = Color.BORDER
            )
        )
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
