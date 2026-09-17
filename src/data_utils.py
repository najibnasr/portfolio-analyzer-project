"""Data import, filtering and analytics functions for the portfolio analyzer."""

import pandas as pd
import yfinance as yf


def download_prices(tickers, start, end):
    """Download adjusted close prices from Yahoo Finance.

    Returns a DataFrame with one column per ticker, indexed by date.
    """
    if not tickers:
        raise ValueError("tickers list cannot be empty")
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = data["Close"]
    if isinstance(prices, pd.Series):  # single ticker -> Series
        prices = prices.to_frame(name=tickers[0])
    prices = prices.dropna(how="all")
    if prices.empty:
        raise ValueError(f"No data returned for tickers {tickers}")
    return prices


def filter_by_date(prices, start, end):
    """Keep only rows between start and end (inclusive)."""
    if prices.empty:
        raise ValueError("prices DataFrame is empty")
    start, end = pd.to_datetime(start), pd.to_datetime(end)
    if start > end:
        raise ValueError("start date must be before end date")
    return prices.loc[(prices.index >= start) & (prices.index <= end)]


def compute_returns(prices):
    """Daily simple returns from a price DataFrame."""
    if prices.empty:
        raise ValueError("prices DataFrame is empty")
    return prices.pct_change().dropna(how="all")


def compute_cumulative_returns(returns):
    """Cumulative growth of 1 unit invested at the start."""
    if returns.empty:
        raise ValueError("returns DataFrame is empty")
    return (1 + returns).cumprod()


def compute_rolling_volatility(returns, window=21):
    """Annualized rolling volatility (default window: 21 trading days)."""
    if window <= 1:
        raise ValueError("window must be greater than 1")
    if len(returns) < window:
        raise ValueError(f"need at least {window} rows, got {len(returns)}")
    return returns.rolling(window).std().dropna(how="all") * (252 ** 0.5)


def compute_drawdown(prices):
    """Drawdown series: percentage drop from the running maximum."""
    if prices.empty:
        raise ValueError("prices DataFrame is empty")
    running_max = prices.cummax()
    return prices / running_max - 1


def compute_correlation(returns):
    """Correlation matrix of asset returns."""
    if returns.shape[1] < 2:
        raise ValueError("need at least 2 assets to compute correlations")
    return returns.corr()
