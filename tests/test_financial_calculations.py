"""Unit tests for financial calculations: volatility, Sharpe ratio, and correlations."""

import numpy as np
import pandas as pd
import pytest
from src.constants import RISK_FREE_RATE_PCT


class TestPortfolioCalculations:
    def test_annualized_volatility_and_sharpe_ratio(self):
        # 100 days of returns for 3 assets
        np.random.seed(42)
        ret1 = np.random.normal(0.001, 0.015, 100)
        ret2 = np.random.normal(0.0008, 0.012, 100)
        ret3 = np.random.normal(0.0012, 0.018, 100)

        returns_df = pd.DataFrame({"AssetA": ret1, "AssetB": ret2, "AssetC": ret3})

        num_assets = len(returns_df.columns)
        weights = np.ones(num_assets) / num_assets
        cov_matrix = returns_df.cov() * 252
        port_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
        port_volatility = float(np.sqrt(max(port_variance, 0.0)) * 100)

        annual_returns = (returns_df.mean() * 252) * 100
        port_return = float(np.dot(weights, annual_returns))
        sharpe_ratio = (
            (port_return - RISK_FREE_RATE_PCT) / port_volatility if port_volatility > 0 else 0.0
        )

        assert port_volatility > 0.0
        assert isinstance(sharpe_ratio, float)
        assert not np.isnan(sharpe_ratio)
        assert not np.isinf(sharpe_ratio)

    def test_zero_volatility_asset_handled_safely(self):
        # Asset with flat 0 returns
        returns_df = pd.DataFrame({"AssetA": [0.0] * 50, "AssetB": [0.0] * 50})
        num_assets = 2
        weights = np.ones(num_assets) / num_assets
        cov_matrix = returns_df.cov() * 252
        port_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
        port_volatility = float(np.sqrt(max(port_variance, 0.0)) * 100)
        sharpe = (0.0 - RISK_FREE_RATE_PCT) / port_volatility if port_volatility > 0 else 0.0

        assert port_volatility == 0.0
        assert sharpe == 0.0

    def test_correlation_matrix_properties(self):
        df = pd.DataFrame(
            {
                "A": [1.0, 2.0, 3.0, 4.0, 5.0],
                "B": [5.0, 4.0, 3.0, 2.0, 1.0],
                "C": [1.0, 1.0, 2.0, 2.0, 3.0],
            }
        )
        corr = df.corr()
        # Diagonal elements must be 1.0
        for col in df.columns:
            assert np.isclose(corr.loc[col, col], 1.0)
        # Perfectly inverse series must have correlation -1.0
        assert np.isclose(corr.loc["A", "B"], -1.0)
        # All correlation values bounded between -1 and +1
        assert (corr.values >= -1.0 - 1e-6).all()
        assert (corr.values <= 1.0 + 1e-6).all()
