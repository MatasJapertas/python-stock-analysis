"""Quick script to exercise repository features with the NVO ticker.

The script pulls live data via yfinance, computes fundamentals and valuation
series, runs DCA/Monte Carlo simulations, and saves example plots. It is meant
as a temporary all-in-one sanity check for visual outputs and calculations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

# Allow running the script without installing the package
import sys

to_src = Path(__file__).resolve().parents[1] / "src"
if str(to_src) not in sys.path:
    sys.path.append(str(to_src))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.fundamentals import summarize_fundamentals
from analysis.investment import (
    build_dca_balance_series,
    simulate_dca_monte_carlo,
    summarize_monte_carlo_results,
)
from analysis.screener import run_simple_screener
from analysis.valuation import build_pe_series, compute_pe_stats, compute_rolling_pe
from data.prices import get_benchmark_prices, get_current_price, get_price_history
from viz.plots import (
    plot_dca_balance,
    plot_monte_carlo_histogram,
    plot_pe_with_rolling,
    plot_screener_bar,
)


OUTPUT_DIR = Path("tmp/nvo_demo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_fig(fig: plt.Figure, name: str) -> Path:
    path = OUTPUT_DIR / name
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def _describe_df(df: pd.DataFrame, name: str) -> None:
    if df.empty:
        print(f"[WARN] {name} dataframe is empty")
        return
    print(f"\n{name} head:\n", df.head())
    print(f"\n{name} summary:\n", df.describe(include="all"))


def _display_dict(title: str, values: dict | None) -> None:
    print(f"\n{title}:")
    if not values:
        print("  (no data)")
        return
    for key, value in values.items():
        print(f"  {key}: {value}")


def _run_price_checks(ticker: str) -> None:
    print("Fetching price history and current price...")
    history = get_price_history(ticker, period="1y", interval="1d")
    _describe_df(history, f"{ticker} price history")

    current_price = get_current_price(ticker)
    print(f"Current price for {ticker}: {current_price}")

    benchmark = get_benchmark_prices(period="1y", interval="1d")
    _describe_df(benchmark, "S&P 500 benchmark")


def _run_fundamentals(ticker: str) -> None:
    print("\nComputing fundamentals snapshot...")
    snapshot = summarize_fundamentals(ticker)
    print(snapshot)


def _run_valuation(ticker: str) -> None:
    print("\nBuilding P/E series and rolling average...")
    pe_series = build_pe_series(ticker, period="2y")
    if pe_series.empty:
        print("[WARN] Unable to build P/E series")
        return

    rolling = compute_rolling_pe(pe_series, window_days=30)
    stats = compute_pe_stats(pe_series)
    _display_dict("P/E stats", stats)

    fig = plot_pe_with_rolling(pe_series, rolling, title=f"{ticker} P/E with 30-day Rolling")
    path = _save_fig(fig, "pe_with_rolling.png")
    print(f"Saved P/E plot to {path}")


def _run_investment_scenarios(ticker: str) -> None:
    print("\nRunning DCA and Monte Carlo simulations...")
    monthly_contribution = 500
    expected_return = 0.08
    return_volatility = 0.15
    years = 10

    balances = build_dca_balance_series(monthly_contribution, expected_return, years)
    fig = plot_dca_balance(balances, years, title=f"{ticker} DCA Projection ({years}y)")
    path = _save_fig(fig, "dca_balance.png")
    print(f"Saved DCA balance plot to {path}")

    final_values = simulate_dca_monte_carlo(
        monthly_contribution=monthly_contribution,
        years=years,
        annual_return_mean=expected_return,
        annual_return_std=return_volatility,
        n_sims=500,
    )
    fig = plot_monte_carlo_histogram(final_values, bins=40, title=f"{ticker} DCA Monte Carlo Outcomes")
    mc_path = _save_fig(fig, "monte_carlo_histogram.png")
    print(f"Saved Monte Carlo histogram to {mc_path}")

    summary = summarize_monte_carlo_results(final_values, target=monthly_contribution * years * 12)
    _display_dict("Monte Carlo summary", summary)


def _run_screener(tickers: Iterable[str]) -> None:
    print("\nRunning simple screener...")
    results = run_simple_screener(list(tickers))
    _describe_df(results, "Screener results")

    if not results.empty:
        fig = plot_screener_bar(results, column="score_composite", top_n=len(results), title="Composite Score")
        path = _save_fig(fig, "screener_scores.png")
        print(f"Saved screener bar chart to {path}")


def main() -> None:
    ticker = "NVO"
    print(f"\n=== Running full functionality demo for {ticker} ===\n")

    _run_price_checks(ticker)
    _run_fundamentals(ticker)
    _run_valuation(ticker)
    _run_investment_scenarios(ticker)
    _run_screener([ticker, "AAPL", "MSFT", "NVDA"])

    print(f"\nAll artifacts saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
