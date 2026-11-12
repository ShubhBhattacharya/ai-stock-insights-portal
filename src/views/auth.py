"""Authentication and Demo Access view."""

from __future__ import annotations

import streamlit as st

from src.state import login_as
from src.styles import render_page_header


def render_login_page() -> None:
    """Render the responsive Sign-In / Registration portal."""
    render_page_header(
        title="📈 AI Stock Insights Portal",
        subtitle="A Web-Based Technical-Analysis Dashboard for Indian Equity Markets | Mini Project BCC 351",
        badge="DRONACHARYA GROUP OF INSTITUTIONS • AKTU",
    )

    _, col_center, _ = st.columns([1, 2.2, 1])
    with col_center:
        st.markdown(
            '<div class="surface-card">'
            '<h3 style="margin:0 0 0.25rem 0; font-size:1.25rem;">🔐 User Portal Sign-In</h3>'
            '<p style="margin:0; color:#94a3b8; font-size:0.88rem;">'
            "Access real-time NSE technical signals, ML price forecasts, paper trading, and portfolio risk tools."
            "</p></div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "⚡ 1-Click Guest / Evaluator Access (Demo Mode)",
            type="primary",
            width="stretch",
        ):
            login_as("Academic Evaluator")
            st.rerun()

        st.markdown(
            '<p style="text-align:center; color:#64748b; font-size:0.8rem; margin:0.85rem 0;">'
            "— OR SIGN IN WITH ACCOUNT —"
            "</p>",
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input("Username", value="admin", key="login_username")
                password_input = st.text_input(
                    "Password", type="password", value="admin123", key="login_password"
                )
                submitted = st.form_submit_button("Sign In to Portal", width="stretch")

            if submitted:
                uname = username_input.strip().lower()
                valid_pass = st.session_state["users"].get(uname)
                if valid_pass and valid_pass == password_input:
                    login_as(username_input.strip().capitalize())
                    st.rerun()
                else:
                    st.error(
                        "Invalid credentials. Try username 'admin' and password 'admin123' or use 1-Click Demo!"
                    )

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                new_user = st.text_input("Choose Username", key="reg_username")
                new_pass = st.text_input("Choose Password", type="password", key="reg_password")
                confirm_pass = st.text_input(
                    "Confirm Password", type="password", key="reg_confirm"
                )
                reg_submitted = st.form_submit_button("Register New User", width="stretch")

            if reg_submitted:
                clean_user = new_user.strip()
                if not clean_user or not new_pass:
                    st.error("Username and password are required.")
                elif len(clean_user) < 3:
                    st.error("Username must be at least 3 characters long.")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters long.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif clean_user.lower() in st.session_state["users"]:
                    st.error("Username already taken.")
                else:
                    st.session_state["users"][clean_user.lower()] = new_pass
                    st.success(
                        f"User '{clean_user}' created successfully! Switch to 'Sign In' to enter."
                    )

        st.markdown("---")
        st.caption(
            "🎓 **B.Tech Mini Project BCC 351** | Dronacharya Group of Institutions (AKTU) | Session 2025–26"
        )
