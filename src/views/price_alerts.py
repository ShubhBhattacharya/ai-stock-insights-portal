"""Module 6: Real-Time Price Alerts & WANTED Target Bounties."""

from __future__ import annotations

import html
import streamlit as st

from src.constants import NSE_STOCKS
from src.services.market_data import get_stock_analysis
from src.state import (
    add_price_alert,
    compute_dynamic_wanted_stars,
    is_default_theme,
    is_doomsday,
    remove_price_alert,
    set_context_risk_heat,
)
from src.styles import render_page_header


def _sync_alert_default_target() -> None:
    """Suggest a realistic target price near the newly selected stock's live close."""
    name = st.session_state.get("alert_stock_select")
    if name in NSE_STOCKS:
        metrics, _ = get_stock_analysis(NSE_STOCKS[name])
        if metrics:
            st.session_state["alert_target_price"] = round(float(metrics["close"]) * 1.02, 2)


def render_price_alerts() -> None:
    """Render theme-adaptive Price Alerts setup and live threshold monitor."""
    default_pro = is_default_theme()
    doomsday = is_doomsday()
    alerts_count = len(st.session_state.get("alerts", []))
    set_context_risk_heat(min(6, 2 + alerts_count))

    if default_pro:
        hdr_title = "Real-Time Price Alerts"
        hdr_sub = "Configure automated spot-price threshold triggers for NSE equities"
        hdr_badge = "THRESHOLD MONITOR • PRO STANDARD"
    elif doomsday:
        hdr_title = "EMERGENCY RADIATION // Price Tripwires"
        hdr_sub = "Arm bunker perimeter thresholds and intercept emergency NSE radiation alarms"
        hdr_badge = "DEFCON-1 SIREN • EMERGENCY TRIPWIRES"
    else:
        hdr_title = "WANTED LEVEL // Price Alert Bounties"
        hdr_sub = "Arm digital target thresholds and intercept live breakout alerts on NSE equities"
        hdr_badge = "WANTED RADAR • THRESHOLD TRIGGERS"

    render_page_header(
        title=hdr_title,
        subtitle=hdr_sub,
        badge=hdr_badge,
        wanted_stars=compute_dynamic_wanted_stars(),
    )

    stock_names = list(NSE_STOCKS.keys())
    if "alert_target_price" not in st.session_state:
        first_metrics, _ = get_stock_analysis(NSE_STOCKS[stock_names[0]])
        st.session_state["alert_target_price"] = (
            round(float(first_metrics["close"]) * 1.02, 2) if first_metrics else 1500.0
        )

    col_a1, col_a2, col_a3 = st.columns([2, 1, 1])
    with col_a1:
        alert_name = st.selectbox(
            "Select Equity:" if default_pro else "LOCK BOUNTY TARGET:",
            stock_names,
            key="alert_stock_select",
            on_change=_sync_alert_default_target,
        )
        alert_sym = NSE_STOCKS[alert_name]
    with col_a2:
        direction = st.selectbox("Condition:" if default_pro else "TRIGGER CONDITION:", ["Crosses Above", "Falls Below"])
    with col_a3:
        target_lbl = (
            "Target Price (INR):"
            if default_pro
            else ("TARGET TRIPWIRE (INR):" if doomsday else "TARGET BOUNTY (INR):")
        )
        target = float(
            st.number_input(
                target_lbl,
                min_value=1.0,
                step=10.0,
                key="alert_target_price",
            )
        )

    live_metrics, _ = get_stock_analysis(alert_sym)
    if live_metrics:
        live_close = float(live_metrics["close"])
        diff_pct = ((target - live_close) / live_close) * 100 if live_close else 0.0
        st.caption(
            f"Spot Price for **{alert_name}**: **₹{live_close:,.2f}** "
            f"(Target is {diff_pct:+.2f}% from spot)"
        )

    if st.button("Set New Price Alert", type="primary"):
        add_price_alert(alert_name, alert_sym, direction, target)
        st.toast(f"Price alert created for {alert_name} at ₹{target:,.2f}.", icon="🔔")

    st.markdown("---")
    monitor_hdr = (
        "Active Threshold Monitor"
        if default_pro
        else ("☢️ Active Radiation Tripwire Monitor" if doomsday else "🚨 Active WANTED Threshold Monitor")
    )
    st.subheader(monitor_hdr)

    alerts = st.session_state["alerts"]
    if not alerts:
        empty_msg = (
            "No active price alerts configured. Add a threshold trigger above."
            if default_pro
            else (
                "No bunker radiation tripwires configured. Arm a target trigger above."
                if doomsday
                else "No active target bounties configured. Add a WANTED threshold trigger above."
            )
        )
        st.info(empty_msg)
        return

    for alert in list(alerts):
        alert_id = alert.get("id", f"{alert['symbol']}_{alert['created']}")
        metrics, err = get_stock_analysis(alert["symbol"])

        col_card, col_del = st.columns([5, 1])
        with col_card:
            if metrics:
                live_p = float(metrics["close"])
                triggered = (
                    (live_p >= alert["target"])
                    if alert["condition"] == "Crosses Above"
                    else (live_p <= alert["target"])
                )
                if triggered:
                    if default_pro:
                        st.markdown(
                            f'<div class="wanted-alert-flash">'
                            f'<div style="color:#10b981; font-size:0.84rem; font-weight:700;">'
                            f"● PRICE ALERT TRIGGERED</div>"
                            f'<div style="color:#f8fafc; font-size:0.95rem; margin-top:0.22rem;">'
                            f'<strong>{html.escape(alert["name"])} ({html.escape(alert["symbol"])})</strong> — '
                            f'{html.escape(alert["condition"])} ₹{alert["target"]:,.2f} | '
                            f'<span style="color:#10b981; font-weight:700;">Spot: ₹{live_p:,.2f}</span>'
                            f"</div></div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        banner_title = (
                            "☢️ RADIATION THRESHOLD BREACHED // EMERGENCY ALARM · ⚠️⚠️⚠️⚠️⚠️⚠️"
                            if doomsday
                            else "🚨 TARGET TRIGGERED / WANTED · ★★★★★★"
                        )
                        banner_head_color = "#ff4500" if doomsday else "#fee440"
                        live_accent = "#39ff14" if doomsday else "#00f5d4"
                        st.markdown(
                            f'<div class="wanted-alert-flash">'
                            f'<div style="font-family:\'Orbitron\',sans-serif; color:{banner_head_color}; font-size:0.84rem; font-weight:800; letter-spacing:0.06em;">'
                            f'{banner_title}</div>'
                            f'<div style="font-family:\'Share Tech Mono\',monospace; color:#ffffff; font-size:0.95rem; margin-top:0.25rem;">'
                            f'<strong>{html.escape(alert["name"])} ({html.escape(alert["symbol"])})</strong> — '
                            f'{html.escape(alert["condition"])} ₹{alert["target"]:,.2f} | '
                            f'<span style="color:{live_accent}; font-weight:700;">LIVE: ₹{live_p:,.2f}</span>'
                            f"</div></div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.info(
                        f"**{alert['name']} ({alert['symbol']})** | "
                        f"{alert['condition']} ₹{alert['target']:,.2f} | "
                        f"Spot: ₹{live_p:,.2f} · Monitoring..."
                    )
            else:
                st.warning(
                    f"**{alert['name']} ({alert['symbol']})** — "
                    f"Target: ₹{alert['target']:,.2f} | Live feed temporarily unavailable ({err or 'timeout'})."
                )
        with col_del:
            if st.button("Delete", key=f"del_{alert_id}", width="stretch"):
                remove_price_alert(alert_id)
                st.rerun()
