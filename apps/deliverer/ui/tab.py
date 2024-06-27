from typing import TYPE_CHECKING

from arcade.gui import UIOnChangeEvent

from apps.deliverer.component.deliverer import Deliverer
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
        text = f"Перемещено грузов: {self.tab.view.score}"
        if self.text != text:
            self.text = text


class FigureLabel(TabLabel):
    def update_text(self) -> None:
        text = self.tab.view.figure_new.name_rus
        if self.text != text:
            self.text = text


class FigureAngleLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Угол фигуры: {int(self.tab.view.figure_angle_new)}°"
        if self.text != text:
            self.text = text


class FigureRotationSpeedLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Изменение угла фигуры: {self.tab.view.figure_rotation_speed}°/с"
        if self.text != text:
            self.text = text


class InterestPointsAmountLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Количество точек: {self.tab.view.interest_points_amount}"
        if self.text != text:
            self.text = text


class DeliverersAmountLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Количество курьеров: {len(self.tab.view.deliverers)}/{int(self.tab.deliverers_amount_slider.value)}"
        if self.text != text:
            self.text = text


class DelivererRadiusLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Радиус курьера: {Deliverer.radius}"
        if self.text != text:
            self.text = text


class DelivererPowerLabel(TabLabel):
    def update_text(self) -> None:
        text = f"Мощность курьера: {Deliverer.power}"
        if self.text != text:
            self.text = text


class DelivererMaxCargoLabel(TabLabel):
    def update_text(self) -> None:
        self.text = f"Грузоподъемность: {Deliverer.max_cargo}"


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
        # обновляется в SimulationView.on_draw()
        # self.tab.figure_angle_label.update_text()
        self.tab.view.rotate_interest_points()


class FigureRotationSpeedSlider(TabSlider):
    default_value = 20
    default_min_value = 0
    default_max_value = 40
    offset = default_value

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.figure_rotation_speed = int(self.value) - self.offset
        self.tab.figure_rotation_speed_label.update_text()


class InterestPointsAmountSlider(TabSlider):
    default_value = 4
    default_max_value = 20

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.interest_points_amount = int(self.value)
        self.tab.view.recreate_interest_points()
        self.tab.interest_points_amount_label.update_text()


class DeliverersAmountSlider(TabSlider):
    default_value = 50
    default_max_value = 100

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        self.tab.view.deliverers_amount = int(self.value)
        self.tab.deliverers_amount_label.update_text()


class DelivererRadiusSlider(TabSlider):
    default_value = Deliverer.default_radius
    default_min_value = 1
    default_max_value = 10

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        Deliverer.radius = int(self.value)
        for deliverer in self.tab.view.deliverers:
            deliverer.resize()
            deliverer.update_physics()
        self.tab.deliverer_radius_label.update_text()


class DelivererPowerSlider(TabSlider):
    default_step = 100
    default_value = Deliverer.default_power
    default_min_value = 100
    default_max_value = 5000

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        Deliverer.power = int(self.value)
        self.tab.deliverer_power_label.update_text()


class DelivererMaxCargoSlider(TabSlider):
    default_value = Deliverer.default_max_cargo
    default_min_value = 1
    default_max_value = 10

    def on_change(self, event: UIOnChangeEvent) -> None:
        super().on_change(event)
        Deliverer.max_cargo = int(self.value)
        self.tab.deliverer_max_cargo_label.update_text()
        for deliverer in self.tab.view.deliverers:
            deliverer.update_color()


class Tab(BoxLayout):
    gap = 10

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view

        self.score_label = ScoreLabel(self)
        self.figure_slider = FigureSlider(self)
        self.figure_label = FigureLabel(self)
        self.figure_angle_slider = FigureAngleSlider(self)
        self.figure_angle_label = FigureAngleLabel(self)
        self.figure_rotation_speed_slider = FigureRotationSpeedSlider(self)
        self.figure_rotation_speed_label = FigureRotationSpeedLabel(self)
        self.interest_points_amount_slider = InterestPointsAmountSlider(self)
        self.interest_points_amount_label = InterestPointsAmountLabel(self)
        self.deliverers_amount_slider = DeliverersAmountSlider(self)
        self.deliverers_amount_label = DeliverersAmountLabel(self)
        self.deliverer_radius_slider = DelivererRadiusSlider(self)
        self.deliverer_radius_label = DelivererRadiusLabel(self)
        self.deliverer_power_slider = DelivererPowerSlider(self)
        self.deliverer_power_label = DelivererPowerLabel(self)
        self.deliverer_max_cargo_slider = DelivererMaxCargoSlider(self)
        self.deliverer_max_cargo_label = DelivererMaxCargoLabel(self)
        children = [
            self.score_label,
            self.figure_label,
            self.figure_slider,
            self.figure_angle_label,
            self.figure_angle_slider,
            self.figure_rotation_speed_label,
            self.figure_rotation_speed_slider,
            self.interest_points_amount_label,
            self.interest_points_amount_slider,
            self.deliverers_amount_label,
            self.deliverers_amount_slider,
            self.deliverer_radius_label,
            self.deliverer_radius_slider,
            self.deliverer_power_label,
            self.deliverer_power_slider,
            self.deliverer_max_cargo_label,
            self.deliverer_max_cargo_slider,
        ]

        super().__init__(children = children, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(texture = Texture.create_rounded_rectangle(self.size))
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
