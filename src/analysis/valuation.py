"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from ..utils import get_logger

_logger = get_logger(__name__)


def _get_row(df: pd.DataFrame | None, label: str) -> pd.Series | None:
    """Safely retrieve a row by label."""

    if df is None or df.empty or label not in df.index:
        return None
    return df.loc[label]


def _safe_eps_row(df: pd.DataFrame | None) -> pd.Series | None:
    """Retrieve an EPS row while swallowing unexpected statement formats."""

    try:
        return _get_row(df, "Diluted EPS")
    except AttributeError as exc:  # Defensive: yfinance objects can be quirky
        _logger.warning("Could not read EPS row: %s", exc)
        return None


def _get_eps_history(ticker_obj: yf.Ticker) -> pd.Series:
    """Return a historical EPS series from the ticker's financial statements."""

    quarterly_eps = _safe_eps_row(ticker_obj.quarterly_income_stmt)
    if quarterly_eps is not None and not quarterly_eps.empty:
        quarterly_eps.index = pd.to_datetime(quarterly_eps.index)
        return quarterly_eps.sort_index()

    annual_eps = _safe_eps_row(ticker_obj.income_stmt)
    if annual_eps is not None and not annual_eps.empty:
        annual_eps.index = pd.to_datetime(annual_eps.index)
        return annual_eps.sort_index()

    trailing_eps = ticker_obj.info.get("trailingEps")
    if trailing_eps is not None:
        return pd.Series({pd.Timestamp.today().normalize(): trailing_eps})

    return pd.Series(dtype=float)


def build_pe_series(ticker: str, period: str = "5y") -> pd.Series:
    """Build a P/E ratio series using historical prices and time-aware EPS."""

    ticker_obj = yf.Ticker(ticker)
    history = ticker_obj.history(period=period)
    eps_history = _get_eps_history(ticker_obj)
    if eps_history.empty:
        _logger.warning("Missing EPS for %s; cannot compute P/E series", ticker)
        return pd.Series(dtype=float)

    aligned_eps = eps_history.reindex(history.index, method="ffill")
    aligned_eps = aligned_eps.replace(0, pd.NA)
    if aligned_eps.isna().all():
        _logger.warning("No usable EPS values for %s; cannot compute P/E series", ticker)
        return pd.Series(dtype=float)

    pe_series = history["Close"] / aligned_eps
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
