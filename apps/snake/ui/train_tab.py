import datetime
from typing import TYPE_CHECKING

from apps.snake.service.color import Color
from apps.snake.settings import Settings
from apps.snake.ui.mixin import SnakeStyleButtonMixin
from core.service.anchor import Anchor
from core.texture import Texture
from core.ui.layout.box_layout import BoxLayout
from core.ui.text.label import Label as CoreLabel


if TYPE_CHECKING:
    from apps.snake.view.simulation import SimulationView


class TrainLabel(SnakeStyleButtonMixin, CoreLabel):
    default_width = 400
    default_height = 50

    def __init__(self, train_tab: "TrainTab", **kwargs):
        self.train_tab = train_tab
        self.view = self.train_tab.view
        super().__init__(width = self.default_width, height = self.default_height, **kwargs)
        self.place_text(Anchor.X.LEFT, align_x = 5)
        self.update_text()

    def get_text(self) -> str:
        raise NotImplementedError()

    def update_text(self) -> None:
        text = self.get_text()
        if self.text != text:
            self.text = text


class GenerationLabel(TrainLabel):
    def get_text(self) -> str:
        return f"Поколение: {self.view.reference_brains[0].generation}/{self.view.max_generation}"


class ScoreLabel(TrainLabel):
    def get_text(self) -> str:
        return f"Последний счёт: {tuple(x.pretty_score for x in self.view.reference_brains)}"


class AgeLabel(TrainLabel):
    def get_text(self) -> str:
        return f"Последний возраст: {tuple(x.age for x in self.view.reference_brains)}"


class ArenaLabel(TrainLabel):
    def get_text(self) -> str:
        return f"Арена: {self.view.training_arena_index}/{len(self.view.training_arenas)}"


class AverageTimeLabel(TrainLabel):
    average_time: float = None

    def get_text(self) -> str:
        if self.view.last_generation_trained_time is None:
            time = "∞"
        else:
            try:
                all_time = self.view.last_generation_trained_time - self.view.training_start_time
                trained_generations = self.view.reference_brains[0].generation - self.view.start_generation
                self.__class__.average_time = all_time.total_seconds() / trained_generations
                time = self.get_average_time()
            except ZeroDivisionError:
                time = "∞"
        return f"Время на поколение: {time}"

    def get_average_time(self) -> datetime.timedelta:
        return datetime.timedelta(seconds = self.__class__.average_time)


class EstimatedTime(TrainLabel):
    def get_text(self) -> str:
        if self.train_tab.average_time_label.average_time is None:
            time = "∞"
        else:
            generations_left = self.view.max_generation - self.view.reference_brains[0].generation
            time = self.train_tab.average_time_label.get_average_time() * generations_left
        return f"Оставшееся время: {time}"


class TrainTab(BoxLayout):
    settings = Settings()

    def __init__(self, view: "SimulationView", **kwargs) -> None:
        self.view = view
        self.average_time_label = AverageTimeLabel(self)
        self.labels = [
            GenerationLabel(self),
            ScoreLabel(self),
            AgeLabel(self),
            ArenaLabel(self),
            self.average_time_label,
            EstimatedTime(self)
        ]
        super().__init__(children = self.labels, **kwargs)

        self.with_padding(all = self.gap)
        self.fit_content()
        self.with_background(
            texture = Texture.create_rounded_rectangle(
                self.size,
                5,
                color = Color.NORMAL,
                border_color = Color.BORDER
            )
        )
        self.move_to(0, self.view.window.height, Anchor.X.LEFT, Anchor.Y.TOP)

    def update_labels(self) -> None:
        for label in self.children:
            label: TrainLabel
            label.update_text()
