"""
Created on 2025.12.11

@author: Matas Japertas
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def plot_pe_with_rolling(pe: pd.Series, rolling_pe: pd.Series | None = None, title: str | None = None) -> Figure:
    """Plot P/E series with optional rolling average."""

    fig, ax = plt.subplots()
    pe.plot(ax=ax, label="P/E")
    if rolling_pe is not None and not rolling_pe.empty:
        rolling_pe.plot(ax=ax, label="Rolling P/E", linestyle="--")
    ax.set_title(title or "Price-to-Earnings")
    ax.set_xlabel("Date")
    ax.set_ylabel("P/E")
    ax.legend()
    ax.grid(True)
    return fig


def plot_multiple_pe(pe_map: dict[str, pd.Series], title: str | None = None) -> Figure:
    """Overlay multiple P/E ratio series on the same axis."""

    fig, ax = plt.subplots()
    for label, series in pe_map.items():
        if series is None or series.empty:
            continue
        series.plot(ax=ax, label=label)

    ax.set_title(title or "P/E Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("P/E")
    ax.legend()
    ax.grid(True)
    return fig


def plot_price_history(prices: pd.DataFrame | pd.Series, value_column: str = "Close", title: str | None = None) -> Figure:
    """Plot a share's value over time."""

    fig, ax = plt.subplots()
    if isinstance(prices, pd.Series):
        prices.plot(ax=ax, label=value_column)
    else:
        if value_column not in prices.columns:
            available = ", ".join(prices.columns)
            raise ValueError(
                f"Column '{value_column}' not found in prices DataFrame. Available columns: {available}"
            )
        prices[value_column].plot(ax=ax, label=value_column)

    ax.set_title(title or "Share Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
    return fig


def plot_dca_balance(balances: list[float], years: int, title: str | None = None) -> Figure:
    """Plot DCA balance growth over time."""

    fig, ax = plt.subplots()
    months = list(range(1, len(balances) + 1))
    ax.plot(months, balances, label="Balance")
    ax.set_title(title or "DCA Balance Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance")
    ax.grid(True)
    return fig


def plot_monte_carlo_histogram(final_values: np.ndarray, bins: int = 30, title: str | None = None) -> Figure:
    """Plot histogram of final values from Monte Carlo simulations."""

    fig, ax = plt.subplots()
    ax.hist(final_values, bins=bins, alpha=0.7, color="steelblue")
    ax.set_title(title or "Monte Carlo Outcomes")
    ax.set_xlabel("Final Value")
    ax.set_ylabel("Frequency")
    ax.grid(True)
    return fig


def plot_screener_bar(df: pd.DataFrame, column: str, top_n: int = 10, title: str | None = None) -> Figure:
    """Plot a bar chart for screener scores."""
    if column not in df.columns:
        available = ", ".join(df.columns)
        raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {available}")

    fig, ax = plt.subplots()
    subset = df.nlargest(top_n, column)
    positions = np.arange(len(subset))
    ax.bar(positions, subset[column])
    ax.set_title(title or f"Top {top_n} by {column}")
    ax.set_xlabel("Ticker")
    ax.set_ylabel(column)
    ax.set_xticks(positions)
    ax.set_xticklabels(subset["ticker"], rotation=45, ha="right")
    ax.grid(True, axis="y")
    return fig

def plot_fcf_growth_histogram(fcf_series: pd.Series, title: str | None = None) -> Figure:
    """Plot histogram of year-over-year free cash flow growth rates (percent)."""

    sorted_series = fcf_series.sort_index()
    growth_rates = sorted_series.pct_change().dropna() * 100

    fig, ax = plt.subplots()
    ax.hist(growth_rates, bins=min(30, max(len(growth_rates), 1)), color="seagreen", alpha=0.75)
    ax.set_title(title or "Free Cash Flow Growth Distribution")
    ax.set_xlabel("YoY Growth (%)")
    ax.set_ylabel("Frequency")
    ax.grid(True)
    return fig
