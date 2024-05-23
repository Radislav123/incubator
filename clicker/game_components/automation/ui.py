from typing import TYPE_CHECKING

import PIL.Image
from arcade.gui import UIOnClickEvent

from clicker.game_components.automation.logic import Logic
from clicker.settings import Settings
from core.service import Anchor, Color
from core.texture import Texture
from core.ui.button import TextureButton
from core.ui.layout import BoxLayout


if TYPE_CHECKING:
    from clicker.view.game_view import GameView

BUTTON_DEFAULT_TEXTURES = {
    True: {
        "normal": Texture.create_rounded_rectangle(color = Color.STATE_ENABLED_NORMAL),
        "hover": Texture.create_rounded_rectangle(color = Color.STATE_ENABLED_HOVERED),
        "press": Texture.create_rounded_rectangle(color = Color.STATE_ENABLED_PRESSED),
        "disabled": Texture.create_rounded_rectangle(color = Color.STATE_ENABLED_DISABLED)
    },
    False: {
        "normal": Texture.create_rounded_rectangle(color = Color.STATE_DISABLED_NORMAL),
        "hover": Texture.create_rounded_rectangle(color = Color.STATE_DISABLED_HOVERED),
        "press": Texture.create_rounded_rectangle(color = Color.STATE_DISABLED_PRESSED),
        "disabled": Texture.create_rounded_rectangle(color = Color.STATE_DISABLED_DISABLED)
    },
    None: {
        "normal": Texture.create_rounded_rectangle(color = Color.STATE_INDETERMINATE_NORMAL),
        "hover": Texture.create_rounded_rectangle(color = Color.STATE_INDETERMINATE_HOVERED),
        "press": Texture.create_rounded_rectangle(color = Color.STATE_INDETERMINATE_PRESSED),
        "disabled": Texture.create_rounded_rectangle(color = Color.STATE_INDETERMINATE_DISABLED)
    }
}


class AutomationBox(BoxLayout):
    def __init__(self, automation_buttons: list["AutomationButton"], view: "SimulationView", **kwargs) -> None:
        super().__init__(**kwargs)
        self.automation_buttons = automation_buttons
        self.view = view
        self.visible = True

    def init(self) -> None:
        for button in self.automation_buttons:
            self.add(button)

        self.fit_content()
        self.with_padding(all = self.gap)
        self.with_background(texture = Texture.create_rounded_rectangle(self.size))
        self.move_to(self.view.automation_box_button.right + 1, 0, Anchor.X.LEFT, Anchor.Y.DOWN)


class Button(TextureButton):
    settings = Settings()
    enabled: bool

    default_textures: dict[bool | None, dict[str: Texture]]
    button_image_path: str
    default_textures_changed = False

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.init_default_textures()
        kwargs.update(self.get_textures_init())

        super().__init__(**kwargs)

    def get_textures_init(self) -> dict[str, Texture]:
        return {
            "texture": self.default_textures[self.enabled]["normal"],
            "texture_hovered": self.default_textures[self.enabled]["hover"],
            "texture_pressed": self.default_textures[self.enabled]["press"],
            "texture_disabled": self.default_textures[self.enabled]["disabled"]
        }

    @classmethod
    def init_default_textures(cls) -> None:
        if not cls.default_textures_changed:
            cls.default_textures_changed = True
            image = PIL.Image.open(cls.button_image_path)
            cls.default_textures = {button_state: {state: Texture.from_texture(texture).with_image(image)
                                                   for state, texture in dictionary.items()}
                                    for button_state, dictionary in BUTTON_DEFAULT_TEXTURES.items()}

    def update_textures(self) -> None:
        self._textures = self.default_textures[self.enabled]


class AutomationButton(Button):
    def __init__(self, logic: Logic, view: "SimulationView", **kwargs) -> None:
        self.logic = logic
        super().__init__(view, **kwargs)

    def on_click(self, event: UIOnClickEvent) -> None:
        self.logic.change_state()
        self.update_textures()
        self.view.automation_box_button.update_textures()

    @property
    def enabled(self) -> bool:
        return self.logic.enabled


class AutoUpgradeButton(AutomationButton):
    button_image_path = f"{Button.settings.IMAGES_FOLDER}/refund_0.png"


class AutoClickButton(AutomationButton):
    button_image_path = f"{Button.settings.IMAGES_FOLDER}/click_0.png"


class AutomationBoxButton(Button):
    button_image_path = f"{Button.settings.IMAGES_FOLDER}/gears_0.png"

    def on_click(self, event: UIOnClickEvent) -> None:
        self.view.automation_box.visible = not self.view.automation_box.visible

    @property
    def enabled(self) -> bool:
        enabled_buttons = sum(x.enabled for x in self.view.automation_box.automation_buttons)
        if enabled_buttons == len(self.view.automation_box.automation_buttons):
            state = True
        elif enabled_buttons == 0:
            state = False
        else:
            state = None

        return state
