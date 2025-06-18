import logging
import sys
from pathlib import Path

from bot.config import settings

LOG_FILE_PATH = settings.paths.logs / "log.txt"
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str = "") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.logging.log_level.upper(), logging.INFO))
    # Проверяем есть ли хендлеры такие же
    if not logger.hasHandlers():
        logger.addHandler(logging.StreamHandler(sys.stdout))  # Для docker logs
        handler = logging.FileHandler(
            filename=LOG_FILE_PATH,
            mode='a',
            encoding='utf-8'
        )
        formatter = logging.Formatter(settings.logging.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
