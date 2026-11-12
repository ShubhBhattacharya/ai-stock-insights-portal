"""Collapsible iFruit Market Phone right-edge floating HUD mini-widget."""

from __future__ import annotations

import html
import streamlit as st

from src.constants import IFRUIT_WATCHLIST
from src.services.market_data import fetch_batch_overview, get_stock_analysis
from src.state import execute_buy_order, execute_sell_order


def render_ifruit_phone_widget() -> None:
    """Render a collapsible floating iFruit smartphone card on the right edge."""
    is_open = bool(st.session_state.get("ifruit_open", False))
    alerts_count = len(st.session_state.get("alerts", []))
    portfolio = st.session_state.get("portfolio", {})

    with st.container():
        st.markdown('<span class="ifruit-anchor"></span>', unsafe_allow_html=True)

        toggle_label = (
            f"📱 iFruit Phone ▾ (🚨 {alerts_count} Alerts)"
            if is_open
            else f"📱 iFruit Market Phone ▸ (🚨 {alerts_count})"
        )
        if st.button(toggle_label, key="ifruit_toggle_btn", width="stretch"):
            st.session_state["ifruit_open"] = not is_open
            st.rerun()

        if not is_open:
            return

        overview = fetch_batch_overview(IFRUIT_WATCHLIST)
        rows_html: list[str] = []
        price_lookup: dict[str, tuple[str, float]] = {}

        for row in overview:
            name = str(row["Company Name"])
            sym = str(row["Symbol"])
            full_sym = f"{sym}.NS" if "." not in sym else sym
            price = float(row["Price"])
            chg = float(row["Change %"])
            sig = str(row["Signal"])
            dot = "🟢" if sig == "BUY" else ("🔴" if sig == "SELL" else "🟡")
            chg_color = "#39ff14" if chg >= 0 else "#ff2a85"
            price_lookup[sym] = (name, price)
            rows_html.append(
                f'<div style="display:flex; justify-content:space-between; align-items:center; '
                f'padding:0.22rem 0; border-bottom:1px dashed rgba(0,245,212,0.18); '
                f'font-family:\'Share Tech Mono\',monospace; font-size:0.74rem;">'
                f'<span style="color:#f8fafc;">{dot} <strong>{html.escape(sym)}</strong></span>'
                f'<span style="color:#cbd5e1;">₹{price:,.0f}</span>'
                f'<span style="color:{chg_color}; font-weight:700;">{chg:+.2f}%</span>'
                f"</div>"
            )

        st.markdown(
            f'<div style="background:rgba(7,3,18,0.88); border:1px solid rgba(255,42,133,0.45); '
            f'border-radius:10px; padding:0.45rem 0.55rem; margin:0.2rem 0 0.45rem 0;">'
            f'<div style="display:flex; justify-content:space-between; font-family:\'Orbitron\',sans-serif; '
            f'font-size:0.65rem; color:#00f5d4; margin-bottom:0.28rem;">'
            f'<span> iFRUIT MINI-MARKET</span><span>🚨 {alerts_count} ALERTS</span>'
            f"</div>"
            f'{"".join(rows_html) if rows_html else "<div style=\'color:#cbd5e1;font-size:0.74rem;\'>Syncing BAWSAQ quotes...</div>"}'
            f"</div>",
            unsafe_allow_html=True,
        )

        choices = list(price_lookup.keys()) or ["RELIANCE", "TCS", "INFY", "SBIN"]
        picked_short = st.selectbox(
            "Quick Trade Target",
            choices,
            key="ifruit_quick_symbol",
            label_visibility="collapsed",
        )
        full_sym = f"{picked_short}.NS" if "." not in picked_short else picked_short
        held = int(portfolio.get(full_sym, {}).get("qty", 0))

        c_buy, c_sell = st.columns(2)
        with c_buy:
            if st.button("🟢 BUY 1", key="ifruit_quick_buy", width="stretch"):
                target_name, live_p = price_lookup.get(picked_short, (picked_short, 0.0))
                if live_p <= 0:
                    m, _ = get_stock_analysis(full_sym)
                    live_p = float(m["close"]) if m else 0.0
                ok, msg = execute_buy_order(full_sym, target_name, 1, live_p)
                if ok:
                    st.toast(f"iFruit Trade: {msg}", icon="📱")
                    st.rerun()
                else:
                    st.error(msg)
        with c_sell:
            if st.button("🔴 SELL 1", key="ifruit_quick_sell", width="stretch", disabled=held < 1):
                target_name, live_p = price_lookup.get(picked_short, (picked_short, 0.0))
                if live_p <= 0:
                    m, _ = get_stock_analysis(full_sym)
                    live_p = float(m["close"]) if m else 0.0
                ok, msg = execute_sell_order(full_sym, target_name, 1, live_p)
                if ok:
                    st.toast(f"iFruit Trade: {msg}", icon="📱")
                    st.rerun()
                else:
                    st.error(msg)
