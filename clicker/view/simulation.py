from arcade.gui import UIBoxLayout

from clicker.components.automation.logic import AutoClicker, AutoUpgrader, Logic
from clicker.components.automation.ui import AutoClickButton, AutoUpgradeButton, AutomationBox, AutomationBoxButton, \
    AutomationButton
from clicker.components.increment import AutoIncrementButton, IncrementButton
from clicker.components.info import InfoBox, InfoButton
from clicker.settings import Settings
from core.ui.text import Label
from core.view.simulation import SimulationView as CoreSimulationView


class SimulationView(CoreSimulationView):
    settings = Settings()

    score: float
    displayed_score: str
    total_score: float
    displayed_total_score: str
    auto_increment: float
    displayed_auto_increment: str
    default_increments = [1, 5, 10, 50]

    increment_buttons: list[IncrementButton]
    auto_increment_buttons: list[AutoIncrementButton]

    info_box: InfoBox
    info_button: InfoButton
    automation_box: AutomationBox
    automation_box_button: AutomationBoxButton
    logics: dict[Logic, type[AutomationButton]]

    time: float

    def reset_info(self) -> None:
        self.score = 0
        self.displayed_score = self.get_displayed_score()
        self.total_score = 0
        self.displayed_total_score = self.get_displayed_total_score()
        self.auto_increment = 0
        self.displayed_auto_increment = self.get_displayed_auto_increment()

        self.time = 0

    def prepare_increment(self) -> None:
        label_kwargs = {
            "multiline": True,
            "height": 100
        }
        increment_label = Label(text = "Кнопки активного прироста", **label_kwargs)
        auto_increment_label = Label(text = "Кнопки пассивного прироста", **label_kwargs)

        increment_layout = UIBoxLayout(children = (increment_label,))
        auto_increment_layout = UIBoxLayout(children = (auto_increment_label,))
        layout = UIBoxLayout(
            vertical = False,
            children = (auto_increment_layout, increment_layout),
            space_between = 100
        )

        self.increment_buttons = []
        self.auto_increment_buttons = []
        for increment in self.default_increments:
            button = IncrementButton(increment, self)
            increment_layout.add(button)
            self.increment_buttons.append(button)

            auto_button = AutoIncrementButton(increment, self)
            auto_increment_layout.add(auto_button)
            self.auto_increment_buttons.append(auto_button)

        layout.fit_content()
        layout.center_on_screen()
        self.ui_manager.add(layout)

    def prepare_info(self) -> None:
        self.info_box = InfoBox(self)

        self.info_button = InfoButton(self, text = self.get_displayed_score())
        self.ui_manager.add(self.info_button)

        self.info_box.init()
        self.ui_manager.add(self.info_box)

    def prepare_automation(self) -> None:
        self.logics = {
            AutoClicker(self, self.settings.AUTOMATION_PERIOD): AutoClickButton,
            AutoUpgrader(self, self.settings.AUTOMATION_PERIOD): AutoUpgradeButton
        }
        automation_buttons = [button_class(logic, self) for logic, button_class in self.logics.items()]
        self.automation_box = AutomationBox(automation_buttons, self)

        self.automation_box_button = AutomationBoxButton(self)
        self.ui_manager.add(self.automation_box_button)

        self.automation_box.init()
        self.automation_box_button.update_textures()
        self.ui_manager.add(self.automation_box)

    def on_show_view(self) -> None:
        super().on_show_view()

        self.reset_info()
        self.prepare_info()
        self.prepare_increment()
        self.prepare_automation()

    def get_displayed_score(self) -> str:
        return f"Счет: {int(self.score)}"

    def get_displayed_total_score(self) -> str:
        return f"Общий счет: {int(self.total_score)}"

    def get_displayed_auto_increment(self) -> str:
        return f"Пассивный доход: {int(self.auto_increment)}"

    def on_draw(self) -> None:
        if (score := self.get_displayed_score()) != self.displayed_score:
            self.info_button.text = score
            self.displayed_score = score
        if (total_score := self.get_displayed_total_score()) != self.displayed_total_score:
            self.info_box.total_score_label.text = total_score
            self.displayed_total_score = total_score
        if (self.info_box.visible and
                (auto_increment := self.get_displayed_auto_increment()) != self.displayed_auto_increment):
            self.info_box.auto_increment_label.text = auto_increment
            self.displayed_auto_increment = auto_increment
        super().on_draw()

    def on_update(self, delta_time: float) -> None:
        self.time += delta_time

        delta_score = self.auto_increment * delta_time
        self.score += delta_score
        self.total_score += delta_score

        for logic in self.logics:
            if logic.enabled:
                logic.perform()
