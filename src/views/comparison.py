"""Module 3: Two-Stock Technical Comparison Engine (BAWSAQ vs LCN Turf War)."""

from __future__ import annotations

import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.constants import NSE_STOCKS
from src.services.market_data import get_stock_analysis
from src.state import (
    compute_dynamic_wanted_stars,
    is_default_theme,
    is_doomsday,
    set_context_risk_heat,
)
from src.styles import render_page_header, render_signal_badge, render_wanted_stars_html, style_plotly_figure


def _compute_race_scores(metrics: dict) -> dict[str, int]:
    """Compute normalized 0-100 Street Race scores for RSI, SMA50 trend, and AI confidence."""
    rsi = float(metrics.get("rsi", 50.0))
    close = float(metrics.get("close", 1.0))
    sma50 = float(metrics.get("sma50", close)) or close
    conf = int(metrics.get("confidence", 65))
    sig = str(metrics.get("signal", "HOLD")).upper()

    rsi_score = int(round(max(15.0, min(100.0, 100.0 - abs(rsi - 52.0) * 1.45))))
    sma_pct = ((close / sma50) - 1.0) * 100.0
    sma_score = int(round(max(15.0, min(100.0, 52.0 + sma_pct * 4.2))))
    if sig == "BUY":
        ai_score = min(100, conf + 8)
    elif sig == "SELL":
        ai_score = max(18, conf - 25)
    else:
        ai_score = conf

    overall = int(round((rsi_score * 0.30) + (sma_score * 0.35) + (ai_score * 0.35)))
    return {"rsi": rsi_score, "sma": sma_score, "ai": ai_score, "overall": overall}


def _render_street_race_arena(name1: str, m1: dict, name2: str, m2: dict) -> None:
    """Render animated segmented racing bars (Cyan/Pink in GTA VI or Green/Red in Doomsday)."""
    doomsday = is_doomsday()
    c1_color = "#39ff14" if doomsday else "#00f5d4"
    c2_color = "#ff4500" if doomsday else "#ff2a85"
    s1 = _compute_race_scores(m1)
    s2 = _compute_race_scores(m2)
    if s1["overall"] >= s2["overall"]:
        winner_label = f"🏆 WINNER: TEAM {m1['symbol'].replace('.NS', '').replace('.BO', '')} ({s1['overall']} PTS)"
    else:
        winner_label = f"🏆 WINNER: TEAM {m2['symbol'].replace('.NS', '').replace('.BO', '')} ({s2['overall']} PTS)"

    t1 = html.escape(name1.split("(")[0].strip())
    t2 = html.escape(name2.split("(")[0].strip())

    def _bar_pair(title: str, v1: int, v2: int, detail1: str, detail2: str) -> str:
        return (
            f'<div class="race-metric-block">'
            f'<div style="display:flex; justify-content:space-between; font-family:\'Orbitron\',sans-serif; font-size:0.74rem; color:#fee440; margin-bottom:0.2rem;">'
            f'<span>▸ {html.escape(title)}</span>'
            f'<span style="font-family:\'Share Tech Mono\',monospace; color:#cbd5e1;">'
            f'<span style="color:{c1_color};">{t1}: {detail1}</span> &nbsp;|&nbsp; <span style="color:{c2_color};">{t2}: {detail2}</span>'
            f"</span></div>"
            f'<div class="race-track"><div class="race-fill-cyan" style="width:{v1}%;"></div></div>'
            f'<div class="race-track"><div class="race-fill-pink" style="width:{v2}%;"></div></div>'
            f"</div>"
        )

    bars_html = (
        _bar_pair("OVERALL COMPOSITE SCORE", s1["overall"], s2["overall"], f"{s1['overall']}/100", f"{s2['overall']}/100")
        + _bar_pair("RSI MOMENTUM HEALTH", s1["rsi"], s2["rsi"], f"RSI {m1['rsi']:.1f} ({s1['rsi']} pts)", f"RSI {m2['rsi']:.1f} ({s2['rsi']} pts)")
        + _bar_pair("50-SMA TREND VECTOR", s1["sma"], s2["sma"], f"₹{m1['sma50']:,.0f} ({s1['sma']} pts)", f"₹{m2['sma50']:,.0f} ({s2['sma']} pts)")
        + _bar_pair("AI SIGNAL CONFIDENCE", s1["ai"], s2["ai"], f"{m1['signal']} {m1['confidence']}%", f"{m2['signal']} {m2['confidence']}%")
    )

    arena_sub = (
        "TACTICAL WAR SIMULATION // TOXIC GREEN VS WAR AMBER"
        if doomsday
        else "STREET RACE MODE: ACTIVE // CYAN VS HOT PINK"
    )
    arena_title = "⚔️ TACTICAL WAR SIMULATION" if doomsday else "🏁 HEAD-TO-HEAD STREET RACE"

    st.markdown(
        f'<div class="street-race-board">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.6rem; margin-bottom:0.85rem;">'
        f'<div><span style="font-family:\'Share Tech Mono\',monospace; color:{c1_color}; font-size:0.72rem; letter-spacing:0.08em;">'
        f"{arena_sub}</span>"
        f'<h3 style="margin:0.1rem 0 0 0; font-family:\'Orbitron\',sans-serif; color:#ffffff;">{arena_title}</h3></div>'
        f'<span class="race-winner-pill">{html.escape(winner_label)}</span>'
        f"</div>"
        f"{bars_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_stock_summary_card(name: str, metrics: dict, corner_tag: str) -> None:
    """Render a theme-adaptive comparison summary card."""
    default_pro = is_default_theme()
    badge = render_signal_badge(metrics["signal"], metrics["confidence"])
    delta_color = (
        ("#10b981" if metrics["day_change_pct"] >= 0 else "#ef4444")
        if default_pro
        else ("#39ff14" if metrics["day_change_pct"] >= 0 else "#ff2a6d")
    )
    abs_chg = abs(float(metrics["day_change_pct"]))
    heat_stars = 6 if abs_chg >= 3 else (4 if abs_chg >= 1.5 else 2)
    stars_html = "" if default_pro else render_wanted_stars_html(active_stars=heat_stars, total_stars=6)
    tag_color = "#3b82f6" if default_pro else "#ff2a85"
    sym_color = "#10b981" if default_pro else "#00f5d4"
    title_font = "" if default_pro else "font-family:'Orbitron',sans-serif; "
    st.markdown(
        f'<div class="surface-card">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.35rem;">'
        f'<span style="font-size:0.74rem; font-weight:700; color:{tag_color}; letter-spacing:0.05em;">'
        f"{html.escape(corner_tag)}</span>"
        f"{stars_html}"
        f"</div>"
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
        f'<div><strong style="{title_font}font-size:1.05rem;">{html.escape(name)}</strong>'
        f'<div style="color:{sym_color}; font-size:0.82rem;">{html.escape(metrics["symbol"])}</div></div>'
        f"{badge}"
        f"</div>"
        f'<div style="margin-top:0.75rem; font-size:1.5rem; font-weight:700; font-variant-numeric:tabular-nums;">'
        f'₹{metrics["close"]:,.2f} '
        f'<span style="font-size:0.92rem; color:{delta_color};">({metrics["day_change_pct"]:+.2f}%)</span>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_stock_comparison() -> None:
    """Render theme-adaptive two-stock comparison benchmark, metrics table, and cumulative return plot."""
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    if default_pro:
        hdr_title = "Stock Comparison Engine"
        hdr_sub = "Side-by-side NSE equity benchmark comparing RSI momentum, SMA trend vectors, and 1-year cumulative returns"
        hdr_badge = "EQUITY BENCHMARK • PRO STANDARD"
        lbl1, lbl2 = "Select First Stock:", "Select Second Stock:"
    elif doomsday:
        hdr_title = "DEFCON DUEL // Tactical War Simulation"
        hdr_sub = "Side-by-side survival benchmark comparing RSI stability, SMA vector & AI confidence"
        hdr_badge = "TACTICAL WAR SIMULATION • BUNKER DUEL"
        lbl1, lbl2 = "SECTOR UNIT 1 (ALPHA):", "SECTOR UNIT 2 (OMEGA):"
    else:
        hdr_title = "BAWSAQ vs LCN // Head-to-Head Street Race"
        hdr_sub = "Animated Cyan vs. Hot Pink segmented racing bars comparing RSI, SMA, and AI confidence"
        hdr_badge = "STREET RACE MODE • SYNDICATE DUEL"
        lbl1, lbl2 = "CORNER 1 (BAWSAQ):", "CORNER 2 (LCN):"

    render_page_header(
        title=hdr_title,
        subtitle=hdr_sub,
        badge=hdr_badge,
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    stock_names = list(NSE_STOCKS.keys())
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        s1_name = st.selectbox(lbl1, stock_names, index=0, key="comp_stock_1")
        s1_sym = NSE_STOCKS[s1_name]
    with col_c2:
        s2_name = st.selectbox(lbl2, stock_names, index=1, key="comp_stock_2")
        s2_sym = NSE_STOCKS[s2_name]

    if s1_name == s2_name:
        if default_pro:
            st.warning("Select two different equities to compare performance and technical indicators.")
        elif doomsday:
            st.warning("Select two different sector assets to run a tactical war simulation.")
        else:
            st.warning("Select two different targets to initiate a BAWSAQ vs LCN turf comparison.")
        return

    spin_txt = (
        "Loading comparative technical and return metrics..."
        if default_pro
        else (
            "Running Bunker Tactical head-to-head telemetry scan..."
            if doomsday
            else "Running BAWSAQ vs LCN head-to-head telemetry scan..."
        )
    )
    with st.spinner(spin_txt):
        m1, e1 = get_stock_analysis(s1_sym)
        m2, e2 = get_stock_analysis(s2_sym)

    if e1 or e2:
        st.error(f"Error fetching data: {e1 or e2}")
        return

    if not (m1 and m2):
        return

    max_chg = max(abs(float(m1["day_change_pct"])), abs(float(m2["day_change_pct"])))
    set_context_risk_heat(5 if max_chg >= 2.5 else (3 if max_chg >= 1.0 else 2))

    if default_pro:
        s1 = _compute_race_scores(m1)
        s2 = _compute_race_scores(m2)
        win_sym = m1["symbol"].replace(".NS", "") if s1["overall"] >= s2["overall"] else m2["symbol"].replace(".NS", "")
        win_pts = max(s1["overall"], s2["overall"])
        st.markdown(
            f'<div class="street-race-board">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.6rem;">'
            f'<div><span style="color:#94a3b8; font-size:0.74rem; font-weight:600; text-transform:uppercase;">Composite Technical Score</span>'
            f'<h3 style="margin:0.1rem 0 0 0; font-size:1.15rem; font-weight:700; color:#f8fafc;">Side-by-Side Technical Benchmark</h3></div>'
            f'<span class="race-winner-pill">Leader: {html.escape(win_sym)} ({win_pts}/100)</span>'
            f"</div></div>",
            unsafe_allow_html=True,
        )
    else:
        _render_street_race_arena(s1_name, m1, s2_name, m2)

    card_c1, card_c2 = st.columns(2)
    with card_c1:
        tag1 = (
            "EQUITY 01"
            if default_pro
            else ("▸▸ UNIT 01 // BUNKER ALPHA" if doomsday else "▸▸ CHALLENGER 01 // BAWSAQ FEED")
        )
        _render_stock_summary_card(s1_name, m1, tag1)
    with card_c2:
        tag2 = (
            "EQUITY 02"
            if default_pro
            else ("▸▸ UNIT 02 // SECTOR OMEGA" if doomsday else "▸▸ CHALLENGER 02 // LCN FEED")
        )
        _render_stock_summary_card(s2_name, m2, tag2)

    metric_col = "Financial Metric" if default_pro else "Telemetry Metric"
    comp_table = {
        metric_col: [
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

    matrix_hdr = (
        "Comparative Financial & Technical Matrix"
        if default_pro
        else ("📋 Bunker Tactical Comparative Matrix" if doomsday else "📋 BAWSAQ vs LCN Comparative Matrix")
    )
    st.subheader(matrix_hdr)
    st.dataframe(pd.DataFrame(comp_table), width="stretch", hide_index=True)

    ret_hdr = (
        "1-Year Normalized Cumulative Return (%)"
        if default_pro
        else ("📈 1-Year Bunker Sector Survival Return (%)" if doomsday else "📈 1-Year Normalized Percentage Return Turf War")
    )
    st.subheader(ret_hdr)
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

    line1_col = "#10b981" if default_pro else ("#39ff14" if doomsday else "#00f0ff")
    line2_col = "#3b82f6" if default_pro else ("#ff4500" if doomsday else "#ff2a85")
    zero_col = "rgba(148, 163, 184, 0.35)" if default_pro else ("rgba(255, 183, 3, 0.45)" if doomsday else "rgba(255, 230, 0, 0.45)")
    chart_title = (
        "1-Year Cumulative Return Comparison (%)"
        if default_pro
        else ("BUNKER SECTOR SURVIVAL RETURN (%)" if doomsday else "CUMULATIVE RETURN TURF WAR (%)")
    )

    fig_comp = go.Figure()
    fig_comp.add_trace(
        go.Scatter(
            x=norm1.index,
            y=norm1,
            mode="lines",
            name=f"{s1_name} ({norm1.iloc[-1]:+.1f}%)",
            line=dict(color=line1_col, width=2.4),
        )
    )
    fig_comp.add_trace(
        go.Scatter(
            x=norm2.index,
            y=norm2,
            mode="lines",
            name=f"{s2_name} ({norm2.iloc[-1]:+.1f}%)",
            line=dict(color=line2_col, width=2.4),
        )
    )
    fig_comp.add_hline(y=0, line_dash="dot", line_color=zero_col)
    style_plotly_figure(fig_comp, height=460, title=chart_title)
    fig_comp.update_yaxes(title_text="Return (%)")
    st.plotly_chart(fig_comp, width="stretch", config={"displayModeBar": False})
