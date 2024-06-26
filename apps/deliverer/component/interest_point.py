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

    default_size = 100
    radius = 10
    zone_size_coeff = 5

    def __init__(self, view: "SimulationView", center_x: float, center_y: float, size: int, **kwargs) -> None:
        self.view = view
        self.size = size

        texture = Texture.create_circle(self.radius, 2, color = Color.INTEREST_POINT)
        super().__init__(texture, 1, center_x, center_y, **kwargs)

        zone_radius = self.radius * self.zone_size_coeff
        zone_texture = Texture.create_circle(zone_radius, 1, color = Color.INTEREST_POINT_ZONE)
        self.zone = InterestPointZone(zone_texture, 1, center_x, center_y, **kwargs)

        self.resize()
        self.view.physics_engine.add_sprite(self, self.size, body_type = PymunkPhysicsEngine.KINEMATIC)
        self.physics_body = self.view.physics_engine.get_physics_object(self).body

    def __repr__(self) -> str:
        return f"InterestPoint{self.position}"

    def resize(self) -> None:
        scale = self.size / self.default_size
        self.scale = scale
        self.zone.scale = scale
