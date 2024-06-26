import math
import random
from typing import TYPE_CHECKING

import PIL.Image
import arcade.hitbox
import pymunk
from arcade import Sprite

from apps.deliverer.component.interest_point import InterestPoint
from apps.deliverer.settings import Settings
from core.texture import Texture


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView


class Deliverer(Sprite):
    settings = Settings()
    physics_body: pymunk.Body

    radius = 10
    default_mass = 10

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.departure: int = random.choices(range(len(self.view.interest_points)), k = 1)[0]
        self.destination: int | None = None

        self.max_cargo = 1
        self.cargo = 0

        image = PIL.Image.open(f"{self.settings.IMAGES_FOLDER}/circle_0.png")
        texture = Texture(image, hit_box_algorithm = arcade.hitbox.algo_detailed)
        scale = self.radius / sum(texture.size) * 4
        position = list(self.view.interest_points[self.departure].position)
        angle = random.random() * math.pi * 2
        position[0] = position[0] + InterestPoint.radius * 2 * math.cos(angle)
        position[1] = position[1] + InterestPoint.radius * 2 * math.sin(angle)
        super().__init__(texture, scale, position[0], position[1], angle, **kwargs)

        self.view.physics_engine.add_sprite(self, self.default_mass)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body
        self.physics_body.velocity_func = self.velocity_callback

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

    def load_cargo(self) -> None:
        cargo = min(self.max_cargo - self.cargo, self.view.interest_points[self.departure].size)

        self.view.interest_points[self.departure].size -= cargo
        self.cargo += cargo
        self.physics_body.mass += cargo

    def unload_cargo(self) -> None:
        cargo = self.cargo

        self.view.interest_points[self.destination].size += cargo
        self.physics_body.mass -= cargo
        self.cargo -= cargo
