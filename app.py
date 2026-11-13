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
from src.state import (
    compute_dynamic_wanted_stars,
    get_portal_theme,
    init_session_state,
    is_default_theme,
    is_doomsday,
    logout,
)
try:
    from src.styles import (
        build_gta_chase_transition_html,
        inject_global_styles,
        render_doomsday_reboot_overlay,
        render_edition_toggle,
        render_gta_chase_transition,
        render_login_transition_overlay,
        render_wanted_stars_html,
    )
except Exception:
    try:
        import src.styles as _styles_mod
        build_gta_chase_transition_html = getattr(_styles_mod, "build_gta_chase_transition_html", lambda *a, **k: "")
        inject_global_styles = getattr(_styles_mod, "inject_global_styles", lambda *a, **k: None)
        render_doomsday_reboot_overlay = getattr(_styles_mod, "render_doomsday_reboot_overlay", lambda *a, **k: None)
        render_edition_toggle = getattr(_styles_mod, "render_edition_toggle", lambda *a, **k: None)
        render_gta_chase_transition = getattr(_styles_mod, "render_gta_chase_transition", lambda *a, **k: None)
        render_login_transition_overlay = getattr(_styles_mod, "render_login_transition_overlay", lambda *a, **k: None)
        render_wanted_stars_html = getattr(_styles_mod, "render_wanted_stars_html", lambda *a, **k: "")
    except Exception:
        build_gta_chase_transition_html = lambda *a, **k: ""  # type: ignore[assignment]
        inject_global_styles = lambda *a, **k: None  # type: ignore[assignment]
        render_doomsday_reboot_overlay = lambda *a, **k: None  # type: ignore[assignment]
        render_edition_toggle = lambda *a, **k: None  # type: ignore[assignment]
        render_gta_chase_transition = lambda *a, **k: None  # type: ignore[assignment]
        render_login_transition_overlay = lambda *a, **k: None  # type: ignore[assignment]
        render_wanted_stars_html = lambda *a, **k: ""  # type: ignore[assignment]
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

_GTM_ID = "GTM-K8XN5Z86"
_GTM_SCRIPT = (
    '<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-K8XN5Z86"></script>'
    "<script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());</script>"
)
_GTM_CHECKED = False


def inject_google_tag() -> None:
    """Locate Streamlit's static/index.html and inject the Google Tag Manager snippet once after <head>."""
    global _GTM_CHECKED
    if _GTM_CHECKED:
        return
    _GTM_CHECKED = True
    try:
        index_path = Path(st.__file__).resolve().parent / "static" / "index.html"
        if not index_path.is_file():
            return
        html_content = index_path.read_text(encoding="utf-8")
        if _GTM_ID in html_content:
            return
        if "<head>" in html_content:
            updated = html_content.replace("<head>", f"<head>\n    {_GTM_SCRIPT}", 1)
            index_path.write_text(updated, encoding="utf-8")
    except OSError:
        # Gracefully skip if package directory is read-only on hosted platforms.
        pass


inject_google_tag()

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
    """Render clean theme-aware sidebar profile, cash balance, logout, 3-mode switcher, and nav."""
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    username = html.escape(str(st.session_state["username"]))
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])

    if default_pro:
        st.sidebar.markdown(
            f'<div class="sidebar-profile-card">'
            f'<div class="sidebar-profile-name">👤 {username}</div>'
            f'<div class="sidebar-cash-pill">Cash: ₹{cash_balance:,.2f}</div>'
            f'<div style="color:#94a3b8; font-size:0.78rem; margin-top:0.28rem;">'
            f"{num_holdings} Holdings · {num_alerts} Active Alerts"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("🚪 Sign Out", width="stretch"):
            logout()
            st.rerun()

        st.sidebar.markdown("---")
        render_edition_toggle(in_sidebar=True)
        st.sidebar.markdown("---")

        active_mod = str(st.session_state.get("active_module", NAV_ITEMS[0]))
        active_idx = NAV_ITEMS.index(active_mod) if active_mod in NAV_ITEMS else 0

        selected_mode = st.sidebar.radio(
            "Navigation Modules",
            NAV_ITEMS,
            index=active_idx,
        )

        st.sidebar.markdown("---")
        st.sidebar.info(
            "**AI Stock Insights Portal (Pro Standard)**\n"
            "- Academic Project: BCC 351\n"
            "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
            "- Data Feed: NSE India Equities"
        )
        return selected_mode

    upper_name = username.upper()
    wanted_level = compute_dynamic_wanted_stars()
    wanted_html = render_wanted_stars_html(active_stars=wanted_level, total_stars=6)

    user_line = f"👤 AUTHORIZED USER: {upper_name}" if doomsday else f"👤 WELCOME, {upper_name}"
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
    render_edition_toggle(in_sidebar=True)
    st.sidebar.markdown("---")

    active_mod = str(st.session_state.get("active_module", NAV_ITEMS[0]))
    active_idx = NAV_ITEMS.index(active_mod) if active_mod in NAV_ITEMS else 0

    selected_mode = st.sidebar.radio(
        "☢️ BUNKER MODULES" if doomsday else "🕹️ MODULE SELECTOR",
        NAV_ITEMS,
        index=active_idx,
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
    """Bootstrap active portal theme styles, session state, transitions, and dashboard."""
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
        time.sleep(1.5 if is_default_theme() else 2.0)
        st.session_state["transitioning"] = False
        st.rerun()
        return

    if not st.session_state["authenticated"]:
        render_edition_toggle(in_sidebar=False)
        render_login_page()
        return

    # 1. Persistent Full-Screen GTA VI Module-Switch Transition Overlay with Auto-Timeout (3.5s)
    if st.session_state.get("show_gta_transition", False):
        transition_placeholder = st.empty()
        with transition_placeholder.container():
            render_gta_chase_transition(wanted_stars=compute_dynamic_wanted_stars())
        time.sleep(3.5)
        st.session_state["show_gta_transition"] = False
        transition_placeholder.empty()
        st.rerun()
        return

    # 2. Render sidebar and track current module
    selected_mode = render_sidebar()
    prev_mode = st.session_state.get("prev_module", selected_mode)

    # 3. Detect module switch and trigger GTA VI transition
    portal_theme = get_portal_theme()
    is_gta_theme = portal_theme == "GTA VI" or (not is_default_theme() and not is_doomsday())

    if is_gta_theme and selected_mode != prev_mode:
        st.session_state["show_gta_transition"] = True
        st.session_state["prev_module"] = selected_mode
        st.session_state["active_module"] = selected_mode
        st.rerun()
        return

    # Keep active and prev module synced
    st.session_state["prev_module"] = selected_mode
    st.session_state["active_module"] = selected_mode

    view_fn = VIEW_DISPATCH.get(selected_mode, render_market_overview)
    view_fn()
    if not is_default_theme():
        render_ifruit_phone_widget()


if __name__ == "__main__":
    main()
