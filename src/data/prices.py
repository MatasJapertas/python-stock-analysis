"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd
import yfinance as yf

from ..utils import get_logger

_logger = get_logger(__name__)


def get_price_history(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical prices for a single ticker."""

    _logger.info("Fetching price history for %s", ticker)
    ticker_obj = yf.Ticker(ticker)
    history = ticker_obj.history(period=period, interval=interval)
    if history.empty:
        _logger.warning("No history returned for %s", ticker)
    return history


def get_multiple_price_histories(
    tickers: Iterable[str], period: str = "5y", interval: str = "1d"
) -> dict[str, pd.DataFrame]:
    """Fetch historical prices for multiple tickers."""

    histories: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        histories[ticker] = get_price_history(ticker, period=period, interval=interval)
    return histories


def get_current_price(ticker: str) -> float | None:
    """Fetch the latest closing price for a ticker."""

    _logger.info("Fetching current price for %s", ticker)
    ticker_obj = yf.Ticker(ticker)
    price = ticker_obj.fast_info.get("last_price") if hasattr(ticker_obj, "fast_info") else None
    if price is None:
        _logger.warning("Could not fetch current price for %s", ticker)
    return price


def get_benchmark_prices(benchmark_ticker: str = "^GSPC", period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Fetch benchmark index prices (defaults to S&P 500)."""

    return get_price_history(benchmark_ticker, period=period, interval=interval)
