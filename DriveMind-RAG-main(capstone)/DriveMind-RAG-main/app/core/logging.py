"""
logging.py — Centralised logging configuration.
Call setup_logging() once at app startup (in main.py).
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with a clean formatter."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Avoid duplicate handlers if called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)


# Module-level logger for core package
logger = logging.getLogger(__name__)
