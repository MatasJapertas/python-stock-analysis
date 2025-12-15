from __future__ import annotations

import pandas as pd
import pytest

from src.data import fundamentals as fundamentals_data
from src.data import prices as prices_data


class DummyTicker:
    def __init__(self, history_df=None, info=None, income_stmt=None, cashflow=None, balance_sheet=None, fast_info=None):
        self._history_df = history_df if history_df is not None else pd.DataFrame()
        self.info = info or {}
        self.income_stmt = income_stmt
        self.quarterly_income_stmt = income_stmt
        self.cashflow = cashflow
        self.quarterly_cashflow = cashflow
        self.balance_sheet = balance_sheet
        self.quarterly_balance_sheet = balance_sheet
        self.fast_info = fast_info or {}

    def history(self, period="5y", interval="1d"):
        return self._history_df


class RaisingTicker:
    def __init__(self, *args, **kwargs):
        pass

    def history(self, *args, **kwargs):
        raise RuntimeError("network error")


@pytest.fixture
def sample_history():
    return pd.DataFrame({"Close": [1.0, 2.0, 3.0]})


def test_get_price_history_returns_data(monkeypatch, sample_history):
    monkeypatch.setattr(prices_data.yf, "Ticker", lambda ticker: DummyTicker(history_df=sample_history))

    result = prices_data.get_price_history("MSFT", period="1y", interval="1wk")

    pd.testing.assert_frame_equal(result, sample_history)


def test_get_price_history_handles_errors(monkeypatch):
    monkeypatch.setattr(prices_data.yf, "Ticker", lambda ticker: RaisingTicker())

    result = prices_data.get_price_history("MSFT")

    assert result.empty


def test_get_multiple_price_histories(monkeypatch, sample_history):
    monkeypatch.setattr(prices_data, "get_price_history", lambda ticker, period, interval: sample_history)

    result = prices_data.get_multiple_price_histories(["AAPL", "GOOG"], period="6mo", interval="1d")

    assert set(result.keys()) == {"AAPL", "GOOG"}
    for history in result.values():
        pd.testing.assert_frame_equal(history, sample_history)


def test_get_current_price_returns_value(monkeypatch):
    ticker = DummyTicker(fast_info={"last_price": 123.45})
    monkeypatch.setattr(prices_data.yf, "Ticker", lambda ticker_symbol: ticker)

    assert prices_data.get_current_price("TSLA") == 123.45


def test_get_current_price_warns_when_missing(monkeypatch):
    ticker = DummyTicker(fast_info={})
    monkeypatch.setattr(prices_data.yf, "Ticker", lambda ticker_symbol: ticker)

    assert prices_data.get_current_price("TSLA") is None


def test_get_benchmark_prices_delegates(monkeypatch, sample_history):
    monkeypatch.setattr(prices_data, "get_price_history", lambda ticker, period, interval: sample_history)

    result = prices_data.get_benchmark_prices("^IXIC", period="3y", interval="1mo")

    pd.testing.assert_frame_equal(result, sample_history)


def test_get_company_info_returns_info(monkeypatch):
    monkeypatch.setattr(fundamentals_data.yf, "Ticker", lambda ticker: DummyTicker(info={"marketCap": 1_000_000}))

    info = fundamentals_data.get_company_info("MSFT")

    assert info["marketCap"] == 1_000_000


def test_get_company_info_handles_errors(monkeypatch):
    def raising(_):
        raise RuntimeError("bad")

    monkeypatch.setattr(fundamentals_data.yf, "Ticker", raising)

    assert fundamentals_data.get_company_info("MSFT") == {}


def test_financial_statement_fetchers(monkeypatch):
    income = pd.DataFrame({"2023": [1]}, index=["Revenue"])
    cashflow = pd.DataFrame({"2023": [2]}, index=["Free Cash Flow"])
    balance_sheet = pd.DataFrame({"2023": [3]}, index=["Total Debt"])
    dummy = DummyTicker(income_stmt=income, cashflow=cashflow, balance_sheet=balance_sheet)
    monkeypatch.setattr(fundamentals_data.yf, "Ticker", lambda ticker: dummy)

    assert fundamentals_data.get_income_statement("MSFT").equals(income)
    assert fundamentals_data.get_cashflow_statement("MSFT").equals(cashflow)
    assert fundamentals_data.get_balance_sheet("MSFT").equals(balance_sheet)


def test_statement_fetchers_handle_errors(monkeypatch):
    def raising(_):
        raise RuntimeError("fail")

    monkeypatch.setattr(fundamentals_data.yf, "Ticker", raising)

    assert fundamentals_data.get_income_statement("MSFT").empty
    assert fundamentals_data.get_cashflow_statement("MSFT").empty
    assert fundamentals_data.get_balance_sheet("MSFT").empty


def test_get_market_cap_from_info():
    info = {"marketCap": 500}

    assert fundamentals_data.get_market_cap_from_info(info) == 500
