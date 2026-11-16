"""Unit tests for AI Stock Tutor, symbol extraction, speech sanitization, and fallback."""

from src.services.tutor import (
    _extract_mentioned_symbols,
    _is_hinglish,
    generate_tutor_turn,
    sanitize_speech_text,
)


class TestTutorEngine:
    def test_extract_explicit_symbols(self):
        query = "Can you analyze RELIANCE.NS and TCS.NS today?"
        syms = _extract_mentioned_symbols(query)
        assert "RELIANCE.NS" in syms
        assert "TCS.NS" in syms

    def test_extract_natural_company_names(self):
        query = "Tell me about Infosys and HDFC Bank performance"
        syms = _extract_mentioned_symbols(query)
        assert "INFY.NS" in syms
        assert "HDFCBANK.NS" in syms

    def test_hinglish_detection(self):
        assert _is_hinglish("Reliance ka RSI kaisa hai bhai?") is True
        assert _is_hinglish("What is the current 50 SMA for TCS?") is False

    def test_speech_sanitizer(self):
        raw = "### 📈 High Alert: [Reliance](https://nse.com) is at ₹2,500.00! // BUY"
        cleaned = sanitize_speech_text(raw)
        assert "₹" not in cleaned
        assert "Rupees" in cleaned
        assert "###" not in cleaned
        assert "https://" not in cleaned

    def test_educational_disclaimer_and_empty_query(self):
        reply, mood, scans = generate_tutor_turn("", edition="DEFAULT")
        assert len(reply) > 0
        assert mood == "neutral"
