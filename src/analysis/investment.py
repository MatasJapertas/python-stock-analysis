"""Investment math for DCA and Monte Carlo simulations."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def future_value_monthly(monthly_contribution: float, annual_rate: float, years: float) -> float:
    """Calculate future value with monthly contributions and compounding."""

    monthly_rate = annual_rate / 12
    periods = int(years * 12)
    if monthly_rate == 0:
        return monthly_contribution * periods
    return monthly_contribution * ((1 + monthly_rate) ** periods - 1) / monthly_rate


def build_dca_balance_series(monthly_contribution: float, annual_rate: float, years: float) -> list[float]:
    """Generate the balance series for a DCA plan."""

    balances = []
    balance = 0.0
    monthly_rate = annual_rate / 12
    periods = int(years * 12)
    for _ in range(periods):
        balance = balance * (1 + monthly_rate) + monthly_contribution
        balances.append(balance)
    return balances


def simulate_dca_monte_carlo(
    monthly_contribution: float,
    years: float,
    annual_return_mean: float,
    annual_return_std: float,
    n_sims: int = 1000,
) -> np.ndarray:
    """Simulate DCA outcomes using log-normal return paths."""

    periods = int(years * 12)
    monthly_mean = annual_return_mean / 12
    monthly_std = annual_return_std / math.sqrt(12)

    final_values = np.zeros(n_sims)
    for i in range(n_sims):
        balance = 0.0
        for _ in range(periods):
            monthly_return = np.random.normal(monthly_mean, monthly_std)
            balance = balance * (1 + monthly_return) + monthly_contribution
        final_values[i] = balance
    return final_values


def summarize_monte_carlo_results(final_values: np.ndarray, target: float | None = None) -> dict[str, float]:
    """Summarize simulation results with key statistics."""

    if final_values.size == 0:
        return {"mean": float("nan"), "median": float("nan"), "p10": float("nan"), "p90": float("nan"), "success_prob": float("nan")}

    mean = float(np.mean(final_values))
    median = float(np.median(final_values))
    p10 = float(np.percentile(final_values, 10))
    p90 = float(np.percentile(final_values, 90))
    success_prob = float(np.mean(final_values >= target)) if target is not None else float("nan")

    return {
        "mean": mean,
        "median": median,
        "p10": p10,
        "p90": p90,
        "success_prob": success_prob,
    }
