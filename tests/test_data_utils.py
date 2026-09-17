"""Unit tests for src.data_utils (no network access needed)."""

import pandas as pd
import pytest

from src.data_utils import (
    download_prices,
    filter_by_date,
    compute_returns,
    compute_cumulative_returns,
    compute_rolling_volatility,
    compute_drawdown,
    compute_correlation,
)


@pytest.fixture
def prices():
    """Small price DataFrame with known values."""
    return pd.DataFrame(
        {"AAA": [100.0, 110.0, 105.0, 120.0], "BBB": [50.0, 52.0, 51.0, 55.0]},
        index=pd.date_range("2026-01-01", periods=4),
    )


# --- download_prices (input validation only, no network) ---

def test_download_prices_empty_tickers():
    with pytest.raises(ValueError):
        download_prices([], "2026-01-01", "2026-02-01")


# --- filter_by_date ---

def test_filter_by_date_keeps_range(prices):
    out = filter_by_date(prices, "2026-01-02", "2026-01-03")
    assert len(out) == 2
    assert out.index.min() == pd.Timestamp("2026-01-02")
    assert out.index.max() == pd.Timestamp("2026-01-03")

def test_filter_by_date_inverted_dates(prices):
    with pytest.raises(ValueError):
        filter_by_date(prices, "2026-02-01", "2026-01-01")

def test_filter_by_date_empty_input():
    with pytest.raises(ValueError):
        filter_by_date(pd.DataFrame(), "2026-01-01", "2026-02-01")


# --- compute_returns ---

def test_compute_returns_values(prices):
    r = compute_returns(prices)
    assert r.loc["2026-01-02", "AAA"] == pytest.approx(0.10)
    assert r.loc["2026-01-03", "AAA"] == pytest.approx(-5 / 110)
    assert len(r) == 3  # first row dropped

def test_compute_returns_empty():
    with pytest.raises(ValueError):
        compute_returns(pd.DataFrame())


# --- compute_cumulative_returns ---

def test_cumulative_returns_final_value(prices):
    cum = compute_cumulative_returns(compute_returns(prices))
    # total growth = last price / first price
    assert cum.iloc[-1]["AAA"] == pytest.approx(120 / 100)
    assert cum.iloc[-1]["BBB"] == pytest.approx(55 / 50)


# --- compute_rolling_volatility ---

def test_rolling_volatility_shape(prices):
    r = compute_returns(prices)
    vol = compute_rolling_volatility(r, window=2)
    assert not vol.empty
    assert (vol.dropna() >= 0).all().all()

def test_rolling_volatility_bad_window(prices):
    r = compute_returns(prices)
    with pytest.raises(ValueError):
        compute_rolling_volatility(r, window=1)

def test_rolling_volatility_not_enough_rows(prices):
    r = compute_returns(prices)  # 3 rows
    with pytest.raises(ValueError):
        compute_rolling_volatility(r, window=10)


# --- compute_drawdown ---

def test_drawdown_values(prices):
    dd = compute_drawdown(prices)
    assert dd.loc["2026-01-03", "AAA"] == pytest.approx(105 / 110 - 1)
    assert (dd <= 0).all().all()  # drawdown is never positive
    assert dd.iloc[0]["AAA"] == 0  # first day is the running max


# --- compute_correlation ---

def test_correlation_matrix(prices):
    corr = compute_correlation(compute_returns(prices))
    assert corr.shape == (2, 2)
    assert corr.loc["AAA", "AAA"] == pytest.approx(1.0)
    assert corr.loc["AAA", "BBB"] == pytest.approx(corr.loc["BBB", "AAA"])

def test_correlation_single_asset(prices):
    r = compute_returns(prices[["AAA"]])
    with pytest.raises(ValueError):
        compute_correlation(r)
