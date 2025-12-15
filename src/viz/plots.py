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
