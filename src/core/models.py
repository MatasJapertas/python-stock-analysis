"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Stock:
    """Basic stock metadata and identifiers."""

    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    currency: str = "USD"


@dataclass
class FundamentalsSnapshot:
    """Simplified snapshot of fundamental metrics for a given stock."""

    ticker: str
    market_cap: Optional[float]
    revenue: Optional[float]
    free_cash_flow: Optional[float]
    net_income: Optional[float]
    equity: Optional[float]
    debt: Optional[float]
    pe_ratio: Optional[float]
    pfcf_ratio: Optional[float]
    fcf_yield: Optional[float]
    revenue_cagr: Optional[float]
    fcf_cagr: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    score_value: Optional[float]
    score_growth: Optional[float]
    score_quality: Optional[float]
    score_composite: Optional[float]
    as_of: Optional[date] = None


@dataclass
class DCFResult:
    """Results of a discounted cash flow calculation."""

    ticker: str
    intrinsic_value: Optional[float]
    implied_upside: Optional[float]
    discount_rate: float
    terminal_growth_rate: float
    as_of: Optional[date] = None


@dataclass
class PortfolioStats:
    """Aggregated portfolio-level statistics for simulations or backtests."""

    total_value: float
    annual_return: Optional[float]
    volatility: Optional[float]
    max_drawdown: Optional[float]
    sharpe_ratio: Optional[float]
    period_years: Optional[float] = None
