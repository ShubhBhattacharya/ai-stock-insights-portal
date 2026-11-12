"""Module 2: Single Stock AI Technical Analysis & ML Price Forecast (Lester's Intel Edition)."""

from __future__ import annotations

import html
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.constants import NSE_STOCKS
from src.services.forecasting import predict_stock_prices
from src.services.market_data import fetch_news_sentiment, get_stock_analysis
from src.services.reporting import generate_text_report
from src.styles import (
    render_kpi_grid,
    render_page_header,
    render_signal_badge,
    style_plotly_figure,
)


def _sync_symbol_from_select() -> None:
    """Update custom ticker input when user picks a stock from the dropdown."""
    selected = st.session_state.get("single_stock_select")
    if selected in NSE_STOCKS:
        st.session_state["single_stock_symbol"] = NSE_STOCKS[selected]


def _build_technical_chart(
    df: pd.DataFrame,
    pred_df: pd.DataFrame,
    symbol: str,
    forecast_days: int,
    show_bbands: bool,
) -> go.Figure:
    """Create a synthwave 3-panel Candlestick, Volume, and RSI Plotly figure."""
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            f"▸ {symbol} // BAWSAQ OHLC + SMAs + {forecast_days}D ML VECTOR",
            "▸ DETECTED VOLUME SURGE",
            "▸ RSI-14 MOMENTUM RADAR",
        ),
        row_heights=[0.6, 0.2, 0.2],
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC Price",
            increasing_line_color="#39ff14",
            increasing_fillcolor="rgba(57, 255, 20, 0.72)",
            decreasing_line_color="#ff2a6d",
            decreasing_fillcolor="rgba(255, 42, 109, 0.75)",
        ),
        row=1,
        col=1,
    )

    if show_bbands and {"BBU", "BBL"}.issubset(df.columns):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BBU"],
                mode="lines",
                name="Upper BB (20,2)",
                line=dict(color="rgba(0, 240, 255, 0.5)", width=1.1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["BBL"],
                mode="lines",
                name="Lower BB (20,2)",
                line=dict(color="rgba(255, 42, 133, 0.5)", width=1.1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(192, 132, 252, 0.08)",
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_50"],
            mode="lines",
            name="50 SMA (Laser)",
            line=dict(color="#ffe600", width=2.0),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_200"],
            mode="lines",
            name="200 SMA (Cyber)",
            line=dict(color="#00f0ff", width=2.0),
        ),
        row=1,
        col=1,
    )

    if not pred_df.empty:
        fig.add_trace(
            go.Scatter(
                x=pred_df.index,
                y=pred_df["Predicted_Close"],
                mode="lines+markers",
                name=f"{forecast_days}D Neon ML Forecast",
                line=dict(color="#ff2a85", width=2.6, dash="dash"),
                marker=dict(size=5, color="#ffe600", symbol="diamond"),
            ),
            row=1,
            col=1,
        )

    vol_colors = [
        "#39ff14" if close_v >= open_v else "#ff2a6d"
        for close_v, open_v in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.82,
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            mode="lines",
            name="RSI (14)",
            line=dict(color="#c084fc", width=1.9),
        ),
        row=3,
        col=1,
    )

    fig.add_hline(y=70, line_dash="dot", line_color="#ff2a6d", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#39ff14", row=3, col=1)

    style_plotly_figure(fig, height=770)
    fig.update_annotations(font=dict(family="Orbitron, sans-serif", size=12, color="#00f0ff"))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def render_single_stock_analysis() -> None:
    """Render single-stock technical breakdown, Lester's Intel dossier, and ML forecast."""
    render_page_header(
        title="BAWSAQ Target Intel & ML Forecast",
        subtitle="Deep synthwave technical telemetry, Lester's classified dossier, and ML trend vector",
        badge="LESTER'S UNDERGROUND INTEL • ML ENGINE",
        wanted_stars=4,
    )

    stock_names = list(NSE_STOCKS.keys())
    if "single_stock_symbol" not in st.session_state:
        st.session_state["single_stock_symbol"] = NSE_STOCKS[stock_names[0]]

    col_s1, col_s2, col_s3 = st.columns([2, 1.2, 1])
    with col_s1:
        st.selectbox(
            "LOCK NSE TARGET FROM LIST:",
            stock_names,
            index=0,
            key="single_stock_select",
            on_change=_sync_symbol_from_select,
        )
    with col_s2:
        custom_sym = (
            st.text_input(
                "OR ENTER CUSTOM TICKER:",
                key="single_stock_symbol",
                placeholder="e.g. RELIANCE.NS",
            )
            .upper()
            .strip()
        )
    with col_s3:
        forecast_days = st.selectbox("ML HORIZON:", [7, 15, 30], index=2)

    if not custom_sym:
        st.info("Enter a valid NSE/BSE ticker symbol (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`).")
        return

    with st.spinner(f"Decrypting BAWSAQ telemetry & ML trendline for {custom_sym}..."):
        metrics, error = get_stock_analysis(custom_sym)

    if error:
        st.error(f"🚨 {error}")
        st.info("Tip: Ensure the symbol is a valid NSE/BSE ticker, e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`.")
        return

    if not metrics:
        return

    df = metrics["df"]
    signal_badge_html = render_signal_badge(metrics["signal"], metrics["confidence"])

    st.markdown(
        f'<div class="surface-card" style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:0.75rem;">'
        f'<h3 style="margin:0; font-family:\'Orbitron\',sans-serif; color:#00f0ff;">'
        f'🎯 TARGET LOCKED // {html.escape(metrics["symbol"])}</h3>'
        f"<div>{signal_badge_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    change_tone = "up" if metrics["day_change"] >= 0 else "down"
    rsi_tone = "up" if metrics["rsi"] < 40 else ("down" if metrics["rsi"] > 65 else "warn")

    render_kpi_grid(
        [
            {
                "label": "Live Market Quote",
                "value": f"₹{metrics['close']:,.2f}",
                "delta": f"{metrics['day_change']:+.2f} ({metrics['day_change_pct']:+.2f}%)",
                "tone": change_tone,
            },
            {
                "label": "RSI (14) Radar",
                "value": f"{metrics['rsi']:.1f}",
                "delta": "Oversold" if metrics["rsi"] < 35 else ("Overbought" if metrics["rsi"] > 70 else "Neutral Zone"),
                "tone": rsi_tone,
            },
            {
                "label": "50-Day SMA (Laser)",
                "value": f"₹{metrics['sma50']:,.2f}",
                "delta": "Above SMA50" if metrics["close"] >= metrics["sma50"] else "Below SMA50",
                "tone": "up" if metrics["close"] >= metrics["sma50"] else "down",
            },
            {
                "label": "200-Day SMA (Cyber)",
                "value": f"₹{metrics['sma200']:,.2f}",
                "delta": "Golden Bias" if metrics["sma50"] > metrics["sma200"] else "Bearish Bias",
                "tone": "up" if metrics["sma50"] > metrics["sma200"] else "down",
            },
            {
                "label": "52-Week Perimeter",
                "value": f"₹{metrics['low_52w']:,.0f} – ₹{metrics['high_52w']:,.0f}",
                "delta": f"Vol: {metrics['volume']:,}",
                "tone": "neutral",
            },
        ]
    )

    col_dec1, col_dec2 = st.columns([3, 2])
    with col_dec1:
        st.subheader(
            f"🕶️ Lester's Classified Directive: {metrics['signal']} ({metrics['confidence']}% Confidence)"
        )
        if metrics["signal"] == "BUY":
            st.success(f"**Mission Intel:** {metrics['final_reason']}")
        elif metrics["signal"] == "SELL":
            st.error(f"**Heat Warning:** {metrics['final_reason']}")
        else:
            st.warning(f"**Hold Position:** {metrics['final_reason']}")

        st.markdown("**Explainable Signal Tripwires:**")
        for reason in metrics["reasons"]:
            st.markdown(f"- {reason}")

    with col_dec2:
        st.subheader("📡 Street Wire & News Sentiment")
        sentiment, msg, news_items = fetch_news_sentiment(metrics["symbol"])
        st.markdown(f"**Wire Sentiment:** {sentiment}")
        st.caption(msg)
        if news_items:
            for item in news_items[:3]:
                safe_title = html.escape(item["title"])
                safe_pub = html.escape(item["publisher"])
                safe_url = html.escape(item["url"], quote=True)
                st.markdown(
                    f'<div class="news-item-card">'
                    f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_title}</a>'
                    f'<div class="news-publisher">{safe_pub}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            label="📥 Download Lester's Underground Dossier (.txt)",
            data=generate_text_report(metrics),
            file_name=f"{metrics['symbol']}_Lester_Intel_Dossier.txt",
            mime="text/plain",
            width="stretch",
        )
    with dcol2:
        csv_data = df.to_csv().encode("utf-8")
        st.download_button(
            label="📊 Export Intercepted Telemetry & Bars (.csv)",
            data=csv_data,
            file_name=f"{metrics['symbol']}_1Y_Telemetry.csv",
            mime="text/csv",
            width="stretch",
        )

    st.markdown("---")

    chart_header_col1, chart_header_col2 = st.columns([3, 1])
    with chart_header_col1:
        st.subheader(f"📈 Synthwave Technical Chart & {forecast_days}-Day Neon ML Forecast")
    with chart_header_col2:
        show_bbands = st.checkbox("Show Bollinger Bands (20, 2)", value=False)

    pred_df, r2_score = predict_stock_prices(df, days=forecast_days)
    if not pred_df.empty:
        target_price = float(pred_df["Predicted_Close"].iloc[-1])
        proj_pct = ((target_price - metrics["close"]) / metrics["close"]) * 100 if metrics["close"] else 0.0
        st.caption(
            f"ML Vector Engine: Linear Trend Regression ($R^2$ Fit = {r2_score:.2f}) · "
            f"{forecast_days}-Trading-Day Projected Target: **₹{target_price:,.2f}** ({proj_pct:+.2f}%)"
        )
    else:
        st.caption(f"ML Vector Engine: Linear Trend Regression ($R^2$ Fit = {r2_score:.2f})")

    fig = _build_technical_chart(
        df=df,
        pred_df=pred_df,
        symbol=metrics["symbol"],
        forecast_days=forecast_days,
        show_bbands=show_bbands,
    )
    st.plotly_chart(fig, width="stretch")
