"""Authentication and Vice City VIP Demo Access view."""

from __future__ import annotations

import streamlit as st

from src.state import is_doomsday, login_as
from src.styles import render_page_header, render_weazel_flash_ticker


def render_login_page() -> None:
    """Render edition-adaptive Sign-In / Registration portal (GTA VI or Doomsday)."""
    doomsday = is_doomsday()
    render_page_header(
        title="AI Stock Insights Portal",
        subtitle="A Web-Based Technical-Analysis Dashboard for Indian Equity Markets | Mini Project BCC 351",
        badge=(
            "DOOMSDAY BUNKER EDITION • DRONACHARYA GROUP OF INSTITUTIONS"
            if doomsday
            else "VICE CITY EDITION • DRONACHARYA GROUP OF INSTITUTIONS"
        ),
        use_calligraphy=not doomsday,
        wanted_stars=6 if doomsday else 5,
    )

    _, col_center, _ = st.columns([0.8, 2.5, 0.8])
    with col_center:
        if doomsday:
            card_sub = "☣️ SECURITY LEVEL: DEFCON-1 // BUNKER.NET UPLINK"
            card_title = "🔒 ⚠️ DOOMSDAY SIGN-IN PORTAL 🔒"
            card_desc = "Access survival market matrices, radiation-adjusted forecasts, war-capital trading, and bunker defense tools."
            right_emblem = '<div style="font-size:2.7rem; filter:drop-shadow(0 0 12px #ffb703);">☣️</div>'
            demo_btn_label = "💣 ENTER FALLOUT COVERT ACCESS (DEMO)"
            tabs = ["☢️ BUNKER AUTH", "🪪 ENLIST SURVIVOR"]
        else:
            card_sub = "⚠️ CLASSIFIED TERMINAL // BAWSAQ &amp; LCN UPLINK"
            card_title = "🔐 User Portal Sign-In"
            card_desc = "Unlock live NSE BAWSAQ technical signals, 30-day ML forecasts, Broker-Heist paper trading, and Syndicate risk tools."
            right_emblem = '<div class="graffiti-vi">VI</div>'
            demo_btn_label = "🌴 ⚡ HAZARD / VIP ACCESS — 1-CLICK DEMO ✨"
            tabs = ["🕹️ SIGN IN CONSOLE", "🪪 CREATE OPERATOR"]

        st.markdown(
            f'<div class="steel-rivet-card">'
            f'<span class="rivet-dot rivet-tl"></span>'
            f'<span class="rivet-dot rivet-tr"></span>'
            f'<span class="rivet-dot rivet-bl"></span>'
            f'<span class="rivet-dot rivet-br"></span>'
            f'<div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; padding:0.25rem 0;">'
            f'<div style="flex:1; min-width:220px;">'
            f'<div style="font-family:\'Orbitron\',sans-serif; font-size:0.72rem; color:{"#39ff14" if doomsday else "#ffe600"}; letter-spacing:0.1em; margin-bottom:0.25rem;">'
            f"{card_sub}"
            f"</div>"
            f'<h3 style="margin:0 0 0.3rem 0; font-family:\'Orbitron\',sans-serif; font-size:1.25rem; color:#ffffff; text-shadow:0 0 10px rgba(57,255,20,0.6);">'
            f"{card_title}"
            f"</h3>"
            f'<p style="margin:0; color:#cbd5e1; font-size:0.9rem;">'
            f"{card_desc}"
            f"</p>"
            f"</div>"
            f"{right_emblem}"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if st.button(demo_btn_label, type="primary", width="stretch"):
            login_as("Academic Evaluator" if not doomsday else "ADMIN")
            st.rerun()

        st.markdown(
            '<div class="console-hud-ruler">'
            "<span>000 ┼ 100 ┼ 200</span>"
            "<span>— OR AUTHENTICATE TERMINAL ACCESS —</span>"
            "<span>300 ┼ 400 ┼ [TARGET]</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(tabs)

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input(
                    "AUTHORIZED ID (USERNAME)" if doomsday else "OPERATOR ID (USERNAME)",
                    value="admin",
                    placeholder="e.g. admin",
                    key="login_username",
                )
                password_input = st.text_input(
                    "CLEARANCE KEY (PASSWORD)" if doomsday else "ACCESS KEY (PASSWORD)",
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
                        "🚨 ACCESS DENIED: Try username 'admin' and password 'admin123' or click the Covert Demo button above!"
                    )

        with tab_register:
            with st.form("register_form", clear_on_submit=True):
                new_user = st.text_input("CHOOSE SURVIVOR HANDLE" if doomsday else "CHOOSE OPERATOR HANDLE", key="reg_username")
                new_pass = st.text_input("SET ACCESS KEY", type="password", key="reg_password")
                confirm_pass = st.text_input("CONFIRM ACCESS KEY", type="password", key="reg_confirm")
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
                        f"✅ Clearance granted for '{clean_user}'! Switch to Sign-In tab to enter."
                    )

        if doomsday:
            render_weazel_flash_ticker(
                [
                    "⚠️ CRITICAL BREAKING: GLOBAL CAPITAL MARKETS UNDER DEFCON-1 VOLATILITY PROTOCOL",
                    "☣️ SCRAMBLE SECURE SERVER NETWORKS — NSE FALLOUT FEED ROUTED TO BUNKER.NET",
                    "☢️ RADIATION ALERT: MONITOR PORTFOLIOS VIA SHIELDED TERMINAL",
                ]
            )

        st.markdown("---")
        st.caption(
            f"{'☢️' if doomsday else '🌴'} **B.Tech Mini Project BCC 351 // {'Doomsday Bunker Terminal' if doomsday else 'Vice City Terminal'}** | Dronacharya Group of Institutions (AKTU) | Session 2025–26"
        )
