"""Module 5: Dynamic Portfolio Risk & Correlation Analyzer (Syndicate Heat Matrix)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.constants import NSE_STOCKS, RISK_FREE_RATE_PCT
from src.services.market_data import fetch_batch_returns
from src.state import compute_dynamic_wanted_stars, is_doomsday, set_context_risk_heat
from src.styles import render_kpi_grid, render_page_header, render_wanted_stars_html, style_plotly_figure


def render_risk_optimizer() -> None:
    """Render portfolio volatility gauge meter, Sharpe ratio, and dual-world heatmap."""
    doomsday = is_doomsday()
    render_page_header(
        title=(
            "FALLOUT HEAT // Radiation & Risk Matrix"
            if doomsday
            else "Syndicate Heat // Portfolio Risk Matrix"
        ),
        subtitle=(
            "Quantify bunker basket annualized volatility meters, Sharpe ratio, and DEFCON radiation heat"
            if doomsday
            else "Quantify multi-stock annualized volatility meters, Sharpe ratio, and Wanted-level heat"
        ),
        badge=(
            "EMERGENCY RADIATION & QUANT ENGINE"
            if doomsday
            else "WANTED HEAT & QUANT ENGINE"
        ),
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    selected_stocks = st.multiselect(
        "Select Basket of BAWSAQ Equities to Analyze:",
        list(NSE_STOCKS.keys()),
        default=[
            "Reliance Industries",
            "Tata Consultancy Services (TCS)",
            "HDFC Bank",
            "Infosys",
        ],
    )

    if len(selected_stocks) < 2:
        st.warning("Select at least 2 equities to calculate syndicate portfolio heat and correlation.")
        return

    items = tuple((name, NSE_STOCKS[name]) for name in selected_stocks)

    with st.spinner("Calculating syndicate returns and covariance matrix..."):
        returns_dict = fetch_batch_returns(items)

    if len(returns_dict) < 2:
        st.error("Unable to retrieve sufficient historical data for at least 2 selected equities.")
        return

    returns_df = pd.DataFrame(returns_dict).dropna()
    if len(returns_df) < 15 or returns_df.shape[1] < 2:
        st.error("Insufficient overlapping trading history across the selected basket.")
        return

    num_assets = len(returns_df.columns)
    weights = np.ones(num_assets) / num_assets
    cov_matrix = returns_df.cov() * 252
    port_variance = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
    port_volatility = float(np.sqrt(max(port_variance, 0.0)) * 100)

    annual_returns = (returns_df.mean() * 252) * 100
    annual_vols = (returns_df.std() * np.sqrt(252)) * 100
    port_return = float(np.dot(weights, annual_returns))
    sharpe_ratio = (
        (port_return - RISK_FREE_RATE_PCT) / port_volatility if port_volatility > 0 else 0.0
    )

    vol_tone = "up" if port_volatility < 18 else ("warn" if port_volatility < 28 else "down")
    ret_tone = "up" if port_return >= RISK_FREE_RATE_PCT else "down"
    sharpe_tone = "up" if sharpe_ratio >= 1.0 else ("warn" if sharpe_ratio >= 0 else "down")

    render_kpi_grid(
        [
            {
                "label": "Annualized Volatility",
                "value": f"{port_volatility:.2f}%",
                "delta": f"{num_assets} equal-weight drops",
                "tone": vol_tone,
            },
            {
                "label": "Expected Annual Return",
                "value": f"{port_return:.2f}%",
                "delta": f"vs {RISK_FREE_RATE_PCT:.1f}% safe-house yield",
                "tone": ret_tone,
            },
            {
                "label": "Syndicate Sharpe Ratio",
                "value": f"{sharpe_ratio:.2f}",
                "delta": "Elite" if sharpe_ratio >= 1.0 else ("Moderate" if sharpe_ratio >= 0 else "Negative"),
                "tone": sharpe_tone,
            },
        ]
    )

    if port_volatility < 18:
        heat_stars, heat_label, heat_color, heat_msg = (
            2,
            "SECTOR CONTAINED // LOW RADIATION" if doomsday else "LOW STREET HEAT PROFILE",
            "#39ff14",
            (
                "Sub-threshold fallout volatility — ideal for armored bunker reserve preservation."
                if doomsday
                else "Smooth volatility — ideal for armored capital preservation."
            ),
        )
    elif port_volatility < 28:
        heat_stars, heat_label, heat_color, heat_msg = (
            4,
            "ELEVATED FALLOUT HEAT // DEFCON-2" if doomsday else "MODERATE HEAT PROFILE",
            "#ffb703" if doomsday else "#fee440",
            (
                "Tactical risk-reward bunker mix under shifting market shockwaves."
                if doomsday
                else "Balanced risk-reward street mix."
            ),
        )
    else:
        heat_stars, heat_label, heat_color, heat_msg = (
            6,
            "CRITICAL RADIATION SURGE // DEFCON-1" if doomsday else "MAX WANTED HEAT PROFILE",
            "#ff2a00" if doomsday else "#ff2a6d",
            (
                "Severe radiation drawdown exposure detected — reinforce hedges immediately!"
                if doomsday
                else "Aggressive high-volatility basket; watch for sharp drawdowns!"
            ),
        )

    set_context_risk_heat(heat_stars)

    heat_accent = "#39ff14" if doomsday else "#00f5d4"
    gauge_num_color = "#ff4500" if doomsday else "#fee440"
    gauge_bg = "rgba(18, 12, 8, 0.92)" if doomsday else "rgba(11, 5, 36, 0.85)"
    gauge_steps = (
        [
            {"range": [0, 18], "color": "rgba(57, 255, 20, 0.18)"},
            {"range": [18, 28], "color": "rgba(255, 183, 3, 0.22)"},
            {"range": [28, 45], "color": "rgba(255, 42, 0, 0.28)"},
        ]
        if doomsday
        else [
            {"range": [0, 18], "color": "rgba(0, 245, 212, 0.18)"},
            {"range": [18, 28], "color": "rgba(254, 228, 64, 0.20)"},
            {"range": [28, 45], "color": "rgba(255, 42, 133, 0.25)"},
        ]
    )
    corr_scale = ["#ff2a00", "#1b1008", "#39ff14"] if doomsday else ["#ff2a85", "#14082d", "#00f0ff"]

    col_heat_info, col_gauge = st.columns([1.4, 1])
    with col_heat_info:
        st.markdown(
            f'<div class="surface-card" style="display:flex; flex-direction:column; justify-content:space-between; gap:0.75rem; border-color:{heat_color}; min-height:220px;">'
            f'<div><strong style="font-family:\'Orbitron\',sans-serif; color:{heat_color}; font-size:1.05rem;">{heat_label}</strong>'
            f'<div style="font-family:\'Share Tech Mono\',monospace; color:#e2e8f0; font-size:0.88rem; margin-top:0.35rem;">{heat_msg}</div></div>'
            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
            f'<span style="font-family:\'Share Tech Mono\',monospace; color:{heat_accent}; font-size:0.82rem;">'
            f'{"RADIATION VOLATILITY" if doomsday else "PORTFOLIO HEAT"}: {port_volatility:.2f}% σ</span>'
            f"{render_wanted_stars_html(active_stars=heat_stars, total_stars=6)}"
            f"</div></div>",
            unsafe_allow_html=True,
        )
    with col_gauge:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=round(port_volatility, 2),
                number={"suffix": "%", "font": {"family": "Share Tech Mono, monospace", "color": gauge_num_color, "size": 28}},
                title={
                    "text": "RADIATION GAUGE" if doomsday else "VOLATILITY METER",
                    "font": {"family": "Orbitron, sans-serif", "color": heat_accent, "size": 13},
                },
                gauge={
                    "axis": {"range": [0, 45], "tickcolor": "#cbd5e1"},
                    "bar": {"color": heat_color},
                    "bgcolor": gauge_bg,
                    "borderwidth": 1.5,
                    "bordercolor": heat_accent,
                    "steps": gauge_steps,
                },
            )
        )
        style_plotly_figure(fig_gauge, height=235)
        fig_gauge.update_layout(margin={"l": 18, "r": 18, "t": 36, "b": 8})
        st.plotly_chart(fig_gauge, width="stretch", config={"displayModeBar": False})

    st.markdown("---")
    col_heat, col_table = st.columns([3, 2])

    with col_heat:
        st.subheader(
            "☢️ Bunker Sector Correlation Heatmap"
            if doomsday
            else "🔥 Synthwave Asset Correlation Heatmap"
        )
        corr_df = returns_df.corr()
        fig_corr = px.imshow(
            corr_df,
            text_auto=".2f",
            aspect="auto",
            zmin=-1.0,
            zmax=1.0,
            color_continuous_scale=corr_scale,
            title="CROSS-ASSET RETURN CORRELATION (-1 TO +1)",
        )
        style_plotly_figure(fig_corr, height=450)
        fig_corr.update_layout(hovermode="closest")
        st.plotly_chart(fig_corr, width="stretch", config={"displayModeBar": False})

    with col_table:
        st.subheader("📊 Per-Asset Breakdown")
        asset_summary = pd.DataFrame(
            {
                "Asset": returns_df.columns,
                "Weight %": [round(100.0 / num_assets, 1)] * num_assets,
                "Annual Return %": [round(float(annual_returns[c]), 2) for c in returns_df.columns],
                "Volatility %": [round(float(annual_vols[c]), 2) for c in returns_df.columns],
            }
        )
        st.dataframe(
            asset_summary,
            width="stretch",
            hide_index=True,
            column_config={
                "Weight %": st.column_config.NumberColumn(format="%.1f%%"),
                "Annual Return %": st.column_config.NumberColumn(format="%.2f%%"),
                "Volatility %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )
