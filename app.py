"""AI Stock Insights Portal | NSE India — GTA VI / Vice City Neon Edition Entry Point."""

from __future__ import annotations

import html
import io
import os
from pathlib import Path
import sys
import time
import streamlit as st

# Safe import for streamlit-mic-recorder
try:
    from streamlit_mic_recorder import mic_recorder
    HAS_MIC_RECORDER = True
except Exception:
    HAS_MIC_RECORDER = False
    mic_recorder = None

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
from src.services.voice_service import dispatch_voice_command, render_voice_input_controls
try:
    from src.styles import (
        inject_global_styles,
        render_doomsday_reboot_overlay,
        render_edition_toggle,
        render_login_transition_overlay,
        render_wanted_stars_html,
    )
except Exception:
    try:
        import src.styles as _styles_mod
        inject_global_styles = getattr(_styles_mod, "inject_global_styles", lambda *a, **k: None)
        render_doomsday_reboot_overlay = getattr(_styles_mod, "render_doomsday_reboot_overlay", lambda *a, **k: None)
        render_edition_toggle = getattr(_styles_mod, "render_edition_toggle", lambda *a, **k: None)
        render_login_transition_overlay = getattr(_styles_mod, "render_login_transition_overlay", lambda *a, **k: None)
        render_wanted_stars_html = getattr(_styles_mod, "render_wanted_stars_html", lambda *a, **k: "")
    except Exception:
        inject_global_styles = lambda *a, **k: None  # type: ignore[assignment]
        render_doomsday_reboot_overlay = lambda *a, **k: None  # type: ignore[assignment]
        render_edition_toggle = lambda *a, **k: None  # type: ignore[assignment]
        render_login_transition_overlay = lambda *a, **k: None  # type: ignore[assignment]
        render_wanted_stars_html = lambda *a, **k: ""  # type: ignore[assignment]
from src.views.ai_tutor import render_ai_tutor
from src.views.auth import render_login_page
from src.views.comparison import render_stock_comparison
from src.views.ifruit_widget import render_ifruit_phone_widget
from src.views.market_overview import render_market_overview
from src.views.paper_trading import render_paper_trading
from src.views.price_alerts import render_price_alerts
from src.views.home import render_home_dashboard
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
    "🏠 Home": render_home_dashboard,
    "📈 Stock Analysis": render_single_stock_analysis,
    "🤖 Single Stock AI & ML Prediction": render_single_stock_analysis,
    "🌐 Market Overview": render_market_overview,
    "📊 Market Overview": render_market_overview,
    "✨ AI Insights": render_ai_tutor,
    "🎓 AI Stock Tutor & Chatbot": render_ai_tutor,
    "⚖️ Two-Stock Comparison": render_stock_comparison,
    "💼 Virtual Paper Trading": render_paper_trading,
    "🎯 Portfolio Risk Optimizer": render_risk_optimizer,
    "🚨 Price Alerts": render_price_alerts,
    "ℹ️ About & Synopsis": render_synopsis,
    "📜 Project Synopsis & Credits": render_synopsis,
}


def on_module_change() -> None:
    """Instantly handle module switch on single click via native Streamlit radio callback."""
    chosen = st.session_state.get("module_selector")
    if chosen:
        st.session_state["active_module"] = chosen
        st.session_state["prev_module"] = chosen


def set_pending_navigation(target: str) -> None:
    """Safely queue navigation target without directly mutating widget keys after instantiation."""
    if target in NAV_ITEMS:
        st.session_state["pending_nav_target"] = target
        st.session_state["active_module"] = target
        st.session_state["prev_module"] = target
    elif target in VIEW_DISPATCH:
        view_func = VIEW_DISPATCH[target]
        for item in NAV_ITEMS:
            if VIEW_DISPATCH.get(item) == view_func:
                st.session_state["pending_nav_target"] = item
                st.session_state["active_module"] = item
                st.session_state["prev_module"] = item
                break


def apply_pending_navigation() -> None:
    """Apply queued navigation before any sidebar widgets instantiate to prevent StreamlitWidgetAlreadyInstantiatedError."""
    target = st.session_state.pop("pending_nav_target", None)
    if target and target in NAV_ITEMS:
        st.session_state["module_selector"] = target
        st.session_state["active_module"] = target
        st.session_state["prev_module"] = target


def _render_sidebar_voice_widget(default_pro: bool) -> None:
    """Render sidebar voice command & stock query mic recorder powered by Whisper."""
    with st.sidebar.expander("🎙️ Voice Command (Whisper)", expanded=True):
        def _on_sidebar_voice(transcript: str) -> None:
            if not transcript or not transcript.strip():
                return
            cmd = dispatch_voice_command(transcript)
            if cmd["action"] == "navigate":
                set_pending_navigation(cmd["target"])
                st.toast(f"Navigating to {cmd['target']} via voice!", icon="🚀")
                st.rerun()
            else:
                set_pending_navigation("✨ AI Insights")
                st.session_state.setdefault("messages", []).append({"role": "user", "content": transcript})
                try:
                    from src.services.tutor import (
                        adapt_tutor_text_for_edition,
                        generate_tutor_turn,
                        sanitize_speech_text,
                    )
                    reply, mood, scans = generate_tutor_turn(transcript, edition=get_portal_theme())
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.session_state["tutor_mood"] = mood
                    st.session_state["tutor_scans"] = scans
                    st.session_state["tutor_turn_id"] = int(st.session_state.get("tutor_turn_id", 0)) + 1
                    st.session_state["tutor_just_spoke"] = True
                    adapted = adapt_tutor_text_for_edition(reply, edition=get_portal_theme())
                    st.session_state["latest_bot_reply"] = sanitize_speech_text(adapted)
                    st.session_state["reply_id"] = f"{len(st.session_state.messages)}-{time.time_ns()}"
                except Exception:
                    pass
                st.toast(f"Transcribed voice query: '{transcript}'", icon="🎙️")
                st.rerun()

        render_voice_input_controls(
            key_prefix=f"sidebar_voice_{'pro' if default_pro else 'vice'}",
            on_transcript_received=_on_sidebar_voice,
            button_label="🎙️ Speak Voice Command",
            stop_label="⏹️ Transcribe",
        )


def render_top_voice_dictation_bar(portal_theme: str) -> None:
    """Render a prominent voice dictation Whisper banner directly on the user interface."""
    doomsday = is_doomsday()
    default_pro = is_default_theme()

    accent_color = "#3b82f6" if default_pro else ("#39ff14" if doomsday else "#00f5d4")
    border_color = (
        "rgba(59, 130, 246, 0.35)"
        if default_pro
        else ("rgba(57, 255, 20, 0.45)" if doomsday else "rgba(255, 42, 133, 0.45)")
    )
    bg_color = (
        "rgba(15, 23, 42, 0.65)"
        if default_pro
        else ("rgba(18, 12, 8, 0.85)" if doomsday else "rgba(13, 6, 34, 0.85)")
    )
    title_label = (
        "🎙️ VOICE DICTATION & COMMAND BAR (WHISPER AI)"
        if default_pro
        else ("🎙️ BUNKER VOICE COMMS // WHISPER UPLINK" if doomsday else "🎙️ VICE VOICE DICTATION // WHISPER-1")
    )

    st.markdown(
        f'<div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px; '
        f'padding:0.45rem 0.85rem; margin-bottom:0.6rem; display:flex; justify-content:space-between; '
        f'align-items:center; flex-wrap:wrap; gap:0.4rem;">'
        f'<span style="font-weight:700; font-size:0.84rem; color:{accent_color}; letter-spacing:0.04em;">{title_label}</span>'
        f'<span style="font-size:0.72rem; color:#94a3b8;">⚡ Speak any NSE stock query or navigation command</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    def _on_top_voice_transcribed(transcript: str) -> None:
        if not transcript or not transcript.strip():
            return
        cmd = dispatch_voice_command(transcript)
        if cmd["action"] == "navigate":
            set_pending_navigation(cmd["target"])
            st.toast(f"Navigating to {cmd['target']} via voice!", icon="🚀")
            st.rerun()
        else:
            set_pending_navigation("✨ AI Insights")
            st.session_state.setdefault("messages", []).append({"role": "user", "content": transcript})
            try:
                from src.services.tutor import (
                    adapt_tutor_text_for_edition,
                    generate_tutor_turn,
                    sanitize_speech_text,
                )
                reply, mood, scans = generate_tutor_turn(transcript, edition=get_portal_theme())
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state["tutor_mood"] = mood
                st.session_state["tutor_scans"] = scans
                st.session_state["tutor_turn_id"] = int(st.session_state.get("tutor_turn_id", 0)) + 1
                st.session_state["tutor_just_spoke"] = True
                adapted = adapt_tutor_text_for_edition(reply, edition=get_portal_theme())
                st.session_state["latest_bot_reply"] = sanitize_speech_text(adapted)
                st.session_state["reply_id"] = f"{len(st.session_state.messages)}-{time.time_ns()}"
            except Exception:
                pass
            st.toast(f"Transcribed voice query: '{transcript}'", icon="🎙️")
            st.rerun()

    render_voice_input_controls(
        key_prefix="main_top_voice",
        on_transcript_received=_on_top_voice_transcribed,
        button_label="🎙️ Speak Query / Command (Whisper)",
        stop_label="⏹️ Stop & Transcribe",
    )


def render_sidebar() -> str:
    """Render clean theme-aware sidebar profile, cash balance, logout, 3-mode switcher, and nav."""
    apply_pending_navigation()
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    username = html.escape(str(st.session_state["username"]))
    cash_balance = float(st.session_state["cash_balance"])
    num_holdings = len(st.session_state["portfolio"])
    num_alerts = len(st.session_state["alerts"])

    active_mod = str(st.session_state.get("active_module", NAV_ITEMS[0]))
    active_idx = NAV_ITEMS.index(active_mod) if active_mod in NAV_ITEMS else 0
    if "module_selector" not in st.session_state:
        st.session_state["module_selector"] = active_mod

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

        _render_sidebar_voice_widget(default_pro=True)
        st.sidebar.markdown("---")

        selected_mode = st.sidebar.radio(
            "Navigation Modules",
            NAV_ITEMS,
            key="module_selector",
            on_change=on_module_change,
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

    # Top Brand Logo for Leonida / Vice City Mode
    if not is_default_theme() and not doomsday:
        st.sidebar.markdown(
            """
            <div class="ref-sidebar-logo-container">
              <div class="ref-sidebar-logo-icon">🌴🏙️</div>
              <div class="ref-sidebar-logo-text">
                <div class="ref-logo-title">AI Stock</div>
                <div class="ref-logo-sub">Insights Portal</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

    _render_sidebar_voice_widget(default_pro=False)
    st.sidebar.markdown("---")

    selected_mode = st.sidebar.radio(
        "☢️ BUNKER MODULES" if doomsday else "🕹️ MODULE SELECTOR",
        NAV_ITEMS,
        key="module_selector",
        on_change=on_module_change,
    )

    st.sidebar.markdown("---")
    if not is_default_theme() and not doomsday:
        st.sidebar.markdown(
            """
            <div class="ref-sidebar-powered-card">
              <div class="ref-powered-top">
                <span class="ref-crown-icon">👑</span>
                <span class="ref-powered-title">Powered by AI</span>
              </div>
              <div class="ref-powered-desc">Smarter Decisions.<br>Bigger Opportunities.</div>
              <div class="ref-powered-chart">📈 🌴</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif doomsday:
        st.sidebar.info(
            "**BUNKER NET TERMINAL // DEFCON-1:**\n"
            "- Mission: BCC 351 Mini Project\n"
            "- Stack: Streamlit, yfinance, Plotly, pandas-ta\n"
            "- Feed: NSE India (FALLOUT NODE)"
        )
    return selected_mode


def main() -> None:
    """Bootstrap active portal theme styles, session state, transitions, and dashboard."""
    init_session_state()
    apply_pending_navigation()
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

    # Render sidebar with native single-click module selector
    current_module = render_sidebar()
    prev_module = st.session_state.get("prev_module", current_module)
    portal_theme = str(st.session_state.get("portal_theme", "GTA VI (Vice City)"))
    is_gta_theme = (
        "GTA VI" in portal_theme
        or "Vice City" in portal_theme
        or "VICE CITY" in portal_theme.upper()
        or (not is_default_theme() and not is_doomsday())
    )

    # Fast CSS Fade & Neon Glow Transition for GTA VI (Vice City) mode
    if is_gta_theme:
        st.markdown(
            '<div class="gta-neon-glow-line"></div>',
            unsafe_allow_html=True,
        )

    st.session_state["active_module"] = current_module
    st.session_state["prev_module"] = current_module

    # Prominent Voice Dictation Whisper Bar directly on user interface (on submodules)
    if current_module != "🏠 Home":
        render_top_voice_dictation_bar(portal_theme)

    module_container = st.container()
    with module_container:
        view_fn = VIEW_DISPATCH.get(current_module, render_home_dashboard)
        if current_module == "🏠 Home" or view_fn == render_home_dashboard:
            def _nav_from_home(target_dest: str) -> None:
                set_pending_navigation(target_dest)
                st.rerun()

            render_home_dashboard(on_navigate=_nav_from_home)
        else:
            view_fn()
    if not is_default_theme():
        render_ifruit_phone_widget()


if __name__ == "__main__":
    main()
