import random
from typing import TYPE_CHECKING

import pymunk
from arcade import Sprite


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView


class Deliverer(Sprite):
    physics_body: pymunk.Body

    def __init__(self, view: "SimulationView", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view
        self.departure: int = random.choices(range(len(self.view.interest_points)), k = 1)[0]
        self.destination: int | None = None

        self.position = self.view.interest_points[self.departure].position


    # оригинал описан в PymunkPhysicsEngine.add_sprite
    def velocity_callback(
            self,
            body: pymunk.Body,
            gravity: tuple[float, float],
            damping: float,
            delta_time: float
    ) -> None:
        if self.pymunk.gravity is not None:
            # todo: прописать гравитацию к точкам интереса
            gravity = self.pymunk.gravity

        pymunk.Body.update_velocity(body, gravity, damping, delta_time)

    def choose_destination(self) -> None:
        max_size = max(x.size for x in self.view.interest_points)
        self.destination = random.choices(
            range(len(self.view.interest_points)),
            [max_size - x.size for x in self.view.interest_points]
        )[0]
