# Portfolio Analyzer

[![CI](https://github.com/najibnasr/portfolio-analyzer-project/actions/workflows/ci.yml/badge.svg)](https://github.com/najibnasr/portfolio-analyzer-project/actions/workflows/ci.yml)

A Streamlit web app to compare stock performance: cumulative returns, rolling
volatility, drawdown and correlation matrix. Market data is fetched from
Yahoo Finance via `yfinance`.

Final project for the *Tooling for the Data Scientist* course
(X-HEC / École Polytechnique, MScT Data Science for Business).

## Features

- Pick tickers from a dropdown (or type any Yahoo Finance ticker) and a date range
- Cumulative returns (growth of 1 invested)
- Rolling volatility (annualized, adjustable window)
- Drawdown from running maximum
- Correlation matrix of daily returns

## Project structure

- `app.py` - Streamlit UI layer
- `src/data_utils.py` - pure data functions (import, filtering, analytics)
- `tests/test_data_utils.py` - pytest unit tests (16 tests, ~95% coverage,
  network calls mocked with `monkeypatch`)
- `.github/workflows/ci.yml` - CI running the test suite on every push
- `Dockerfile` - containerized deployment

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```bash
pip install pytest pytest-cov
python -m pytest tests/ -v --cov=src
```

Tests run without network access: the `yfinance` download is mocked, and all
analytics are tested on small hand-built DataFrames with known expected values.

## Run with Docker

From Docker Hub (no build needed):

```bash
docker run -p 8501:8501 najibnasr/portfolio-analyzer
```

Or build locally:

```bash
docker build -t portfolio-analyzer .
docker run -p 8501:8501 portfolio-analyzer
```

Then open http://localhost:8501

## Continuous Integration

Every push to `main` triggers GitHub Actions: dependencies are installed from
scratch on a clean Ubuntu runner and the full test suite is executed. The badge
above shows the current status.
