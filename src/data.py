"""Compatibility alias for market data services."""

from src.services.market_data import *  # noqa: F401, F403
from src.services.market_data import (
    clear_market_cache,
    fetch_batch_overview,
    fetch_batch_returns,
    fetch_news_sentiment,
    fetch_stock_dataframe,
    fetch_tactical_board_quotes,
    get_stock_analysis,
)

__all__ = [
    "clear_market_cache",
    "fetch_batch_overview",
    "fetch_batch_returns",
    "fetch_news_sentiment",
    "fetch_stock_dataframe",
    "fetch_tactical_board_quotes",
    "get_stock_analysis",
]
