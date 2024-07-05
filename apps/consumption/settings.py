from core.settings import Settings as CoreSettings


class Settings(CoreSettings):
    APP_NAME = "consumption"
    APP_INDEX = 6

    def __init__(self) -> None:
        super().__init__()

        self.SETTLEMENTS_FOLDER = f"{self.IMAGES_FOLDER}/settlement"
