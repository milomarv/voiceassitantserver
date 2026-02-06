from depends import Logger, Settings


class BaseService:
    def __init__(self, location: str) -> None:
        self.settings = Settings.from_env()
        self.logger = Logger(location)
