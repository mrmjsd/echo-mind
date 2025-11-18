import logging
import os
from typing import Optional


_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def setup_logging(level: Optional[str] = None) -> None:
    """Configure root logging once for the application.

    Respects LOG_LEVEL env (default INFO). Safe to call multiple times.
    """
    if logging.getLogger().handlers:
        # Already configured
        return

    env_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, env_level, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a module-specific logger with app-wide configuration applied."""
    setup_logging()
    return logging.getLogger(name)
