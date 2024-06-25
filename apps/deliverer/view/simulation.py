import math

from arcade import SpriteList

from apps.deliverer.component.interest_point import InterestPoint
from apps.deliverer.settings import Settings
from apps.deliverer.ui.tab import AmountSlider, FigureAngleSlider, Tab
from core.service.figure import Circle, Figure
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int

    interest_points_amount = AmountSlider.default_value
    figures: list[Figure] = None
    figure: Figure = None
    figure_angle_old: int | None = None
    figure_angle_new: int | None = None
    interest_points_center_x: int
    interest_points_center_y: int

    interest_points = SpriteList(True)
    interest_point_zones = SpriteList(True)

    def reset_info(self) -> None:
        self.score = 0

    def prepare_figures(self) -> None:
        self.interest_points_center_x = int(self.window.width * 59 / 100)
        self.interest_points_center_y = int(self.window.center_y)
        self.figure_angle_old = 0
        self.figure_angle_new = FigureAngleSlider.default_value

        # todo: добавить другие фигуры
        self.figures = [
            Circle(200, self.interest_points_center_x, self.interest_points_center_y)
        ]

    def rotate_interest_points(self) -> None:
        if self.figure_angle_new != self.figure_angle_old:
            angle = math.radians(self.figure_angle_new - self.figure_angle_old)

            for point in self.interest_points:
                x_old = point.center_x - self.figure.center_x
                y_old = point.center_y - self.figure.center_y

                x_new = x_old * math.cos(angle) - y_old * math.sin(angle)
                y_new = x_old * math.sin(angle) + y_old * math.cos(angle)

                new_position = (self.figure.center_x + x_new, self.figure.center_y + y_new)
                point.position = new_position
                point.zone.position = new_position

            self.figure_angle_old = self.figure_angle_new

    def recreate_interest_points(self) -> None:
        self.interest_points.clear()
        self.interest_point_zones.clear()

        if self.interest_points_amount > 0:
            for x, y in self.figure.get_walk_around_points(self.interest_points_amount):
                point = InterestPoint(center_x = int(x), center_y = int(y))
                self.interest_points.append(point)
                self.interest_point_zones.append(point.zone)
        self.rotate_interest_points()

    def on_show_view(self) -> None:
        super().on_show_view()
        self.reset_info()

        self.prepare_figures()
        interest_points_tab = Tab(self)
        self.ui_manager.add(interest_points_tab)

        self.recreate_interest_points()

    def on_draw(self) -> None:
        super().on_draw()

        self.interest_point_zones.draw()
        self.interest_points.draw()
