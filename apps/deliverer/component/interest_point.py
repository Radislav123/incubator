from typing import TYPE_CHECKING

import pymunk
from arcade import PymunkPhysicsEngine, Sprite

from apps.deliverer.service.color import Color
from apps.deliverer.settings import Settings
from core.texture import Texture


if TYPE_CHECKING:
    from apps.deliverer.view.simulation import SimulationView


class InterestPointZone(Sprite):
    settings = Settings()


class InterestPoint(Sprite):
    settings = Settings()
    physics_body: pymunk.Body

    default_size = 1000
    radius = 10
    zone_size_coeff = 5
    # в секундах
    resize_period = 1

    def __init__(self, view: "SimulationView", center_x: float, center_y: float, size: int, **kwargs) -> None:
        self.view = view
        self.size = size

        texture = Texture.create_circle(self.radius, 2, color = Color.INTEREST_POINT)
        super().__init__(texture, 1, center_x, center_y, **kwargs)

        zone_radius = self.radius * self.zone_size_coeff
        zone_texture = Texture.create_circle(zone_radius, 1, color = Color.INTEREST_POINT_ZONE)
        self.zone = InterestPointZone(zone_texture, 1, center_x, center_y, **kwargs)

        self.resize()
        self.update_physics()
        self.resize_timer = 0

    def __repr__(self) -> str:
        return f"InterestPoint{self.position}"

    def resize(self) -> bool:
        min_scale = 0.7
        max_scale = 1.5

        # https://www.desmos.com/calculator/bbkja3xg2w?lang=ru
        if self.size >= self.default_size * max_scale:
            scale = max_scale
        elif self.size >= self.default_size * min_scale:
            scale = (self.size - self.default_size * min_scale) / self.default_size + min_scale
        else:
            scale = min_scale

        if scale != self.scale:
            self.scale = scale
            self.zone.scale = scale
            resized = True
        else:
            resized = False

        return resized

    def update_physics(self) -> None:
        if self.physics_engines:
            self.view.physics_engine.remove_sprite(self)

        self.view.physics_engine.add_sprite(self, self.size, body_type = PymunkPhysicsEngine.KINEMATIC)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body

    # noinspection PyMethodOverriding
    def on_update(self, delta_time) -> None:
        resized = self.resize()
        self.resize_timer += delta_time
        if resized and self.resize_timer > self.resize_period:
            self.update_physics()
            self.resize_timer = 0
