"""Portfolio Analyzer - Streamlit app."""

import datetime as dt

import streamlit as st

from src.data_utils import (
    download_prices,
    filter_by_date,
    compute_returns,
    compute_cumulative_returns,
    compute_rolling_volatility,
    compute_drawdown,
    compute_correlation,
)

st.set_page_config(page_title="Portfolio Analyzer", layout="wide")
st.title("Portfolio Analyzer")
st.write("Compare stocks: cumulative returns, volatility, drawdown and correlations.")

# --- Sidebar: user inputs ---
st.sidebar.header("Settings")

TICKER_CHOICES = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
    "JPM", "GS", "V", "KO", "MCD", "DIS",
    "MC.PA", "AIR.PA", "OR.PA", "TTE.PA", "BNP.PA", "SAN.PA",
]

tickers = st.sidebar.multiselect(
    "Tickers (pick from the list or type your own)",
    options=TICKER_CHOICES,
    default=["AAPL", "MSFT", "GOOGL"],
    accept_new_options=True,
)
tickers = [t.strip().upper() for t in tickers if t.strip()]

today = dt.date.today()
start_date, end_date = st.sidebar.slider(
    "Date range",
    min_value=today - dt.timedelta(days=5 * 365),
    max_value=today,
    value=(today - dt.timedelta(days=365), today),
    format="YYYY-MM-DD",
)

show_cumulative = st.sidebar.checkbox("Cumulative returns", value=True)
show_volatility = st.sidebar.checkbox("Rolling volatility")
vol_window = st.sidebar.slider("Volatility window (days)", 5, 63, 21)
show_drawdown = st.sidebar.checkbox("Drawdown")
show_correlation = st.sidebar.checkbox("Correlation matrix")


@st.cache_data
def load_prices(tickers, start, end):
    """Cached wrapper around download_prices."""
    return download_prices(list(tickers), start, end)


if not tickers:
    st.warning("Select at least one ticker in the sidebar.")
    st.stop()

try:
    prices = load_prices(tuple(tickers), start_date, end_date)
except ValueError as e:
    st.error(f"Data error: {e}")
    st.stop()

prices = filter_by_date(prices, start_date, end_date)
returns = compute_returns(prices)

st.subheader("Prices")
st.line_chart(prices)

if show_cumulative:
    st.subheader("Cumulative returns (growth of 1 invested)")
    st.line_chart(compute_cumulative_returns(returns))

if show_volatility:
    st.subheader(f"Rolling volatility ({vol_window}-day, annualized)")
    try:
        st.line_chart(compute_rolling_volatility(returns, window=vol_window))
    except ValueError as e:
        st.info(f"Not enough data: {e}")

if show_drawdown:
    st.subheader("Drawdown")
    st.line_chart(compute_drawdown(prices))

if show_correlation:
    st.subheader("Correlation matrix of daily returns")
    try:
        st.dataframe(compute_correlation(returns).round(2))
    except ValueError as e:
        st.info(str(e))

with st.expander("Raw data"):
    st.dataframe(prices)
