from arcade.gui import UIBoxLayout, UIOnClickEvent

from apps.clicker.view.simulation import SimulationView as ClickerSimulationView
from apps.consumption.view.simulation import SimulationView as ConsumptionSimulationView
from apps.deliverer.view.simulation import SimulationView as SimpleDelivererSimulationView
from apps.gravity.view.simulation import SimulationView as GravitySimulationView
from apps.simple_clicker.view.simulation import SimulationView as SimpleClickerSimulationView
from apps.snake.view.simulation import SimulationView as SnakeSimulationView
from core.ui.button.texture_button import TextureButton
from core.view.menu import MenuView
from core.view.simulation import SimulationView


class GameButton(TextureButton):
    def __init__(self, view: SimulationView, **kwargs) -> None:
        super().__init__(width = 200, height = 50, **kwargs)
        self.view = view

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.window.show_view(self.view)


class MainMenuView(MenuView):
    def __init__(self) -> None:
        super().__init__()

        self.app_views = (
            SimpleClickerSimulationView(),
            ClickerSimulationView(),
            GravitySimulationView(),
            SnakeSimulationView(),
            SimpleDelivererSimulationView(),
            ConsumptionSimulationView()
        )

    def construct_app_buttons(self) -> None:
        layout = UIBoxLayout()

        for view in self.app_views:
            button = GameButton(view, text = view.settings.PRETTY_APP_NAME)
            layout.add(button)

        layout.fit_content()
        layout.center_on_screen()
        self.ui_manager.add(layout)

    def on_show_view(self) -> None:
        super().on_show_view()

        self.construct_app_buttons()
