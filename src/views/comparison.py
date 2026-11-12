"""Module 3: Two-Stock Technical Comparison Engine (BAWSAQ vs LCN Turf War)."""

from __future__ import annotations

import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.constants import NSE_STOCKS
from src.services.market_data import get_stock_analysis
from src.styles import render_page_header, render_signal_badge, style_plotly_figure


def _render_stock_summary_card(name: str, metrics: dict, corner_tag: str) -> None:
    """Render a neon Vice City comparison summary card for one stock."""
    badge = render_signal_badge(metrics["signal"], metrics["confidence"])
    delta_color = "#39ff14" if metrics["day_change_pct"] >= 0 else "#ff2a6d"
    st.markdown(
        f'<div class="surface-card">'
        f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; color:#ff2a85; letter-spacing:0.08em; margin-bottom:0.25rem;">'
        f"{html.escape(corner_tag)}"
        f"</div>"
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
        f'<div><strong style="font-family:\'Orbitron\',sans-serif; font-size:1.05rem;">{html.escape(name)}</strong>'
        f'<div style="font-family:\'Share Tech Mono\',monospace; color:#00f0ff; font-size:0.8rem;">{html.escape(metrics["symbol"])}</div></div>'
        f"{badge}"
        f"</div>"
        f'<div style="margin-top:0.75rem; font-family:\'Share Tech Mono\',monospace; font-size:1.5rem; font-weight:700; font-variant-numeric:tabular-nums;">'
        f'₹{metrics["close"]:,.2f} '
        f'<span style="font-size:0.92rem; color:{delta_color};">({metrics["day_change_pct"]:+.2f}%)</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_stock_comparison() -> None:
    """Render head-to-head BAWSAQ vs LCN stock metrics and normalized cumulative returns."""
    render_page_header(
        title="BAWSAQ vs LCN // Turf War Comparison",
        subtitle="Head-to-head Vice City benchmark of RSI, SMA vectors, and 1-year normalized returns",
        badge="BAWSAQ & LCN • SYNDICATE DUEL",
        wanted_stars=3,
    )

    stock_names = list(NSE_STOCKS.keys())
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        s1_name = st.selectbox("CORNER 1 (BAWSAQ):", stock_names, index=0, key="comp_stock_1")
        s1_sym = NSE_STOCKS[s1_name]
    with col_c2:
        s2_name = st.selectbox("CORNER 2 (LCN):", stock_names, index=1, key="comp_stock_2")
        s2_sym = NSE_STOCKS[s2_name]

    if s1_name == s2_name:
        st.warning("Select two different targets to initiate a BAWSAQ vs LCN turf comparison.")
        return

    with st.spinner("Running BAWSAQ vs LCN head-to-head telemetry scan..."):
        m1, e1 = get_stock_analysis(s1_sym)
        m2, e2 = get_stock_analysis(s2_sym)

    if e1 or e2:
        st.error(f"Error fetching data: {e1 or e2}")
        return

    if not (m1 and m2):
        return

    card_c1, card_c2 = st.columns(2)
    with card_c1:
        _render_stock_summary_card(s1_name, m1, "▸▸ CHALLENGER 01 // BAWSAQ FEED")
    with card_c2:
        _render_stock_summary_card(s2_name, m2, "▸▸ CHALLENGER 02 // LCN FEED")

    comp_table = {
        "Telemetry Metric": [
            "Current Price",
            "Day Change (%)",
            "52-Week High",
            "52-Week Low",
            "RSI (14)",
            "50-Day SMA",
            "200-Day SMA",
            "AI Signal",
            "Confidence Score",
        ],
        s1_name: [
            f"₹{m1['close']:,.2f}",
            f"{m1['day_change_pct']:+.2f}%",
            f"₹{m1['high_52w']:,.2f}",
            f"₹{m1['low_52w']:,.2f}",
            f"{m1['rsi']:.1f}",
            f"₹{m1['sma50']:,.2f}",
            f"₹{m1['sma200']:,.2f}",
            m1["signal"],
            f"{m1['confidence']}%",
        ],
        s2_name: [
            f"₹{m2['close']:,.2f}",
            f"{m2['day_change_pct']:+.2f}%",
            f"₹{m2['high_52w']:,.2f}",
            f"₹{m2['low_52w']:,.2f}",
            f"{m2['rsi']:.1f}",
            f"₹{m2['sma50']:,.2f}",
            f"₹{m2['sma200']:,.2f}",
            m2["signal"],
            f"{m2['confidence']}%",
        ],
    }

    st.subheader("📋 BAWSAQ vs LCN Comparative Matrix")
    st.dataframe(pd.DataFrame(comp_table), width="stretch", hide_index=True)

    st.subheader("📈 1-Year Normalized Percentage Return Turf War")
    close1 = m1["df"]["Close"]
    close2 = m2["df"]["Close"]
    common_idx = close1.index.intersection(close2.index)

    if len(common_idx) < 2:
        st.warning("Insufficient overlapping trading dates to plot normalized comparison.")
        return

    aligned1 = close1.loc[common_idx]
    aligned2 = close2.loc[common_idx]
    norm1 = ((aligned1 / aligned1.iloc[0]) - 1) * 100
    norm2 = ((aligned2 / aligned2.iloc[0]) - 1) * 100

    fig_comp = go.Figure()
    fig_comp.add_trace(
        go.Scatter(
            x=norm1.index,
            y=norm1,
            mode="lines",
            name=f"{s1_name} ({norm1.iloc[-1]:+.1f}%)",
            line=dict(color="#00f0ff", width=2.4),
        )
    )
    fig_comp.add_trace(
        go.Scatter(
            x=norm2.index,
            y=norm2,
            mode="lines",
            name=f"{s2_name} ({norm2.iloc[-1]:+.1f}%)",
            line=dict(color="#ff2a85", width=2.4),
        )
    )
    fig_comp.add_hline(y=0, line_dash="dot", line_color="rgba(255, 230, 0, 0.45)")
    style_plotly_figure(fig_comp, height=460, title="CUMULATIVE RETURN TURF WAR (%)")
    fig_comp.update_yaxes(title_text="Return (%)")
    st.plotly_chart(fig_comp, width="stretch")
