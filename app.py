"""AI Stock Insights Portal | NSE India — GTA VI / Vice City Neon Edition Entry Point."""

from __future__ import annotations

import html
import time
import streamlit as st

from src.constants import NAV_ITEMS
from src.state import init_session_state, logout
from src.styles import (
    inject_global_styles,
    render_login_transition_overlay,
    render_sidebar_minimap_html,
    render_wanted_stars_html,
)
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
    page_title="AI Stock Insights Portal | GTA VI Leonida Terminal",
    page_icon="🌴",
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
    """Render Vice City HUD sidebar profile, navigation radio buttons, and bottom mini-map radar."""
    username = html.escape(str(st.session_state["username"]).upper())
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])
    wanted_level = min(6, max(1, 1 + num_holdings + num_alerts))
    wanted_html = render_wanted_stars_html(active_stars=wanted_level, total_stars=6)

    st.sidebar.markdown(
        f'<div class="sidebar-profile-card">'
        f'<div class="sidebar-profile-name">👤 WELCOME, {username}</div>'
        f'<div class="sidebar-cash-pill">💰 CASH: ₹{cash_balance:,.2f}</div>'
        f'<div style="margin:0.38rem 0;">{wanted_html}</div>'
        f'<div style="font-family:\'Share Tech Mono\',monospace; color:#cbd5e1; font-size:0.76rem;">'
        f"💼 {num_holdings} Drops · 🎯 {num_alerts} Wanted Bounties"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("🚪 JACK OUT / LOGOUT", width="stretch"):
        logout()
        st.rerun()

    st.sidebar.markdown("---")

    selected_mode = st.sidebar.radio(
        "🕹️ MODULE SELECTOR",
        NAV_ITEMS,
        index=0,
    )

    st.sidebar.markdown(render_sidebar_minimap_html(), unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**LEONIDA INTEL TERMINAL:**\n"
        "- Mission: BCC 351 Mini Project\n"
        "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
        "- Feed: NSE India (BAWSAQ / LCN)"
    )
    return selected_mode


def main() -> None:
    """Bootstrap Leonida synthwave styles, session state, login transition, and dashboard."""
    inject_global_styles()
    init_session_state()

    if not st.session_state["authenticated"]:
        render_login_page()
        return

    if st.session_state.get("transitioning"):
        render_login_transition_overlay(str(st.session_state["username"]))
        time.sleep(2.0)
        st.session_state["transitioning"] = False
        st.rerun()
        return

    selected_mode = render_sidebar()
    view_fn = VIEW_DISPATCH.get(selected_mode, render_market_overview)
    view_fn()


if __name__ == "__main__":
    main()
