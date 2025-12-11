"""Convenience script to exercise package functionality for Novo Nordisk (NVO).

Run this module to fetch fundamentals, compute valuation metrics, and plot
several visualizations. The script is intended for manual testing while
experimenting locally; it relies on live data from Yahoo Finance.
"""

from __future__ import annotations

from dataclasses import asdict
import pathlib
import sys

import matplotlib.pyplot as plt

# Ensure the repository root (containing the ``src`` package) is on ``sys.path``
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.analysis import fundamentals, investment, valuation
from src.viz.plots import plot_dca_balance, plot_monte_carlo_histogram, plot_pe_with_rolling



def show_fundamentals(ticker: str) -> None:
    """Fetch and print a fundamentals snapshot for the ticker."""

    snapshot = fundamentals.summarize_fundamentals(ticker)
    print("\nFundamentals snapshot:")
    for key, value in asdict(snapshot).items():
        print(f"  {key}: {value}")


def show_pe_plots(ticker: str, period: str = "5y") -> None:
    """Plot historical P/E and a rolling average."""

    pe_series = valuation.build_pe_series(ticker, period=period)
    rolling_pe = valuation.compute_rolling_pe(pe_series)
    stats = valuation.compute_pe_stats(pe_series)

    print("\nP/E stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    if pe_series.empty:
        print("No P/E data available to plot.")
        return

    fig = plot_pe_with_rolling(pe_series, rolling_pe, title=f"{ticker} P/E")
    fig.tight_layout()


def show_investment_simulations(monthly_contribution: float, years: float) -> None:
    """Run DCA and Monte Carlo simulations and plot the results."""

    annual_return_mean = 0.08
    annual_return_std = 0.15

    balances = investment.build_dca_balance_series(monthly_contribution, annual_return_mean, years)
    fig_balance = plot_dca_balance(balances, years, title="DCA balance projection")
    fig_balance.tight_layout()

    final_values = investment.simulate_dca_monte_carlo(
        monthly_contribution=monthly_contribution,
        years=years,
        annual_return_mean=annual_return_mean,
        annual_return_std=annual_return_std,
        n_sims=2000,
    )
    stats = investment.summarize_monte_carlo_results(final_values, target=monthly_contribution * 12 * years)

    print("\nMonte Carlo summary:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    fig_mc = plot_monte_carlo_histogram(final_values, title="Monte Carlo outcomes")
    fig_mc.tight_layout()


def main() -> None:
    ticker = "NVO"
    show_fundamentals(ticker)
    show_pe_plots(ticker)
    show_investment_simulations(monthly_contribution=500, years=10)

    # Display all open figures at once for interactive review.
    plt.show()


if __name__ == "__main__":
    main()
