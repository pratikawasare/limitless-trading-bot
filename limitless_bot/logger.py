import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import Config


def setup_logger(config: Config) -> logging.Logger:
    logger = logging.getLogger("limitless_bot")
    logger.setLevel(getattr(logging, config.log_level, logging.INFO))
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler: Optional[RotatingFileHandler] = RotatingFileHandler(
        config.log_file, maxBytes=5_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
