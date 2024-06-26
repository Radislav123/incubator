import math
import random

from arcade import PymunkPhysicsEngine, SpriteList

from apps.deliverer.component.deliverer import Deliverer
from apps.deliverer.component.interest_point import InterestPoint, InterestPointZone
from apps.deliverer.settings import Settings
from apps.deliverer.ui.tab import AmountSlider, FigureAngleSlider, Tab
from core.service.figure import Circle, Ellipse, Figure
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()
    physics_engine = PymunkPhysicsEngine()

    score: int

    figures: list[Figure] = None
    figure_old: Figure = None
    figure_new: Figure = None
    figure_angle_old: int | None = None
    figure_angle_new: int | None = None
    figure_center_x: int
    figure_center_y: int

    interest_points_amount = AmountSlider.default_value
    interest_points = SpriteList[InterestPoint](True)
    interest_point_zones = SpriteList[InterestPointZone](True)

    deliverers_amount = 10
    deliverers = SpriteList[Deliverer](True)

    def reset_info(self) -> None:
        self.score = 0

    def prepare_figures(self) -> None:
        self.figure_center_x = int(self.window.width * 59 / 100)
        self.figure_center_y = int(self.window.center_y)
        self.figure_angle_old = 0
        self.figure_angle_new = FigureAngleSlider.default_value

        center = (self.figure_center_x, self.figure_center_y)
        self.figures = [
            Circle(220, *center),
            Ellipse(220, 150, *center)
        ]

    def rotate_interest_points(self) -> None:
        if self.figure_angle_new != self.figure_angle_old:
            angle = math.radians(self.figure_angle_old - self.figure_angle_new)

            for point in self.interest_points:
                x_old = point.center_x - self.figure_new.center_x
                y_old = point.center_y - self.figure_new.center_y

                x_new = x_old * math.cos(angle) - y_old * math.sin(angle)
                y_new = x_old * math.sin(angle) + y_old * math.cos(angle)

                new_position = (self.figure_new.center_x + x_new, self.figure_new.center_y + y_new)
                point.position = new_position
                point.physics_body.position = new_position
                point.zone.position = new_position

            self.figure_angle_old = self.figure_angle_new

    def recreate_interest_points(self) -> None:
        if self.interest_points_amount != len(self.interest_points) or self.figure_new != self.figure_old:
            for point in self.interest_points:
                self.physics_engine.remove_sprite(point)
            self.interest_points.clear()
            self.interest_point_zones.clear()

            if self.interest_points_amount > 0:
                sizes = [0 for _ in range(self.interest_points_amount)]
                for potion in range(self.interest_points_amount * InterestPoint.default_size):
                    sizes[random.randint(0, self.interest_points_amount - 1)] += 1

                for index, (x, y) in enumerate(self.figure_new.get_walk_around_points(self.interest_points_amount)):
                    # noinspection PyTypeChecker
                    point = InterestPoint(self, int(x), int(y), sizes[index])
                    self.interest_points.append(point)
                    self.interest_point_zones.append(point.zone)

                self.figure_angle_old = 0
                self.rotate_interest_points()

            self.figure_old = self.figure_new

    def prepare_deliverers(self) -> None:
        self.deliverers.clear()

        for _ in range(self.deliverers_amount):
            deliverer = Deliverer(self)
            self.deliverers.append(deliverer)

    def on_show_view(self) -> None:
        super().on_show_view()
        self.reset_info()

        self.prepare_figures()
        interest_points_tab = Tab(self)
        self.ui_manager.add(interest_points_tab)

        self.recreate_interest_points()
        self.prepare_deliverers()

    def on_draw(self) -> None:
        super().on_draw()

        self.interest_point_zones.draw()
        self.interest_points.draw()

        self.deliverers.draw()

    def on_update(self, delta_time: float) -> None:
        for point in self.interest_points:
            point.on_update()
            point.zone.on_update()

        for deliverer in self.deliverers:
            deliverer.on_update()

        self.physics_engine.step(delta_time)
