"""Module 7: Lester's Cyber Uplink — AI Stock Tutor & Underground Learning Console."""

from __future__ import annotations

import streamlit as st

from src.services.tutor import CURRICULUM_MODULES, QUICK_PROMPTS, generate_bot_response
from src.styles import render_page_header


def _handle_chat_turn(prompt: str) -> None:
    """Append user prompt and Lester's cyber-hacker response to chat history."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = generate_bot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})


def render_ai_tutor() -> None:
    """Render encrypted financial curriculum and Lester's cyber hacker assistant."""
    render_page_header(
        title="Lester's Cyber Uplink // AI Stock Tutor",
        subtitle="Decode RSI, moving averages, valuations & BAWSAQ heist rules with your hacker strategist",
        badge="UNDERGROUND CYBER ASSISTANT • ENCRYPTED",
        wanted_stars=4,
    )

    tab_course, tab_assistant = st.tabs(["📚 DECRYPTED CURRICULUM", "🕶️ CYBER HACKER CHAT"])

    with tab_course:
        st.subheader("📖 Classified Street Curriculum")
        topic = st.selectbox(
            "Select Intel File to Decrypt:",
            list(CURRICULUM_MODULES.keys()),
        )
        st.markdown("---")
        st.markdown(CURRICULUM_MODULES[topic])

    with tab_assistant:
        st.subheader("💬 Encrypted Uplink — Ask Lester")

        st.caption("Quick terminal commands:")
        quick_cols = st.columns(len(QUICK_PROMPTS))
        for idx, q_text in enumerate(QUICK_PROMPTS):
            with quick_cols[idx]:
                if st.button(q_text, key=f"quick_prompt_{idx}", width="stretch"):
                    _handle_chat_turn(q_text)
                    st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input(
            "Transmit query... E.g., How does the BUY signal trigger? Or ₹10,000 budget drop..."
        ):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reply = generate_bot_response(prompt)
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
