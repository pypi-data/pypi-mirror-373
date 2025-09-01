import logging


class SimpleLogger:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled: bool = enabled
        self.logger: logging.Logger = logging.getLogger("simple_logger")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def log(self, message: str) -> None:
        if self.enabled:
            self.logger.debug(message)


default_logger: SimpleLogger = SimpleLogger(enabled=True)
