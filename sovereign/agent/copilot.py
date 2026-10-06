"""Sovereign Copilot Agent Orchestrator.

Integrates Privacy Sanitizer, Temporal Architectural Memory, and Nebius/NVIDIA inference
to execute safe, context-aware engineering tasks.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

from sovereign.config import Config
from sovereign.privacy.sanitizer import PrivacySanitizer
from sovereign.memory.temporal_graph import TemporalMemory
from sovereign.llm.client import NebiusLLMClient
from sovereign.tools.git_tools import LocalToolExecutor


class SovereignCopilot:
    def __init__(self, config: Config):
        self.config = config
        self.sanitizer = PrivacySanitizer()
        self.memory = TemporalMemory(config.db_path)
        self.llm = NebiusLLMClient(config)
        self.tools = LocalToolExecutor(Path.cwd())

    def execute_engineering_task(
        self,
        task_prompt: str,
        code_context: str = "",
        auto_test: bool = False,
        test_command: str = "pytest",
    ) -> Dict[str, Any]:
        """Executes an engineering task following the sovereign privacy-first pipeline."""
        # 1. Local Privacy Sanitization
        raw_combined = f"{task_prompt}\n{code_context}"
        sanitized_input, redaction_count = self.sanitizer.sanitize(raw_combined)

        # 2. Temporal Memory Retrieval
        relevant_adrs = self.memory.query_active_decisions(query=task_prompt, limit=5)
        memory_context = self.memory.format_context_for_prompt(relevant_adrs)

        # 3. System Prompt Construction
        system_prompt = (
            "You are Sovereign Engineering Copilot, an expert AI engineer that respects "
            "past architectural decisions and writes robust, production-grade code.\n\n"
            f"{memory_context}\n\n"
            "RULES:\n"
            "- Strictly adhere to past Architectural Decisions (ADRs) cited above.\n"
            "- Never re-introduce anti-patterns or superseded patterns.\n"
            "- Provide clean, structured output."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sanitized_input},
        ]

        # 4. High-Level Reasoning via Nebius (NVIDIA Nemotron)
        reasoning_output = self.llm.complete(messages)

        # 5. Local Automated Testing (if requested)
        test_result = None
        if auto_test:
            test_result = self.tools.run_automated_tests(test_command)

        return {
            "task": task_prompt,
            "redactions_count": redaction_count,
            "active_adrs_applied": [adr["id"] for adr in relevant_adrs],
            "adrs_details": relevant_adrs,
            "reasoning_output": reasoning_output,
            "test_result": test_result,
            "model_used": self.config.model_name,
            "mock_mode": self.config.mock_mode,
        }

    def record_new_decision(
        self,
        title: str,
        rationale: str,
        context: str = "",
        tags: Optional[List[str]] = None,
        supersedes_id: Optional[int] = None,
    ) -> int:
        """Records a new architectural decision into Temporal Memory."""
        new_id = self.memory.add_decision(title, rationale, context, tags)
        if supersedes_id:
            self.memory.supersede_decision(supersedes_id, new_id, reason=f"Superseded by ADR #{new_id}")
        return new_id
