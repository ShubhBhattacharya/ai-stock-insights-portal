"""Module 5: Dynamic Portfolio Risk & Correlation Analyzer (Syndicate Heat Matrix)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.constants import NSE_STOCKS, RISK_FREE_RATE_PCT
from src.services.market_data import fetch_batch_returns
from src.styles import render_kpi_grid, render_page_header, render_wanted_stars_html, style_plotly_figure


def render_risk_optimizer() -> None:
    """Render portfolio volatility, Sharpe ratio, and synthwave correlation heatmap."""
    render_page_header(
        title="Syndicate Heat // Portfolio Risk Matrix",
        subtitle="Quantify multi-stock annualized volatility, Sharpe ratio, and Wanted-level heat",
        badge="WANTED HEAT & QUANT ENGINE",
        wanted_stars=6,
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
            "LOW STREET HEAT PROFILE",
            "#39ff14",
            "Smooth volatility — ideal for armored capital preservation.",
        )
    elif port_volatility < 28:
        heat_stars, heat_label, heat_color, heat_msg = (
            4,
            "MODERATE HEAT PROFILE",
            "#fee440",
            "Balanced risk-reward street mix.",
        )
    else:
        heat_stars, heat_label, heat_color, heat_msg = (
            6,
            "MAX WANTED HEAT PROFILE",
            "#ff2a6d",
            "Aggressive high-volatility basket; watch for sharp drawdowns!",
        )

    st.markdown(
        f'<div class="surface-card" style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:0.75rem; border-color:{heat_color};">'
        f'<div><strong style="font-family:\'Orbitron\',sans-serif; color:{heat_color};">{heat_label}</strong>'
        f'<div style="font-family:\'Share Tech Mono\',monospace; color:#e2e8f0; font-size:0.86rem; margin-top:0.2rem;">{heat_msg}</div></div>'
        f"{render_wanted_stars_html(active_stars=heat_stars, total_stars=6)}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col_heat, col_table = st.columns([3, 2])

    with col_heat:
        st.subheader("🔥 Synthwave Asset Correlation Heatmap")
        corr_df = returns_df.corr()
        fig_corr = px.imshow(
            corr_df,
            text_auto=".2f",
            aspect="auto",
            zmin=-1.0,
            zmax=1.0,
            color_continuous_scale=["#ff2a85", "#14082d", "#00f0ff"],
            title="CROSS-ASSET RETURN CORRELATION (-1 TO +1)",
        )
        style_plotly_figure(fig_corr, height=450)
        fig_corr.update_layout(hovermode="closest")
        st.plotly_chart(fig_corr, width="stretch")

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
