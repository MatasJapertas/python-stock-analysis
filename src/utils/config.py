"""Configuration loading and access helpers."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .logging import get_logger

DEFAULT_CONFIG: dict[str, Any] = {
    "data": {
        "default_period": "5y",
        "default_interval": "1d",
    },
    "analysis": {
        "discount_rate": 0.08,
        "terminal_growth_rate": 0.02,
    },
}

_CONFIG_CACHE: dict[str, Any] | None = None
_logger = get_logger(__name__)


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load configuration from JSON or return defaults."""

    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = path or Path("config.json")
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                _CONFIG_CACHE = json.load(f)
                _logger.info("Loaded config from %s", config_path)
        except (json.JSONDecodeError, OSError) as exc:
            _logger.error("Failed to load config from %s: %s", config_path, exc)
            _CONFIG_CACHE = DEFAULT_CONFIG
    else:
        _logger.warning("Config file not found at %s, using defaults", config_path)
        _CONFIG_CACHE = DEFAULT_CONFIG

    return _CONFIG_CACHE


def get_config_value(path: str, default: Any | None = None) -> Any | None:
    """Retrieve a nested config value using dot-separated paths."""

    config = load_config()
    parts = path.split(".")
    value: Any = config
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            _logger.debug("Missing config path %s; returning default", path)
            return default
    return value
