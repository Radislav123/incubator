from apps.consumption.settings import Settings
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()

    def __init__(self) -> None:
        super().__init__()

    def on_show_view(self) -> None:
        super().on_show_view()

    def on_update(self, delta_time: float) -> None:
        print(delta_time)
