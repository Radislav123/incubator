from arcade import Sprite

from apps.deliverer.service.color import Color
from apps.deliverer.settings import Settings
from core.texture import Texture


class InterestPointZone(Sprite):
    settings = Settings()


class InterestPoint(Sprite):
    settings = Settings()

    def __init__(self, center_x: float, center_y: float, **kwargs) -> None:
        radius = 10
        texture = Texture.create_circle(radius, 2, color = Color.INTEREST_POINT)
        super().__init__(texture, 1, center_x, center_y, **kwargs)

        zone_radius = radius + 20
        zone_color = tuple(
            (Color.INTEREST_POINT[x] + Color.BACKGROUND[x]) // 2
            for x in range(len(Color.INTEREST_POINT))
        )
        zone_texture = Texture.create_circle(zone_radius, 1, color = zone_color)
        self.zone = InterestPointZone(zone_texture, 1, center_x, center_y, **kwargs)

    def __repr__(self) -> str:
        return f"InterestPoint{self.position}"
