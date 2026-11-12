"""AI Stock Insights Portal | NSE India — Streamlit Application Entry Point."""

from __future__ import annotations

import html
import streamlit as st

from src.constants import NAV_ITEMS
from src.state import init_session_state, logout
from src.styles import inject_global_styles
from src.views.ai_tutor import render_ai_tutor
from src.views.auth import render_login_page
from src.views.comparison import render_stock_comparison
from src.views.market_overview import render_market_overview
from src.views.paper_trading import render_paper_trading
from src.views.price_alerts import render_price_alerts
from src.views.risk_optimizer import render_risk_optimizer
from src.views.single_stock import render_single_stock_analysis
from src.views.synopsis import render_synopsis

st.set_page_config(
    page_title="AI Stock Insights Portal | NSE India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

VIEW_DISPATCH = {
    "📊 Market Overview": render_market_overview,
    "🤖 Single Stock AI & ML Prediction": render_single_stock_analysis,
    "⚖️ Two-Stock Comparison": render_stock_comparison,
    "💼 Virtual Paper Trading": render_paper_trading,
    "🎯 Portfolio Risk Optimizer": render_risk_optimizer,
    "🚨 Price Alerts": render_price_alerts,
    "🎓 AI Stock Tutor & Chatbot": render_ai_tutor,
    "📜 Project Synopsis & Credits": render_synopsis,
}


def render_sidebar() -> str:
    """Render branded sidebar profile card, navigation menu, and project info."""
    username = html.escape(str(st.session_state["username"]))
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])

    st.sidebar.markdown(
        f'<div class="sidebar-profile-card">'
        f'<div class="sidebar-profile-name">👤 {username}</div>'
        f'<div class="sidebar-cash-pill">💰 Cash: ₹{cash_balance:,.2f}</div>'
        f'<div style="color:#94a3b8; font-size:0.78rem; margin-top:0.25rem;">'
        f"📁 {num_holdings} Holdings · 🔔 {num_alerts} Alerts"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("🚪 Logout", width="stretch"):
        logout()
        st.rerun()

    st.sidebar.markdown("---")

    selected_mode = st.sidebar.radio(
        "Navigation",
        NAV_ITEMS,
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Project Info:**\n"
        "- Mini Project: BCC 351\n"
        "- Tech: Streamlit, yfinance, Plotly, pandas-ta\n"
        "- Market: NSE India"
    )
    return selected_mode


def main() -> None:
    """Bootstrap styles, session state, and route between auth and dashboard views."""
    inject_global_styles()
    init_session_state()

    if not st.session_state["authenticated"]:
        render_login_page()
        return

    selected_mode = render_sidebar()
    view_fn = VIEW_DISPATCH.get(selected_mode, render_market_overview)
    view_fn()


if __name__ == "__main__":
    main()
