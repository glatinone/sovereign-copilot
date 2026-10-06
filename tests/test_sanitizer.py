"""Unit tests for PrivacySanitizer."""

from sovereign.privacy.sanitizer import PrivacySanitizer


def test_sanitize_and_restore_credentials():
    sanitizer = PrivacySanitizer()
    code_with_secrets = """
    DATABASE_URL = "postgres://user:password=super_secret_1234567890@192.168.1.50:5432/db"
    API_KEY = "sk-proj-999888777666555444333222111"
    SUPPORT_EMAIL = "admin@internal.company.corp"
    """

    sanitized, count = sanitizer.sanitize(code_with_secrets)
    assert count >= 3
    assert "super_secret_1234567890" not in sanitized
    assert "sk-proj-999888777666555444333222111" not in sanitized
    assert "192.168.1.50" not in sanitized
    assert "[SOVEREIGN_REDACTED_" in sanitized

    # Verify restoration
    restored = sanitizer.restore(sanitized)
    assert "super_secret_1234567890" in restored
    assert "sk-proj-999888777666555444333222111" in restored
    assert "192.168.1.50" in restored


def test_benign_code_unchanged():
    sanitizer = PrivacySanitizer()
    clean_code = "def add(a: int, b: int) -> int:\n    return a + b"
    sanitized, count = sanitizer.sanitize(clean_code)
    assert count == 0
    assert sanitized == clean_code
