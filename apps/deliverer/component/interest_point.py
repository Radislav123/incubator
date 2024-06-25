from arcade import Sprite

from apps.deliverer.service.color import Color
from apps.deliverer.settings import Settings
from core.texture import Texture


class InterestPointZone(Sprite):
    settings = Settings()


class InterestPoint(Sprite):
    settings = Settings()
    default_size = 100

    def __init__(self, center_x: float, center_y: float, size: int, **kwargs) -> None:
        self.size = size

        radius = 10
        texture = Texture.create_circle(radius, 2, color = Color.INTEREST_POINT)
        super().__init__(texture, 1, center_x, center_y, **kwargs)

        zone_radius = radius + 20
        zone_texture = Texture.create_circle(zone_radius, 1, color = Color.INTEREST_POINT_ZONE)
        self.zone = InterestPointZone(zone_texture, 1, center_x, center_y, **kwargs)

        self.resize()

    def resize(self) -> None:
        scale = self.size / self.default_size
        self.scale = scale
        self.zone.scale = scale

    def __repr__(self) -> str:
        return f"InterestPoint{self.position}"
