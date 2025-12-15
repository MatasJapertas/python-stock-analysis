# Python Stock Analysis

A lightweight toolkit for fetching market data, computing fundamental metrics, running simple screeners, and visualizing results. The package is organized into small, composable modules so you can mix and match data retrieval, analytics, simulation, and plotting utilities in your own scripts or notebooks.

## Installation

```bash
pip install -r requirements.txt
```

All examples assume you are working in a Python 3.11+ environment with the repository root on your `PYTHONPATH` (or installed as a package).

## Package layout

```
src/
  core/      # Data models and enums
  data/      # Price and fundamentals fetchers (yfinance-based)
  analysis/  # Fundamental metrics, valuations, screeners, simulations
  viz/       # Matplotlib-based chart helpers
  utils/     # Logging and configuration helpers
```

Import helpers are re-exported in the respective `__init__.py` files so you can do concise imports such as `from src.analysis import build_pe_series`.

---
## Core models and enums (`src/core`)

### Models
- **`Stock`** — basic metadata container (ticker, name, sector, industry, exchange, currency).
- **`FundamentalsSnapshot`** — simplified snapshot of fundamental metrics such as trailing EPS, market cap, revenue, cash flow, margins, and composite scores.
- **`DCFResult`** — holds DCF assumptions (discount and terminal growth rate) and the resulting intrinsic value/upside.
- **`PortfolioStats`** — aggregate portfolio statistics (total value, annual return, volatility, drawdown, Sharpe ratio).

### Enums
- **`RebalanceFrequency`** — `monthly`, `quarterly`, or `yearly` (for backtests/allocations).
- **`ScoreStyle`** — `value`, `quality`, `growth`, or `composite` scoring.
- **`ValuationMethod`** — `pe`, `pfcf`, or `dcf` identifiers.
- **`ReturnFrequency`** — `daily`, `weekly`, or `monthly` return cadence.

Example:
```python
from src.core import Stock, FundamentalsSnapshot
from src.core.enums import ScoreStyle

stock = Stock(ticker="AAPL", name="Apple Inc.", sector="Technology")
print(stock)
print(ScoreStyle.VALUE.value)
```

---
## Data access (`src/data`)

All data fetchers rely on [`yfinance`](https://pypi.org/project/yfinance/). Network/API failures are logged and functions return empty DataFrames or `None` so you can handle errors gracefully.

### Price helpers (`prices.py`)
- `get_price_history(ticker, period="5y", interval="1d")` — download historical OHLCV prices for a single ticker.
- `get_multiple_price_histories(tickers, period="5y", interval="1d")` — fetch a dict of ticker → history DataFrames.
- `get_current_price(ticker)` — read the most recent close/last trade if available.
- `get_benchmark_prices(benchmark_ticker="^GSPC", ...)` — convenience wrapper for index/benchmark series.

Example:
```python
from src.data import get_price_history, get_multiple_price_histories

aapl = get_price_history("AAPL", period="1y")
portfolio = get_multiple_price_histories(["AAPL", "MSFT", "GOOGL"], interval="1wk")
print(aapl.tail())
print(portfolio["MSFT"].head())
```

### Fundamentals helpers (`fundamentals.py`)
- `get_company_info(ticker)` — return the `Ticker.info` dictionary.
- `get_income_statement(ticker, annual=True)` — annual or quarterly income statement DataFrame.
- `get_cashflow_statement(ticker, annual=True)` — annual or quarterly cashflow statement DataFrame.
- `get_balance_sheet(ticker, annual=True)` — annual or quarterly balance sheet DataFrame.
- `get_market_cap_from_info(info)` — small helper to pull `marketCap` out of an info dict.

Example:
```python
from src.data import get_company_info, get_income_statement

info = get_company_info("MSFT")
income = get_income_statement("MSFT")
print(info.get("marketCap"))
print(income.loc["Total Revenue"].head())
```

---
## Fundamental analysis (`src/analysis/fundamentals.py`)

Utility math helpers:
- `safe_div(numerator, denominator)` — guard against zero/None division.
- `compute_pe(price, eps)` / `compute_pfcf(price, fcf_per_share)` — quick ratio helpers.
- `compute_fcf_yield(fcf, market_cap)` — returns percent FCF yield when possible.
- `cagr(start, end, years)` — compound annual growth rate (returns `None` for invalid inputs).

Derived metrics:
- `compute_revenue_cagr(income_stmt)` — CAGR of total revenue (uses available history).
- `compute_fcf_cagr(cashflow)` — CAGR of free cash flow.
- `compute_margins(income_stmt)` — tuple of (gross, operating, net) margins in percent.
- `compute_value_score(fcf_yield, pe_ratio)` — simple value proxy combining FCF yield and inverse P/E.
- `compute_growth_score(revenue_cagr, fcf_cagr)` — sum of growth CAGRs.
- `compute_quality_score(gross_margin, operating_margin, net_margin)` — average of available margins.
- `compute_composite_score(value_score, growth_score, quality_score)` — mean of provided sub-scores.

End-to-end summary:
- `summarize_fundamentals(ticker)` — pulls yfinance statements/info, computes the metrics above, and returns a `FundamentalsSnapshot` populated with margins, ratios, scores, and the `as_of` date.

Example:
```python
from src.analysis.fundamentals import summarize_fundamentals, compute_margins
from src.data import get_income_statement

snapshot = summarize_fundamentals("AAPL")
print(snapshot.pe_ratio, snapshot.score_composite)

aapl_income = get_income_statement("AAPL")
gross, op, net = compute_margins(aapl_income)
print(gross, op, net)
```

---
## Valuation analytics (`src/analysis/valuation.py`)

- `_get_eps_history(ticker_obj)` — internal helper that builds a time-aware EPS series using quarterly then annual statements, falling back to trailing EPS.
- `build_pe_series(ticker, period="5y")` — constructs a P/E ratio series by aligning historical prices with EPS history.
- `compute_rolling_pe(pe, window_days=30)` — rolling mean of a P/E series (uses calendar-day windows when indexed by dates).
- `compute_pe_stats(pe)` — dictionary with mean/median/min/max for a P/E series.

Example:
```python
from src.analysis.valuation import build_pe_series, compute_rolling_pe, compute_pe_stats

pe = build_pe_series("MSFT", period="3y")
rolling = compute_rolling_pe(pe, window_days=60)
stats = compute_pe_stats(pe)
print(stats)
```

---
## Screener (`src/analysis/screener.py`)

- `screen_tickers(tickers, min_fcf_yield=None, max_pe=None, max_debt_to_equity=None)` — fetches `FundamentalsSnapshot` objects for each ticker, computes debt/equity, and filters by the provided thresholds. Returns a tidy DataFrame.
- `run_simple_screener(tickers)` — convenience wrapper that applies `min_fcf_yield=2.0` and `max_pe=25.0`.

Example:
```python
from src.analysis.screener import run_simple_screener

candidates = run_simple_screener(["AAPL", "MSFT", "GOOGL", "TSLA"])
print(candidates.sort_values("score_composite", ascending=False))
```

---
## Investment simulations (`src/analysis/investment.py`)

- `future_value_monthly(monthly_contribution, annual_rate, years)` — closed-form future value with monthly contributions/compounding.
- `build_dca_balance_series(monthly_contribution, annual_rate, years)` — deterministic month-by-month balance growth list for plotting.
- `simulate_dca_monte_carlo(monthly_contribution, years, annual_return_mean, annual_return_std, n_sims=1000)` — Monte Carlo simulation of monthly contributions with normally distributed returns (log-normal approximation).
- `summarize_monte_carlo_results(final_values, target=None)` — stats (mean, median, p10, p90, success probability vs. target) for simulation results.

Example:
```python
from src.analysis.investment import (
    build_dca_balance_series,
    simulate_dca_monte_carlo,
    summarize_monte_carlo_results,
)

balances = build_dca_balance_series(500, annual_rate=0.07, years=5)
results = simulate_dca_monte_carlo(500, years=5, annual_return_mean=0.07, annual_return_std=0.15)
stats = summarize_monte_carlo_results(results, target=50000)
print(stats)
```

---
## Visualization helpers (`src/viz/plots.py`)

All plotters return a Matplotlib `Figure` for further customization or saving.

- `plot_pe_with_rolling(pe, rolling_pe=None, title=None)` — overlay raw and rolling P/E series.
- `plot_dca_balance(balances, years, title=None)` — line chart of DCA balance growth (x-axis in months).
- `plot_monte_carlo_histogram(final_values, bins=30, title=None)` — histogram of Monte Carlo ending balances.
- `plot_screener_bar(df, column, top_n=10, title=None)` — bar chart of the top-N tickers by a chosen metric.

Example:
```python
import matplotlib.pyplot as plt
from src.analysis.valuation import build_pe_series, compute_rolling_pe
from src.viz import plot_pe_with_rolling

pe = build_pe_series("AAPL", period="2y")
rolling = compute_rolling_pe(pe, window_days=45)
fig = plot_pe_with_rolling(pe, rolling)
fig.savefig("aapl_pe.png", dpi=150)
plt.close(fig)
```

---
## Utilities (`src/utils`)

- `get_logger(name)` — returns a cached logger configured with console and `logs/app.log` file handlers. Handlers are attached only once per name.
- `load_config(path=None)` — load JSON config (`config.json` by default) or fall back to `DEFAULT_CONFIG`. The result is cached.
- `get_config_value(path, default=None)` — dot-path accessor into the loaded config (e.g., `analysis.discount_rate`).

Example:
```python
from src.utils import get_logger, get_config_value

logger = get_logger(__name__)
logger.info("Starting analysis")
discount_rate = get_config_value("analysis.discount_rate", default=0.1)
print(discount_rate)
```

---
## Visualization-ready workflows

Putting it together:
```python
from src.analysis import build_pe_series, compute_rolling_pe, run_simple_screener
from src.viz import plot_pe_with_rolling, plot_screener_bar
import matplotlib.pyplot as plt

# P/E history with smoothing
pe = build_pe_series("MSFT", period="3y")
rolling_pe = compute_rolling_pe(pe, window_days=30)
pe_fig = plot_pe_with_rolling(pe, rolling_pe)
pe_fig.savefig("msft_pe.png", dpi=150)
plt.close(pe_fig)

# Quick screener overview
results = run_simple_screener(["AAPL", "MSFT", "GOOGL", "AMZN", "META"])
bar_fig = plot_screener_bar(results, column="score_composite", top_n=5)
bar_fig.savefig("screener.png", dpi=150)
plt.close(bar_fig)
```

## Notes
- The library favors simplicity and transparency; many calculations are intentionally light-weight placeholders meant to be refined.
- Network access is required for `yfinance` calls. Handle empty DataFrames/`None` responses when data is unavailable.
- Logging output is written to `logs/app.log` in the current working directory by default.