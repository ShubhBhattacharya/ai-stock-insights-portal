"""Market data retrieval, technical indicator computation, batch scanning, and news sentiment."""

from __future__ import annotations

import concurrent.futures
import re
from typing import Any

import pandas as pd
import streamlit as st

try:
    import pandas_ta as ta
except Exception:  # pragma: no cover - pure-pandas fallback handles indicators
    ta = None

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None

from src.constants import MIN_HISTORY_ROWS, get_stock_sector

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


def _safe_rsi(close_series: pd.Series, length: int = 14) -> pd.Series:
    """Compute RSI-14 via pandas_ta with a pure-pandas Wilder EWM fallback."""
    if ta is not None:
        try:
            res = ta.rsi(close_series, length=length)
            if res is not None and not res.dropna().empty:
                return res
        except Exception:
            pass
    delta = close_series.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()
    rsi = pd.Series(50.0, index=close_series.index, dtype=float)
    valid = gain.notna() & loss.notna()
    zero_loss = valid & (loss == 0.0)
    nonzero = valid & (loss > 0.0)
    rsi.loc[zero_loss & (gain > 0.0)] = 100.0
    rsi.loc[nonzero] = 100.0 - (100.0 / (1.0 + (gain.loc[nonzero] / loss.loc[nonzero])))
    return rsi


def _safe_sma(close_series: pd.Series, length: int) -> pd.Series:
    """Compute SMA via pandas_ta with a pure-pandas rolling fallback."""
    win = max(1, min(int(length), len(close_series)))
    if ta is not None:
        try:
            res = ta.sma(close_series, length=win)
            if res is not None and not res.dropna().empty:
                return res
        except Exception:
            pass
    return close_series.rolling(window=win, min_periods=1).mean()


def _safe_bbands(close_series: pd.Series, length: int = 20, std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Bollinger Bands (BBL, BBM, BBU) with a pure-pandas rolling fallback."""
    if ta is not None:
        try:
            bbands = ta.bbands(close_series, length=length, std=std)
            if bbands is not None and not bbands.empty and bbands.shape[1] >= 3:
                return bbands.iloc[:, 0], bbands.iloc[:, 1], bbands.iloc[:, 2]
        except Exception:
            pass
    win = max(2, min(length, len(close_series)))
    mid = close_series.rolling(window=win, min_periods=1).mean()
    sd = close_series.rolling(window=win, min_periods=1).std(ddof=0).fillna(0.0)
    return mid - std * sd, mid, mid + std * sd


def _fetch_stock_dataframe_raw(ticker_symbol: str) -> tuple[pd.DataFrame, str]:
    """Uncached 1-year daily OHLCV downloader safe for use in background worker threads."""
    candidates = _build_symbol_candidates(ticker_symbol)
    if not candidates or yf is None:
        return pd.DataFrame(), candidates[0] if candidates else ""

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


def _extract_ticker_slice(raw: pd.DataFrame, sym: str, total_tickers: int) -> pd.DataFrame:
    """Extract and normalize one ticker's OHLCV slice from a batched yf.download result."""
    if raw is None or raw.empty:
        return pd.DataFrame()
    if total_tickers == 1 or not isinstance(raw.columns, pd.MultiIndex):
        return _normalize_ohlcv_df(raw)
    lvl0 = raw.columns.get_level_values(0)
    if sym in lvl0:
        return _normalize_ohlcv_df(raw[sym])
    lvl1 = raw.columns.get_level_values(1)
    if sym in lvl1:
        return _normalize_ohlcv_df(raw.xs(sym, axis=1, level=1))
    return pd.DataFrame()


def _analyze_dataframe(df: pd.DataFrame, formatted_ticker: str) -> tuple[dict[str, Any] | None, str | None]:
    """Compute technical indicators & rule-based signal from a cleaned OHLCV DataFrame."""
    try:
        if df.empty or len(df) < MIN_HISTORY_ROWS:
            return None, f"Insufficient or unavailable market data for '{formatted_ticker}'."

        df = df.copy()
        close_series = df["Close"].astype(float)

        df["RSI"] = _safe_rsi(close_series, length=14)
        df["SMA_50"] = _safe_sma(close_series, length=min(50, len(df) - 1))
        df["SMA_200"] = _safe_sma(close_series, length=min(200, len(df) - 1))
        bbl, bbm, bbu = _safe_bbands(close_series, length=20, std=2.0)
        df["BBL"] = bbl
        df["BBM"] = bbm
        df["BBU"] = bbu

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


def _compute_stock_analysis_raw(ticker_symbol: str) -> tuple[dict[str, Any] | None, str | None]:
    """Uncached technical indicator & synopsis decision computation."""
    cleaned_symbol = ticker_symbol.strip().upper()
    if not cleaned_symbol:
        return None, "Please enter a valid NSE/BSE ticker symbol."

    df, formatted_ticker = _fetch_stock_dataframe_raw(cleaned_symbol)
    if df.empty or len(df) < MIN_HISTORY_ROWS:
        return None, f"Insufficient or unavailable market data for '{cleaned_symbol}'."
    return _analyze_dataframe(df, formatted_ticker)


@st.cache_data(ttl=300, show_spinner=False)
def get_stock_analysis(ticker_symbol: str) -> tuple[dict[str, Any] | None, str | None]:
    """Cached technical indicator and AI rule-based decision engine."""
    return _compute_stock_analysis_raw(ticker_symbol)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_tactical_board_quotes(
    board_items: tuple[tuple[str, str], ...],
) -> dict[str, dict[str, Any]]:
    """
    Fetch all watchlist tickers in one batched yf.download(period='5d', group_by='ticker', threads=True)
    call for sub-1.5s Market Overview rendering across both editions.
    """
    quotes: dict[str, dict[str, Any]] = {}
    if not board_items or yf is None:
        return quotes

    symbols = [sym for _, sym in board_items]
    raw = pd.DataFrame()
    try:
        raw = yf.download(
            symbols,
            period="5d",
            interval="1d",
            group_by="ticker",
            threads=True,
            auto_adjust=False,
            progress=False,
        )
    except Exception:
        raw = pd.DataFrame()

    for label, sym in board_items:
        df_s = _extract_ticker_slice(raw, sym, len(symbols))
        if df_s.empty:
            try:
                df_s = _normalize_ohlcv_df(yf.Ticker(sym).history(period="5d"))
            except Exception:
                df_s = pd.DataFrame()

        if not df_s.empty:
            latest = df_s.iloc[-1]
            prev = df_s.iloc[-2] if len(df_s) > 1 else latest
            close = float(latest["Close"])
            prev_close = float(prev["Close"]) or close
            high = float(latest["High"])
            low = float(latest["Low"])
            change_pct = ((close - prev_close) / prev_close) * 100 if prev_close else 0.0
            range_pct = ((high - low) / prev_close) * 100 if prev_close else 0.0
            quotes[sym] = {
                "label": label,
                "symbol": sym,
                "close": round(close, 2),
                "change_pct": round(change_pct, 2),
                "range_pct": round(range_pct, 2),
            }
        else:
            quotes[sym] = {
                "label": label,
                "symbol": sym,
                "close": 0.0,
                "change_pct": 0.0,
                "range_pct": 0.0,
            }

    return quotes


@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_overview(stock_items: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    """
    Download and analyze multiple equities using a single batched yf.download call
    (threads=True) with thread-safe individual fallback if a ticker slice is absent.
    """
    if not stock_items:
        return []

    symbols = [sym for _, sym in stock_items]
    batched_raw = pd.DataFrame()
    if yf is not None:
        try:
            batched_raw = yf.download(
                symbols,
                period="1y",
                interval="1d",
                group_by="ticker",
                threads=True,
                auto_adjust=False,
                progress=False,
            )
        except Exception:
            batched_raw = pd.DataFrame()

    results: list[dict[str, Any]] = []
    missing_items: list[tuple[str, str]] = []

    for name, sym in stock_items:
        df_slice = _extract_ticker_slice(batched_raw, sym, len(symbols))
        metrics, _ = _analyze_dataframe(df_slice, sym) if len(df_slice) >= MIN_HISTORY_ROWS else (None, None)
        if metrics:
            results.append(
                {
                    "Company Name": name,
                    "Symbol": sym.replace(".NS", "").replace(".BO", ""),
                    "Sector": get_stock_sector(sym),
                    "Price": metrics["close"],
                    "Change %": metrics["day_change_pct"],
                    "RSI": metrics["rsi"],
                    "SMA 50": metrics["sma50"],
                    "Signal": metrics["signal"],
                    "Confidence": metrics["confidence"],
                    "Strategic Insight": metrics["final_reason"],
                }
            )
        else:
            missing_items.append((name, sym))

    if missing_items:
        def analyze_missing(item: tuple[str, str]) -> dict[str, Any] | None:
            name, sym = item
            metrics, _ = _compute_stock_analysis_raw(sym)
            if not metrics:
                return None
            return {
                "Company Name": name,
                "Symbol": sym.replace(".NS", "").replace(".BO", ""),
                "Sector": get_stock_sector(sym),
                "Price": metrics["close"],
                "Change %": metrics["day_change_pct"],
                "RSI": metrics["rsi"],
                "SMA 50": metrics["sma50"],
                "Signal": metrics["signal"],
                "Confidence": metrics["confidence"],
                "Strategic Insight": metrics["final_reason"],
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            for future in concurrent.futures.as_completed([executor.submit(analyze_missing, it) for it in missing_items]):
                try:
                    rec = future.result()
                    if rec:
                        results.append(rec)
                except Exception:
                    continue

    return sorted(results, key=lambda x: x["Company Name"])


@st.cache_data(ttl=300, show_spinner=False)
def fetch_batch_returns(stock_items: tuple[tuple[str, str], ...]) -> dict[str, pd.Series]:
    """Fetch 1-year daily return series for a basket in a single batched yf.download call."""
    if not stock_items:
        return {}

    symbols = [sym for _, sym in stock_items]
    batched_raw = pd.DataFrame()
    if yf is not None:
        try:
            batched_raw = yf.download(
                symbols,
                period="1y",
                interval="1d",
                group_by="ticker",
                threads=True,
                auto_adjust=False,
                progress=False,
            )
        except Exception:
            batched_raw = pd.DataFrame()

    ordered: dict[str, pd.Series] = {}
    for name, sym in stock_items:
        df_s = _extract_ticker_slice(batched_raw, sym, len(symbols))
        if df_s.empty:
            df_s, _ = _fetch_stock_dataframe_raw(sym)
        if not df_s.empty:
            series = df_s["Close"].pct_change().dropna()
            if not series.empty:
                ordered[name] = series
    return ordered


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_sentiment(ticker_symbol: str) -> tuple[str, str, list[dict[str, str]]]:
    """Fetch recent news headlines from yfinance and compute rule-based sentiment."""
    if yf is None:
        return "Neutral 🟡", "Live news feed module unavailable.", []
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
        err_text = str(exc)
        if "CURRENTLY DOWN" in err_text.upper() or "YF" in type(exc).__name__.upper():
            return "Neutral 🟡", "Live news headlines temporarily unavailable from Yahoo Finance.", []
        return "Neutral 🟡", f"News feed unavailable: {err_text}", []


def clear_market_cache() -> None:
    """Clear all cached market data so users can trigger a true live refresh."""
    fetch_stock_dataframe.clear()
    get_stock_analysis.clear()
    fetch_tactical_board_quotes.clear()
    fetch_batch_overview.clear()
    fetch_batch_returns.clear()
    fetch_news_sentiment.clear()
