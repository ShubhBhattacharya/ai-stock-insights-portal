"""Module 1: Real-Time NSE Market Overview (BAWSAQ & LCN Vice Market Scanner)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.constants import NSE_STOCKS
from src.services.market_data import clear_market_cache, fetch_batch_overview
from src.state import compute_dynamic_wanted_stars, set_context_risk_heat
from src.styles import (
    render_kpi_grid,
    render_page_header,
    render_weazel_flash_ticker,
    style_plotly_figure,
)


def render_market_overview() -> None:
    """Render concurrent multi-stock BAWSAQ / LCN heist board with Sector Turf Map & Weazel Flash."""
    wanted_stars = compute_dynamic_wanted_stars()
    render_page_header(
        title="BAWSAQ / LCN — LIVE NSE HEIST BOARD",
        subtitle="Real-time Leonida scanner of NSE equities, Sector Turf Map, and neon BUY/SELL triggers",
        badge="BAWSAQ / LCN • LIVE NSE HEIST BOARD",
        wanted_stars=wanted_stars,
    )

    st.markdown(
        '<div class="console-hud-ruler">'
        "<span>FEED: BAWSAQ // LCN EQUITY RELAY</span>"
        "<span>UPTIME: 99.9% · MULTI-THREAD SCANNER</span>"
        "<span>SECTOR: NSE INDIA</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        stock_count = st.slider(
            "Select number of BAWSAQ / NSE targets to scan:",
            min_value=5,
            max_value=50,
            value=15,
            step=5,
        )
    with col_ctrl2:
        st.markdown("<div style='height: 1.65rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", type="primary", width="stretch"):
            clear_market_cache()
            st.toast("BAWSAQ cache wiped — pulling fresh NSE quotes!", icon="🔄")

    selected_items = tuple(list(NSE_STOCKS.items())[:stock_count])

    with st.spinner(f"Scanning {stock_count} BAWSAQ / NSE Equities via cyber threads..."):
        overview_data = fetch_batch_overview(selected_items)

    if not overview_data:
        st.warning("Unable to load BAWSAQ / LCN market overview right now. Please try refreshing in a moment.")
        return

    df_ov = pd.DataFrame(overview_data)
    if "Sector" not in df_ov.columns:
        df_ov["Sector"] = "Broad Market"
    total_scanned = len(df_ov)
    buy_signals = int((df_ov["Signal"] == "BUY").sum())
    sell_signals = int((df_ov["Signal"] == "SELL").sum())
    hold_signals = int((df_ov["Signal"] == "HOLD").sum())
    heat = 6 if sell_signals >= max(3, total_scanned // 3) else (4 if sell_signals >= 1 else 2)
    set_context_risk_heat(heat)

    render_kpi_grid(
        [
            {"label": "BAWSAQ Targets", "value": str(total_scanned), "delta": "NSE Live Tickers", "tone": "neutral"},
            {
                "label": "🟢 BAWSAQ BUY",
                "value": str(buy_signals),
                "delta": f"{(buy_signals / total_scanned) * 100:.0f}% surge signal",
                "tone": "up",
            },
            {
                "label": "🔴 LCN SELL",
                "value": str(sell_signals),
                "delta": f"{(sell_signals / total_scanned) * 100:.0f}% heat warning",
                "tone": "down",
            },
            {
                "label": "🟡 STANDBY HOLD",
                "value": str(hold_signals),
                "delta": f"{(hold_signals / total_scanned) * 100:.0f}% neutral",
                "tone": "warn",
            },
        ]
    )

    col_f1, col_f2 = st.columns([2, 1.5])
    with col_f1:
        filter_choice = st.radio(
            "Filter BAWSAQ Feed by Signal:",
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
        st.info("No BAWSAQ / LCN targets match the selected signal filter or search query.")
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
    st.subheader("🗺️ Leonida Sector Turf Map (BAWSAQ Heat Treemap)")
    treemap_df = df_ov.copy()
    treemap_df["TurfWeight"] = treemap_df["Confidence"].clip(lower=20)
    fig_tree = px.treemap(
        treemap_df,
        path=[px.Constant("NSE LEONIDA TURF"), "Sector", "Symbol"],
        values="TurfWeight",
        color="Change %",
        color_continuous_scale=["#ff2a85", "#1b0b3a", "#00f5d4"],
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
    style_plotly_figure(fig_tree, height=430, title="SECTOR CONTROL MAP (CYAN = GAIN // PINK = SELLOFF)")
    fig_tree.update_traces(
        textinfo="label+text",
        texttemplate="<b>%{label}</b><br>%{customdata[2]:+.2f}%",
        marker=dict(line=dict(width=1.5, color="#090314")),
    )
    fig_tree.update_layout(hovermode="closest")
    st.plotly_chart(fig_tree, width="stretch")

    strong_signals = df_ov[df_ov["Confidence"] >= 80]
    flash_headlines = [
        f"🚨 {row['Symbol']} ({row['Signal']} · {row['Confidence']}% CONF) @ ₹{row['Price']:,.2f} ({row['Change %']:+.2f}%) · RSI {row['RSI']:.1f}"
        for _, row in strong_signals.iterrows()
    ]
    render_weazel_flash_ticker(flash_headlines)
