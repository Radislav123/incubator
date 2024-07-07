import math

from pyglet.math import Vec2, Vec3

from apps.consumption.component.world import World
from apps.consumption.settings import Settings
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()

    world: World | None = None

    def on_show_view(self) -> None:
        super().on_show_view()

        self.world = World(Vec3(1000, 1000, 1000))
        self.world.projection.prepare(self.window)

    def on_hide_view(self) -> None:
        super().on_hide_view()

        self.world = None

    def on_draw(self) -> None:
        super().on_draw()

        if self.world is not None:
            self.world.on_draw()

    def on_update(self, delta_time: float) -> None:
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int) -> None:
        # ЛКМ - смещение
        if _buttons == 1:
            self.world.projection.offset += Vec2(dx, dy)
            self.world.projection.valid = False
        # ПКМ - поворот
        elif _buttons == 4:
            # от центра окна
            from_center = Vec2(x - self.world.projection.offset.x, y - self.world.projection.offset.y)
            radius = from_center.mag

            sin_degrees = math.degrees(math.asin(dy / radius))
            cos_degrees = math.degrees(math.acos(dx / radius))
            # noinspection PyChainedComparisons
            if from_center.x >= 0 and from_center.y >= 0:
                pass
            elif from_center.x < 0 and from_center.y >= 0:
                sin_degrees = -sin_degrees
            elif from_center.x < 0 and from_center.y < 0:
                sin_degrees = -sin_degrees
                cos_degrees = -cos_degrees
            else:
                cos_degrees = -cos_degrees

            angle = sin_degrees + cos_degrees - math.copysign(90, sin_degrees + cos_degrees)
            # поправка на ошибки округлений
            angle /= 1.269
            self.world.projection.angle += angle
            self.world.projection.valid = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        self.world.projection.scale += scroll_y / 10
        min_scale = 0.1
        max_scale = 2
        self.world.projection.scale = max(min(self.world.projection.scale, max_scale), min_scale)
        self.world.projection.valid = False
