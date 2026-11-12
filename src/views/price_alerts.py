"""Module 6: Real-Time Price Alerts & Trigger System."""

from __future__ import annotations

import streamlit as st

from src.constants import NSE_STOCKS
from src.services.market_data import get_stock_analysis
from src.state import add_price_alert, remove_price_alert
from src.styles import render_page_header


def _sync_alert_default_target() -> None:
    """Suggest a realistic target price near the newly selected stock's live close."""
    name = st.session_state.get("alert_stock_select")
    if name in NSE_STOCKS:
        metrics, _ = get_stock_analysis(NSE_STOCKS[name])
        if metrics:
            st.session_state["alert_target_price"] = round(float(metrics["close"]) * 1.02, 2)


def render_price_alerts() -> None:
    """Render target price alert creation and live monitoring cards."""
    render_page_header(
        title="🚨 Real-Time Price Alerts & Trigger System",
        subtitle="Set threshold price targets with live trigger status indicators",
        badge="LIVE THRESHOLD MONITOR",
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
            "Select Target Stock:",
            stock_names,
            key="alert_stock_select",
            on_change=_sync_alert_default_target,
        )
        alert_sym = NSE_STOCKS[alert_name]
    with col_a2:
        direction = st.selectbox("Condition:", ["Crosses Above", "Falls Below"])
    with col_a3:
        target = float(
            st.number_input(
                "Target Price (INR):",
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
            f"Current market price for **{alert_name}**: **₹{live_close:,.2f}** "
            f"(Target is {diff_pct:+.2f}% from current price)"
        )

    if st.button("Set New Price Alert", type="primary"):
        add_price_alert(alert_name, alert_sym, direction, target)
        st.toast(f"Alert added for {alert_name} at ₹{target:,.2f}", icon="🔔")

    st.markdown("---")
    st.subheader("🔔 Active Alerts Monitor")

    alerts = st.session_state["alerts"]
    if not alerts:
        st.info("No active alerts. Configure one above to receive price alerts.")
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
                status_badge = "🚨 TRIGGERED!" if triggered else "⏳ Monitoring..."
                message = (
                    f"**{alert['name']} ({alert['symbol']})** — "
                    f"{alert['condition']} ₹{alert['target']:,.2f} | "
                    f"Live: ₹{live_p:,.2f} ➔ **{status_badge}**"
                )
                if triggered:
                    st.error(message)
                else:
                    st.info(message)
            else:
                st.warning(
                    f"**{alert['name']} ({alert['symbol']})** — "
                    f"Target: ₹{alert['target']:,.2f} | Live price temporarily unavailable ({err or 'timeout'})."
                )
        with col_del:
            if st.button("Delete", key=f"del_{alert_id}", width="stretch"):
                remove_price_alert(alert_id)
                st.rerun()
