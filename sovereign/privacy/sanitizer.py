"""Local Privacy Sanitizer.

Prevents proprietary source code secrets, tokens, API keys, credentials,
and internal infrastructure details from leaving the local perimeter.
"""

import re
from typing import Dict, Tuple


class PrivacySanitizer:
    def __init__(self):
        self._token_map: Dict[str, str] = {}
        self._reverse_map: Dict[str, str] = {}
        self._counter: int = 0

        # Regex patterns for common credentials and sensitive tokens
        self._patterns = [
            # High-entropy API keys (OpenAI, AWS, GitHub, Nebius, etc.)
            (
                "KEY",
                re.compile(
                    r"(?:api[_-]?key|secret|token|password|pass|pwd|auth)[\s:=]+['\"]?([a-zA-Z0-9_\-\.]{16,})['\"]?",
                    re.IGNORECASE,
                ),
            ),
            # Bearer tokens
            ("BEARER", re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE)),
            # Private keys
            (
                "PRIVKEY",
                re.compile(
                    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[^-]+-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                    re.DOTALL,
                ),
            ),
            # Internal IP addresses (RFC 1918)
            (
                "IP",
                re.compile(
                    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})\b"
                ),
            ),
            # Email addresses
            (
                "EMAIL",
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
            ),
        ]

    def sanitize(self, text: str) -> Tuple[str, int]:
        """Sanitizes text by replacing sensitive patterns with pseudo-tokens.

        Returns (sanitized_text, count_of_redactions).
        """
        if not text:
            return "", 0

        sanitized = text
        redaction_count = 0

        for label, pattern in self._patterns:
            def replacer(match):
                nonlocal redaction_count
                sensitive_val = match.group(1) if match.groups() else match.group(0)

                # Return existing pseudonym token if already mapped
                if sensitive_val in self._token_map:
                    token = self._token_map[sensitive_val]
                else:
                    self._counter += 1
                    token = f"[SOVEREIGN_REDACTED_{label}_{self._counter:03d}]"
                    self._token_map[sensitive_val] = token
                    self._reverse_map[token] = sensitive_val

                redaction_count += 1
                # Replace only the captured sensitive group, preserving formatting
                full_match = match.group(0)
                if match.groups():
                    return full_match.replace(match.group(1), token)
                return token

            sanitized = pattern.sub(replacer, sanitized)

        return sanitized, redaction_count

    def restore(self, text: str) -> str:
        """Restores pseudo-tokens back to their original values locally."""
        if not text:
            return ""
        restored = text
        for token, original in self._reverse_map.items():
            restored = restored.replace(token, original)
        return restored

    def clear(self):
        """Clears the token map."""
        self._token_map.clear()
        self._reverse_map.clear()
        self._counter = 0
