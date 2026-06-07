import logging

from colorlog import ColoredFormatter
from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings

LOG_LEVEL = settings.LOG_LEVEL.upper()
ENVIROMENT = settings.ENVIRONMENT.lower()


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler()

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

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
