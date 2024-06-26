from typing import TYPE_CHECKING

from arcade.gui import UIOnChangeEvent

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.layout.box_layout import BoxLayout
from core.ui.slider.step_slider import StepSlider
from core.ui.text.label import Label


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView


class TabLabel(Label):
    default_width = 300
    default_height = 50

    def __init__(self, tab: "Tab", **kwargs) -> None:
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


class TabSlider(StepSlider):
    def __init__(self, tab: "Tab", **kwargs) -> None:
        self.tab = tab
        super().__init__(width = TabLabel.default_width, **kwargs)


class ScoreLabel(TabLabel):
    def update_text(self) -> None:
        self.text = str(self.tab.view.score)


class FigureLabel(TabLabel):
    def update_text(self) -> None:
        self.text = self.tab.view.figure_new.name_rus


class FigureAngleLabel(TabLabel):
    def update_text(self) -> None:
        self.text = f"Угол: {self.tab.view.figure_angle_new}"


class AmountLabel(TabLabel):
    def update_text(self) -> None:
        self.text = f"Количество: {self.tab.view.interest_points_amount}"


class FigureSlider(TabSlider):
    default_value = 0

    def __init__(self, tab: "Tab", **kwargs) -> None:
        self.default_max_value = len(tab.view.figures) - 1
        super().__init__(tab, **kwargs)
        self.set_figure()

    def set_figure(self) -> None:
        self.tab.view.figure_new = self.tab.view.figures[int(self.value)]

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.set_figure()
        self.tab.view.recreate_interest_points()
        self.tab.figure_label.update_text()


class FigureAngleSlider(TabSlider):
    default_value = 0
    default_max_value = 720

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.figure_angle_new = int(self.value)
        self.tab.figure_angle_label.update_text()
        self.tab.view.rotate_interest_points()


class AmountSlider(TabSlider):
    default_value = 4
    default_max_value = 20

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.interest_points_amount = int(self.value)
        self.tab.view.recreate_interest_points()
        self.tab.amount_label.update_text()


class Tab(BoxLayout):
    gap = 10

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view

        figure_slider = FigureSlider(self)
        self.score_label = ScoreLabel(self)
        self.figure_label = FigureLabel(self)
        self.figure_angle_label = FigureAngleLabel(self)
        self.amount_label = AmountLabel(self)
        children = [
            self.score_label,
            self.figure_label,
            figure_slider,
            self.figure_angle_label,
            FigureAngleSlider(self),
            self.amount_label,
            AmountSlider(self)
        ]

        super().__init__(children = children, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(texture = Texture.create_rounded_rectangle(self.size))
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
