import copy
import glob
import os
from pathlib import Path
from typing import TYPE_CHECKING

from arcade.gui import UIOnClickEvent, UITextureButton

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
    settings = Settings()

    default_width = 400
    default_height = 50

    latest_normal_style = UITextureButton.UIStyle(
        font_size = 14,
        font_name = settings.FONTS,
        font_color = Color.LATEST_PATH_TEXT
    )
    latest_hovered_style = UITextureButton.UIStyle(
        font_size = 16,
        font_name = settings.FONTS,
        font_color = Color.LATEST_PATH_TEXT
    )
    LATEST_DEFAULT_STYLE = {
        "normal": latest_normal_style,
        "hover": latest_hovered_style,
        "press": latest_hovered_style,
        "disabled": latest_normal_style
    }

    def __init__(self, load_tab: "LoadTab", path: str | None, **kwargs) -> None:
        self.load_tab = load_tab
        self.view = self.load_tab.view
        self.path = path

        if self.path is None:
            self.brain = Brain.get_default()
            text = "Новый"
        else:
            self.brain = Brain.load_from_file(self.path)
            text = [
                self.brain.loading_dict["generation"],
                self.brain.loading_dict["score"],
                self.path.split('\\')[-1].split('.')[0]
            ]
            text = " ".join(str(x) for x in text)

        super().__init__(text = text, width = self.default_width, height = self.default_height, **kwargs)

    def __gt__(self, other: "Load") -> bool:
        if self.path is not None and other.path is not None:
            params = ["score", "generation"]
            for param in params:
                self_param = self.brain.loading_dict[param]
                other_param = other.brain.loading_dict[param]
                if self_param != other_param:
                    greater = self_param < other_param
                    break
            else:
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

    def update_style(self, latest: bool) -> None:
        if latest:
            style = self.LATEST_DEFAULT_STYLE
        else:
            style = self.DEFAULT_STYLE
        if self.style != style:
            self.style = style


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
            new_paths = set(glob.glob(f"{self.settings.BRAINS_PATH}/*.{Brain.file_extension}"))
            latest_path = max(new_paths, key = os.path.getctime)
        else:
            new_paths = set()
            latest_path = None
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
            load.update_style(load.path == latest_path)

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
