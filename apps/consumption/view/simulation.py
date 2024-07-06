from pyglet.math import Vec3

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
