"""
Created on 2025.12.15

@author: Matas Japertas
"""

import math

import pandas as pd
import pytest

from src.analysis import valuation


class DummyTicker:
    def __init__(self, history_df, quarterly_income_stmt=None, annual_income_stmt=None, info=None):
        self._history_df = history_df
        self.quarterly_income_stmt = quarterly_income_stmt
        self.income_stmt = annual_income_stmt
        self.info = info or {}

    def history(self, period="5y"):
        return self._history_df


def test_build_pe_series_with_quarterly_eps(monkeypatch):
    dates = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
    history = pd.DataFrame({"Close": [10.0, 12.0, 14.0]}, index=dates)
    eps_dates = pd.to_datetime(["2023-10-01", "2024-01-01", "2024-04-01"])
    quarterly_income_stmt = pd.DataFrame(
        [[1.0, 1.1, 1.2]], index=["Diluted EPS"], columns=eps_dates
    )
    dummy = DummyTicker(history, quarterly_income_stmt=quarterly_income_stmt, info={})
    monkeypatch.setattr(valuation.yf, "Ticker", lambda ticker: dummy)

    pe_series = valuation.build_pe_series("MSFT", period="1y")

    assert list(pe_series.index) == list(history.index)
    expected = history["Close"] / [1.1, 1.1, 1.1]
    pd.testing.assert_series_equal(pe_series, expected, check_names=False)


def test_build_pe_series_with_missing_eps(monkeypatch):
    history = pd.DataFrame({"Close": [10.0]}, index=pd.date_range("2024-01-01", periods=1))
    dummy = DummyTicker(history, quarterly_income_stmt=pd.DataFrame())
    monkeypatch.setattr(valuation.yf, "Ticker", lambda ticker: dummy)

    pe_series = valuation.build_pe_series("MSFT")

    assert pe_series.empty


def test_compute_rolling_pe_with_datetime_index():
    series = pd.Series([10, 20, 30], index=pd.date_range("2024-01-01", periods=3))

    rolled = valuation.compute_rolling_pe(series, window_days=2)

    assert rolled.iloc[0] == 10
    assert rolled.iloc[2] == pytest.approx((20 + 30) / 2)


def test_compute_rolling_pe_with_numeric_index():
    series = pd.Series([10, 20, 30])

    rolled = valuation.compute_rolling_pe(series, window_days=2)

    assert list(rolled) == [10, 15, 25]


def test_compute_pe_stats_handles_empty():
    stats = valuation.compute_pe_stats(pd.Series(dtype=float))

    assert math.isnan(stats["mean"])
    assert math.isnan(stats["median"])


def test_compute_pe_stats_returns_numbers():
    series = pd.Series([1.0, 2.0, 3.0])

    stats = valuation.compute_pe_stats(series)

    assert stats == {"mean": 2.0, "median": 2.0, "min": 1.0, "max": 3.0}
