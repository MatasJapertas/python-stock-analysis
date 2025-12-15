"""
Created on 2025.12.15

@author: Matas Japertas
"""

import logging
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils import config as config_utils
from src.utils import logging as logging_utils


@pytest.fixture(autouse=True)
def reset_environment(tmp_path, monkeypatch):
    """Reset caches and work inside a temp directory for isolation."""

    monkeypatch.chdir(tmp_path)

    for logger in list(logging_utils._LOGGER_CACHE.values()):
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
    logging_utils._LOGGER_CACHE.clear()

    config_utils._CONFIG_CACHE = None

    yield

    # Ensure no lingering log files hold open handles
    for logger_name, logger in logging.Logger.manager.loggerDict.items():
        if not isinstance(logger, logging.Logger):
            continue
        for handler in list(logger.handlers):
            if isinstance(getattr(handler, "baseFilename", None), str) and handler.baseFilename.startswith(
                str(tmp_path)
            ):
                logger.removeHandler(handler)
                handler.close()

    # Clean up temporary log directories if created
    log_dir = Path(os.getcwd()) / "logs"
    if log_dir.exists():
        for log_file in log_dir.glob("*"):
            log_file.unlink()
        log_dir.rmdir()
