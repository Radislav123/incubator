from arcade.gui import UIOnClickEvent

from core.service.anchor import Anchor
from core.ui.button.texture_button import TextureButton
from core.view.base import BaseView


class ExitButton(TextureButton):
    def __init__(self, view: "SimulationView", **kwargs) -> None:
        super().__init__(text = "Выход", **kwargs)

        self.view = view
        self.main_menu_view = self.view.window.main_menu_view

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.window.show_view(self.main_menu_view)


class SimulationView(BaseView):
    exit_button_class = ExitButton
    exit_button: exit_button_class

    def on_show_view(self) -> None:
        super().on_show_view()

        self.exit_button = self.exit_button_class(self)
        self.exit_button.move_to(self.window.width, self.window.height, Anchor.X.RIGHT, Anchor.Y.TOP)
        self.ui_manager.add(self.exit_button)
