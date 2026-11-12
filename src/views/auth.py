"""Authentication and Vice City VIP Demo Access view."""

from __future__ import annotations

import streamlit as st

from src.state import login_as
from src.styles import render_page_header


def render_login_page() -> None:
    """Render the GTA VI / Vice City styled Sign-In / Registration portal."""
    render_page_header(
        title="AI Stock Insights Portal",
        subtitle="A Web-Based Technical-Analysis Dashboard for Indian Equity Markets | Mini Project BCC 351",
        badge="VICE CITY EDITION • DRONACHARYA GROUP OF INSTITUTIONS",
        use_calligraphy=True,
        wanted_stars=5,
    )

    _, col_center, _ = st.columns([0.8, 2.5, 0.8])
    with col_center:
        st.markdown(
            '<div class="steel-rivet-card">'
            '<span class="rivet-dot rivet-tl"></span>'
            '<span class="rivet-dot rivet-tr"></span>'
            '<span class="rivet-dot rivet-bl"></span>'
            '<span class="rivet-dot rivet-br"></span>'
            '<div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; padding:0.25rem 0;">'
            '<div style="flex:1; min-width:220px;">'
            '<div style="font-family:\'Orbitron\',sans-serif; font-size:0.72rem; color:#ffe600; letter-spacing:0.1em; margin-bottom:0.25rem;">'
            '⚠️ CLASSIFIED TERMINAL // BAWSAQ &amp; LCN UPLINK'
            "</div>"
            '<h3 style="margin:0 0 0.3rem 0; font-family:\'Orbitron\',sans-serif; font-size:1.25rem; color:#ffffff; text-shadow:0 0 10px rgba(0,240,255,0.6);">'
            "🔐 User Portal Sign-In"
            "</h3>"
            '<p style="margin:0; color:#cbd5e1; font-size:0.9rem;">'
            "Unlock live NSE BAWSAQ technical signals, 30-day ML forecasts, Broker-Heist paper trading, and Syndicate risk tools."
            "</p>"
            "</div>"
            '<div class="graffiti-vi">VI</div>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "🌴 ⚡ HAZARD / VIP ACCESS — 1-CLICK DEMO ✨",
            type="primary",
            width="stretch",
        ):
            login_as("Academic Evaluator")
            st.rerun()

        st.markdown(
            '<div class="console-hud-ruler">'
            "<span>000 ┼ 100 ┼ 200</span>"
            "<span>— OR AUTHENTICATE OPERATOR CONSOLE —</span>"
            "<span>300 ┼ 400 ┼ [TARGET]</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🕹️ SIGN IN CONSOLE", "🪪 CREATE OPERATOR"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input(
                    "OPERATOR ID (USERNAME)",
                    value="admin",
                    placeholder="e.g. admin",
                    key="login_username",
                )
                password_input = st.text_input(
                    "ACCESS KEY (PASSWORD)",
                    type="password",
                    value="",
                    placeholder="Demo password: admin123",
                    key="login_password",
                )
                submitted = st.form_submit_button("▸▸ SIGN IN TO PORTAL", width="stretch")

            if submitted:
                uname = username_input.strip().lower()
                valid_pass = st.session_state["users"].get(uname)
                if valid_pass and valid_pass == password_input:
                    login_as(username_input.strip().capitalize())
                    st.rerun()
                else:
                    st.error(
                        "🚨 ACCESS DENIED: Try username 'admin' and password 'admin123' or hit HAZARD / VIP ACCESS above!"
                    )

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                new_user = st.text_input("CHOOSE OPERATOR HANDLE", key="reg_username")
                new_pass = st.text_input("SET ACCESS KEY", type="password", key="reg_password")
                confirm_pass = st.text_input(
                    "CONFIRM ACCESS KEY", type="password", key="reg_confirm"
                )
                reg_submitted = st.form_submit_button("▸▸ REGISTER NEW OPERATOR", width="stretch")

            if reg_submitted:
                clean_user = new_user.strip()
                if not clean_user or not new_pass:
                    st.error("Operator handle and access key are required.")
                elif len(clean_user) < 3:
                    st.error("Operator handle must be at least 3 characters long.")
                elif len(new_pass) < 4:
                    st.error("Access key must be at least 4 characters long.")
                elif new_pass != confirm_pass:
                    st.error("Access keys do not match.")
                elif clean_user.lower() in st.session_state["users"]:
                    st.error("Operator handle already taken.")
                else:
                    st.session_state["users"][clean_user.lower()] = new_pass
                    st.success(
                        f"✅ Operator '{clean_user}' cleared! Switch to 'SIGN IN CONSOLE' to enter."
                    )

        st.markdown("---")
        st.caption(
            "🌴 **B.Tech Mini Project BCC 351 // Vice City Terminal** | Dronacharya Group of Institutions (AKTU) | Session 2025–26"
        )
