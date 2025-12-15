"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import pandas as pd

from ..core import FundamentalsSnapshot
from ..utils import get_logger
from .fundamentals import summarize_fundamentals

_logger = get_logger(__name__)


def screen_tickers(
    tickers: list[str],
    min_fcf_yield: float | None = None,
    max_pe: float | None = None) -> pd.DataFrame:
    """Return a DataFrame of tickers passing basic filters."""

    rows = []
    for ticker in tickers:
        snapshot = summarize_fundamentals(ticker)

        rows.append(
            {
                "ticker": ticker,
                "fcf_yield": snapshot.fcf_yield,
                "pe_ratio": snapshot.pe_ratio,
            }
        )

    df = pd.DataFrame(rows)
    if min_fcf_yield is not None:
        df = df[(df["fcf_yield"] >= min_fcf_yield) | df["fcf_yield"].isna()]
    if max_pe is not None:
        df = df[(df["pe_ratio"] <= max_pe) | df["pe_ratio"].isna()]

    return df.reset_index(drop=True)


def run_simple_screener(tickers: list[str]) -> pd.DataFrame:
    """Run a screener with default thresholds and return results."""

    return screen_tickers(tickers)
