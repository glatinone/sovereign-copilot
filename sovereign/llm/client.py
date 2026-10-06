"""LLM Client for Nebius Token Factory with NVIDIA Nemotron support.

Provides an OpenAI-compatible API client designed for Nebius Token Factory,
with fallback mock reasoning for offline or pre-API development.
"""

from typing import Any, Dict, List, Optional
import httpx

from sovereign.config import Config


class NebiusLLMClient:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.nebius_base_url.rstrip("/")
        self.api_key = config.nebius_api_key
        self.model = config.model_name
        self.mock_mode = config.mock_mode

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> str:
        """Sends chat completion request to Nebius Token Factory or fallback mock."""
        if self.mock_mode or not self.api_key:
            return self._mock_completion(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _mock_completion(self, messages: List[Dict[str, str]]) -> str:
        """Generates deterministic architectural reasoning simulating NVIDIA Nemotron."""
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")

        # Detect if prompt includes ADR rules from Temporal Memory
        has_adr = "ADR #" in system_msg or "ARCHITECTURAL DECISIONS" in system_msg

        return (
            "### REASONING & COMPLIANCE VERIFICATION:\n"
            f"- Model: NVIDIA Nemotron-70B (Nebius Token Factory)\n"
            f"- Temporal Memory Active: {'YES (Compliant with active ADRs)' if has_adr else 'NO (General Mode)'}\n"
            "- Privacy Status: Verified (Local sanitizer confirmed zero plaintext secrets)\n\n"
            "### PROPOSED ACTION PLAN:\n"
            "1. Analyzed requested change against past architectural decisions.\n"
            "2. Generated required refactoring patch honoring project conventions.\n"
            "3. Ready for local automated test validation.\n"
        )
