"""Module 4: Virtual Paper Trading Simulator."""

from __future__ import annotations

import math
import pandas as pd
import streamlit as st

from src.constants import INITIAL_VIRTUAL_CAPITAL, NSE_STOCKS
from src.services.market_data import get_stock_analysis
from src.state import execute_buy_order, execute_sell_order, reset_paper_portfolio
from src.styles import render_kpi_grid, render_page_header, render_signal_badge


def render_paper_trading() -> None:
    """Render risk-free virtual paper trading simulator with live P&L tracking."""
    render_page_header(
        title="💼 Virtual Paper Trading Simulator",
        subtitle="Practice trading live NSE equities with ₹1,00,000 risk-free virtual balance",
        badge="PAPER TRADING SANDBOX",
    )

    portfolio = st.session_state["portfolio"]
    live_prices: dict[str, float] = {}
    holdings_value = 0.0

    for sym, pos in portfolio.items():
        metrics_pos, _ = get_stock_analysis(sym)
        curr_price = metrics_pos["close"] if metrics_pos else float(pos["buy_price"])
        live_prices[sym] = curr_price
        holdings_value += curr_price * pos["qty"]

    cash_balance = float(st.session_state["cash_balance"])
    total_net_worth = cash_balance + holdings_value
    total_pnl = total_net_worth - INITIAL_VIRTUAL_CAPITAL
    total_pnl_pct = (total_pnl / INITIAL_VIRTUAL_CAPITAL) * 100

    render_kpi_grid(
        [
            {
                "label": "Available Cash",
                "value": f"₹{cash_balance:,.2f}",
                "delta": f"{(cash_balance / total_net_worth) * 100:.1f}% liquid" if total_net_worth else "0%",
                "tone": "neutral",
            },
            {
                "label": "Holdings Value",
                "value": f"₹{holdings_value:,.2f}",
                "delta": f"{len(portfolio)} active positions",
                "tone": "neutral",
            },
            {
                "label": "Total Net Worth",
                "value": f"₹{total_net_worth:,.2f}",
                "delta": f"₹{total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)",
                "tone": "up" if total_pnl >= 0 else "down",
            },
        ]
    )

    st.subheader("🛒 Execute New Order")
    trade_name = st.selectbox("Select Stock to Trade:", list(NSE_STOCKS.keys()), key="paper_trade_stock")
    trade_sym = NSE_STOCKS[trade_name]

    trade_metric, trade_err = get_stock_analysis(trade_sym)
    if trade_err or not trade_metric:
        st.error(f"Could not fetch live quote for {trade_name}: {trade_err or 'Unavailable'}")
    else:
        live_price = float(trade_metric["close"])
        held_qty = int(portfolio.get(trade_sym, {}).get("qty", 0))
        max_affordable = math.floor(cash_balance / live_price) if live_price > 0 else 0

        badge_html = render_signal_badge(trade_metric["signal"], trade_metric["confidence"])
        st.markdown(
            f'<div class="surface-card" style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:0.75rem;">'
            f'<div><span style="color:#94a3b8; font-size:0.82rem;">LIVE QUOTE</span><br/>'
            f'<strong style="font-size:1.15rem;">{trade_name} ({trade_sym})</strong> — '
            f'<strong style="color:#38bdf8; font-size:1.15rem;">₹{live_price:,.2f}</strong></div>'
            f'<div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap;">'
            f'<span style="color:#cbd5e1; font-size:0.85rem;">Owned: <strong>{held_qty}</strong> · Max Buy: <strong>{max_affordable}</strong></span>'
            f"{badge_html}"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        col_qty, col_val = st.columns([1, 1])
        with col_qty:
            order_qty = int(
                st.number_input("Shares Quantity", min_value=1, value=10, step=1, key="paper_qty")
            )
        order_val = order_qty * live_price
        with col_val:
            st.markdown(
                f'<div class="surface-card" style="padding:0.7rem 1rem; margin-top:1.45rem;">'
                f'<span style="color:#94a3b8; font-size:0.8rem;">ESTIMATED ORDER VALUE</span><br/>'
                f'<strong style="font-size:1.15rem; font-variant-numeric:tabular-nums;">₹{order_val:,.2f}</strong>'
                f"</div>",
                unsafe_allow_html=True,
            )

        can_buy = cash_balance >= order_val
        can_sell = held_qty >= order_qty

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(
                "🟢 BUY Shares",
                width="stretch",
                disabled=not can_buy,
                type="primary",
            ):
                ok, msg = execute_buy_order(trade_sym, trade_name, order_qty, live_price)
                if ok:
                    st.toast(msg, icon="🟢")
                    st.rerun()
                else:
                    st.error(msg)
            if not can_buy:
                st.caption("Insufficient cash for this quantity.")

        with col_btn2:
            if st.button("🔴 SELL Shares", width="stretch", disabled=not can_sell):
                ok, msg = execute_sell_order(trade_sym, trade_name, order_qty, live_price)
                if ok:
                    st.toast(msg, icon="🔴")
                    st.rerun()
                else:
                    st.error(msg)
            if not can_sell:
                st.caption(f"You hold {held_qty} shares of this stock.")

    st.markdown("---")

    st.subheader("📁 Current Portfolio Holdings")
    if portfolio:
        port_records = []
        for s_sym, data in portfolio.items():
            c_price = live_prices.get(s_sym, float(data["buy_price"]))
            buy_price = float(data["buy_price"])
            qty = int(data["qty"])
            cur_val = c_price * qty
            pnl = (c_price - buy_price) * qty
            pnl_pct = ((c_price - buy_price) / buy_price) * 100 if buy_price > 0 else 0.0

            port_records.append(
                {
                    "Stock": data.get("name", s_sym),
                    "Symbol": s_sym.replace(".NS", "").replace(".BO", ""),
                    "Quantity": qty,
                    "Avg Buy Price": round(buy_price, 2),
                    "Live Price": round(c_price, 2),
                    "Position Value": round(cur_val, 2),
                    "Unrealized P&L": round(pnl, 2),
                    "P&L %": round(pnl_pct, 2),
                }
            )
        st.dataframe(
            pd.DataFrame(port_records),
            width="stretch",
            hide_index=True,
            column_config={
                "Avg Buy Price": st.column_config.NumberColumn(format="₹%.2f"),
                "Live Price": st.column_config.NumberColumn(format="₹%.2f"),
                "Position Value": st.column_config.NumberColumn(format="₹%.2f"),
                "Unrealized P&L": st.column_config.NumberColumn(format="₹%.2f"),
                "P&L %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )
    else:
        st.info("No active holdings. Execute a BUY order above to start building your portfolio.")

    if st.session_state["trade_history"]:
        with st.expander("📜 Order Execution Log", expanded=False):
            history_df = pd.DataFrame(list(reversed(st.session_state["trade_history"])))
            st.dataframe(
                history_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Price": st.column_config.NumberColumn(format="₹%.2f"),
                    "Total": st.column_config.NumberColumn(format="₹%.2f"),
                },
            )

    if st.button("🔄 Reset Portfolio to ₹1,00,000 Starting Cash"):
        reset_paper_portfolio()
        st.toast("Portfolio reset to ₹1,00,000!", icon="🔄")
        st.rerun()
