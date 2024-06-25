from arcade import SpriteList

from apps.simple_deliverer.component.interest_point import InterestPoint, InterestPointZone
from apps.simple_deliverer.settings import Settings
from core.service.anchor import Anchor
from core.service.figure import Circle
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
    interest_points: SpriteList[InterestPoint]
    interest_point_zones: SpriteList[InterestPointZone]

    def reset_info(self) -> None:
        self.score = 0

    def prepare_interest_points(self) -> None:
        figure = Circle(200, self.window.center_x, self.window.center_y)
        amount = 4

        self.interest_points = SpriteList(True)
        self.interest_point_zones = SpriteList(True)
        for x, y in figure.get_walk_around_points(amount):
            point = InterestPoint(center_x = int(x), center_y = int(y))
            self.interest_points.append(point)
            self.interest_point_zones.append(point.zone)

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.score_label = ScoreLabel(self)
        self.ui_manager.add(self.score_label)
        self.score_label.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)

        self.prepare_interest_points()

    def on_draw(self) -> None:
        super().on_draw()

        self.interest_point_zones.draw()
        self.interest_points.draw()
