from arcade.gui import UIOnClickEvent

from core.ui.button.texture_button import TextureButton
from core.view.simulation import SimulationView as CoreSimulationView
from apps.simple_clicker.settings import Settings


class ScoreButton(TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        super().__init__(text = str(self.view.score), **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.score += 1
        self.text = self.view.score


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int
    score_button: ScoreButton

    def reset_info(self) -> None:
        self.score = 0

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.score_button = ScoreButton(self)
        self.ui_manager.add(self.score_button)
        self.score_button.center_on_screen()
