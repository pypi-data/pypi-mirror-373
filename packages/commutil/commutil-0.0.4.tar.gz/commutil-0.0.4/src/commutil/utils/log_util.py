import logging
import sys
import threading
from typing import Dict, Optional

LOG_CONFIG = {
    "console": {
        "level": "INFO",
        "format": f"\033[32m%(asctime)s \033[33m[%(levelname)s] \033[34m%(filename)s:%(lineno)d \033[0m%(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "file": {
        "level": "DEBUG",
        "format": f"%(asctime)s [%(levelname)s %(filename)s:%(funcName)s:%(lineno)d] %(message)s"
    }
}

_LOGGER_CACHE = {}
_LOGGER_LOCK = threading.RLock()


def get_logger(
        name: str = "global",
        log_config: Optional[Dict] = None
) -> logging.Logger:
    with _LOGGER_LOCK:
        if name in _LOGGER_CACHE:
            return _LOGGER_CACHE[name]

        log_config = log_config or LOG_CONFIG
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        if logger.hasHandlers():
            logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_config["console"]["format"], datefmt=log_config["console"].get("datefmt", None)))
        console_handler.setLevel(log_config["console"]["level"])
        logger.addHandler(console_handler)

        _LOGGER_CACHE[name] = logger
        return logger

def attach_file_handler(logger: logging.Logger, log_path: str, log_config: str=None) -> None:
    log_config = log_config or LOG_CONFIG
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_config["file"]["format"], datefmt=log_config["file"].get("datefmt", None)))
    file_handler.setLevel(log_config["file"]["level"])
    logger.addHandler(file_handler)