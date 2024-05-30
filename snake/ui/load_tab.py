import os
from typing import TYPE_CHECKING

from arcade.gui import UIOnClickEvent

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.ui.layout.box_layout import BoxLayout
from snake.component.brain import Brain
from snake.service.color import Color
from snake.settings import Settings
from snake.ui.mixin import SnakeStyleButtonMixin


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView


class Load(SnakeStyleButtonMixin, TextureButton):
    def __init__(self, load_tab: "LoadTab", path: str | None, **kwargs) -> None:
        self.load_tab = load_tab
        self.view = self.load_tab.view
        self.path = path
        if self.path is not None:
            text = self.path.split('.')[0]
        else:
            text = "clean"
        super().__init__(text = text, width = 400, height = 50, **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        if self.path is None:
            self.view.reference_brain = Brain.get_default()
        else:
            self.view.reference_brain = Brain.load_from_file(self.path)
        self.view.ui_manager.remove(self.load_tab)
        self.view.prepare_actions_tab()


class LoadTab(BoxLayout):
    settings = Settings()

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        super().__init__(**kwargs)
        self.view = view
        self.with_padding(all = self.gap)
        self.loads: dict[str | None, Load] = {}

    def update_loads(self) -> None:
        new_paths = set(os.listdir(self.settings.BRAINS_PATH))
        new_paths.add(None)
        old_amount = len(self.children)

        for child in self.children:
            child: Load
            if child.path not in new_paths:
                self.remove(child)

        for path in new_paths:
            if path not in self.loads:
                load = Load(self, path)
                self.loads[path] = load
                self.add(load)

        if old_amount != len(self.children):
            self.fit_content()
            self.with_background(
                texture = Texture.create_rounded_rectangle(
                    self.size,
                    color = Color.NORMAL,
                    border_color = Color.BORDER
                )
            )
            self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
