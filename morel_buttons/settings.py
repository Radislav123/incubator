from core.settings import Settings as CoreSettings


class Settings(CoreSettings):
    APP_NAME = "more_buttons"
    APP_INDEX = 2

    def __init__(self) -> None:
        super().__init__()

        # в секундах
        self.AUTOMATION_PERIOD = 1
