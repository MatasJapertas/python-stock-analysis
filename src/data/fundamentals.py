"""Fundamentals data loaders using yfinance."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from ..utils import get_logger

_logger = get_logger(__name__)


def get_company_info(ticker: str) -> dict:
    """Return basic company info dictionary."""

    _logger.info("Fetching company info for %s", ticker)
    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.info or {}


def get_income_statement(ticker: str, annual: bool = True) -> pd.DataFrame:
    """Return income statement as a DataFrame."""

    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.income_stmt if annual else ticker_obj.quarterly_income_stmt


def get_cashflow_statement(ticker: str, annual: bool = True) -> pd.DataFrame:
    """Return cashflow statement as a DataFrame."""

    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.cashflow if annual else ticker_obj.quarterly_cashflow


def get_balance_sheet(ticker: str, annual: bool = True) -> pd.DataFrame:
    """Return balance sheet as a DataFrame."""

    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.balance_sheet if annual else ticker_obj.quarterly_balance_sheet


def get_market_cap_from_info(info: dict) -> float | None:
    """Extract market cap from the info dictionary if present."""

    return info.get("marketCap")
