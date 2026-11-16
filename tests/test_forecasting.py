"""Unit tests for ML forecasting, out-of-sample evaluation, and metrics."""

import numpy as np
import pandas as pd
import pytest
from src.services.forecasting import evaluate_forecast_model, predict_stock_prices


@pytest.fixture
def synthetic_stock_df():
    """Generate 100 days of deterministic synthetic stock prices for testing."""
    dates = pd.bdate_range("2025-01-01", periods=100)
    # Upward trending series with minor oscillation
    prices = 1000.0 + np.arange(100) * 5.0 + np.sin(np.linspace(0, 10, 100)) * 10.0
    return pd.DataFrame({"Close": prices}, index=dates)


class TestForecastingModel:
    def test_insufficient_data_returns_empty(self):
        short_df = pd.DataFrame({"Close": [100.0, 105.0, 102.0]})
        pred_df, score = predict_stock_prices(short_df, days=15)
        assert pred_df.empty
        assert float(score) == 0.0

        eval_res = evaluate_forecast_model(short_df)
        assert eval_res.get("status") == "insufficient_data"
        assert "limitations" in eval_res

    def test_chronological_evaluation_metrics_populated(self, synthetic_stock_df):
        metrics = evaluate_forecast_model(synthetic_stock_df, test_ratio=0.20)
        assert metrics["model_name"] == "Linear Trend Regression"
        assert metrics["train_samples"] == 80
        assert metrics["test_samples"] == 20
        assert "train_r2" in metrics
        assert "test_r2" in metrics
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics
        assert "directional_accuracy" in metrics
        assert "baseline_mae" in metrics
        assert metrics["mae"] >= 0.0
        assert metrics["rmse"] >= 0.0
        assert 0.0 <= metrics["directional_accuracy"] <= 100.0

    def test_predict_stock_prices_returns_forecast_score(self, synthetic_stock_df):
        pred_df, score = predict_stock_prices(synthetic_stock_df, days=30)
        assert not pred_df.empty
        assert len(pred_df) == 30
        assert "Predicted_Close" in pred_df.columns
        assert (pred_df["Predicted_Close"] > 0).all()

        # Score behaves as float
        assert isinstance(score, float)
        assert score > 0.0

        # Score contains evaluation metrics dictionary
        assert hasattr(score, "metrics")
        assert score.metrics["train_samples"] == 80
        assert "limitations" in score.metrics

    def test_non_negative_predictions_guaranteed(self):
        # Sharp downtrend that would extrapolate negative if unconstrained
        dates = pd.bdate_range("2025-01-01", periods=30)
        prices = 100.0 - np.arange(30) * 3.5
        df = pd.DataFrame({"Close": prices}, index=dates)
        pred_df, _ = predict_stock_prices(df, days=60)
        assert not pred_df.empty
        assert (pred_df["Predicted_Close"] >= 0.01).all()
