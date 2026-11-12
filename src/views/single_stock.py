"""Module 2: Single Stock AI Technical Analysis & ML Price Forecast (Classified Intel Dossier)."""

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
from src.state import (
    compute_dynamic_wanted_stars,
    get_portal_theme,
    is_default_theme,
    is_doomsday,
    set_context_risk_heat,
)
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
    """Create a theme-adaptive 3-panel Candlestick, Volume, and RSI Plotly figure."""
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    if default_pro:
        up_col, dn_col = "#10b981", "#ef4444"
        sma50_col, sma200_col, ml_col = "#3b82f6", "#f59e0b", "#10b981"
        sub1 = f"{symbol} — Candlestick, 50/200-SMA & {forecast_days}-Day ML Forecast"
        sub2, sub3 = "Trading Volume", "RSI (14)"
        ml_name = f"{forecast_days}D ML Forecast"
        font_family = "Plus Jakarta Sans, Inter, sans-serif"
        ann_bg = "rgba(17, 24, 39, 0.92)"
    elif doomsday:
        up_col, dn_col = "#39ff14", "#ff2a00"
        sma50_col, sma200_col, ml_col = "#ffb703", "#39ff14", "#ff2a00"
        sub1 = f"▸ {symbol} // FALLOUT CANDLES + AMBER 50-SMA + {forecast_days}D RED ML SCENARIO"
        sub2, sub3 = "▸ TRADING VOLUME PULSE", "▸ RSI-14 MOMENTUM RADAR"
        ml_name = f"{forecast_days}D Fallout Scenario"
        font_family = "Orbitron, sans-serif"
        ann_bg = "rgba(16, 10, 8, 0.9)"
    else:
        up_col, dn_col = "#00f5d4", "#ff2a85"
        sma50_col, sma200_col, ml_col = "#fee440", "#00f5d4", "#ff2a85"
        sub1 = f"▸ {symbol} // CYAN-PINK CANDLES + NEON 50-SMA + {forecast_days}D ML FORECAST"
        sub2, sub3 = "▸ TRADING VOLUME PULSE", "▸ RSI-14 MOMENTUM RADAR"
        ml_name = f"{forecast_days}D Magenta ML Curve"
        font_family = "Orbitron, sans-serif"
        ann_bg = "rgba(11, 5, 36, 0.88)"

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(sub1, sub2, sub3),
        row_heights=[0.6, 0.2, 0.2],
    )

    inc_fill = "rgba(16, 185, 129, 0.72)" if default_pro else ("rgba(57, 255, 20, 0.72)" if doomsday else "rgba(0, 245, 212, 0.72)")
    dec_fill = "rgba(239, 68, 68, 0.72)" if default_pro else ("rgba(255, 42, 0, 0.76)" if doomsday else "rgba(255, 42, 133, 0.76)")

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=up_col,
            increasing_fillcolor=inc_fill,
            decreasing_line_color=dn_col,
            decreasing_fillcolor=dec_fill,
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
                line=dict(color=up_col, width=1.1, dash="dot"),
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
                line=dict(color=dn_col, width=1.1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(255, 69, 0, 0.08)" if doomsday else "rgba(192, 132, 252, 0.08)",
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_50"],
            mode="lines",
            name="50 SMA",
            line=dict(color=sma50_col, width=2.1),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_200"],
            mode="lines",
            name="200 SMA",
            line=dict(color=sma200_col, width=1.9),
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
                name=ml_name,
                line=dict(color=ml_col, width=2.6, dash="dot"),
                marker=dict(size=5, color=sma50_col, symbol="diamond"),
            ),
            row=1,
            col=1,
        )
        last_pred_date = pred_df.index[-1]
        last_pred_val = float(pred_df["Predicted_Close"].iloc[-1])
        fig.add_annotation(
            x=last_pred_date,
            y=last_pred_val,
            text=f"{forecast_days}D Target: ₹{last_pred_val:,.2f}" if default_pro else f"🎯 {forecast_days}D TARGET: ₹{last_pred_val:,.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=ml_col,
            font=dict(family=font_family, size=11, color=sma50_col),
            bgcolor=ann_bg,
            bordercolor=ml_col,
            borderwidth=1,
            row=1,
            col=1,
        )

    last_hist_date = df.index[-1]
    last_hist_close = float(df["Close"].iloc[-1])
    fig.add_annotation(
        x=last_hist_date,
        y=last_hist_close,
        text=f"Spot: ₹{last_hist_close:,.2f}" if default_pro else f"CROSSHAIR SPOT: ₹{last_hist_close:,.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=up_col,
        font=dict(family=font_family, size=11, color=up_col),
        bgcolor=ann_bg,
        bordercolor=up_col,
        borderwidth=1,
        ax=-55,
        ay=-36,
        row=1,
        col=1,
    )

    vol_colors = [
        up_col if close_v >= open_v else dn_col
        for close_v, open_v in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.84,
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
            line=dict(color="#ffb703" if doomsday else "#c084fc", width=1.9),
        ),
        row=3,
        col=1,
    )

    fig.add_hline(y=70, line_dash="dot", line_color=dn_col, row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color=up_col, row=3, col=1)

    style_plotly_figure(fig, height=780)
    fig.update_annotations(font=dict(family=font_family, size=12, color=up_col))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig


def render_single_stock_analysis() -> None:
    """Render single-stock technical breakdown, signal report, and ML forecast."""
    stock_names = list(NSE_STOCKS.keys())
    if "single_stock_symbol" not in st.session_state:
        st.session_state["single_stock_symbol"] = NSE_STOCKS[stock_names[0]]

    peek_sym = str(st.session_state.get("single_stock_symbol", NSE_STOCKS[stock_names[0]])).upper().strip()
    peek_metrics, _ = get_stock_analysis(peek_sym) if peek_sym else (None, None)
    if peek_metrics:
        rsi_v = float(peek_metrics["rsi"])
        chg_v = abs(float(peek_metrics["day_change_pct"]))
        stock_heat = 6 if (rsi_v > 72 or rsi_v < 28 or chg_v >= 3.0) else (4 if (peek_metrics["signal"] == "SELL" or chg_v >= 1.5) else 2)
        set_context_risk_heat(stock_heat)

    default_pro = is_default_theme()
    doomsday = is_doomsday()
    if default_pro:
        hdr_title = "Single Stock AI & ML Prediction"
        hdr_sub = "NSE candlestick indicators, RSI-14, 50/200-SMA, Bollinger Bands & Linear Regression forecast"
        hdr_badge = "EQUITY RESEARCH • ML FORECASTING"
    elif doomsday:
        hdr_title = "🚨 FALLOUT SCENARIO FORECAST"
        hdr_sub = "Armored bunker candlestick radar, glowing red Fallout ML trend vector & survival dossiers"
        hdr_badge = "FALLOUT SCENARIO INTEL • ML FORECASTING"
    else:
        hdr_title = "BAWSAQ Target Intel & ML Forecast"
        hdr_sub = "Deep indigo synthwave candlestick radar, ML trend vector, and Classified Intel Dossiers"
        hdr_badge = "CLASSIFIED INTEL DOSSIERS • ML FORECASTING"

    render_page_header(
        title=hdr_title,
        subtitle=hdr_sub,
        badge=hdr_badge,
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    col_s1, col_s2, col_s3 = st.columns([2, 1.2, 1])
    with col_s1:
        st.selectbox(
            "Select NSE Equity:" if default_pro else "LOCK NSE TARGET FROM LIST:",
            stock_names,
            index=0,
            key="single_stock_select",
            on_change=_sync_symbol_from_select,
        )
    with col_s2:
        custom_sym = (
            st.text_input(
                "Or Enter Custom Ticker:" if default_pro else "OR ENTER CUSTOM TICKER:",
                key="single_stock_symbol",
                placeholder="e.g. RELIANCE.NS",
            )
            .upper()
            .strip()
        )
    with col_s3:
        forecast_days = st.selectbox("Forecast Horizon (Days):" if default_pro else "ML HORIZON:", [7, 15, 30], index=2)

    if not custom_sym:
        st.info("Enter a valid NSE/BSE ticker symbol (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`).")
        return

    spin_msg = (
        f"Loading technical analysis and ML forecast for {custom_sym}..."
        if default_pro
        else f"Decrypting Classified Intel Dossier & ML vector for {custom_sym}..."
    )
    with st.spinner(spin_msg):
        metrics, error = get_stock_analysis(custom_sym)

    if error:
        st.error(f"🚨 {error}")
        st.info("Tip: Ensure the symbol is a valid NSE/BSE ticker, e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`.")
        return

    if not metrics:
        return

    df = metrics["df"]
    signal_badge_html = render_signal_badge(metrics["signal"], metrics["confidence"])

    sym_heading = (
        html.escape(metrics["symbol"])
        if default_pro
        else f'🎯 TARGET LOCKED // {html.escape(metrics["symbol"])}'
    )
    sym_style = (
        "margin:0; font-size:1.15rem; font-weight:700; color:#f8fafc;"
        if default_pro
        else "margin:0; font-family:'Orbitron',sans-serif; color:#00f5d4;"
    )
    st.markdown(
        f'<div class="surface-card" style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:0.75rem;">'
        f'<h3 style="{sym_style}">{sym_heading}</h3>'
        f"<div>{signal_badge_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    change_tone = "up" if metrics["day_change"] >= 0 else "down"
    rsi_tone = "up" if metrics["rsi"] < 40 else ("down" if metrics["rsi"] > 65 else "warn")

    render_kpi_grid(
        [
            {
                "label": "Market Price" if default_pro else "Live Market Quote",
                "value": f"₹{metrics['close']:,.2f}",
                "delta": f"{metrics['day_change']:+.2f} ({metrics['day_change_pct']:+.2f}%)",
                "tone": change_tone,
            },
            {
                "label": "RSI (14)" if default_pro else ("RSI (14) Geiger" if doomsday else "RSI (14) Radar"),
                "value": f"{metrics['rsi']:.1f}",
                "delta": "Oversold" if metrics["rsi"] < 35 else ("Overbought" if metrics["rsi"] > 70 else "Neutral Zone"),
                "tone": rsi_tone,
            },
            {
                "label": "50-Day SMA" if default_pro else "50-Day SMA (Laser)",
                "value": f"₹{metrics['sma50']:,.2f}",
                "delta": "Above SMA50" if metrics["close"] >= metrics["sma50"] else "Below SMA50",
                "tone": "up" if metrics["close"] >= metrics["sma50"] else "down",
            },
            {
                "label": "200-Day SMA" if default_pro else "200-Day SMA (Trend)",
                "value": f"₹{metrics['sma200']:,.2f}",
                "delta": "Golden Bias" if metrics["sma50"] > metrics["sma200"] else "Bearish Bias",
                "tone": "up" if metrics["sma50"] > metrics["sma200"] else "down",
            },
            {
                "label": "52-Week Range" if default_pro else "52-Week Perimeter",
                "value": f"₹{metrics['low_52w']:,.0f} – ₹{metrics['high_52w']:,.0f}",
                "delta": f"Vol: {metrics['volume']:,}",
                "tone": "neutral",
            },
        ]
    )

    col_dec1, col_dec2 = st.columns([3, 2])
    with col_dec1:
        st.subheader(
            f"Signal Summary: {metrics['signal']} ({metrics['confidence']}% Confidence)"
            if default_pro
            else f"📁 CLASSIFIED INTEL DOSSIER: {metrics['signal']} ({metrics['confidence']}% Confidence)"
        )
        if metrics["signal"] == "BUY":
            st.success(f"**{'Signal Rationale:' if default_pro else 'Mission Directive:'}** {metrics['final_reason']}")
        elif metrics["signal"] == "SELL":
            st.error(f"**{'Risk Warning:' if default_pro else 'Heat Warning:'}** {metrics['final_reason']}")
        else:
            st.warning(f"**{'Neutral Stance:' if default_pro else 'Hold Position:'}** {metrics['final_reason']}")

        st.markdown("**Rule-Based Trigger Conditions:**" if default_pro else "**Explainable Signal Tripwires:**")
        for reason in metrics["reasons"]:
            st.markdown(f"- {reason}")

    with col_dec2:
        st.subheader("Market News & Sentiment" if default_pro else "📡 Street Wire & News Sentiment")
        sentiment, msg, news_items = fetch_news_sentiment(metrics["symbol"])
        st.markdown(f"**{'Sentiment:' if default_pro else 'Wire Sentiment:'}** {sentiment}")
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
        rep_label = (
            "📥 Download Research Report (.txt)"
            if default_pro
            else ("📥 Download Bunker Tactical Dossier (.txt)" if doomsday else "📥 Download Classified Intel Dossier (.txt)")
        )
        rep_filename = (
            f"{metrics['symbol']}_Analysis_Report.txt"
            if default_pro
            else (
                f"{metrics['symbol']}_Bunker_Tactical_Dossier.txt"
                if doomsday
                else f"{metrics['symbol']}_Classified_Intel_Dossier.txt"
            )
        )
        st.download_button(
            label=rep_label,
            data=generate_text_report(metrics, edition=get_portal_theme()),
            file_name=rep_filename,
            mime="text/plain",
            width="stretch",
        )
    with dcol2:
        st.download_button(
            label="📊 Export Historical OHLCV & Indicators (.csv)" if default_pro else "📊 Export Intercepted Telemetry & Bars (.csv)",
            data=df.to_csv().encode("utf-8"),
            file_name=f"{metrics['symbol']}_1Y_Telemetry.csv",
            mime="text/csv",
            width="stretch",
        )

    st.markdown("---")

    chart_header_col1, chart_header_col2 = st.columns([3, 1])
    with chart_header_col1:
        chart_sub = (
            f"Technical Chart & {forecast_days}-Day ML Forecast"
            if default_pro
            else (
                f"📈 DEFCON Technical Chart & {forecast_days}-Day Fallout ML Curve"
                if doomsday
                else f"📈 Synthwave Technical Chart & {forecast_days}-Day Magenta ML Curve"
            )
        )
        st.subheader(chart_sub)
    with chart_header_col2:
        show_bbands = st.checkbox("Show Bollinger Bands (20, 2)", value=False)

    pred_df, r2_score = predict_stock_prices(df, days=forecast_days)
    if not pred_df.empty:
        target_price = float(pred_df["Predicted_Close"].iloc[-1])
        proj_pct = ((target_price - metrics["close"]) / metrics["close"]) * 100 if metrics["close"] else 0.0
        st.caption(
            f"Linear Trend Regression ($R^2$ Fit = {r2_score:.2f}) · "
            f"{forecast_days}-Trading-Day Projected Target: **₹{target_price:,.2f}** ({proj_pct:+.2f}%)"
        )
    else:
        st.caption(f"Linear Trend Regression ($R^2$ Fit = {r2_score:.2f})")

    fig = _build_technical_chart(
        df=df,
        pred_df=pred_df,
        symbol=metrics["symbol"],
        forecast_days=forecast_days,
        show_bbands=show_bbands,
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
