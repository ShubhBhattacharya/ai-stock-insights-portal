"""Unit tests for stock market data cleaning, indicator math, and confluence signals."""

import numpy as np
import pandas as pd
import pytest
from src.services.market_data import (
    _analyze_dataframe,
    _normalize_ohlcv_df,
    _safe_bbands,
    _safe_rsi,
    _safe_sma,
    validate_ticker_symbol,
)


class TestTickerValidation:
    def test_valid_tickers(self):
        valid = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "SBIN.BO", "TATAMOTORS", "BAJAJ-AUTO.NS"]
        for t in valid:
            assert validate_ticker_symbol(t) is True, f"Failed for {t}"

    def test_invalid_tickers(self):
        invalid = ["", "   ", "SELECT *", "RELIANCE;DROP", "A" * 30]
        for t in invalid:
            assert validate_ticker_symbol(t) is False, f"Expected invalid for {t}"


class TestOHLCVNormalization:
    def test_multiindex_and_nan_cleaning(self):
        dates = pd.date_range("2025-01-01", periods=10)
        raw_df = pd.DataFrame(
            {
                "Open": [100.0, np.nan, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
                "High": [105.0, 102.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0],
                "Low": [95.0, 98.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0],
                "Close": [102.0, 101.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0],
                "Volume": [1000, 2000, np.nan, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
            },
            index=dates,
        )
        cleaned = _normalize_ohlcv_df(raw_df)
        assert not cleaned.empty
        assert len(cleaned) == 10
        assert cleaned["Volume"].isna().sum() == 0
        assert (cleaned["High"] >= cleaned["Low"]).all()
        assert (cleaned["Close"] > 0).all()


class TestTechnicalIndicatorMath:
    def test_rsi_bounds(self):
        series = pd.Series([100.0 + i * 2.0 for i in range(50)])
        rsi = _safe_rsi(series, length=14)
        valid = rsi.dropna()
        assert (valid >= 0.0).all()
        assert (valid <= 100.0).all()
        # Consistently rising series should have high RSI (> 70)
        assert valid.iloc[-1] > 70.0

    def test_sma_calculation(self):
        series = pd.Series([10.0] * 30 + [20.0] * 30)
        sma = _safe_sma(series, length=10)
        assert sma.iloc[-1] == 20.0
        assert sma.iloc[20] == 10.0

    def test_bbands_order(self):
        series = pd.Series(np.random.normal(100.0, 5.0, 60))
        bbl, bbm, bbu = _safe_bbands(series, length=20, std=2.0)
        valid = pd.DataFrame({"bbl": bbl, "bbm": bbm, "bbu": bbu}).dropna()
        assert not valid.empty
        assert (valid["bbl"] <= valid["bbm"]).all()
        assert (valid["bbm"] <= valid["bbu"]).all()


class TestSignalConfluence:
    def test_dynamic_confluence_scoring(self):
        dates = pd.date_range("2024-01-01", periods=60)
        prices = 100.0 + np.arange(60) * 1.5
        df = pd.DataFrame(
            {
                "Open": prices - 1.0,
                "High": prices + 2.0,
                "Low": prices - 2.0,
                "Close": prices,
                "Volume": [10000] * 60,
            },
            index=dates,
        )
        res, err = _analyze_dataframe(df, "TEST.NS")
        assert err is None
        assert res is not None
        assert res["signal"] in ["BUY", "SELL", "HOLD"]
        assert 0 <= res["confidence"] <= 100
        assert res["signal_type"] == "Rule-Based Confluence"
        assert "last_updated" in res
        assert "educational_disclaimer" in res
        assert len(res["reasons"]) > 0
