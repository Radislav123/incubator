from core.service.anchor import Anchor
from core.ui.button.texture_button import TextureButton
from core.view.simulation import SimulationView as CoreSimulationView
from simple_deliverer.settings import Settings


class ScoreLabel(TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        super().__init__(text = str(self.view.score), **kwargs)


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: int
    score_label: ScoreLabel

    def reset_info(self) -> None:
        self.score = 0

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.score_label = ScoreLabel(self)
        self.ui_manager.add(self.score_label)
        self.score_label.move_to(0, self.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
