"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import logging
import os
from pathlib import Path


_LOGGER_CACHE: dict[str, logging.Logger] = {}


def _ensure_log_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with console and file handlers.

    The function caches loggers to avoid duplicate handler attachment.
    """

    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_dir = Path(os.getcwd()) / "logs"
        _ensure_log_dir(log_dir)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _LOGGER_CACHE[name] = logger
    return logger
