"""Valuation helpers for price-to-earnings metrics."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from ..utils import get_logger

_logger = get_logger(__name__)


def build_pe_series(ticker: str, period: str = "5y") -> pd.Series:
    """Build a simple P/E ratio series using price history and trailing EPS.

    TODO: Enhance to use rolling EPS values over time instead of a single trailing value.
    """

    ticker_obj = yf.Ticker(ticker)
    history = ticker_obj.history(period=period)
    eps = ticker_obj.info.get("trailingEps")
    if eps is None or eps == 0:
        _logger.warning("Missing EPS for %s; cannot compute P/E series", ticker)
        return pd.Series(dtype=float)
    pe_series = history["Close"] / eps
    pe_series.name = f"{ticker} P/E"
    return pe_series


def compute_rolling_pe(pe: pd.Series, window_days: int = 30) -> pd.Series:
    """Compute a rolling average P/E over the given window."""

    if pe.empty:
        return pe
    return pe.rolling(window=window_days, min_periods=1).mean()


def compute_pe_stats(pe: pd.Series) -> dict[str, float]:
    """Return basic statistics for a P/E series."""

    if pe.empty:
        return {"mean": float("nan"), "median": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "mean": pe.mean(),
        "median": pe.median(),
        "min": pe.min(),
        "max": pe.max(),
    }
