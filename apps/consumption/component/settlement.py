import PIL.Image
from arcade import Sprite
from pyglet.math import Vec3

from apps.consumption.component.manufacturer import Manufacturer
from apps.consumption.component.population import Population
from apps.consumption.service.unique import Unique
from apps.consumption.settings import Settings
from core.texture import Texture


class SettlementProjection(Sprite):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_angle = self.angle
        self.default_scale = self.scale
        self.default_color = self.color


class Settlement(Unique):
    settings = Settings()
    images: dict[int, PIL.Image.Image] = {}

    def __init__(self, position: Vec3) -> None:
        self.stage = 0
        self.position = position
        self.populations: list[Population] = []
        self.manufacturers: list[Manufacturer] = []

        texture = self.get_texture()
        self.projection = SettlementProjection(texture)

    def get_texture(self) -> Texture:
        if self.stage not in self.images:
            image = PIL.Image.open(f"{self.settings.SETTLEMENTS_FOLDER}/settlement_0.png")
            image = image.resize((50, 50))
            self.images[self.stage] = image
        texture = Texture(self.images[self.stage])
        return texture
