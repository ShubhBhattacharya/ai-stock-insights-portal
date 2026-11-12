"""Module 7: Interactive Vice City Character Terminal — AI Stock Tutor & Live NSE Bot."""

from __future__ import annotations

import html
import streamlit as st

from src.services.tutor import CURRICULUM_MODULES, QUICK_PROMPTS, generate_tutor_turn
from src.state import compute_dynamic_wanted_stars
from src.styles import render_page_header
from src.views.character_stage import render_character_stage


def _handle_chat_turn(prompt: str) -> None:
    """Append user prompt, analyze live NSE stocks if mentioned, and drive character state."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply, mood, scans = generate_tutor_turn(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state["tutor_mood"] = mood
    st.session_state["tutor_scans"] = scans
    st.session_state["tutor_turn_id"] = int(st.session_state.get("tutor_turn_id", 0)) + 1
    st.session_state["tutor_just_spoke"] = True


def render_ai_tutor() -> None:
    """Render full-body animated Vice City character stage + Arcade Chat Terminal + Curriculum."""
    render_page_header(
        title="UNDERGROUND CYBER HACKER / LESTER INTEL TERMINAL",
        subtitle="Full-body Vice City AI Insider powered by live NSE telemetry, RSI scanners & Hinglish chat",
        badge="INTERACTIVE CHARACTER TERMINAL • LIVE NSE AI",
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    st.session_state.setdefault("tutor_mood", "neutral")
    st.session_state.setdefault("tutor_scans", [])
    st.session_state.setdefault("tutor_turn_id", 0)

    tab_assistant, tab_course = st.tabs(
        ["🕹️ ARCADE CHAT TERMINAL", "📚 DECRYPTED CURRICULUM"]
    )

    with tab_assistant:
        col_avatar, col_chat = st.columns([1.2, 2], gap="medium")

        with col_avatar:
            is_speaking = bool(st.session_state.pop("tutor_just_spoke", False))
            render_character_stage(
                mood=str(st.session_state.get("tutor_mood", "neutral")),
                is_speaking=is_speaking,
                turn_id=int(st.session_state.get("tutor_turn_id", 0)),
                operator_name=str(st.session_state.get("username", "SHUBH")),
            )

        with col_chat:
            st.markdown(
                '<div class="steel-rivet-card" style="padding:0.8rem 1.15rem; margin-bottom:0.75rem;">'
                '<span class="rivet-dot rivet-tl"></span><span class="rivet-dot rivet-tr"></span>'
                '<span class="rivet-dot rivet-bl"></span><span class="rivet-dot rivet-br"></span>'
                '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
                '<span style="font-family:\'Orbitron\',sans-serif; font-size:0.95rem; font-weight:800; color:#00f5d4;">'
                "🕹️ ARCADE CHAT TERMINAL // LIVE NSE UPLINK"
                "</span>"
                '<span style="font-family:\'Share Tech Mono\',monospace; font-size:0.72rem; color:#39ff14;">'
                "● STATUS: ACTIVE / ENCRYPTED"
                "</span>"
                "</div></div>",
                unsafe_allow_html=True,
            )

            st.caption("Quick terminal commands (live stock scan & rules):")
            q_row1 = st.columns(2)
            q_row2 = st.columns(2)
            prompt_cols = [q_row1[0], q_row1[1], q_row2[0], q_row2[1]]
            for idx, q_text in enumerate(QUICK_PROMPTS[:4]):
                with prompt_cols[idx]:
                    if st.button(q_text, key=f"quick_prompt_{idx}", width="stretch"):
                        _handle_chat_turn(q_text)
                        st.rerun()

            chat_box = st.container(height=330)
            with chat_box:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            scans = st.session_state.get("tutor_scans", [])
            if scans:
                scan_badges = []
                for m in scans:
                    sig = m["signal"]
                    tone_col = "#39ff14" if sig == "BUY" else ("#ff4d8d" if sig == "SELL" else "#fee440")
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

            if prompt := st.chat_input(
                "Poochiye apna question... (e.g., Reliance ka price & RSI batao, or ₹10,000 budget)"
            ):
                _handle_chat_turn(prompt)
                st.rerun()

    with tab_course:
        st.subheader("📖 Classified Street Curriculum")
        topic = st.selectbox(
            "Select Intel File to Decrypt:",
            list(CURRICULUM_MODULES.keys()),
        )
        st.markdown("---")
        st.markdown(CURRICULUM_MODULES[topic])
