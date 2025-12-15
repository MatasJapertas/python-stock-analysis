from datetime import date

import pandas as pd
import pytest

from src.analysis import fundamentals
from src.core import FundamentalsSnapshot


def test_safe_division_handles_none_and_zero():
    assert fundamentals.safe_div(None, 1) is None
    assert fundamentals.safe_div(1, 0) is None
    assert fundamentals.safe_div(4, 2) == 2


def test_compute_ratios_and_yield():
    assert fundamentals.compute_pe(10, 2) == 5
    assert fundamentals.compute_pfcf(10, 5) == 2
    assert fundamentals.compute_fcf_yield(200, 1000) == 20


def test_cagr_guard_conditions():
    assert fundamentals.cagr(None, 2, 1) is None
    assert fundamentals.cagr(0, 2, 1) is None
    assert fundamentals.cagr(1, 2, 0) is None


def test_compute_revenue_and_fcf_cagr():
    income_stmt = pd.DataFrame({"2020": [100], "2023": [200]}, index=["Total Revenue"])
    cashflow = pd.DataFrame({"2020": [50], "2023": [100]}, index=["Free Cash Flow"])

    revenue_cagr = fundamentals.compute_revenue_cagr(income_stmt)
    fcf_cagr = fundamentals.compute_fcf_cagr(cashflow)

    assert revenue_cagr == fundamentals.cagr(200, 100, 1)
    assert fcf_cagr == fundamentals.cagr(100, 50, 1)


def test_compute_margins_returns_percentages():
    income_stmt = pd.DataFrame(
        {
            "2023": [1000, 500, 300, 200],
        },
        index=["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
    )

    gross, operating, net = fundamentals.compute_margins(income_stmt)

    assert gross == 50
    assert operating == 30
    assert net == 20


def test_score_functions():
    assert fundamentals.compute_value_score(5, 10) == 5 + 0.1
    assert fundamentals.compute_growth_score(0.1, 0.2) == pytest.approx(0.3)
    assert fundamentals.compute_quality_score(10, 20, None) == 15
    assert fundamentals.compute_composite_score(1, None, 3) == 2


def test_summarize_fundamentals(monkeypatch):
    company_info = {
        "marketCap": 1_000_000,
        "trailingEps": 2.0,
        "currentPrice": 50,
        "freeCashflow": 100_000,
        "fcfPerShare": 5,
        "totalStockholderEquity": 300_000,
        "totalDebt": 50_000,
    }

    income_stmt = pd.DataFrame(
        {
            "2023": [1_000_000, 400_000, 200_000, 150_000],
            "2022": [900_000, 350_000, 180_000, 130_000],
        },
        index=["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
    )
    cashflow = pd.DataFrame({"2023": [100_000], "2022": [80_000]}, index=["Free Cash Flow"])

    monkeypatch.setattr(fundamentals, "get_company_info", lambda ticker: company_info)
    monkeypatch.setattr(fundamentals, "get_income_statement", lambda ticker, annual=True: income_stmt)
    monkeypatch.setattr(fundamentals, "get_cashflow_statement", lambda ticker, annual=True: cashflow)

    snapshot = fundamentals.summarize_fundamentals("MSFT")

    assert isinstance(snapshot, FundamentalsSnapshot)
    assert snapshot.ticker == "MSFT"
    assert snapshot.market_cap == 1_000_000
    assert snapshot.pe_ratio == 25
    assert snapshot.pfcf_ratio == 10
    assert snapshot.fcf_yield == 10
    assert snapshot.score_composite is not None
    assert snapshot.as_of == date.today()
