"""Unit and integration tests for database persistence, transactions, and user isolation."""

import pytest
from src.constants import INITIAL_VIRTUAL_CAPITAL
from src.services.db import (
    db_add_price_alert,
    db_execute_buy_order,
    db_execute_sell_order,
    db_remove_price_alert,
    db_reset_portfolio,
    db_trigger_price_alert,
    db_update_price_alert,
    get_user_alerts,
    get_user_portfolio,
    init_db,
    register_user,
    set_database_path,
)

TEST_PASSWORD = "StrongPassword2026!#"


@pytest.fixture(autouse=True)
def setup_test_db():
    set_database_path(":memory:")
    init_db()


class TestPortfolioTransactions:
    def test_buy_order_cash_and_holdings_update(self):
        _, _, u = register_user("trader_alpha", TEST_PASSWORD)
        uid = u["id"]

        ok, msg = db_execute_buy_order(uid, "RELIANCE.NS", "Reliance Industries", 10, 2500.0)
        assert ok is True
        port = get_user_portfolio(uid)
        assert port["cash_balance"] == INITIAL_VIRTUAL_CAPITAL - 25000.0
        assert "RELIANCE.NS" in port["portfolio"]
        assert port["portfolio"]["RELIANCE.NS"]["qty"] == 10
        assert port["portfolio"]["RELIANCE.NS"]["buy_price"] == 2500.0
        assert len(port["trade_history"]) == 1
        assert port["trade_history"][0]["Action"] == "BUY"

    def test_weighted_average_price_on_multiple_buys(self):
        _, _, u = register_user("trader_beta", TEST_PASSWORD)
        uid = u["id"]

        # Buy 10 shares @ 100
        db_execute_buy_order(uid, "TCS.NS", "TCS", 10, 100.0)
        # Buy 10 shares @ 200 -> Average should be (1000 + 2000) / 20 = 150.0
        db_execute_buy_order(uid, "TCS.NS", "TCS", 10, 200.0)

        port = get_user_portfolio(uid)
        assert port["portfolio"]["TCS.NS"]["qty"] == 20
        assert port["portfolio"]["TCS.NS"]["buy_price"] == 150.0

    def test_insufficient_cash_prevents_buy(self):
        _, _, u = register_user("trader_gamma", TEST_PASSWORD)
        uid = u["id"]

        # Attempt to buy more than ₹100,000 capital
        ok, msg = db_execute_buy_order(uid, "INFY.NS", "Infosys", 1000, 2000.0)
        assert ok is False
        assert "insufficient cash" in msg.lower()
        port = get_user_portfolio(uid)
        assert port["cash_balance"] == INITIAL_VIRTUAL_CAPITAL
        assert "INFY.NS" not in port["portfolio"]

    def test_partial_and_full_sell_orders(self):
        _, _, u = register_user("trader_delta", TEST_PASSWORD)
        uid = u["id"]

        db_execute_buy_order(uid, "HDFCBANK.NS", "HDFC Bank", 20, 1500.0)
        # Partial sell: 10 shares @ 1600.0
        ok_sell, _ = db_execute_sell_order(uid, "HDFCBANK.NS", "HDFC Bank", 10, 1600.0)
        assert ok_sell is True
        port = get_user_portfolio(uid)
        assert port["portfolio"]["HDFCBANK.NS"]["qty"] == 10
        assert port["cash_balance"] == (INITIAL_VIRTUAL_CAPITAL - 30000.0) + 16000.0

        # Full sell: remaining 10 shares
        db_execute_sell_order(uid, "HDFCBANK.NS", "HDFC Bank", 10, 1650.0)
        port2 = get_user_portfolio(uid)
        assert "HDFCBANK.NS" not in port2["portfolio"]

    def test_selling_unowned_shares_rejected(self):
        _, _, u = register_user("trader_epsilon", TEST_PASSWORD)
        uid = u["id"]

        ok, msg = db_execute_sell_order(uid, "SBIN.NS", "State Bank of India", 5, 800.0)
        assert ok is False
        assert "do not hold enough shares" in msg.lower()

    def test_portfolio_reset(self):
        _, _, u = register_user("trader_zeta", TEST_PASSWORD)
        uid = u["id"]
        db_execute_buy_order(uid, "LT.NS", "Larsen & Toubro", 5, 3000.0)
        db_reset_portfolio(uid)
        port = get_user_portfolio(uid)
        assert port["cash_balance"] == INITIAL_VIRTUAL_CAPITAL
        assert len(port["portfolio"]) == 0
        assert len(port["trade_history"]) == 0


class TestUserIsolation:
    def test_user_data_strictly_isolated(self):
        _, _, u1 = register_user("user_one", TEST_PASSWORD)
        _, _, u2 = register_user("user_two", TEST_PASSWORD)

        db_execute_buy_order(u1["id"], "TITAN.NS", "Titan", 5, 3000.0)

        port1 = get_user_portfolio(u1["id"])
        port2 = get_user_portfolio(u2["id"])

        assert "TITAN.NS" in port1["portfolio"]
        assert "TITAN.NS" not in port2["portfolio"]
        assert port2["cash_balance"] == INITIAL_VIRTUAL_CAPITAL


class TestAlertsPersistence:
    def test_alert_lifecycle(self):
        _, _, u = register_user("alert_watcher", TEST_PASSWORD)
        uid = u["id"]

        ok, msg, alert_id = db_add_price_alert(uid, "Reliance", "RELIANCE.NS", "Crosses Above", 2600.0)
        assert ok is True
        assert len(alert_id) > 0

        alerts = get_user_alerts(uid)
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "RELIANCE.NS"
        assert alerts[0]["target"] == 2600.0

        db_trigger_price_alert(alert_id)
        updated = get_user_alerts(uid)
        assert updated[0]["is_active"] == 0

        del_ok, _ = db_remove_price_alert(uid, alert_id)
        assert del_ok is True
        assert len(get_user_alerts(uid)) == 0

    def test_duplicate_alert_prevented(self):
        _, _, u = register_user("alert_dedup_user", TEST_PASSWORD)
        uid = u["id"]

        ok1, _, id1 = db_add_price_alert(uid, "Infosys", "INFY.NS", "Crosses Above", 1850.0)
        assert ok1 is True
        assert len(id1) > 0

        # Attempt to add exact duplicate active alert
        ok2, msg2, id2 = db_add_price_alert(uid, "Infosys", "INFY.NS", "Crosses Above", 1850.0)
        assert ok2 is False
        assert "already exists" in msg2.lower()

    def test_update_price_alert(self):
        _, _, u = register_user("alert_edit_user", TEST_PASSWORD)
        uid = u["id"]

        ok, _, alert_id = db_add_price_alert(uid, "TCS", "TCS.NS", "Crosses Above", 4000.0)
        assert ok is True

        up_ok, up_msg = db_update_price_alert(uid, alert_id, 4100.0, "Crosses Below")
        assert up_ok is True

        alerts = get_user_alerts(uid)
        assert len(alerts) == 1
        assert alerts[0]["target"] == 4100.0
        assert alerts[0]["condition"] == "Crosses Below"
