"""Centralized Streamlit session state initialization and mutations."""

from __future__ import annotations

import datetime
from typing import Any
import streamlit as st

from src.constants import INITIAL_VIRTUAL_CAPITAL, NAV_ITEMS
from src.services.db import (
    db_add_price_alert,
    db_execute_buy_order,
    db_execute_sell_order,
    db_remove_price_alert,
    db_reset_portfolio,
    get_user_alerts,
    get_user_portfolio,
    get_user_theme,
    init_db,
    set_user_theme,
)


def _normalize_portal_theme(edition: str | None) -> str:
    """Normalize any edition/theme label to 'DEFAULT', 'GTA VI', or 'DOOMSDAY'."""
    val = str(edition or "GTA VI").strip().upper()
    if val in {"DEFAULT", "PRO", "STANDARD", "PRO STANDARD", "DEFAULT (PRO STANDARD)"}:
        return "DEFAULT"
    if "DOOMSDAY" in val or "APOCALYPSE" in val:
        return "DOOMSDAY"
    return "GTA VI"


def init_session_state() -> None:
    """Ensure all required session state keys exist with safe defaults and active DB connection."""
    init_db()

    defaults: dict[str, Any] = {
        "authenticated": False,
        "username": "",
        "user_id": None,
        "role": "guest",
        "transitioning": False,
        "edition_transitioning": False,
        "portal_theme": "GTA VI",
        "world_edition": "GTA VI",
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
        "home_hero_search_input": "",
        "single_stock_symbol": "RELIANCE.NS",
        "single_stock_select": "Reliance Industries",
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

    # If already authenticated, refresh from persistent database
    user_id = st.session_state.get("user_id")
    if st.session_state.get("authenticated") and user_id is not None:
        sync_user_state_from_db(user_id)


def sync_user_state_from_db(user_id: int) -> None:
    """Synchronize user's portfolio, trade history, alerts, and theme preferences from the database."""
    port_data = get_user_portfolio(user_id)
    st.session_state["cash_balance"] = port_data["cash_balance"]
    st.session_state["portfolio"] = port_data["portfolio"]
    st.session_state["trade_history"] = port_data["trade_history"]
    st.session_state["alerts"] = get_user_alerts(user_id)


def get_portal_theme() -> str:
    """Return active portal theme: 'DEFAULT', 'GTA VI', or 'DOOMSDAY'."""
    return _normalize_portal_theme(
        st.session_state.get("portal_theme", st.session_state.get("world_edition", "GTA VI"))
    )


def is_default_theme() -> bool:
    """Return True when active portal theme is Default (Pro Standard)."""
    return get_portal_theme() == "DEFAULT"


def login_as(
    username: str,
    user_id: int | None = None,
    role: str = "user",
    trigger_transition: bool = True,
) -> None:
    """Mark the current session as authenticated, load user records, and trigger transition."""
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id
    st.session_state["role"] = role
    st.session_state["transitioning"] = trigger_transition

    if user_id is not None:
        sync_user_state_from_db(user_id)
        saved_theme = get_user_theme(user_id)
        if saved_theme:
            st.session_state["portal_theme"] = _normalize_portal_theme(saved_theme)
            st.session_state["world_edition"] = st.session_state["portal_theme"]


def logout() -> None:
    """Clear authentication, reset user identity, and restore clean session state."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["user_id"] = None
    st.session_state["role"] = "guest"
    st.session_state["cash_balance"] = INITIAL_VIRTUAL_CAPITAL
    st.session_state["portfolio"] = {}
    st.session_state["trade_history"] = []
    st.session_state["alerts"] = []
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
    """Switch active portal theme ('DEFAULT', 'GTA VI', or 'DOOMSDAY') and persist in DB."""
    current = get_portal_theme()
    normalized = _normalize_portal_theme(edition)
    st.session_state["portal_theme"] = normalized
    st.session_state["world_edition"] = normalized

    user_id = st.session_state.get("user_id")
    if user_id is not None:
        set_user_theme(user_id, normalized)

    if normalized == "DOOMSDAY" and current != "DOOMSDAY":
        st.session_state["edition_transitioning"] = True
    else:
        st.session_state["edition_transitioning"] = False


def reset_paper_portfolio() -> None:
    """Restore virtual paper-trading account back to starting capital in database and state."""
    user_id = st.session_state.get("user_id")
    if user_id is not None:
        db_reset_portfolio(user_id)
        sync_user_state_from_db(user_id)
    else:
        st.session_state["cash_balance"] = INITIAL_VIRTUAL_CAPITAL
        st.session_state["portfolio"] = {}
        st.session_state["trade_history"] = []


def execute_buy_order(symbol: str, stock_name: str, qty: int, price: float) -> tuple[bool, str]:
    """Execute a virtual BUY order atomically in the database and synchronize session state."""
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive numbers."

    user_id = st.session_state.get("user_id")
    if user_id is not None:
        ok, msg = db_execute_buy_order(user_id, symbol, stock_name, qty, price)
        if ok:
            sync_user_state_from_db(user_id)
        return ok, msg

    # Fallback for transient demo session
    total_cost = round(qty * price, 2)
    if st.session_state["cash_balance"] < total_cost:
        return False, "Insufficient cash balance for this order."

    st.session_state["cash_balance"] = round(st.session_state["cash_balance"] - total_cost, 2)
    portfolio = st.session_state["portfolio"]
    if symbol in portfolio:
        prev_qty = portfolio[symbol]["qty"]
        prev_avg = portfolio[symbol]["buy_price"]
        new_qty = prev_qty + qty
        new_avg = round(((prev_qty * prev_avg) + total_cost) / new_qty, 2)
        portfolio[symbol] = {"name": stock_name, "qty": new_qty, "buy_price": new_avg}
    else:
        portfolio[symbol] = {"name": stock_name, "qty": qty, "buy_price": round(price, 2)}

    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    st.session_state["trade_history"].append(
        {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": "BUY",
            "Stock": stock_name,
            "Symbol": clean_sym,
            "Quantity": int(qty),
            "Price": round(price, 2),
            "Total": total_cost,
        }
    )
    return True, f"Bought {qty} shares of {stock_name} at ₹{price:,.2f}."


def execute_sell_order(symbol: str, stock_name: str, qty: int, price: float) -> tuple[bool, str]:
    """Execute a virtual SELL order atomically in the database and synchronize session state."""
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive numbers."

    user_id = st.session_state.get("user_id")
    if user_id is not None:
        ok, msg = db_execute_sell_order(user_id, symbol, stock_name, qty, price)
        if ok:
            sync_user_state_from_db(user_id)
        return ok, msg

    # Fallback for transient demo session
    portfolio = st.session_state["portfolio"]
    if symbol not in portfolio or portfolio[symbol]["qty"] < qty:
        return False, "You do not hold enough shares of this stock to sell."

    total_proceeds = round(qty * price, 2)
    st.session_state["cash_balance"] = round(st.session_state["cash_balance"] + total_proceeds, 2)
    portfolio[symbol]["qty"] -= qty
    if portfolio[symbol]["qty"] == 0:
        del portfolio[symbol]

    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    st.session_state["trade_history"].append(
        {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": "SELL",
            "Stock": stock_name,
            "Symbol": clean_sym,
            "Quantity": int(qty),
            "Price": round(price, 2),
            "Total": total_proceeds,
        }
    )
    return True, f"Sold {qty} shares of {stock_name} at ₹{price:,.2f}."


def add_price_alert(name: str, symbol: str, condition: str, target: float) -> tuple[bool, str]:
    """Create a new price alert persisted in the database."""
    if target <= 0:
        return False, "Target price must be positive."

    user_id = st.session_state.get("user_id")
    if user_id is not None:
        ok, msg, _ = db_add_price_alert(user_id, name, symbol, condition, target)
        if ok:
            st.session_state["alerts"] = get_user_alerts(user_id)
        return ok, msg

    import uuid
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
    return True, f"Price alert set for {name} ({condition} ₹{target:,.2f})."


def remove_price_alert(alert_id: str) -> tuple[bool, str]:
    """Delete an alert by its unique ID from the database and session state."""
    user_id = st.session_state.get("user_id")
    if user_id is not None:
        ok, msg = db_remove_price_alert(user_id, alert_id)
        if ok:
            st.session_state["alerts"] = get_user_alerts(user_id)
        return ok, msg

    st.session_state["alerts"] = [
        alert for alert in st.session_state["alerts"] if alert.get("id") != alert_id
    ]
    return True, "Alert removed."


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
