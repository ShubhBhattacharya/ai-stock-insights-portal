"""Module 8: Academic Project Synopsis & Credits."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.constants import TEAM_MEMBERS
from src.styles import render_page_header


def render_synopsis() -> None:
    """Render academic credentials, team members, 5-layer architecture, and disclaimer."""
    render_page_header(
        title="📜 Academic Project Synopsis & Architecture",
        subtitle="B.Tech. II Year III Semester Mini Project (BCC 351) | Dronacharya Group of Institutions",
        badge="PROJECT DOCUMENTATION",
    )

    col_cred, col_team = st.columns([1, 1.3])
    with col_cred:
        st.subheader("🎓 Project Credentials")
        st.markdown(
            """
- **Course:** BCC 351 (Internship / Mini Project)
- **Institution:** Dronacharya Group of Institutions, Greater Noida
- **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow
- **Academic Session:** 2025–2026
"""
        )

    with col_team:
        st.subheader("👥 Project Team Members")
        st.dataframe(pd.DataFrame(TEAM_MEMBERS), width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("🏛️ Software Architecture (5-Layer Design)")
    st.markdown(
        """
1. **Presentation Layer:** Built with Streamlit with responsive cards, tabs, forms, Plotly figures, and multi-mode navigation.
2. **Data-Access Layer:** Integrated with `yfinance` to retrieve historical daily OHLCV equity bars with caching (`@st.cache_data`) and concurrent batch execution.
3. **Analytics Layer:** Utilizes `pandas-ta` to calculate 14-period RSI, 50-day SMA, 200-day SMA, and Bollinger Bands.
4. **Decision Layer:** Executes rule-based heuristic logic to generate transparent BUY, SELL, or HOLD decisions with confidence scores alongside Scikit-Learn trend forecasting.
5. **Visualisation Layer:** Employs `plotly.graph_objects` and `plotly.express` to generate interactive multi-panel candlestick, volume, RSI, comparison, and correlation charts.
"""
    )

    st.markdown("---")
    st.info(
        "⚠️ **Academic Disclaimer:** This software dashboard is developed strictly for educational "
        "and academic project purposes. Market data is obtained from public web APIs."
    )
