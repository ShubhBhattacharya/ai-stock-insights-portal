"""Module 7: Interactive Vice City Character Terminal — AI Stock Tutor & Live NSE Bot."""

from __future__ import annotations

import html
import streamlit as st

from src.services.tutor import (
    QUICK_PROMPTS,
    adapt_tutor_text_for_edition,
    generate_tutor_turn,
    get_curriculum_modules,
)
from src.state import compute_dynamic_wanted_stars, get_portal_theme, is_default_theme, is_doomsday
from src.styles import render_page_header
from src.views.character_stage import render_character_stage


def _handle_chat_turn(prompt: str) -> None:
    """Append user prompt, analyze live NSE stocks if mentioned, and drive character state."""
    edition = get_portal_theme()
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply, mood, scans = generate_tutor_turn(prompt, edition=edition)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state["tutor_mood"] = mood
    st.session_state["tutor_scans"] = scans
    st.session_state["tutor_turn_id"] = int(st.session_state.get("tutor_turn_id", 0)) + 1
    st.session_state["tutor_just_spoke"] = True


def _render_chat_panel(doomsday: bool, default_pro: bool = False) -> None:
    """Render the chat terminal panel, quick commands, and live market scanner."""
    if default_pro:
        terminal_title = "AI Equity Assistant // Live NSE Analytics"
        terminal_title_color = "#10b981"
        terminal_status = "● LIVE NSE FEED"
        placeholder_txt = "Ask about any NSE stock, RSI, 50-SMA, BUY/SELL rules, or portfolio allocation..."
    elif doomsday:
        terminal_title = "☣️ BUNKER AI CHAT TERMINAL // ENCRYPTED UPLINK"
        terminal_title_color = "#39ff14"
        terminal_status = "● DEFCON-1 LINK: ACTIVE"
        placeholder_txt = "Poochiye apna question... (e.g., Reliance ka price & RSI batao, or ₹10,000 budget)"
    else:
        terminal_title = "🕹️ ARCADE CHAT TERMINAL // LIVE NSE UPLINK"
        terminal_title_color = "#00f5d4"
        terminal_status = "● STATUS: ACTIVE / ENCRYPTED"
        placeholder_txt = "Poochiye apna question... (e.g., Reliance ka price & RSI batao, or ₹10,000 budget)"

    header_font = "" if default_pro else "font-family:'Orbitron',sans-serif; "
    st.markdown(
        '<div class="surface-card" style="padding:0.8rem 1.15rem; margin-bottom:0.75rem;">'
        '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
        f'<span style="{header_font}font-size:0.95rem; font-weight:700; color:{terminal_title_color};">'
        f"{terminal_title}"
        "</span>"
        '<span style="font-size:0.74rem; font-weight:600; color:#10b981;">'
        f"{terminal_status}"
        "</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.caption("Suggested prompts:" if default_pro else "Quick terminal commands (live stock scan & rules):")
    q_row1 = st.columns(2)
    q_row2 = st.columns(2)
    prompt_cols = [q_row1[0], q_row1[1], q_row2[0], q_row2[1]]
    for idx, q_text in enumerate(QUICK_PROMPTS[:4]):
        with prompt_cols[idx]:
            if st.button(q_text, key=f"quick_prompt_{idx}", width="stretch"):
                _handle_chat_turn(q_text)
                st.rerun()

    active_edition = get_portal_theme()
    chat_box = st.container(height=330)
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                content = (
                    adapt_tutor_text_for_edition(msg["content"], edition=active_edition)
                    if msg.get("role") == "assistant"
                    else msg["content"]
                )
                st.markdown(content)

    scans = st.session_state.get("tutor_scans", [])
    if scans:
        scan_badges = []
        for m in scans:
            sig = m["signal"]
            tone_col = "#10b981" if sig == "BUY" else ("#ef4444" if sig == "SELL" else "#f59e0b")
            dot = "🟢" if sig == "BUY" else ("🔴" if sig == "SELL" else "🟡")
            scan_badges.append(
                f'<span style="color:{tone_col}; font-weight:700;">'
                f"{html.escape(m['symbol'])} {dot} ₹{m['close']:,.2f} "
                f"(RSI {m['rsi']:.1f} · {sig})</span>"
            )
        st.markdown(
            '<div class="console-hud-ruler" style="margin-top:0.5rem;">'
            f"<span>📡 LIVE MARKET SCANNER: {' &nbsp;|&nbsp; '.join(scan_badges)}</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    if prompt := st.chat_input(placeholder_txt):
        _handle_chat_turn(prompt)
        st.rerun()


def render_ai_tutor() -> None:
    """Render AI Equity Assistant (Pro Standard) or 3D Holographic Character Stage + Chat."""
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    edition = get_portal_theme()

    if default_pro:
        hdr_title = "AI Stock Tutor & Chatbot"
        hdr_sub = "Interactive NSE Equity Financial Assistant & Fundamental/Technical Learning Modules"
        hdr_badge = "AI FINANCIAL TUTOR • PRO STANDARD"
        tab_labels = ["AI Chat Assistant", "Learning Curriculum"]
        course_title = "Financial & Technical Analysis Curriculum"
    elif doomsday:
        hdr_title = "DOOMSDAY AI // LATVERIAN COMMAND"
        hdr_sub = "Interactive 3D Holographic Doctor Doom Tactician powered by live NSE telemetry & Hinglish chat"
        hdr_badge = "AVENGERS: DOOMSDAY • 3D HOLOGRAPHIC AI"
        tab_labels = ["🛡️ BUNKER AI CHAT TERMINAL", "📚 SURVIVAL INTEL ARCHIVE"]
        course_title = "📖 Classified Survival Intelligence Archive"
    else:
        hdr_title = "AI TUTOR // LEONIDA BROKER"
        hdr_sub = "Interactive 3D Holographic Jason Broker Stage powered by live NSE telemetry & Hinglish chat"
        hdr_badge = "GTA VI • 3D HOLOGRAPHIC CHARACTER STAGE"
        tab_labels = ["🕹️ ARCADE CHAT TERMINAL", "📚 DECRYPTED CURRICULUM"]
        course_title = "📖 Classified Street Curriculum"

    render_page_header(
        title=hdr_title,
        subtitle=hdr_sub,
        badge=hdr_badge,
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    st.session_state.setdefault("tutor_mood", "neutral")
    st.session_state.setdefault("tutor_scans", [])
    st.session_state.setdefault("tutor_turn_id", 0)

    tab_assistant, tab_course = st.tabs(tab_labels)

    with tab_assistant:
        if default_pro:
            _render_chat_panel(doomsday=False, default_pro=True)
        else:
            col_avatar, col_chat = st.columns([1.2, 2], gap="medium")

            with col_avatar:
                is_speaking = bool(st.session_state.pop("tutor_just_spoke", False))
                render_character_stage(
                    mood=str(st.session_state.get("tutor_mood", "neutral")),
                    is_speaking=is_speaking,
                    turn_id=int(st.session_state.get("tutor_turn_id", 0)),
                    operator_name=str(st.session_state.get("username", "SHUBH")),
                    edition=edition,
                )

            with col_chat:
                _render_chat_panel(doomsday=doomsday, default_pro=False)

    with tab_course:
        st.subheader(course_title)
        modules = get_curriculum_modules(edition=edition)
        topic = st.selectbox(
            "Select Study Module:" if default_pro else "Select Intel File to Decrypt:",
            list(modules.keys()),
        )
        st.markdown("---")
        st.markdown(modules[topic])
