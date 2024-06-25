from typing import TYPE_CHECKING

import pymunk
from arcade import Sprite


if TYPE_CHECKING:
    from apps.simple_deliverer.view.simulation import SimulationView


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
            # todo: прописать гравитацию к точкам интереса
            gravity = self.pymunk.gravity

        # Go ahead and update velocity
        pymunk.Body.update_velocity(body, gravity, damping, delta_time)
