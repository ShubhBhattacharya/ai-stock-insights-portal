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
        assert validate_password_strength("")[0] is False
        assert validate_password_strength("123")[0] is False
        assert validate_password_strength("1234")[0] is True
        assert validate_password_strength("StrongPassword123")[0] is True


class TestAuthenticationFlows:
    def test_register_and_authenticate_new_user(self):
        ok, msg, user = register_user("portfolio_king", "SecurePass123")
        assert ok is True
        assert user is not None
        assert user["username"] == "portfolio_king"
        assert user["id"] > 0

        # Authenticate with correct credentials
        auth_ok, auth_msg, auth_user = authenticate_user("portfolio_king", "SecurePass123")
        assert auth_ok is True
        assert auth_user["id"] == user["id"]

    def test_duplicate_registration_prevented(self):
        ok1, _, _ = register_user("unique_runner", "Pass1234")
        assert ok1 is True
        ok2, msg2, _ = register_user("unique_runner", "Pass5678")
        assert ok2 is False
        assert "already taken" in msg2.lower()

    def test_invalid_login_credentials(self):
        register_user("safe_user", "CorrectKey123")
        ok, msg, user = authenticate_user("safe_user", "WrongKey456")
        assert ok is False
        assert user is None
        assert "invalid" in msg.lower()

    def test_nonexistent_user_safe_error(self):
        ok, msg, user = authenticate_user("completely_unknown_user", "SomeKey123")
        assert ok is False
        assert user is None
        # Does not leak whether account exists
        assert "invalid" in msg.lower()

    def test_default_seeded_accounts_available(self):
        for user, pwd in [("admin", "admin123"), ("evaluator", "evaluator123")]:
            ok, msg, u = authenticate_user(user, pwd)
            assert ok is True, f"Default account {user} failed authentication: {msg}"
            assert u is not None
