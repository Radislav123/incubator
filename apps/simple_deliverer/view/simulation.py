from arcade import SpriteList

from apps.simple_deliverer.component.interest_point import InterestPoint
from apps.simple_deliverer.settings import Settings
from apps.simple_deliverer.ui.interest_points_tab import InterestPointsTab, InterestPointsAmountSlider
from core.service.anchor import Anchor
from core.service.figure import Circle, Figure
from core.ui.button.texture_button import TextureButton
from core.view.simulation import SimulationView as CoreSimulationView


class ScoreLabel(TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        super().__init__(text = str(self.view.score), **kwargs)


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int
    score_label: ScoreLabel

    interest_points_amount = InterestPointsAmountSlider.default_value
    interest_points_figure: Figure = None

    interest_points = SpriteList(True)
    interest_point_zones = SpriteList(True)

    def reset_info(self) -> None:
        self.score = 0

    def recreate_interest_points(self) -> None:
        self.interest_points.clear()
        self.interest_point_zones.clear()

        if self.interest_points_amount > 0:
            # todo: заменить это на слайдер
            if self.interest_points_figure is None:
                self.interest_points_figure = Circle(200, self.window.center_x, self.window.center_y)

            for x, y in self.interest_points_figure.get_walk_around_points(self.interest_points_amount):
                point = InterestPoint(center_x = int(x), center_y = int(y))
                self.interest_points.append(point)
                self.interest_point_zones.append(point.zone)

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.score_label = ScoreLabel(self)
        self.ui_manager.add(self.score_label)
        self.score_label.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)

        self.recreate_interest_points()

        interest_points_tab = InterestPointsTab(self)
        self.ui_manager.add(interest_points_tab)

    def on_draw(self) -> None:
        super().on_draw()

        self.interest_point_zones.draw()
        self.interest_points.draw()
