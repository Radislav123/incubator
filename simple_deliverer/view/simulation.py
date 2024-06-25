import pymunk
from arcade import Sprite, SpriteList

from core.service.anchor import Anchor
from core.service.figure import Circle
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.view.simulation import SimulationView as CoreSimulationView
from simple_deliverer.service.color import Color
from simple_deliverer.settings import Settings


class ScoreLabel(TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        super().__init__(text = str(self.view.score), **kwargs)


class InterestPoint(Sprite):
    settings = Settings()

    def __init__(self, center_x: float, center_y: float, **kwargs) -> None:
        texture = Texture.create_circle(10, 2, color = Color.INTEREST_POINT)
        super().__init__(texture, 1, center_x, center_y, **kwargs)

    def __repr__(self) -> str:
        return f"InterestPoint{self.position}"


class Deliverer(Sprite):
    physics_body: pymunk.Body

    def __init__(self, view: "SimulationView", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view

    # оригинал описан в PymunkPhysicsEngine.add_sprite
    def velocity_callback(
            self,
            body: pymunk.Body,
            gravity: tuple[float, float],
            damping: float,
            delta_time: float
    ) -> None:
        # Custom damping
        if self.pymunk.damping is not None:
            adj_damping = ((self.pymunk.damping * 100.0) / 100.0)**delta_time
            # print(f"Custom damping {sprite.pymunk.damping} {damping} default to {adj_damping}")
            damping = adj_damping

        # Custom gravity
        if self.pymunk.gravity is not None:
            gravity = self.pymunk.gravity

        # Go ahead and update velocity
        pymunk.Body.update_velocity(body, gravity, damping, delta_time)


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int
    score_label: ScoreLabel
    interest_points: SpriteList[InterestPoint]

    def reset_info(self) -> None:
        self.score = 0

    def prepare_interest_points(self) -> None:
        figure = Circle(200, self.window.center_x, self.window.center_y)
        amount = 4

        self.interest_points = SpriteList()
        for x, y in figure.get_walk_around_points(amount):
            self.interest_points.append(InterestPoint(center_x = int(x), center_y = int(y)))

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.score_label = ScoreLabel(self)
        self.ui_manager.add(self.score_label)
        self.score_label.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)

        self.prepare_interest_points()

    def on_draw(self) -> None:
        super().on_draw()

        self.interest_points.draw()
