"""Centralized Streamlit session state initialization and mutations."""

from __future__ import annotations

import datetime
import uuid
import streamlit as st

from src.constants import DEFAULT_USERS, INITIAL_VIRTUAL_CAPITAL


def init_session_state() -> None:
    """Ensure all required session state keys exist with safe defaults."""
    defaults = {
        "authenticated": False,
        "username": "Guest User",
        "users": dict(DEFAULT_USERS),
        "cash_balance": INITIAL_VIRTUAL_CAPITAL,
        "portfolio": {},
        "trade_history": [],
        "alerts": [],
        "messages": [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your AI Stock Tutor. Ask me any question about "
                    "technical indicators, financial metrics, or how the Buy/Sell rules work!"
                ),
            }
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_as(username: str) -> None:
    """Mark the current session as authenticated under the given display username."""
    st.session_state["authenticated"] = True
    st.session_state["username"] = username


def logout() -> None:
    """Clear authentication flag for the current session."""
    st.session_state["authenticated"] = False


def reset_paper_portfolio() -> None:
    """Restore virtual paper-trading account back to starting capital."""
    st.session_state["cash_balance"] = INITIAL_VIRTUAL_CAPITAL
    st.session_state["portfolio"] = {}
    st.session_state["trade_history"] = []


def execute_buy_order(symbol: str, stock_name: str, qty: int, price: float) -> tuple[bool, str]:
    """Execute a virtual BUY order and update cash, holdings, and trade log."""
    total_cost = qty * price
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive."
    if st.session_state["cash_balance"] < total_cost:
        return False, "Insufficient cash balance for this order."

    st.session_state["cash_balance"] -= total_cost
    portfolio = st.session_state["portfolio"]
    if symbol in portfolio:
        prev_qty = portfolio[symbol]["qty"]
        prev_avg = portfolio[symbol]["buy_price"]
        new_qty = prev_qty + qty
        new_avg = ((prev_qty * prev_avg) + total_cost) / new_qty
        portfolio[symbol] = {"name": stock_name, "qty": new_qty, "buy_price": new_avg}
    else:
        portfolio[symbol] = {"name": stock_name, "qty": qty, "buy_price": price}

    st.session_state["trade_history"].append(
        {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": "BUY",
            "Stock": stock_name,
            "Symbol": symbol.replace(".NS", "").replace(".BO", ""),
            "Quantity": int(qty),
            "Price": round(price, 2),
            "Total": round(total_cost, 2),
        }
    )
    return True, f"Bought {qty} shares of {stock_name} at ₹{price:,.2f}."


def execute_sell_order(symbol: str, stock_name: str, qty: int, price: float) -> tuple[bool, str]:
    """Execute a virtual SELL order and update cash, holdings, and trade log."""
    portfolio = st.session_state["portfolio"]
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive."
    if symbol not in portfolio or portfolio[symbol]["qty"] < qty:
        return False, "You do not hold enough shares of this stock to sell."

    total_proceeds = qty * price
    st.session_state["cash_balance"] += total_proceeds
    portfolio[symbol]["qty"] -= qty
    if portfolio[symbol]["qty"] == 0:
        del portfolio[symbol]

    st.session_state["trade_history"].append(
        {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": "SELL",
            "Stock": stock_name,
            "Symbol": symbol.replace(".NS", "").replace(".BO", ""),
            "Quantity": int(qty),
            "Price": round(price, 2),
            "Total": round(total_proceeds, 2),
        }
    )
    return True, f"Sold {qty} shares of {stock_name} at ₹{price:,.2f}."


def add_price_alert(name: str, symbol: str, condition: str, target: float) -> None:
    """Create a new price alert with a stable unique ID."""
    st.session_state["alerts"].append(
        {
            "id": uuid.uuid4().hex[:10],
            "name": name,
            "symbol": symbol,
            "condition": condition,
            "target": float(target),
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )


def remove_price_alert(alert_id: str) -> None:
    """Delete an alert by its unique ID."""
    st.session_state["alerts"] = [
        alert for alert in st.session_state["alerts"] if alert.get("id") != alert_id
    ]
