"""Module 7: AI Stock Tutor & Interactive Learning Assistant."""

from __future__ import annotations

import streamlit as st

from src.services.tutor import CURRICULUM_MODULES, QUICK_PROMPTS, generate_bot_response
from src.styles import render_page_header


def _handle_chat_turn(prompt: str) -> None:
    """Append user prompt and assistant response to chat history."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = generate_bot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})


def render_ai_tutor() -> None:
    """Render structured financial curriculum and conversational AI tutor."""
    render_page_header(
        title="🎓 AI Stock Tutor & Learning Assistant",
        subtitle="Learn financial concepts, technical indicators, and ask investment strategy questions",
        badge="INTERACTIVE LEARNING HUB",
    )

    tab_course, tab_assistant = st.tabs(["📚 Interactive Learning Modules", "🤖 Ask AI Tutor"])

    with tab_course:
        st.subheader("📖 Curated Financial Curriculum")
        topic = st.selectbox(
            "Choose Concept to Explore:",
            list(CURRICULUM_MODULES.keys()),
        )
        st.markdown("---")
        st.markdown(CURRICULUM_MODULES[topic])

    with tab_assistant:
        st.subheader("💬 Ask Your AI Financial Tutor")

        st.caption("Quick starter questions:")
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
            "E.g., How does the BUY signal trigger? Or: Recommend strategy for ₹10,000 budget..."
        ):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            reply = generate_bot_response(prompt)
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
