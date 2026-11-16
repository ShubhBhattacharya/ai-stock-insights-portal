"""Persistent database service for AI Stock Insights Portal.

Supports SQLite by default (stored at data/portal.db) with WAL mode, foreign keys,
and transactional safety. Provides user registration, password hashing (bcrypt / PBKDF2),
portfolio management, trade logging, and price alert persistence.
"""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any, Generator

try:
    import bcrypt  # type: ignore
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False
    bcrypt = None

from src.constants import DEFAULT_USERS, INITIAL_VIRTUAL_CAPITAL

_DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DEFAULT_DB_PATH = _DEFAULT_DB_DIR / "portal.db"

_CURRENT_DB_PATH: str = str(_DEFAULT_DB_PATH)
_MEM_HOLD_CONN: sqlite3.Connection | None = None


def set_database_path(path: str) -> None:
    """Override database file path (useful for tests or custom environment paths)."""
    global _CURRENT_DB_PATH, _MEM_HOLD_CONN
    if path == ":memory:":
        _CURRENT_DB_PATH = "file:memportal?mode=memory&cache=shared"
        _MEM_HOLD_CONN = sqlite3.connect(_CURRENT_DB_PATH, uri=True)
    else:
        _CURRENT_DB_PATH = str(path)
        if _MEM_HOLD_CONN:
            try:
                _MEM_HOLD_CONN.close()
            except Exception:
                pass
            _MEM_HOLD_CONN = None


def get_database_path() -> str:
    """Return active database file path."""
    return _CURRENT_DB_PATH


@contextlib.contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional database connection with Row factory and FKs enabled."""
    db_path = get_database_path()
    is_uri = db_path.startswith("file:")
    if not is_uri and db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=15.0, uri=is_uri)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        if not is_uri and db_path != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
        yield conn
    finally:
        conn.close()


# ==============================================================================
# PASSWORD SECURITY & HASHING
# ==============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt (or PBKDF2-HMAC-SHA256 with 200,000 rounds fallback)."""
    if not password:
        raise ValueError("Password cannot be empty.")

    if HAS_BCRYPT and bcrypt is not None:
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return "bcrypt$" + hashed_bytes.decode("utf-8")

    # Cryptographically secure PBKDF2 fallback
    salt_hex = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_hex.encode("utf-8"),
        200_000,
    )
    return f"pbkdf2$200000${salt_hex}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against stored hash using constant-time comparison."""
    if not password or not hashed:
        return False

    try:
        if hashed.startswith("bcrypt$") and HAS_BCRYPT and bcrypt is not None:
            raw_hash = hashed[len("bcrypt$") :].encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), raw_hash)

        if hashed.startswith("pbkdf2$"):
            parts = hashed.split("$")
            if len(parts) == 4:
                _, rounds_str, salt_hex, key_hex = parts
                rounds = int(rounds_str)
                key = hashlib.pbkdf2_hmac(
                    "sha256",
                    password.encode("utf-8"),
                    salt_hex.encode("utf-8"),
                    rounds,
                )
                return hmac.compare_digest(key.hex(), key_hex)

        # Legacy / fallback plaintext migration check (safely compared)
        return hmac.compare_digest(password, hashed)
    except Exception:
        return False


# ==============================================================================
# SCHEMA CREATION & INITIAL SEEDING
# ==============================================================================

def init_db(db_path: str | None = None) -> None:
    """Initialize database tables, indexes, and default verified demo accounts."""
    if db_path:
        set_database_path(db_path)

    with get_db_connection() as conn:
        with conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolios (
                    user_id INTEGER PRIMARY KEY,
                    cash_balance REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    buy_price REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (user_id, symbol),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    target REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    triggered_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    portal_theme TEXT NOT NULL DEFAULT 'GTA VI',
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
                CREATE INDEX IF NOT EXISTS idx_holdings_user_id ON holdings(user_id);
                CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
                """
            )

        # Seed default verified demo accounts if users table is empty
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()
        for uname, pwd in DEFAULT_USERS.items():
            cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
            row = cursor.fetchone()
            if not row:
                pw_hash = hash_password(pwd)
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                    (uname, pw_hash, "admin" if uname == "admin" else "user", now_str),
                )
                uid = cursor.lastrowid
                cursor.execute(
                    "INSERT OR IGNORE INTO portfolios (user_id, cash_balance, updated_at) VALUES (?, ?, ?)",
                    (uid, INITIAL_VIRTUAL_CAPITAL, now_str),
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO user_preferences (user_id, portal_theme, updated_at) VALUES (?, ?, ?)",
                    (uid, "GTA VI", now_str),
                )

        # Ensure Evaluator account exists for 1-click evaluator demo access
        cursor.execute("SELECT id FROM users WHERE username = ?", ("evaluator",))
        if not cursor.fetchone():
            pw_hash = hash_password("evaluator123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                ("evaluator", pw_hash, "evaluator", now_str),
            )
            eval_uid = cursor.lastrowid
            cursor.execute(
                "INSERT OR IGNORE INTO portfolios (user_id, cash_balance, updated_at) VALUES (?, ?, ?)",
                (eval_uid, INITIAL_VIRTUAL_CAPITAL, now_str),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO user_preferences (user_id, portal_theme, updated_at) VALUES (?, ?, ?)",
                (eval_uid, "GTA VI", now_str),
            )
        conn.commit()


# ==============================================================================
# USER AUTHENTICATION & REGISTRATION
# ==============================================================================

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,25}$")


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username length and character set."""
    clean = str(username or "").strip()
    if not clean:
        return False, "Username is required."
    if len(clean) < 3:
        return False, "Username must be at least 3 characters long."
    if len(clean) > 25:
        return False, "Username cannot exceed 25 characters."
    if not _USERNAME_PATTERN.match(clean):
        return False, "Username may only contain letters, numbers, underscores, and hyphens."
    return True, ""


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength (minimum length and non-empty check)."""
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters long."
    return True, ""


def register_user(
    username: str, password: str, role: str = "user"
) -> tuple[bool, str, dict[str, Any] | None]:
    """Register a new user, initialize their isolated virtual portfolio, and return user dict."""
    ok, err = validate_username(username)
    if not ok:
        return False, err, None

    ok_pw, err_pw = validate_password_strength(password)
    if not ok_pw:
        return False, err_pw, None

    clean_uname = username.strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (clean_uname,))
            if cursor.fetchone():
                return False, "Username is already taken.", None

            pw_hash = hash_password(password)
            with conn:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                    (clean_uname, pw_hash, role, now_str),
                )
                user_id = int(cursor.lastrowid)

                cursor.execute(
                    "INSERT INTO portfolios (user_id, cash_balance, updated_at) VALUES (?, ?, ?)",
                    (user_id, INITIAL_VIRTUAL_CAPITAL, now_str),
                )

                cursor.execute(
                    "INSERT INTO user_preferences (user_id, portal_theme, updated_at) VALUES (?, ?, ?)",
                    (user_id, "GTA VI", now_str),
                )

            return (
                True,
                "Account created successfully.",
                {"id": user_id, "username": clean_uname, "role": role},
            )
    except sqlite3.IntegrityError:
        return False, "Username is already taken.", None
    except Exception as exc:
        return False, f"Registration failed: {exc}", None


def authenticate_user(
    username: str, password: str
) -> tuple[bool, str, dict[str, Any] | None]:
    """Authenticate credentials against stored hash without leaking account existence."""
    clean_uname = str(username or "").strip()
    if not clean_uname or not password:
        return False, "Username and password are required.", None

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = ?",
                (clean_uname,),
            )
            row = cursor.fetchone()
            if not row:
                # Constant-time dummy verification to thwart timing attacks
                verify_password("dummy_password", hash_password("dummy_hash"))
                return False, "Invalid username or password.", None

            if verify_password(password, row["password_hash"]):
                return (
                    True,
                    "Authentication successful.",
                    {"id": row["id"], "username": row["username"], "role": row["role"]},
                )
            return False, "Invalid username or password.", None
    except Exception as exc:
        return False, "Authentication service temporarily unavailable.", None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Retrieve user details by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# ==============================================================================
# USER PREFERENCES & THEMES
# ==============================================================================

def get_user_theme(user_id: int) -> str:
    """Fetch user's saved portal theme preference ('DEFAULT', 'GTA VI', or 'DOOMSDAY')."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT portal_theme FROM user_preferences WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row["portal_theme"] if row else "GTA VI"


def set_user_theme(user_id: int, theme: str) -> None:
    """Persist user's portal theme preference."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO user_preferences (user_id, portal_theme, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET portal_theme = excluded.portal_theme, updated_at = excluded.updated_at
                """,
                (user_id, theme, now_str),
            )


# ==============================================================================
# PORTFOLIO & PAPER TRADING
# ==============================================================================

def get_user_portfolio(user_id: int) -> dict[str, Any]:
    """Retrieve a user's cash balance, current holdings, and full trade history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cash_balance FROM portfolios WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        cash = float(p_row["cash_balance"]) if p_row else INITIAL_VIRTUAL_CAPITAL

        cursor.execute(
            "SELECT symbol, stock_name, quantity, buy_price FROM holdings WHERE user_id = ?",
            (user_id,),
        )
        holdings: dict[str, dict[str, Any]] = {}
        for row in cursor.fetchall():
            holdings[row["symbol"]] = {
                "name": row["stock_name"],
                "qty": int(row["quantity"]),
                "buy_price": float(row["buy_price"]),
            }

        cursor.execute(
            """
            SELECT timestamp as Time, action as Action, stock_name as Stock,
                   symbol as Symbol, quantity as Quantity, price as Price, total as Total
            FROM trades WHERE user_id = ? ORDER BY id ASC
            """,
            (user_id,),
        )
        trades = [dict(r) for r in cursor.fetchall()]

        return {"cash_balance": cash, "portfolio": holdings, "trade_history": trades}


def db_execute_buy_order(
    user_id: int, symbol: str, stock_name: str, qty: int, price: float
) -> tuple[bool, str]:
    """Execute virtual BUY order atomically: validates balance, updates holdings & logs trade."""
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive numbers."

    total_cost = round(float(qty) * float(price), 2)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cash_balance FROM portfolios WHERE user_id = ?", (user_id,))
            p_row = cursor.fetchone()
            if not p_row:
                cursor.execute(
                    "INSERT INTO portfolios (user_id, cash_balance, updated_at) VALUES (?, ?, ?)",
                    (user_id, INITIAL_VIRTUAL_CAPITAL, now_str),
                )
                curr_cash = INITIAL_VIRTUAL_CAPITAL
            else:
                curr_cash = float(p_row["cash_balance"])

            if curr_cash < total_cost:
                return (
                    False,
                    f"Insufficient cash balance. Required: ₹{total_cost:,.2f}, Available: ₹{curr_cash:,.2f}.",
                )

            new_cash = round(curr_cash - total_cost, 2)
            cursor.execute(
                "UPDATE portfolios SET cash_balance = ?, updated_at = ? WHERE user_id = ?",
                (new_cash, now_str, user_id),
            )

            cursor.execute(
                "SELECT quantity, buy_price FROM holdings WHERE user_id = ? AND symbol = ?",
                (user_id, symbol),
            )
            h_row = cursor.fetchone()
            if h_row:
                prev_qty = int(h_row["quantity"])
                prev_avg = float(h_row["buy_price"])
                new_qty = prev_qty + qty
                new_avg = round(((prev_qty * prev_avg) + total_cost) / new_qty, 2)
                cursor.execute(
                    "UPDATE holdings SET quantity = ?, buy_price = ?, updated_at = ? WHERE user_id = ? AND symbol = ?",
                    (new_qty, new_avg, now_str, user_id, symbol),
                )
            else:
                cursor.execute(
                    "INSERT INTO holdings (user_id, symbol, stock_name, quantity, buy_price, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, symbol, stock_name, qty, round(price, 2), now_str),
                )

            clean_sym = symbol.replace(".NS", "").replace(".BO", "")
            cursor.execute(
                """
                INSERT INTO trades (user_id, timestamp, action, stock_name, symbol, quantity, price, total)
                VALUES (?, ?, 'BUY', ?, ?, ?, ?, ?)
                """,
                (user_id, now_str, stock_name, clean_sym, int(qty), round(price, 2), total_cost),
            )

    return True, f"Bought {qty} shares of {stock_name} at ₹{price:,.2f}."


def db_execute_sell_order(
    user_id: int, symbol: str, stock_name: str, qty: int, price: float
) -> tuple[bool, str]:
    """Execute virtual SELL order atomically: validates holdings, updates cash & logs trade."""
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive numbers."

    total_proceeds = round(float(qty) * float(price), 2)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quantity FROM holdings WHERE user_id = ? AND symbol = ?",
                (user_id, symbol),
            )
            h_row = cursor.fetchone()
            if not h_row or int(h_row["quantity"]) < qty:
                held = int(h_row["quantity"]) if h_row else 0
                return (
                    False,
                    f"You do not hold enough shares of {stock_name} to sell. Held: {held}, Requested: {qty}.",
                )

            current_qty = int(h_row["quantity"])
            rem_qty = current_qty - qty
            if rem_qty == 0:
                cursor.execute(
                    "DELETE FROM holdings WHERE user_id = ? AND symbol = ?", (user_id, symbol)
                )
            else:
                cursor.execute(
                    "UPDATE holdings SET quantity = ?, updated_at = ? WHERE user_id = ? AND symbol = ?",
                    (rem_qty, now_str, user_id, symbol),
                )

            cursor.execute("SELECT cash_balance FROM portfolios WHERE user_id = ?", (user_id,))
            p_row = cursor.fetchone()
            curr_cash = float(p_row["cash_balance"]) if p_row else INITIAL_VIRTUAL_CAPITAL
            new_cash = round(curr_cash + total_proceeds, 2)

            cursor.execute(
                "UPDATE portfolios SET cash_balance = ?, updated_at = ? WHERE user_id = ?",
                (new_cash, now_str, user_id),
            )

            clean_sym = symbol.replace(".NS", "").replace(".BO", "")
            cursor.execute(
                """
                INSERT INTO trades (user_id, timestamp, action, stock_name, symbol, quantity, price, total)
                VALUES (?, ?, 'SELL', ?, ?, ?, ?, ?)
                """,
                (user_id, now_str, stock_name, clean_sym, int(qty), round(price, 2), total_proceeds),
            )

    return True, f"Sold {qty} shares of {stock_name} at ₹{price:,.2f}."


def db_reset_portfolio(user_id: int) -> tuple[bool, str]:
    """Reset user's virtual paper portfolio to starting cash (₹100,000) and clear positions."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE portfolios SET cash_balance = ?, updated_at = ? WHERE user_id = ?",
                (INITIAL_VIRTUAL_CAPITAL, now_str, user_id),
            )
            cursor.execute("DELETE FROM holdings WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM trades WHERE user_id = ?", (user_id,))
    return True, "Paper portfolio has been reset to ₹100,000 virtual capital."


# ==============================================================================
# PRICE ALERTS PERSISTENCE
# ==============================================================================

def get_user_alerts(user_id: int) -> list[dict[str, Any]]:
    """Retrieve all price alerts configured by a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, symbol, condition, target, created_at as created, is_active, triggered_at
            FROM alerts WHERE user_id = ? ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


def db_add_price_alert(
    user_id: int, name: str, symbol: str, condition: str, target: float
) -> tuple[bool, str, str]:
    """Add a new price alert and return (success, message, alert_id)."""
    if target <= 0:
        return False, "Target price must be greater than zero.", ""

    alert_id = secrets.token_hex(6)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    with get_db_connection() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO alerts (id, user_id, symbol, name, condition, target, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (alert_id, user_id, symbol, name, condition, float(target), now_str),
            )
    return True, f"Price alert set for {name} ({condition} ₹{target:,.2f}).", alert_id


def db_remove_price_alert(user_id: int, alert_id: str) -> tuple[bool, str]:
    """Remove a user's price alert by ID."""
    with get_db_connection() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM alerts WHERE id = ? AND user_id = ?", (alert_id, user_id)
            )
            if cursor.rowcount > 0:
                return True, "Alert removed."
            return False, "Alert not found."


def db_trigger_price_alert(alert_id: str) -> bool:
    """Mark an alert as triggered."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE alerts SET is_active = 0, triggered_at = ? WHERE id = ?",
                (now_str, alert_id),
            )
            return cursor.rowcount > 0
