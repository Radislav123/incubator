import arcade.gui

from core.settings import Settings
from core.view.main_menu import MainMenuView
from logger import Logger


class Window(arcade.Window):
    settings = Settings()
    width = 1200
    height = 700
    default_update_rate = 1/60

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            self.width,
            self.height,
            self.settings.PROJECT_NAME.capitalize(),
            *args,
            center_window = True,
            update_rate = self.default_update_rate,
            **kwargs
        )

        self.logger = Logger(str(self.__class__))
        self.main_menu_view = MainMenuView()

    def start(self) -> None:
        self.show_view(self.main_menu_view)

    def stop(self) -> None:
        pass
