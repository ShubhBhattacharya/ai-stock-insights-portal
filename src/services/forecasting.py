"""Machine Learning price trend forecasting via Scikit-Learn Linear Regression."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_stock_prices(df: pd.DataFrame, days: int = 30) -> tuple[pd.DataFrame, float]:
    """
    Fit a Scikit-Learn Linear Regression model over historical trading day indices
    to project future price trends for the specified horizon (7, 15, or 30 trading days).
    """
    df_clean = df.dropna(subset=["Close"]).copy()
    if len(df_clean) < 15:
        return pd.DataFrame(), 0.0

    x_train = np.arange(len(df_clean)).reshape(-1, 1)
    y_train = df_clean["Close"].values.astype(float)

    model = LinearRegression()
    model.fit(x_train, y_train)
    r2_score = float(model.score(x_train, y_train))

    future_x = np.arange(len(df_clean), len(df_clean) + days).reshape(-1, 1)
    predictions = model.predict(future_x).flatten()
    # Prevent nonsensical negative price projections on sharp downtrends
    predictions = np.maximum(predictions, 0.01)

    last_date = pd.Timestamp(df_clean.index[-1]).tz_localize(None)
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=days)

    pred_df = pd.DataFrame(
        {"Date": future_dates, "Predicted_Close": np.round(predictions, 2)}
    )
    pred_df.set_index("Date", inplace=True)
    return pred_df, round(r2_score, 3)
