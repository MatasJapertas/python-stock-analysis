"""
Created on 2025.12.15

@author: Matas Japertas
"""

import pandas as pd

from src.analysis import screener
from src.core import FundamentalsSnapshot


def test_screen_tickers_filters_by_thresholds(monkeypatch):
    snapshots = {
        "AAPL": FundamentalsSnapshot(
            ticker="AAPL",
            trailing_eps=3,
            market_cap=1,
            revenue=1,
            free_cash_flow=1,
            net_income=1,
            equity=1,
            debt=1,
            pe_ratio=15,
            pfcf_ratio=20,
            fcf_yield=5,
            revenue_cagr=None,
            fcf_cagr=None,
            gross_margin=None,
            operating_margin=None,
            net_margin=None,
            score_value=None,
            score_growth=None,
            score_quality=None,
            score_composite=None,
        ),
        "MSFT": FundamentalsSnapshot(
            ticker="MSFT",
            trailing_eps=3,
            market_cap=1,
            revenue=1,
            free_cash_flow=1,
            net_income=1,
            equity=1,
            debt=1,
            pe_ratio=30,
            pfcf_ratio=25,
            fcf_yield=2,
            revenue_cagr=None,
            fcf_cagr=None,
            gross_margin=None,
            operating_margin=None,
            net_margin=None,
            score_value=None,
            score_growth=None,
            score_quality=None,
            score_composite=None,
        ),
    }

    monkeypatch.setattr(screener, "summarize_fundamentals", lambda ticker: snapshots[ticker])

    result = screener.screen_tickers(["AAPL", "MSFT"], min_fcf_yield=3, max_pe=20)

    assert list(result["ticker"]) == ["AAPL"]
    assert result.iloc[0]["fcf_yield"] == 5
    assert result.iloc[0]["pe_ratio"] == 15


def test_run_simple_screener(monkeypatch):
    snapshot = FundamentalsSnapshot(
        ticker="AAPL",
        trailing_eps=None,
        market_cap=None,
        revenue=None,
        free_cash_flow=None,
        net_income=None,
        equity=None,
        debt=None,
        pe_ratio=None,
        pfcf_ratio=None,
        fcf_yield=None,
        revenue_cagr=None,
        fcf_cagr=None,
        gross_margin=None,
        operating_margin=None,
        net_margin=None,
        score_value=None,
        score_growth=None,
        score_quality=None,
        score_composite=None,
    )
    monkeypatch.setattr(screener, "summarize_fundamentals", lambda ticker: snapshot)

    result = screener.run_simple_screener(["AAPL"])

    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["ticker"] == "AAPL"
