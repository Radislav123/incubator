import copy
import os
from pathlib import Path
from typing import TYPE_CHECKING

from arcade.gui import UIOnClickEvent

from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.button.texture_button import TextureButton
from core.ui.layout.box_layout import BoxLayout
from core.ui.text.label import Label as CoreLabel
from snake.component.brain import Brain
from snake.service.color import Color
from snake.settings import Settings
from snake.ui.mixin import SnakeStyleButtonMixin


if TYPE_CHECKING:
    from snake.view.simulation import SimulationView


class Load(SnakeStyleButtonMixin, TextureButton):
    default_width = 400
    default_height = 50

    def __init__(self, load_tab: "LoadTab", path: str | None, **kwargs) -> None:
        self.load_tab = load_tab
        self.view = self.load_tab.view
        self.path = path

        if self.path is None:
            self.brain = Brain.get_default()
            text = "clean"
        else:
            self.brain = Brain.load_from_file(f"{self.settings.BRAINS_PATH}/{self.path}")
            text = [
                self.path.split('.')[0],
                self.brain.loading_dict["generation"],
                self.brain.loading_dict["score"]
            ]
            text = " ".join(str(x) for x in text)

        super().__init__(text = text, width = self.default_width, height = self.default_height, **kwargs)

    def __gt__(self, other: "Load") -> bool:
        if self.path is not None and other.path is not None:
            greater = self.path < other.path
        elif self.path is None:
            greater = True
        else:
            greater = False
        return greater

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.ui_manager.remove(self.load_tab)
        self.view.reference_brain = copy.deepcopy(self.brain)
        self.view.prepare_actions_tab()


class Label(SnakeStyleButtonMixin, CoreLabel):
    def __init__(self) -> None:
        text = "Название Поколение Счет"
        texture = Texture.create_empty("load tab label", (Load.default_width, Load.default_height))
        super().__init__(text = text, texture = texture, width = Load.default_width, height = Load.default_height)


class LoadTab(BoxLayout):
    settings = Settings()

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        super().__init__(**kwargs)
        self.view = view
        self.with_padding(all = self.gap)
        self.loads: dict[str | None, Load] = {}
        self.label = Label()

    def update_loads(self) -> None:
        if Path(self.settings.BRAINS_PATH).exists():
            new_paths = set(os.listdir(self.settings.BRAINS_PATH))
        else:
            new_paths = set()
        new_paths.add(None)
        old_loads = self.loads.copy()

        for child in self.children:
            self.remove(child)
            if isinstance(child, Load) and child.path not in new_paths:
                del self.loads[child.path]

        for path in new_paths:
            if path not in self.loads:
                load = Load(self, path)
                self.loads[path] = load

        self.loads = {key: value for key, value in sorted(self.loads.items(), key = lambda x: x[1], reverse = True)}
        self.add(self.label)
        for load in self.loads.values():
            self.add(load)

        if len(old_loads) != len(self.children):
            self.fit_content()
            self.with_background(
                texture = Texture.create_rounded_rectangle(
                    self.size,
                    4,
                    color = Color.NORMAL,
                    border_color = Color.BORDER
                )
            )
            self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)
