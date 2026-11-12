"""Market data retrieval, technical indicator computation, batch scanning, and news sentiment."""

from __future__ import annotations

import concurrent.futures
import re
from typing import Any

import pandas as pd
import pandas_ta as ta
import streamlit as st
import yfinance as yf

from src.constants import MIN_HISTORY_ROWS

_POSITIVE_KEYWORDS = (
    "growth", "profit", "surge", "rise", "record", "gain", "buy", "bullish",
    "expansion", "beat", "rally", "upgrade", "dividend", "revenue", "order",
    "contracts", "milestone", "positive", "high",
)
_NEGATIVE_KEYWORDS = (
    "fall", "loss", "drop", "decline", "slash", "risk", "bearish", "sell",
    "lawsuit", "penalty", "cut", "probe", "investigation", "downgrade",
    "crash", "plunge", "concern", "miss", "weak",
)

_POS_PATTERN = re.compile(r"\b(" + "|".join(re.escape(w) for w in _POSITIVE_KEYWORDS) + r")\b")
_NEG_PATTERN = re.compile(r"\b(" + "|".join(re.escape(w) for w in _NEGATIVE_KEYWORDS) + r")\b")


def _normalize_ohlcv_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean yfinance OHLCV DataFrame: flatten MultiIndex, deduplicate, normalize tz & numeric types."""
    if df is None or df.empty:
        return pd.DataFrame()

    cleaned = df.copy()
    if isinstance(cleaned.columns, pd.MultiIndex):
        cleaned.columns = cleaned.columns.get_level_values(0)

    cleaned = cleaned.loc[:, ~cleaned.columns.duplicated()]

    if "Close" not in cleaned.columns:
        return pd.DataFrame()

    for col in ("Open", "High", "Low", "Close", "Volume"):
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.dropna(subset=["Close"])
    if cleaned.empty:
        return pd.DataFrame()

    # Fill missing OHLC/Volume values safely so downstream charts never break
    for col in ("Open", "High", "Low"):
        if col not in cleaned.columns:
            cleaned[col] = cleaned["Close"]
        else:
            cleaned[col] = cleaned[col].fillna(cleaned["Close"])

    if "Volume" not in cleaned.columns:
        cleaned["Volume"] = 0
    else:
        cleaned["Volume"] = cleaned["Volume"].fillna(0)

    idx = pd.to_datetime(cleaned.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    cleaned.index = idx
    cleaned = cleaned.sort_index()
    return cleaned


def _build_symbol_candidates(ticker_symbol: str) -> list[str]:
    """Generate NSE/BSE fallback ticker candidates."""
    ticker_clean = ticker_symbol.strip().upper()
    if not ticker_clean:
        return []
    if "." in ticker_clean:
        return [ticker_clean]
    return [f"{ticker_clean}.NS", f"{ticker_clean}.BO", ticker_clean]


def _fetch_stock_dataframe_raw(ticker_symbol: str) -> tuple[pd.DataFrame, str]:
    """Uncached 1-year daily OHLCV downloader safe for use in background worker threads."""
    candidates = _build_symbol_candidates(ticker_symbol)
    if not candidates:
        return pd.DataFrame(), ""

    for sym in candidates:
        try:
            raw = yf.download(
                sym,
                period="1y",
                interval="1d",
                auto_adjust=False,
                progress=False,
            )
            cleaned = _normalize_ohlcv_df(raw)
            if len(cleaned) >= MIN_HISTORY_ROWS:
                return cleaned, sym
        except Exception:
            continue

    for sym in candidates:
        try:
            raw = yf.Ticker(sym).history(period="1y")
            cleaned = _normalize_ohlcv_df(raw)
            if len(cleaned) >= MIN_HISTORY_ROWS:
                return cleaned, sym
        except Exception:
            continue

    return pd.DataFrame(), candidates[0]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_dataframe(ticker_symbol: str) -> tuple[pd.DataFrame, str]:
    """Cached 1-year OHLCV downloader for UI views."""
    return _fetch_stock_dataframe_raw(ticker_symbol)


def _compute_stock_analysis_raw(ticker_symbol: str) -> tuple[dict[str, Any] | None, str | None]:
    """Uncached technical indicator & synopsis decision computation."""
    cleaned_symbol = ticker_symbol.strip().upper()
    if not cleaned_symbol:
        return None, "Please enter a valid NSE/BSE ticker symbol."

    try:
        df, formatted_ticker = _fetch_stock_dataframe_raw(cleaned_symbol)
        if df.empty or len(df) < MIN_HISTORY_ROWS:
            return None, f"Insufficient or unavailable market data for '{cleaned_symbol}'."

        df = df.copy()
        close_series = df["Close"].astype(float)

        rsi_series = ta.rsi(close_series, length=14)
        sma50_series = ta.sma(close_series, length=min(50, len(df) - 1))
        sma200_series = ta.sma(close_series, length=min(200, len(df) - 1))
        bbands = ta.bbands(close_series, length=20, std=2)

        df["RSI"] = rsi_series
        df["SMA_50"] = sma50_series
        df["SMA_200"] = sma200_series
        if bbands is not None and not bbands.empty and bbands.shape[1] >= 3:
            df["BBL"] = bbands.iloc[:, 0]
            df["BBM"] = bbands.iloc[:, 1]
            df["BBU"] = bbands.iloc[:, 2]

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        close = float(latest["Close"])
        prev_close = float(prev["Close"])
        day_change = close - prev_close
        day_change_pct = (day_change / prev_close) * 100 if prev_close else 0.0

        rsi = float(latest["RSI"]) if not pd.isna(latest["RSI"]) else 50.0
        sma50 = float(latest["SMA_50"]) if not pd.isna(latest["SMA_50"]) else close
        sma200 = float(latest["SMA_200"]) if not pd.isna(latest["SMA_200"]) else close
        volume = int(float(latest["Volume"])) if not pd.isna(latest["Volume"]) else 0
        high_52w = float(df["High"].max())
        low_52w = float(df["Low"].min())

        reasons: list[str] = []
        if rsi < 35:
            reasons.append(
                f"🟢 **RSI Oversold ({rsi:.1f}):** Momentum indicates potential undervaluation and buying interest."
            )
        elif rsi > 70:
            reasons.append(
                f"🔴 **RSI Overbought ({rsi:.1f}):** Momentum is stretched near upper levels; risk of profit-taking."
            )
        else:
            reasons.append(
                f"🟡 **Neutral RSI ({rsi:.1f}):** Price momentum is within normal bounds (35–70)."
            )

        sma50_ratio = (close / sma50) * 100 if sma50 else 100.0
        if close >= sma50:
            reasons.append(
                f"🟢 **Above 50-Day SMA (₹{sma50:,.2f}):** Trading at {sma50_ratio:.1f}% of SMA50, signaling positive short-term trend."
            )
        else:
            reasons.append(
                f"🔴 **Below 50-Day SMA (₹{sma50:,.2f}):** Trading at {sma50_ratio:.1f}% of SMA50, exhibiting short-term technical resistance."
            )

        if sma50 > sma200:
            reasons.append(
                f"🟢 **Bullish Alignment:** 50-Day SMA (₹{sma50:,.2f}) is above 200-Day SMA (₹{sma200:,.2f})."
            )
        else:
            reasons.append(
                f"🔴 **Bearish Alignment:** 50-Day SMA (₹{sma50:,.2f}) remains below 200-Day SMA (₹{sma200:,.2f})."
            )

        # Exact Synopsis Rule-Based Decision Engine
        if rsi < 40 and close > (sma50 * 0.95):
            signal = "BUY"
            confidence = 88
            final_reason = (
                "Oversold condition near moving-average support. Attractive accumulation opportunity."
            )
        elif rsi > 65 or close < (sma50 * 0.92):
            signal = "SELL"
            confidence = 82
            final_reason = (
                "Overbought condition or notable break below 50-day SMA support. Risk mitigation recommended."
            )
        else:
            signal = "HOLD"
            confidence = 65
            final_reason = (
                "Consolidation or no strong directional trigger. Maintain current exposure."
            )

        return {
            "symbol": formatted_ticker,
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "day_change": round(day_change, 2),
            "day_change_pct": round(day_change_pct, 2),
            "volume": volume,
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "rsi": round(rsi, 2),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "signal": signal,
            "confidence": confidence,
            "reasons": reasons,
            "final_reason": final_reason,
            "df": df,
        }, None
    except Exception as exc:
        return None, str(exc)


@st.cache_data(ttl=300, show_spinner=False)
def get_stock_analysis(ticker_symbol: str) -> tuple[dict[str, Any] | None, str | None]:
    """Cached technical indicator and AI rule-based decision engine."""
    return _compute_stock_analysis_raw(ticker_symbol)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_overview(stock_items: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    """
    Download and analyze multiple equities concurrently using pure worker functions
    to avoid Streamlit ScriptRunContext threading issues.
    """
    results: list[dict[str, Any]] = []

    def analyze_item(item: tuple[str, str]) -> dict[str, Any] | None:
        name, sym = item
        metrics, _ = _compute_stock_analysis_raw(sym)
        if not metrics:
            return None
        return {
            "Company Name": name,
            "Symbol": sym.replace(".NS", "").replace(".BO", ""),
            "Price": metrics["close"],
            "Change %": metrics["day_change_pct"],
            "RSI": metrics["rsi"],
            "SMA 50": metrics["sma50"],
            "Signal": metrics["signal"],
            "Confidence": metrics["confidence"],
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(analyze_item, item) for item in stock_items]
        for future in concurrent.futures.as_completed(futures):
            try:
                record = future.result()
                if record:
                    results.append(record)
            except Exception:
                continue

    return sorted(results, key=lambda x: x["Company Name"])


@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_returns(stock_items: tuple[tuple[str, str], ...]) -> dict[str, pd.Series]:
    """Concurrently fetch daily return series for a basket of stocks."""
    returns_dict: dict[str, pd.Series] = {}

    def load_returns(item: tuple[str, str]) -> tuple[str, pd.Series | None]:
        name, sym = item
        df_s, _ = _fetch_stock_dataframe_raw(sym)
        if df_s.empty:
            return name, None
        return name, df_s["Close"].pct_change().dropna()

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(load_returns, item) for item in stock_items]
        for future in concurrent.futures.as_completed(futures):
            try:
                name, series = future.result()
                if series is not None and not series.empty:
                    returns_dict[name] = series
            except Exception:
                continue

    # Preserve user selection order
    ordered: dict[str, pd.Series] = {}
    for name, _ in stock_items:
        if name in returns_dict:
            ordered[name] = returns_dict[name]
    return ordered


@st.cache_data(ttl=600, show_spinner=False)
def fetch_news_sentiment(ticker_symbol: str) -> tuple[str, str, list[dict[str, str]]]:
    """Fetch recent news headlines from yfinance and compute rule-based sentiment."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        raw_news = ticker.news[:6] if ticker.news else []
        if not raw_news:
            return "Neutral 🟡", "No recent news feed available for this ticker.", []

        news_items: list[dict[str, str]] = []
        for entry in raw_news:
            title = entry.get("title")
            url = entry.get("link")
            publisher = entry.get("publisher", "")

            content = entry.get("content")
            if isinstance(content, dict):
                title = title or content.get("title")
                url = url or (content.get("canonicalUrl") or {}).get("url")
                provider = content.get("provider")
                if isinstance(provider, dict):
                    publisher = publisher or provider.get("displayName", "")

            if title:
                news_items.append(
                    {
                        "title": title,
                        "url": url or "#",
                        "publisher": publisher or "Market Wire",
                    }
                )

        if not news_items:
            return "Neutral 🟡", "News items had no parseable titles.", []

        pos_count = 0
        neg_count = 0
        for item in news_items:
            text = item["title"].lower()
            pos_count += len(_POS_PATTERN.findall(text))
            neg_count += len(_NEG_PATTERN.findall(text))

        if pos_count > neg_count:
            sentiment = "Bullish / Positive 🟢"
        elif neg_count > pos_count:
            sentiment = "Bearish / Negative 🔴"
        else:
            sentiment = "Neutral / Balanced 🟡"

        summary = (
            f"Scanned {len(news_items)} recent headlines "
            f"(Positive cues: {pos_count}, Negative cues: {neg_count})."
        )
        return sentiment, summary, news_items
    except Exception as exc:
        return "Neutral 🟡", f"News feed unavailable: {exc}", []


def clear_market_cache() -> None:
    """Clear all cached market data so users can trigger a true live refresh."""
    fetch_stock_dataframe.clear()
    get_stock_analysis.clear()
    fetch_batch_overview.clear()
    fetch_batch_returns.clear()
    fetch_news_sentiment.clear()
