"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import math
from datetime import date
from typing import Optional

import pandas as pd
import yfinance as yf

from core import FundamentalsSnapshot
from data import get_cashflow_statement, get_company_info, get_income_statement
from utils import get_logger

_logger = get_logger(__name__)


def _get_row(df: pd.DataFrame | None, label: str) -> Optional[pd.Series]:
    """Safely retrieve a row by label."""

    if df is None or df.empty or label not in df.index:
        return None
    return df.loc[label]


def safe_div(numerator: float | None, denominator: float | None) -> Optional[float]:
    """Divide while guarding against zero or None."""

    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def compute_pe(price: float | None, eps: float | None) -> Optional[float]:
    return safe_div(price, eps)


def compute_pfcf(price: float | None, fcf_per_share: float | None) -> Optional[float]:
    return safe_div(price, fcf_per_share)


def compute_fcf_yield(fcf: float | None, market_cap: float | None) -> Optional[float]:
    value = safe_div(fcf, market_cap)
    return value * 100 if value is not None else None


def cagr(start: float | None, end: float | None, years: float | None) -> Optional[float]:
    if None in (start, end, years) or start <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def compute_revenue_cagr(income_stmt: pd.DataFrame) -> Optional[float]:
    if income_stmt is None or income_stmt.empty:
        return None
    revenues = _get_row(income_stmt, "Total Revenue")
    if revenues is None or revenues.empty:
        return None
    years = max(len(revenues) - 1, 1)
    return cagr(revenues.iloc[-1], revenues.iloc[0], years)


def compute_fcf_cagr(cashflow: pd.DataFrame) -> Optional[float]:
    if cashflow is None or cashflow.empty:
        return None
    fcf_series = _get_row(cashflow, "Free Cash Flow")
    if fcf_series is None or fcf_series.empty:
        return None
    years = max(len(fcf_series) - 1, 1)
    return cagr(fcf_series.iloc[-1], fcf_series.iloc[0], years)


def compute_margins(income_stmt: pd.DataFrame) -> tuple[Optional[float], Optional[float], Optional[float]]:
    if income_stmt is None or income_stmt.empty:
        return None, None, None
    revenue = _get_row(income_stmt, "Total Revenue")
    gross_profit = _get_row(income_stmt, "Gross Profit")
    operating_income = _get_row(income_stmt, "Operating Income")
    net_income = _get_row(income_stmt, "Net Income")

    if revenue is None or revenue.empty:
        return None, None, None

    gross_margin = (
        safe_div(gross_profit.iloc[0], revenue.iloc[0]) * 100
        if gross_profit is not None and not gross_profit.empty
        else None
    )
    operating_margin = (
        safe_div(operating_income.iloc[0], revenue.iloc[0]) * 100
        if operating_income is not None and not operating_income.empty
        else None
    )
    net_margin = (
        safe_div(net_income.iloc[0], revenue.iloc[0]) * 100
        if net_income is not None and not net_income.empty
        else None
    )
    return gross_margin, operating_margin, net_margin


def compute_value_score(fcf_yield: Optional[float], pe_ratio: Optional[float]) -> Optional[float]:
    if fcf_yield is None or pe_ratio is None or pe_ratio <= 0:
        return None
    return fcf_yield + (1 / pe_ratio)


def compute_growth_score(revenue_cagr: Optional[float], fcf_cagr: Optional[float]) -> Optional[float]:
    if revenue_cagr is None or fcf_cagr is None:
        return None
    return revenue_cagr + fcf_cagr


def compute_quality_score(gross_margin: Optional[float], operating_margin: Optional[float], net_margin: Optional[float]) -> Optional[float]:
    margins = [m for m in (gross_margin, operating_margin, net_margin) if m is not None]
    if not margins:
        return None
    return sum(margins) / len(margins)


def compute_composite_score(value_score: Optional[float], growth_score: Optional[float], quality_score: Optional[float]) -> Optional[float]:
    scores = [s for s in (value_score, growth_score, quality_score) if s is not None]
    if not scores:
        return None
    return sum(scores) / len(scores)


def summarize_fundamentals(ticker: str) -> FundamentalsSnapshot:
    """Compute a basic fundamentals snapshot for a ticker.

    This is a simplified placeholder that should be refined with more accurate calculations.
    """

    _logger.info("Summarizing fundamentals for %s", ticker)
    info = get_company_info(ticker)
    income_stmt = get_income_statement(ticker)

    market_cap = info.get("marketCap")
    trailing_eps = info.get("trailingEps")
    revenue_series = _get_row(income_stmt, "Total Revenue")
    net_income_series = _get_row(income_stmt, "Net Income")
    revenue = revenue_series.iloc[0] if revenue_series is not None and not revenue_series.empty else None
    net_income = net_income_series.iloc[0] if net_income_series is not None and not net_income_series.empty else None

    price = info.get("currentPrice")

    pe_ratio = compute_pe(price, trailing_eps)
    fcf = info.get("freeCashflow")
    pfcf_ratio = compute_pfcf(price, info.get("fcfPerShare"))
    fcf_yield = compute_fcf_yield(fcf, market_cap)

    revenue_cagr = compute_revenue_cagr(get_income_statement(ticker, annual=True))
    fcf_cagr = compute_fcf_cagr(get_cashflow_statement(ticker, annual=True))
    gross_margin, operating_margin, net_margin = compute_margins(income_stmt)

    value_score = compute_value_score(fcf_yield, pe_ratio)
    growth_score = compute_growth_score(revenue_cagr, fcf_cagr)
    quality_score = compute_quality_score(gross_margin, operating_margin, net_margin)
    composite_score = compute_composite_score(value_score, growth_score, quality_score)

    return FundamentalsSnapshot(
        ticker=ticker,
        trailing_eps=trailing_eps,
        market_cap=market_cap,
        revenue=revenue,
        free_cash_flow=fcf,
        net_income=net_income,
        equity=info.get("totalStockholderEquity"),
        debt=info.get("totalDebt"),
        pe_ratio=pe_ratio,
        pfcf_ratio=pfcf_ratio,
        fcf_yield=fcf_yield,
        revenue_cagr=revenue_cagr,
        fcf_cagr=fcf_cagr,
        gross_margin=gross_margin,
        operating_margin=operating_margin,
        net_margin=net_margin,
        score_value=value_score,
        score_growth=growth_score,
        score_quality=quality_score,
        score_composite=composite_score,
        as_of=date.today(),
    )
