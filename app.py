"""AI Stock Insights Portal | NSE India — Vice City Neon Edition Entry Point."""

from __future__ import annotations

import html
import streamlit as st

from src.constants import NAV_ITEMS
from src.state import init_session_state, logout
from src.styles import inject_global_styles, render_wanted_stars_html
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
    page_title="AI Stock Insights Portal | Vice City NSE Terminal",
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
    """Render Vice City cyber HUD sidebar profile card, arcade navigation, and dossier info."""
    username = html.escape(str(st.session_state["username"]))
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])
    wanted_level = min(6, max(1, 1 + num_holdings + num_alerts))
    wanted_html = render_wanted_stars_html(active_stars=wanted_level, total_stars=6)

    st.sidebar.markdown(
        f'<div class="sidebar-profile-card">'
        f'<div style="font-family:\'Share Tech Mono\',monospace; font-size:0.68rem; color:#ff2a85; letter-spacing:0.1em; margin-bottom:0.2rem;">'
        f'🌴 VICE TERMINAL // OPERATOR HUD'
        f"</div>"
        f'<div class="sidebar-profile-name">🕶️ {username}</div>'
        f'<div style="margin:0.35rem 0;">{wanted_html}</div>'
        f'<div class="sidebar-cash-pill">💵 STASH: ₹{cash_balance:,.2f}</div>'
        f'<div style="font-family:\'Share Tech Mono\',monospace; color:#cbd5e1; font-size:0.76rem; margin-top:0.3rem;">'
        f"💼 {num_holdings} Drops · 🎯 {num_alerts} Bounties"
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

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**VICE INTEL TERMINAL:**\n"
        "- Mission: BCC 351 Mini Project\n"
        "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
        "- Feed: NSE India (BAWSAQ & LCN)"
    )
    return selected_mode


def main() -> None:
    """Bootstrap Vice City synthwave styles, session state, and route views."""
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
