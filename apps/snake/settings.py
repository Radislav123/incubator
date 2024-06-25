from core.settings import Settings as CoreSettings


class Settings(CoreSettings):
    APP_NAME = "snake"
    APP_INDEX = 4

    def __init__(self) -> None:
        super().__init__()

        self.BRAINS_PATH = f"{self.APP_NAME}/brain"
