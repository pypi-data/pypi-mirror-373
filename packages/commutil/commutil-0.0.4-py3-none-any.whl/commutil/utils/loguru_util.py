from typing import Optional
import threading
import sys

LOGURU_CONFIG = {
    "console": {
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> [<level>{level}</level>] <cyan>{name}</cyan>:<cyan>{line}</cyan> <level>{message}</level>",
        "level": "INFO",
    },
    "file": {
        "rotation": "50 MB",
        "retention": "90 days",
        "level": "INFO",
        "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} [{level}] {name}:{function}:{line} {message}",
    },
}


class LoggerFactory:
    _instances = {}
    _lock = threading.RLock()
    _logger = None

    def __new__(cls, name: str = "global", log_path: Optional[str] = None):
        if name not in cls._instances:
            with cls._lock:
                if name not in cls._instances:
                    cls._instances[name] = super().__new__(cls)
                    cls._instances[name]._initialized = False
        return cls._instances[name]

    def __init__(self, name: str = "global", log_path: Optional[str] = None):
        if LoggerFactory._logger is None:
            try:
                from loguru import logger
                LoggerFactory._logger = logger
            except ImportError:
                import logging
                LoggerFactory._logger = logging.getLogger()
                print("Warning: Loguru not found, using standard logging.")

        if not getattr(self, '_initialized', False):
            self.name = name
            self._setup_logger(log_path)
            self._initialized = True

    def _setup_logger(self, log_path: Optional[str] = None):
        logger = LoggerFactory._logger
        logger.remove()

        logger.add(
            sys.stdout,
            format=LOGURU_CONFIG["console"]["format"],
            level=LOGURU_CONFIG["console"]["level"],
            enqueue=True,
            filter=lambda record: record["extra"].get("name") == self.name
        )

        if log_path:
            self._file_handler = logger.add(
                log_path,
                rotation=LOGURU_CONFIG["file"]["rotation"],
                retention=LOGURU_CONFIG["file"]["retention"],
                level=LOGURU_CONFIG["file"]["level"],
                format=LOGURU_CONFIG["file"]["format"],
                enqueue=True,
                compression="zip",
                filter=lambda record: record["extra"].get("name") == self.name
            )

    @property
    def logger(self):
        return LoggerFactory._logger.bind(name=self.name)


def get_Logger(name: str, log_path: str=None):
    return LoggerFactory(name=name, log_path=log_path).logger