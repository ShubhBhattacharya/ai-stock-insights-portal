"""AI Stock Insights Portal | NSE India — GTA VI / Vice City Neon Edition Entry Point."""

from __future__ import annotations

import html
from pathlib import Path
import sys
import time
import streamlit as st

_ROOT_DIR = str(Path(__file__).resolve().parent)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.constants import NAV_ITEMS
from src.state import compute_dynamic_wanted_stars, init_session_state, is_doomsday, logout
from src.styles import (
    inject_global_styles,
    render_doomsday_reboot_overlay,
    render_edition_toggle,
    render_login_transition_overlay,
    render_wanted_stars_html,
)
from src.views.ai_tutor import render_ai_tutor
from src.views.auth import render_login_page
from src.views.comparison import render_stock_comparison
from src.views.ifruit_widget import render_ifruit_phone_widget
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
    """Render clean edition-aware HUD sidebar profile, capital/cash, logout, and navigation."""
    doomsday = is_doomsday()
    username = html.escape(str(st.session_state["username"]).upper())
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])
    wanted_level = compute_dynamic_wanted_stars()
    wanted_html = render_wanted_stars_html(active_stars=wanted_level, total_stars=6)

    user_line = f"👤 AUTHORIZED USER: {username}" if doomsday else f"👤 WELCOME, {username}"
    cash_line = f"💰 WAR CAPITAL: ₹{cash_balance:,.2f}" if doomsday else f"💰 CASH: ₹{cash_balance:,.2f}"
    sub_counts = (
        f"🛡️ {num_holdings} Covert Assets · ☢️ {num_alerts} Alarms"
        if doomsday
        else f"💼 {num_holdings} Holdings · 🎯 {num_alerts} Alerts"
    )
    logout_label = "🚪 EVACUATE SHELTER / LOGOUT" if doomsday else "🚪 JACK OUT / LOGOUT"

    st.sidebar.markdown(
        f'<div class="sidebar-profile-card">'
        f'<div class="sidebar-profile-name">{user_line}</div>'
        f'<div class="sidebar-cash-pill">{cash_line}</div>'
        f'<div style="margin:0.38rem 0;">{wanted_html}</div>'
        f'<div style="font-family:\'Share Tech Mono\',monospace; color:#cbd5e1; font-size:0.76rem;">'
        f"{sub_counts}"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button(logout_label, width="stretch"):
        logout()
        st.rerun()

    st.sidebar.markdown("---")

    selected_mode = st.sidebar.radio(
        "☢️ BUNKER MODULES" if doomsday else "🕹️ MODULE SELECTOR",
        NAV_ITEMS,
        index=0,
    )

    st.sidebar.markdown("---")
    if doomsday:
        st.sidebar.info(
            "**BUNKER NET TERMINAL // DEFCON-1:**\n"
            "- Mission: BCC 351 Mini Project\n"
            "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
            "- Feed: NSE India (FALLOUT NODE)"
        )
    else:
        st.sidebar.info(
            "**LEONIDA INTEL TERMINAL:**\n"
            "- Mission: BCC 351 Mini Project\n"
            "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
            "- Feed: NSE India (BAWSAQ / LCN)"
        )
    return selected_mode


def main() -> None:
    """Bootstrap active world edition styles, session state, transitions, and dashboard."""
    init_session_state()
    inject_global_styles()

    if st.session_state.get("edition_transitioning"):
        render_doomsday_reboot_overlay()
        time.sleep(1.8)
        st.session_state["edition_transitioning"] = False
        st.rerun()
        return

    if st.session_state.get("transitioning"):
        render_login_transition_overlay(str(st.session_state["username"]))
        time.sleep(2.0)
        st.session_state["transitioning"] = False
        st.rerun()
        return

    render_edition_toggle()

    if not st.session_state["authenticated"]:
        render_login_page()
        return

    selected_mode = render_sidebar()
    view_fn = VIEW_DISPATCH.get(selected_mode, render_market_overview)
    view_fn()
    render_ifruit_phone_widget()


if __name__ == "__main__":
    main()
