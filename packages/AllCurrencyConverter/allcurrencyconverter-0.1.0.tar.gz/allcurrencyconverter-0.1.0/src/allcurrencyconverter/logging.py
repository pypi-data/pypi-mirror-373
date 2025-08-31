import sys
import threading

from typing import Any, TextIO, cast

from pydantic import BaseModel
from typeguard import typechecked
from loguru import logger as loguru_logger


class LoggerConfig(BaseModel):
    format: str = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]: <18}</cyan>| "
        "<cyan>{function}:{line}</cyan> - <level>{message}</level>"
    )
    level: str = "INFO"
    compression: str | None = None
    enqueue: bool = False
    backtrace: bool = True
    diagnose: bool = True
    rotation: str = "00:00"
    retention: str = "7 days"


logger_config = LoggerConfig()


@typechecked
class Logger:
    """Setting Loguru + creating loggers"""

    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()
    _console_handler_id: int | None = None

    def __new__(cls, *args: Any, **kwargs: Any):
        if not cls._initialized:
            with cls._lock:
                if not cls._initialized:  # Double-check locking pattern
                    cls._setup()
                    cls._initialized: bool = True
        return super().__new__(cls)

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._logger = loguru_logger.bind(name=name, allcurrencyconverter_logger=True)

    def __getattr__(self, attr: str) -> Any:
        """If class not have attribute - his get Loguru Logger"""
        return getattr(self._logger, attr)

    @classmethod
    def _setup(cls) -> None:
        """Setting Loguru"""
        loguru_logger.level("DEBUG", color="<bold><white>")
        loguru_logger.level("INFO", color="<bold><green>")
        loguru_logger.level("WARNING", color="<bold><yellow>")
        loguru_logger.level("ERROR", color="<bold><red>")
        loguru_logger.level("CRITICAL", color="<bold><light-red>")

        def library_filter(record: Any):
            # Only Logs with this marker
            return record["extra"].get("allcurrencyconverter_logger", False)

        cls._console_handler_id = loguru_logger.add(
            cast(TextIO, sys.stderr),
            format=logger_config.format,
            level=logger_config.level.upper(),
            enqueue=logger_config.enqueue,
            backtrace=logger_config.backtrace,
            diagnose=logger_config.diagnose,
            filter=library_filter,
        )

    @classmethod
    def cleanup(cls) -> None:
        """Remove Loguru handler"""
        if cls._console_handler_id is not None:
            loguru_logger.remove(cls._console_handler_id)
            cls._console_handler_id = None
            cls._initialized = False
