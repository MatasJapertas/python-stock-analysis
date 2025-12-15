import json

from src.utils import config as config_utils
from src.utils import logging as logging_utils


def test_get_logger_creates_cached_logger(tmp_path):
    logger = logging_utils.get_logger("test_logger")
    second = logging_utils.get_logger("test_logger")

    assert logger is second
    assert len(logger.handlers) == 2
    log_file = tmp_path / "logs" / "app.log"
    assert log_file.exists()


def test_get_logger_does_not_duplicate_handlers():
    logger = logging_utils.get_logger("duplicate")
    initial_handlers = list(logger.handlers)
    logger_again = logging_utils.get_logger("duplicate")

    assert logger_again.handlers == initial_handlers


def test_load_config_uses_defaults_when_missing():
    loaded = config_utils.load_config()

    assert loaded == config_utils.DEFAULT_CONFIG
    assert config_utils._CONFIG_CACHE is loaded


def test_load_config_reads_file(tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_data = {"data": {"default_period": "1y", "default_interval": "1wk"}}
    cfg_path.write_text(json.dumps(cfg_data), encoding="utf-8")

    loaded = config_utils.load_config(cfg_path)

    assert loaded["data"]["default_period"] == "1y"
    assert loaded["data"]["default_interval"] == "1wk"


def test_load_config_handles_invalid_json(tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{invalid json", encoding="utf-8")

    loaded = config_utils.load_config(cfg_path)

    assert loaded == config_utils.DEFAULT_CONFIG


def test_get_config_value_with_missing_path_returns_default():
    config_utils._CONFIG_CACHE = {"top": {"nested": 5}}

    assert config_utils.get_config_value("top.missing", default="fallback") == "fallback"


def test_get_config_value_reads_nested_paths():
    config_utils._CONFIG_CACHE = {"outer": {"inner": {"value": 10}}}

    assert config_utils.get_config_value("outer.inner.value") == 10
