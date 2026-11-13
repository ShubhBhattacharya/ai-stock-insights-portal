"""Centralized Streamlit session state initialization and mutations."""

from __future__ import annotations

import datetime
import uuid
import streamlit as st

from src.constants import DEFAULT_USERS, INITIAL_VIRTUAL_CAPITAL, NAV_ITEMS


def _normalize_portal_theme(edition: str | None) -> str:
    """Normalize any edition/theme label to 'DEFAULT', 'GTA VI', or 'DOOMSDAY'."""
    val = str(edition or "GTA VI").strip().upper()
    if val in {"DEFAULT", "PRO", "STANDARD", "PRO STANDARD", "DEFAULT (PRO STANDARD)"}:
        return "DEFAULT"
    if "DOOMSDAY" in val or "APOCALYPSE" in val:
        return "DOOMSDAY"
    return "GTA VI"


def init_session_state() -> None:
    """Ensure all required session state keys exist with safe defaults."""
    defaults = {
        "authenticated": False,
        "transitioning": False,
        "edition_transitioning": False,
        "portal_theme": "GTA VI",
        "world_edition": "GTA VI",
        "username": "Guest User",
        "users": dict(DEFAULT_USERS),
        "cash_balance": INITIAL_VIRTUAL_CAPITAL,
        "portfolio": {},
        "trade_history": [],
        "alerts": [],
        "ifruit_open": False,
        "ifruit_feedback": "",
        "active_risk_heat": 0,
        "voice_enabled": True,
        "latest_bot_reply": "",
        "reply_id": "",
        "active_module": NAV_ITEMS[0],
        "prev_module": NAV_ITEMS[0],
        "module_selector": NAV_ITEMS[0],
        "show_gta_transition": False,
        "messages": [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your NSE Equity AI Assistant. Ask me about RSI, 50/200-SMA trends, "
                    "BUY/SELL signal rules, portfolio allocation, or any NSE-listed stock!"
                ),
            }
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Keep portal_theme and world_edition synchronized in session state
    st.session_state["portal_theme"] = _normalize_portal_theme(
        st.session_state.get("portal_theme", st.session_state.get("world_edition", "GTA VI"))
    )
    st.session_state["world_edition"] = st.session_state["portal_theme"]


def get_portal_theme() -> str:
    """Return active portal theme: 'DEFAULT', 'GTA VI', or 'DOOMSDAY'."""
    return _normalize_portal_theme(
        st.session_state.get("portal_theme", st.session_state.get("world_edition", "GTA VI"))
    )


def is_default_theme() -> bool:
    """Return True when active portal theme is Default (Pro Standard)."""
    return get_portal_theme() == "DEFAULT"


def login_as(username: str, trigger_transition: bool = True) -> None:
    """Mark the current session as authenticated and trigger the entry sequence."""
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["transitioning"] = trigger_transition


def logout() -> None:
    """Clear authentication and transition flags for the current session."""
    st.session_state["authenticated"] = False
    st.session_state["transitioning"] = False
    st.session_state["edition_transitioning"] = False
    st.session_state["show_gta_transition"] = False
    st.session_state["active_module"] = NAV_ITEMS[0]
    st.session_state["prev_module"] = NAV_ITEMS[0]
    st.session_state["module_selector"] = NAV_ITEMS[0]


def is_doomsday() -> bool:
    """Return True when the active world edition is Doomsday (Apocalypse)."""
    return get_portal_theme() == "DOOMSDAY"


def switch_world_edition(edition: str) -> None:
    """Switch active portal theme ('DEFAULT', 'GTA VI', or 'DOOMSDAY') seamlessly."""
    current = get_portal_theme()
    normalized = _normalize_portal_theme(edition)
    st.session_state["portal_theme"] = normalized
    st.session_state["world_edition"] = normalized
    if normalized == "DOOMSDAY" and current != "DOOMSDAY":
        st.session_state["edition_transitioning"] = True
    else:
        st.session_state["edition_transitioning"] = False


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


def set_context_risk_heat(stars: int) -> None:
    """Persist context-driven risk heat stars (1-6) in session state."""
    st.session_state["active_risk_heat"] = max(1, min(6, int(stars)))


def compute_dynamic_wanted_stars(context_heat: int | None = None) -> int:
    """Compute live 1-6 Wanted Level stars from portfolio exposure, alerts, and active risk heat."""
    portfolio = st.session_state.get("portfolio", {})
    alerts = st.session_state.get("alerts", [])
    cash_balance = float(st.session_state.get("cash_balance", INITIAL_VIRTUAL_CAPITAL))
    deployed_ratio = max(0.0, (INITIAL_VIRTUAL_CAPITAL - cash_balance) / INITIAL_VIRTUAL_CAPITAL)

    base_stars = 1
    if len(portfolio) >= 1 or deployed_ratio >= 0.15:
        base_stars += 1
    if len(portfolio) >= 3 or deployed_ratio >= 0.45:
        base_stars += 1
    if len(alerts) >= 1:
        base_stars += 1
    if len(alerts) >= 3:
        base_stars += 1

    heat = context_heat if context_heat is not None else int(st.session_state.get("active_risk_heat", 0))
    return max(1, min(6, max(base_stars, heat)))
