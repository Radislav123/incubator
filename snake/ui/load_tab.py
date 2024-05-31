import copy
import glob
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

from arcade.gui import UIEvent, UIMouseScrollEvent, UIOnClickEvent, UITextureButton
from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

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

    default_width = 450
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
        self.index: int | None = None

        if self.path is None:
            self.brain = Brain.get_default()
        else:
            self.brain = Brain.load_from_file(self.path)

        super().__init__(width = self.default_width, height = self.default_height, **kwargs)

        self.place_text(anchor_x = Anchor.X.LEFT, align_x = 10)

    def __gt__(self, other: "Load") -> bool:
        if self.path is not None and other.path is not None:
            brain_params = ["score", "generation"]
            for param in brain_params:
                self_param = getattr(self.brain, param)
                other_param = getattr(other.brain, param)
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

    def update_text(self) -> None:
        spaces_to_char = 2

        max_index_len = int(math.log10(len(self.load_tab.loads))) + 3
        index_str = f"({self.index})"
        index_str_length = (max_index_len - len(index_str)) * spaces_to_char + len(index_str)
        index_str = index_str.rjust(index_str_length)
        text = [index_str]

        if self.path is None:
            text.append("Новый")
        else:
            max_generation_len = max(len(str(x.brain.generation)) for x in self.load_tab.loads.values())
            generation_str = str(self.brain.generation)
            generation_str_len = (max_generation_len - len(generation_str)) * spaces_to_char + len(generation_str)
            generation_str = generation_str.ljust(generation_str_len)

            max_score_len = max(len(str(x.brain.pretty_score)) for x in self.load_tab.loads.values())
            score_str = str(self.brain.pretty_score)
            score_str_len = (max_score_len - len(score_str)) * spaces_to_char + len(score_str)
            score_str = score_str.ljust(score_str_len)

            extend = [
                generation_str,
                score_str,
                self.path.split('\\')[-1].split('.')[0]
            ]
            text.extend(extend)
        text = LoadTabLabel.separator.join(text)

        if self.text != text:
            self.text = text

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


class LoadTabLabel(SnakeStyleButtonMixin, CoreLabel):
    columns = ["(Индекс)", "Название", "Поколение", "Счет"]
    separator = " | "

    def __init__(self) -> None:
        text = self.separator.join(self.columns)
        texture = Texture.create_empty("load tab label", (Load.default_width, Load.default_height))
        super().__init__(text = text, texture = texture, width = Load.default_width, height = Load.default_height)


class LoadTab(BoxLayout):
    settings = Settings()

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.loads: dict[str | None, Load] = {}
        self.max_loads_amount = (self.view.window.height - self.gap) // Load.default_height - 1
        self.label = LoadTabLabel()
        self.load_pane = BoxLayout()
        self.scroll_offset = 0
        super().__init__(
            width = Load.default_width,
            height = (self.max_loads_amount + 1) * Load.default_height,
            children = [self.label, self.load_pane],
            **kwargs
        )

        self.with_padding(all = self.gap)
        self.with_background(
            texture = Texture.create_rounded_rectangle(
                self.size,
                5,
                color = Color.NORMAL,
                border_color = Color.BORDER
            )
        )
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)

    def update_loads(self) -> None:
        if Path(self.settings.BRAINS_PATH).exists():
            new_paths = set(glob.glob(f"{self.settings.BRAINS_PATH}/*.{Brain.file_extension}"))
        else:
            new_paths = set()

        if len(new_paths) > 0:
            latest_path = max(new_paths, key = os.path.getctime)
        else:
            latest_path = None
        new_paths.add(None)

        self.load_pane.clear()
        for child in self.load_pane.children:
            if isinstance(child, Load) and child.path not in new_paths:
                del self.loads[child.path]

        for path in new_paths:
            if path not in self.loads:
                load = Load(self, path)
                self.loads[path] = load

        self.loads = {key: value for key, value in sorted(self.loads.items(), key = lambda x: x[1], reverse = True)}
        for index, load in enumerate(self.loads.values()):
            load.index = index
            load.update_text()
        for load in self.get_visible_loads():
            self.load_pane.add(load)
            load.update_style(load.path == latest_path)

    def on_event(self, event: UIEvent) -> bool | None:
        if isinstance(event, UIMouseScrollEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self.scroll_offset -= int(event.scroll_y)
                self.scroll_offset = max(0, self.scroll_offset)
                self.scroll_offset = min(
                    self.scroll_offset,
                    len(self.loads) - self.load_pane.height // Load.default_height
                )
                self.load_pane.clear()
                for load in self.get_visible_loads():
                    self.load_pane.add(load)

        if super().on_event(event):
            handled = EVENT_HANDLED
        else:
            handled = EVENT_UNHANDLED
        return handled

    def get_visible_loads(self) -> list[Load]:
        return list(self.loads.values())[self.scroll_offset:self.scroll_offset + self.max_loads_amount]
