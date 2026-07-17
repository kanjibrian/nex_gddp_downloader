"""
Logging configuration for the NEX-GDDP-CMIP6 downloader.
"""

from __future__ import annotations

import logging
from pathlib import Path

LOGGER_NAME = "nex_gddp"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(log_directory: Path) -> logging.Logger:
    """
    Create and configure the application logger.

    - Console handler at INFO level
    - File handler at DEBUG level writing to ``log_directory/downloader.log``
    """

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler
    log_file = Path(log_directory) / "downloader.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger."""
    return logging.getLogger(LOGGER_NAME)
