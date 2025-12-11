"""Core analysis modules for fundamentals, valuation, investment, and screening."""

from .fundamentals import summarize_fundamentals
from .investment import build_dca_balance_series, future_value_monthly, simulate_dca_monte_carlo
from .screener import run_simple_screener
from .valuation import build_pe_series, compute_rolling_pe

__all__ = [
    "summarize_fundamentals",
    "build_pe_series",
    "compute_rolling_pe",
    "future_value_monthly",
    "build_dca_balance_series",
    "simulate_dca_monte_carlo",
    "run_simple_screener",
]
