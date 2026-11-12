"""Module 8: Academic Project Synopsis & Syndicate Credits."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.constants import TEAM_MEMBERS
from src.styles import render_page_header


def render_synopsis() -> None:
    """Render academic credentials, team members, 5-layer architecture, and disclaimer."""
    render_page_header(
        title="Vice Intel Dossier // Synopsis & Credits",
        subtitle="B.Tech. II Year III Semester Mini Project (BCC 351) | Dronacharya Group of Institutions",
        badge="CLASSIFIED PROJECT BRIEFING",
        wanted_stars=2,
    )

    col_cred, col_team = st.columns([1, 1.3])
    with col_cred:
        st.subheader("🎓 Mission Credentials")
        st.markdown(
            """
- **Course:** BCC 351 (Internship / Mini Project)
- **Institution:** Dronacharya Group of Institutions, Greater Noida
- **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow
- **Academic Session:** 2025–2026
"""
        )

    with col_team:
        st.subheader("🕶️ Syndicate Team Roster")
        st.dataframe(pd.DataFrame(TEAM_MEMBERS), width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("🏛️ 5-Layer Terminal Architecture")
    st.markdown(
        """
1. **Presentation Layer:** Vice City synthwave HUD built on Streamlit with glassmorphic steel-rivet cards, neon Plotly figures, and responsive grid layouts.
2. **Data-Access Layer:** Integrated with `yfinance` for 1Y NSE OHLCV feeds using `@st.cache_data` TTL caching and concurrent worker threads.
3. **Analytics Layer:** Uses `pandas-ta` to compute 14-period RSI, 50-day SMA, 200-day SMA, and Bollinger Bands.
4. **Decision Layer:** Executes transparent heuristic BUY / SELL / HOLD rules with confidence levels alongside Scikit-Learn linear trend forecasting.
5. **Visualisation Layer:** Employs `plotly.graph_objects` and `plotly.express` for interactive candlestick, volume, RSI, turf-war comparison, and correlation heatmaps.
"""
    )

    st.markdown("---")
    st.info(
        "⚠️ **Academic Disclaimer:** This software dashboard is developed strictly for educational "
        "and academic project purposes. Market data is obtained from public web APIs."
    )
