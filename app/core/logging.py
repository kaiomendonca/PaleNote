import logging
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter
from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings

LOG_LEVEL = settings.LOG_LEVEL.upper()
ENVIROMENT = settings.ENVIRONMENT.lower()
REPOSITORY_LOGGER_PREFIX = "app.repositories"


class LoggerPrefixFilter(logging.Filter):
    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith(self.prefix)


def configure_logging() -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    root_logger.setLevel(LOG_LEVEL)

    if ENVIROMENT == "production":
        formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    else:
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    repository_handler = RotatingFileHandler(
        filename="logs/repository.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    repository_handler.setFormatter(formatter)

    repository_handler.addFilter(LoggerPrefixFilter(REPOSITORY_LOGGER_PREFIX))

    root_logger.addHandler(repository_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
