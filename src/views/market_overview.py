"""Module 1: Real-Time 3-Column Tactical Command Board (GTA VI & Doomsday Editions)."""

from __future__ import annotations

import html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.constants import NSE_STOCKS, TACTICAL_BOARD_GROUPS, TACTICAL_BOARD_TICKERS
from src.services.forecasting import predict_stock_prices
from src.services.market_data import (
    clear_market_cache,
    fetch_batch_overview,
    fetch_tactical_board_quotes,
    get_stock_analysis,
)
from src.state import compute_dynamic_wanted_stars, is_doomsday, set_context_risk_heat
from src.styles import (
    render_page_header,
    render_wanted_stars_html,
    render_weazel_flash_ticker,
    style_plotly_figure,
)


def _render_tactical_card(
    items: tuple[tuple[str, str], ...],
    quotes: dict[str, dict],
    variant: str = "cyan",
) -> None:
    """Render one 4-row stacked hazard-striped ticker card (STOCK | CHANGE % | RANGE %)."""
    border_cls = "tactical-card-cyan" if variant == "cyan" else "tactical-card-magenta"
    rows_html: list[str] = []
    for label, sym in items:
        q = quotes.get(sym, {})
        chg = float(q.get("change_pct", 0.0))
        rng = float(q.get("range_pct", 0.0))
        chg_cls = "tactical-pos" if chg >= 0 else "tactical-neg"
        rows_html.append(
            f'<div class="tactical-grid-row">'
            f'<span class="tactical-sym">{html.escape(label)}</span>'
            f'<span class="{chg_cls}">{chg:+.2f}%</span>'
            f'<span class="tactical-rng">{rng:.2f}%</span>'
            f"</div>"
        )

    st.markdown(
        f'<div class="tactical-card {border_cls}">'
        f'<div class="tactical-hazard-strip"></div>'
        f'<div class="tactical-card-inner">'
        f'<div class="tactical-grid-head">'
        f'<span>STOCK</span><span style="text-align:right;">CHANGE %</span><span style="text-align:right;">RANGE %</span>'
        f"</div>"
        f'{"".join(rows_html)}'
        f"</div>"
        f'<div class="tactical-hazard-strip"></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _build_tactical_center_chart(
    df: pd.DataFrame,
    pred_df: pd.DataFrame,
    label: str,
    symbol: str,
    doomsday: bool,
) -> go.Figure:
    """Build the glowing tactical candlestick + 50-SMA + EMA + 30d ML forecast chart."""
    recent = df.tail(65).copy()
    ema20 = recent["Close"].astype(float).ewm(span=20, adjust=False).mean()

    if doomsday:
        bg_plot = "rgba(12, 10, 8, 0.96)"
        grid_col = "rgba(57, 255, 20, 0.10)"
        up_line, up_fill = "#39ff14", "rgba(57, 255, 20, 0.85)"
        dn_line, dn_fill = "#ff4500", "rgba(255, 69, 0, 0.85)"
        sma_color = "#ffb703"
        ema_color = "#39ff14"
        ml_color = "#39ff14"
        ml_band_color = "#ff4500"
        title_color = "#39ff14"
        cross_color = "#ffb703"
    else:
        bg_plot = "rgba(10, 5, 28, 0.95)"
        grid_col = "rgba(0, 245, 212, 0.11)"
        up_line, up_fill = "#fee440", "rgba(254, 228, 64, 0.88)"
        dn_line, dn_fill = "#ff2a85", "rgba(255, 42, 133, 0.88)"
        sma_color = "#fee440"
        ema_color = "#00f5d4"
        ml_color = "#00f5d4"
        ml_band_color = "#ff2a85"
        title_color = "#00f5d4"
        cross_color = "#ff2a85"

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=recent.index,
            open=recent["Open"],
            high=recent["High"],
            low=recent["Low"],
            close=recent["Close"],
            name=label,
            increasing_line_color=up_line,
            increasing_fillcolor=up_fill,
            decreasing_line_color=dn_line,
            decreasing_fillcolor=dn_fill,
        )
    )

    if "SMA_50" in recent.columns:
        fig.add_trace(
            go.Scatter(
                x=recent.index,
                y=recent["SMA_50"],
                mode="lines",
                name="50 SMA",
                line=dict(color=sma_color, width=2.0),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=recent.index,
            y=ema20,
            mode="lines",
            name="20 EMA",
            line=dict(color=ema_color, width=2.0),
        )
    )

    if not pred_df.empty:
        last_dt = recent.index[-1]
        last_close = float(recent["Close"].iloc[-1])
        x_ml = [last_dt] + list(pred_df.index)
        y_ml = [last_close] + list(pred_df["Predicted_Close"].astype(float))
        fig.add_trace(
            go.Scatter(
                x=x_ml,
                y=y_ml,
                mode="lines",
                name="ML PRICE FORECAST",
                line=dict(color=ml_color, width=2.3, dash="dot"),
            )
        )
        spread = np.linspace(0.0, 0.035, len(y_ml))
        y_alt = np.array(y_ml) * (1.0 - spread)
        fig.add_trace(
            go.Scatter(
                x=x_ml,
                y=y_alt,
                mode="lines",
                name="DOWNSIDE CONE",
                line=dict(color=ml_band_color, width=1.4, dash="dot"),
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=pred_df.index[-1],
            y=float(pred_df["Predicted_Close"].iloc[-1]),
            text=f"ML TARGET ₹{float(pred_df['Predicted_Close'].iloc[-1]):,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=ml_color,
            ax=-36,
            ay=-24,
            font=dict(family="Share Tech Mono, monospace", size=10, color=ml_color),
            bgcolor="rgba(7, 4, 18, 0.88)",
            bordercolor=ml_color,
            borderwidth=1,
        )

    # Breakout & Crosshair Tactical Markers
    if len(recent) >= 12:
        peak_idx = recent["High"].idxmax()
        peak_val = float(recent.loc[peak_idx, "High"])
        early_slice = recent.iloc[: max(8, len(recent) // 2)]
        low_idx = early_slice["Low"].idxmin()
        low_val = float(early_slice.loc[low_idx, "Low"])

        fig.add_annotation(
            x=peak_idx,
            y=peak_val,
            text="⚠ TARGET TRIGGERED",
            showarrow=True,
            arrowhead=2,
            arrowcolor=ml_band_color,
            ax=0,
            ay=-28,
            font=dict(family="Orbitron, sans-serif", size=9, color="#fee440" if not doomsday else "#ffb703"),
            bgcolor="rgba(22, 8, 12, 0.90)",
            bordercolor=ml_band_color,
            borderwidth=1,
        )
        fig.add_annotation(
            x=low_idx,
            y=low_val,
            text="⌖ RADAR LOCK",
            showarrow=True,
            arrowhead=2,
            arrowcolor=cross_color,
            ax=0,
            ay=26,
            font=dict(family="Orbitron, sans-serif", size=9, color=cross_color),
            bgcolor="rgba(8, 10, 22, 0.88)",
            bordercolor=cross_color,
            borderwidth=1,
        )

    fig.update_layout(
        title=dict(
            text=f"{label} ({symbol}) • LIVE TACTICAL CANDLESTICK & 30D ML FORECAST",
            font=dict(family="Orbitron, sans-serif", size=12, color=title_color),
            x=0.02,
        ),
        height=390,
        margin=dict(l=42, r=18, t=42, b=34),
        paper_bgcolor=bg_plot,
        plot_bgcolor=bg_plot,
        font=dict(family="Share Tech Mono, monospace", color="#cbd5e1", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
        ),
        xaxis=dict(gridcolor=grid_col, showline=True, linecolor="rgba(255,255,255,0.14)"),
        yaxis=dict(gridcolor=grid_col, showline=True, linecolor="rgba(255,255,255,0.14)"),
    )
    return fig


def render_market_overview() -> None:
    """Render the 3-column GTA VI / Doomsday Tactical Command Board + expandable screener."""
    doomsday = is_doomsday()
    render_page_header(
        title=(
            "📊 Indian Market Overview - DEFCON Tactical Board"
            if doomsday
            else "📊 Indian Market Overview - Live Heist Board"
        ),
        subtitle="BUNKER.NET // NSE MARKET FEED" if doomsday else "BAWSAQ / LCN - NSE MARKET FEED",
        badge=(
            "DEFCON TACTICAL BOARD • LIVE NSE 16"
            if doomsday
            else "BAWSAQ / LCN • LIVE HEIST BOARD"
        ),
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    board_quotes = fetch_tactical_board_quotes(TACTICAL_BOARD_TICKERS)
    decliners = sum(1 for q in board_quotes.values() if float(q.get("change_pct", 0.0)) < 0)
    advancers = max(0, len(board_quotes) - decliners)
    heat = 6 if decliners >= 10 else (4 if decliners >= 5 else 2)
    set_context_risk_heat(heat)

    # 3-Column Tactical Command Board ([1.1, 2.2, 1.1])
    col_left, col_center, col_right = st.columns([1.1, 2.2, 1.1], gap="medium")

    with col_left:
        _render_tactical_card(TACTICAL_BOARD_GROUPS["left_top"], board_quotes, variant="cyan")
        _render_tactical_card(TACTICAL_BOARD_GROUPS["left_bottom"], board_quotes, variant="magenta")

    label_to_sym = {lbl: sym for lbl, sym in TACTICAL_BOARD_TICKERS}
    board_labels = list(label_to_sym.keys())

    with col_center:
        st.markdown('<div class="tactical-center-shell">', unsafe_allow_html=True)
        sel_c1, sel_c2 = st.columns([3.5, 1], gap="small")
        with sel_c1:
            selected_label = st.selectbox(
                "Active Tactical Target:",
                board_labels,
                index=board_labels.index("RELIANCE"),
                key="market_board_center_stock",
                label_visibility="collapsed",
            )
        with sel_c2:
            if st.button("🔄 Sync", key="board_sync_btn", width="stretch"):
                clear_market_cache()
                st.toast("Market feed cache cleared — pulled fresh NSE bars!", icon="🔄")
                st.rerun()

        center_sym = label_to_sym[selected_label]
        center_metrics, center_err = get_stock_analysis(center_sym)
        if center_metrics and not center_metrics["df"].empty:
            pred_df, r2_score = predict_stock_prices(center_metrics["df"], days=30)
            fig_center = _build_tactical_center_chart(
                df=center_metrics["df"],
                pred_df=pred_df,
                label=selected_label,
                symbol=center_sym,
                doomsday=doomsday,
            )
            st.plotly_chart(fig_center, width="stretch", config={"displayModeBar": False})
        else:
            r2_score = 0.0
            pred_df = pd.DataFrame()
            st.warning(f"Chart telemetry paused for {selected_label}: {center_err or 'No data'}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        _render_tactical_card(TACTICAL_BOARD_GROUPS["right_top"], board_quotes, variant="cyan")
        _render_tactical_card(TACTICAL_BOARD_GROUPS["right_bottom"], board_quotes, variant="magenta")

    # Bottom Tactical Status Strip
    wanted_stars = compute_dynamic_wanted_stars()
    stars_html = render_wanted_stars_html(active_stars=wanted_stars, total_stars=6)
    center_close = float(center_metrics["close"]) if center_metrics else 0.0
    center_chg = float(center_metrics["day_change_pct"]) if center_metrics else 0.0
    center_sig = str(center_metrics["signal"]) if center_metrics else "HOLD"
    center_rsi = float(center_metrics["rsi"]) if center_metrics else 50.0
    ml_target = (
        float(pred_df["Predicted_Close"].iloc[-1])
        if not pred_df.empty
        else center_close
    )
    accent_main = "#39ff14" if doomsday else "#00f5d4"
    accent_alt = "#ff4500" if doomsday else "#ff2a85"
    risk_badge_title = "☢️ DEFCON-1 ALERT" if doomsday else "🚨 WANTED LEVEL"

    st.markdown(
        f'<div class="tactical-status-strip">'
        f'<div class="tactical-status-card">'
        f'<span style="font-family:\'Orbitron\',sans-serif; font-size:0.68rem; color:{accent_main};">🎯 ACTIVE CENTER TARGET</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:1.15rem; font-weight:700; color:#f8fafc;">'
        f'{html.escape(selected_label)} · ₹{center_close:,.2f}</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; color:{"#39ff14" if center_chg >= 0 else "#ff4d6d"};">'
        f'{center_chg:+.2f}% INTRADAY</span>'
        f"</div>"
        f'<div class="tactical-status-card">'
        f'<span style="font-family:\'Orbitron\',sans-serif; font-size:0.68rem; color:{accent_alt};">🤖 SIGNAL & 30D ML TARGET</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:1.15rem; font-weight:700; color:#f8fafc;">'
        f'{html.escape(center_sig)} · ₹{ml_target:,.0f}</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; color:#cbd5e1;">'
        f'RSI {center_rsi:.1f} · ML R² {r2_score:.2f}</span>'
        f"</div>"
        f'<div class="tactical-status-card">'
        f'<span style="font-family:\'Orbitron\',sans-serif; font-size:0.68rem; color:{accent_main};">📡 WATCHLIST BREADTH (16)</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:1.15rem; font-weight:700; color:#39ff14;">'
        f'{advancers} GAINERS / {decliners} LOSERS</span>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.78rem; color:#cbd5e1;">'
        f'BATCHED CACHED NSE FEED (TTL 300s)</span>'
        f"</div>"
        f'<div class="tactical-status-card tactical-status-wanted">'
        f'<span style="font-family:\'Orbitron\',sans-serif; font-size:0.72rem; font-weight:800; color:{"#ff4500" if doomsday else "#fee440"};">'
        f'{risk_badge_title}</span>'
        f'<div>{stars_html}</div>'
        f'<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.74rem; color:#f8fafc;">'
        f'RISK HEAT: TIER {wanted_stars} / 6</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Collapsible Full NSE Watchlist Table & Sector Turf Map
    with st.expander("📋 Expand Full NSE Watchlist Table & Sector Turf Map", expanded=False):
        stock_count = st.slider(
            "Select number of NSE watchlist targets to scan:",
            min_value=5,
            max_value=50,
            value=15,
            step=5,
        )
        selected_items = tuple(list(NSE_STOCKS.items())[:stock_count])
        overview_data = fetch_batch_overview(selected_items)

        if not overview_data:
            st.warning("Unable to load extended NSE screener right now.")
        else:
            df_ov = pd.DataFrame(overview_data)
            if "Sector" not in df_ov.columns:
                df_ov["Sector"] = "Broad Market"

            col_f1, col_f2 = st.columns([2, 1.5])
            with col_f1:
                filter_choice = st.radio(
                    "Filter Feed by Signal:",
                    ["All", "BUY Only", "SELL Only", "HOLD Only"],
                    horizontal=True,
                )
            with col_f2:
                search_query = st.text_input(
                    "Quick Target Search (Company or Symbol):",
                    placeholder="e.g. TCS, Reliance, Bank...",
                ).strip().lower()

            df_filtered = df_ov.copy()
            if filter_choice == "BUY Only":
                df_filtered = df_filtered[df_filtered["Signal"] == "BUY"]
            elif filter_choice == "SELL Only":
                df_filtered = df_filtered[df_filtered["Signal"] == "SELL"]
            elif filter_choice == "HOLD Only":
                df_filtered = df_filtered[df_filtered["Signal"] == "HOLD"]

            if search_query:
                mask = (
                    df_filtered["Company Name"].str.lower().str.contains(search_query, na=False, regex=False)
                    | df_filtered["Symbol"].str.lower().str.contains(search_query, na=False, regex=False)
                )
                df_filtered = df_filtered[mask]

            if df_filtered.empty:
                st.info("No targets match the selected signal filter or search query.")
            else:
                st.dataframe(
                    df_filtered,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Price": st.column_config.NumberColumn(format="₹%.2f"),
                        "Change %": st.column_config.NumberColumn(format="%.2f%%"),
                        "RSI": st.column_config.NumberColumn(format="%.2f"),
                        "SMA 50": st.column_config.NumberColumn(format="₹%.2f"),
                        "Confidence": st.column_config.ProgressColumn(
                            "Confidence", format="%d%%", min_value=0, max_value=100
                        ),
                    },
                )

            st.markdown("---")
            st.subheader(
                "☢️ Fallout Sector Risk Treemap" if doomsday else "🗺️ Leonida Sector Turf Map (BAWSAQ Heat Treemap)"
            )
            treemap_df = df_ov.copy()
            treemap_df["TurfWeight"] = treemap_df["Confidence"].clip(lower=20)
            tree_scale = ["#ff2a00", "#1f120b", "#39ff14"] if doomsday else ["#ff2a85", "#1b0b3a", "#00f5d4"]
            fig_tree = px.treemap(
                treemap_df,
                path=[px.Constant("DEFCON SECTOR GRID" if doomsday else "NSE LEONIDA TURF"), "Sector", "Symbol"],
                values="TurfWeight",
                color="Change %",
                color_continuous_scale=tree_scale,
                color_continuous_midpoint=0.0,
                hover_data={
                    "Company Name": True,
                    "Price": ":₹,.2f",
                    "Change %": ":+.2f%",
                    "RSI": ":.1f",
                    "Signal": True,
                    "Confidence": True,
                },
            )
            style_plotly_figure(
                fig_tree,
                height=420,
                title="DEFCON SECTOR DIAGNOSTICS" if doomsday else "SECTOR CONTROL MAP (CYAN = GAIN // PINK = SELLOFF)",
            )
            fig_tree.update_traces(
                textinfo="label+text",
                texttemplate="<b>%{label}</b><br>%{customdata[2]:+.2f}%",
                marker=dict(line=dict(width=1.5, color="#090314")),
            )
            fig_tree.update_layout(hovermode="closest")
            st.plotly_chart(fig_tree, width="stretch", config={"displayModeBar": False})

    flash_headlines = [
        f"{'☢️' if q['change_pct'] < 0 else '⚡'} {q['label']} @ ₹{q['close']:,.2f} ({q['change_pct']:+.2f}% · RNG {q['range_pct']:.2f}%)"
        for q in board_quotes.values()
        if abs(float(q.get("change_pct", 0.0))) >= 0.01
    ][:8]
    if not flash_headlines and center_metrics:
        flash_headlines = [
            f"🎯 {selected_label} ({center_sig}) @ ₹{center_close:,.2f} ({center_chg:+.2f}%) · RSI {center_rsi:.1f}"
        ]
    render_weazel_flash_ticker(flash_headlines)
