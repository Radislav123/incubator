from typing import TYPE_CHECKING

from arcade.gui import UIOnChangeEvent

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.layout.box_layout import BoxLayout
from core.ui.slider.step_slider import StepSlider
from core.ui.text.label import Label


if TYPE_CHECKING:
    from apps.simple_deliverer.view.simulation import SimulationView


class InterestPointsTabLabel(Label):
    default_width = 300
    default_height = 50

    def __init__(self, tab: "InterestPointsTab", **kwargs) -> None:
        self.tab = tab
        texture = Texture.create_empty("interest points tab label", (self.default_width, self.default_height))
        super().__init__(
            texture = texture,
            width = self.default_width,
            height = self.default_height,
            **kwargs
        )
        self.update_text()

    def update_text(self) -> None:
        raise NotImplementedError()


class InterestPointsTabSlider(StepSlider):
    def __init__(self, tab: "InterestPointsTab", **kwargs) -> None:
        self.tab = tab
        super().__init__(width = InterestPointsTabLabel.default_width, **kwargs)


class InterestPointsAmountLabel(InterestPointsTabLabel):
    def update_text(self) -> None:
        self.text = f"Точки интереса: {self.tab.view.interest_points_amount}"


class InterestPointsAmountSlider(InterestPointsTabSlider):
    default_value = 4
    default_max_value = 20

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.interest_points_amount = self.value
        self.tab.view.recreate_interest_points()
        self.tab.interest_points_amount_label.update_text()


class InterestPointsTab(BoxLayout):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.interest_points_amount_label = InterestPointsAmountLabel(self)
        children = [
            self.interest_points_amount_label,
            InterestPointsAmountSlider(self)
        ]
        super().__init__(children = children, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(texture = Texture.create_rounded_rectangle(self.size))
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
