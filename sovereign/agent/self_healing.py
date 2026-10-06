"""Autonomous Self-Healing Refactoring Engine.

Implements iterative test-driven repair: executes code modifications, validates with
local test suites, and autonomously iterates if tests fail, strictly respecting
Temporal Architectural Memory constraints.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from sovereign.config import Config
from sovereign.privacy.sanitizer import PrivacySanitizer
from sovereign.memory.temporal_graph import TemporalMemory
from sovereign.llm.client import NebiusLLMClient
from sovereign.tools.git_tools import LocalToolExecutor
from sovereign.tools.tavily_search import TavilySearchTool


class SelfHealingEngine:
    def __init__(self, config: Config, workspace_root: Optional[Path] = None):
        self.config = config
        self.workspace_root = workspace_root or Path.cwd()
        self.sanitizer = PrivacySanitizer()
        self.memory = TemporalMemory(config.db_path)
        self.llm = NebiusLLMClient(config)
        self.tools = LocalToolExecutor(self.workspace_root)
        self.tavily = TavilySearchTool()

    def autonomous_refactor(
        self,
        target_file: str,
        task_prompt: str,
        test_command: str = "pytest",
        max_attempts: int = 3,
        use_web_search: bool = True,
    ) -> Dict[str, Any]:
        """Autonomously refactors code with test-driven self-healing loop."""
        original_code = self.tools.read_code_file(target_file)
        
        # 1. Local Sanitization
        sanitized_prompt, redact_count = self.sanitizer.sanitize(task_prompt)
        
        # 2. Query Temporal Architectural Memory
        active_adrs = self.memory.query_active_decisions(query=task_prompt, limit=5)
        adr_context = self.memory.format_context_for_prompt(active_adrs)

        # 3. Optional Tavily Web Search for best practices
        search_context = ""
        if use_web_search:
            search_res = self.tavily.search(query=task_prompt)
            if search_res.get("answer"):
                search_context = f"\n### VERIFIED BEST PRACTICES (TAVILY):\n{search_res['answer']}\n"

        history: List[Dict[str, Any]] = []
        current_code = original_code
        success = False
        last_error = ""

        system_prompt = (
            "You are Sovereign Engineering Copilot, an expert AI engineer.\n"
            "Your job is to refactor the provided code to satisfy the user request, "
            "strictly adhering to past architectural decisions.\n\n"
            f"{adr_context}\n"
            f"{search_context}\n"
            "RULES:\n"
            "- Output valid Python code only.\n"
            "- Strictly preserve all architectural invariants.\n"
        )

        for attempt in range(1, max_attempts + 1):
            if attempt == 1:
                user_msg = (
                    f"Task: {sanitized_prompt}\n\n"
                    f"Target File: {target_file}\n"
                    f"Current Code:\n```python\n{current_code}\n```"
                )
            else:
                user_msg = (
                    f"Attempt #{attempt-1} failed tests with the following error:\n"
                    f"```\n{last_error}\n```\n"
                    "Please fix the implementation. Ensure compliance with all ADRs.\n"
                    f"Current Code:\n```python\n{current_code}\n```"
                )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ]

            # Generate reasoning & proposed code
            if self.config.mock_mode:
                # In mock/offline mode, produce valid refactored code that passes tests
                refactored_code = self._mock_refactor_generation(current_code, attempt)
            else:
                raw_response = self.llm.complete(messages)
                refactored_code = self._extract_code_block(raw_response, fallback=current_code)

            # Apply candidate code to target file
            self.tools.write_code_file(target_file, refactored_code)
            current_code = refactored_code

            # Run automated test validation
            test_run = self.tools.run_automated_tests(test_command)
            attempt_log = {
                "attempt": attempt,
                "passed": test_run["passed"],
                "exit_code": test_run["exit_code"],
            }
            history.append(attempt_log)

            if test_run["passed"]:
                success = True
                break
            else:
                last_error = test_run["stderr"] or test_run["stdout"]

        if not success:
            # Rollback to original code to preserve working state
            self.tools.write_code_file(target_file, original_code)

        diff = self.tools.get_git_diff()

        return {
            "success": success,
            "target_file": target_file,
            "attempts": len(history),
            "history": history,
            "active_adrs_applied": [a["id"] for a in active_adrs],
            "redactions_count": redact_count,
            "rolled_back": not success,
            "diff": diff,
        }

    def _extract_code_block(self, response_text: str, fallback: str) -> str:
        """Extracts python code block from markdown response."""
        if "```python" in response_text:
            parts = response_text.split("```python")
            if len(parts) > 1:
                return parts[1].split("```")[0].strip()
        elif "```" in response_text:
            parts = response_text.split("```")
            if len(parts) > 1:
                return parts[1].split("```")[0].strip()
        return fallback

    def _mock_refactor_generation(self, code: str, attempt: int) -> str:
        """Simulates iterative repair in offline mode."""
        # Produces clean refactored code preserving idempotency
        if "def process_payment" in code:
            return (
                "# payment_service.py (Autonomously Refactored by Sovereign Copilot)\n"
                "def process_payment(amount: float, idempotency_key: str, retries: int = 3) -> dict:\n"
                "    \"\"\"Processes payment with retry logic while preserving ADR idempotency invariant.\"\"\"\n"
                "    if not idempotency_key:\n"
                "        raise ValueError('Missing idempotency key')\n"
                "    for attempt in range(retries):\n"
                "        try:\n"
                "            # Simulated resilient execution\n"
                "            return {'status': 'success', 'amount': amount, 'key': idempotency_key, 'attempt': attempt + 1}\n"
                "        except Exception:\n"
                "            if attempt == retries - 1:\n"
                "                raise\n"
                "    return {'status': 'failed', 'key': idempotency_key}\n"
            )
        return code
