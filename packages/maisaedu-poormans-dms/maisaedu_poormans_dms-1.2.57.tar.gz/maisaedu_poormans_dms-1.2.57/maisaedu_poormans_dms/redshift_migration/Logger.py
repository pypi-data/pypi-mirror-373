from .Types import LOGGER_PREFECT


class Logger:
    def __init__(self, logger=None):
        if logger is not None:
            if logger["type"] == LOGGER_PREFECT:
                self.logger = logger["instance"]
        else:
            self.logger = None

    def info(self, message):
        if self.logger is not None:
            self.logger.info(message)
        else:
            print(message)

    def error(self, message):
        if self.logger is not None:
            self.logger.error(message)
        else:
            print(message)
