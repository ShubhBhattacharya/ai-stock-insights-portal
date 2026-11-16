"""Unit and integration tests for authentication and password security."""

import pytest
from src.services.db import (
    authenticate_user,
    hash_password,
    init_db,
    register_user,
    set_database_path,
    validate_password_strength,
    validate_username,
    verify_password,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Use an isolated in-memory shared database for tests."""
    set_database_path(":memory:")
    init_db()


class TestPasswordHashing:
    def test_hash_and_verify_correct_password(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password_fails(self):
        hashed = hash_password("CorrectPassword123")
        assert verify_password("WrongPassword456", hashed) is False

    def test_empty_password_raises_error(self):
        with pytest.raises(ValueError):
            hash_password("")


class TestInputValidation:
    def test_valid_usernames(self):
        valid = ["admin", "trader_01", "shubh-b", "InvestUser"]
        for uname in valid:
            ok, err = validate_username(uname)
            assert ok is True, f"Failed for {uname}: {err}"

    def test_invalid_usernames(self):
        invalid = ["", "ab", "user@domain.com", "user name", "a" * 30]
        for uname in invalid:
            ok, err = validate_username(uname)
            assert ok is False, f"Expected invalid for {uname}"

    def test_password_strength_validation(self):
        # Empty
        assert validate_password_strength("")[0] is False
        # Too short (<12 chars)
        assert validate_password_strength("123")[0] is False
        assert validate_password_strength("Short1!")[0] is False
        assert validate_password_strength("Pass1234")[0] is False
        # Missing digits and special characters
        assert validate_password_strength("abcdefghijklmnop")[0] is False
        # Missing letters
        assert validate_password_strength("12345678901234")[0] is False
        # Valid strong passwords (12+ chars, mixed)
        assert validate_password_strength("SecurePass123")[0] is True
        assert validate_password_strength("EvaluatorDemo#2026!")[0] is True


class TestAuthenticationFlows:
    def test_register_and_authenticate_new_user(self):
        ok, msg, user = register_user("portfolio_king", "SecurePass123#")
        assert ok is True
        assert user is not None
        assert user["username"] == "portfolio_king"
        assert user["id"] > 0

        # Authenticate with correct credentials
        auth_ok, auth_msg, auth_user = authenticate_user("portfolio_king", "SecurePass123#")
        assert auth_ok is True
        assert auth_user["id"] == user["id"]

    def test_duplicate_registration_prevented(self):
        ok1, _, _ = register_user("unique_runner", "SecurePass123#")
        assert ok1 is True
        ok2, msg2, _ = register_user("unique_runner", "DifferentPass456!")
        assert ok2 is False
        assert "already taken" in msg2.lower()

    def test_invalid_login_credentials(self):
        register_user("safe_user", "CorrectKey123#")
        ok, msg, user = authenticate_user("safe_user", "WrongKey456!")
        assert ok is False
        assert user is None
        assert "invalid" in msg.lower()

    def test_nonexistent_user_safe_error(self):
        ok, msg, user = authenticate_user("completely_unknown_user", "SomeKey123#")
        assert ok is False
        assert user is None
        # Does not leak whether account exists
        assert "invalid" in msg.lower()

    def test_default_seeded_accounts_available(self):
        seeded = [
            ("evaluator", "EvaluatorDemo#2026!"),
            ("shubh", "ShubhPortfolio#2026!"),
            ("rohit", "RohitIndicator#2026!"),
            ("utkarsh", "UtkarshArchitect#2026!"),
        ]
        for user, pwd in seeded:
            ok, msg, u = authenticate_user(user, pwd)
            assert ok is True, f"Default account {user} failed authentication: {msg}"
            assert u is not None

    def test_registration_prevents_privilege_escalation(self):
        # Even if a user attempts to request an admin role during registration, role must be sanitized
        ok, _, u = register_user("sneaky_admin_attempt", "SecurePass123#", role="admin")
        assert ok is True
        assert u["role"] == "user"

    def test_failed_evaluator_auth_never_bypasses(self):
        # Evaluator account with wrong password must never authenticate
        ok, msg, u = authenticate_user("evaluator", "WrongEvaluatorPass123!")
        assert ok is False
        assert u is None

