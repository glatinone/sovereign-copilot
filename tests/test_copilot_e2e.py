"""End-to-end integration test for Sovereign Copilot."""

import tempfile
from pathlib import Path
from sovereign.config import Config
from sovereign.agent.copilot import SovereignCopilot


def test_copilot_pipeline_e2e():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "e2e_memory.db"
        cfg = Config(
            db_path=db_path,
            workspace_dir=Path(tmpdir),
            mock_mode=True,
        )
        copilot = SovereignCopilot(cfg)

        # 1. Seed past architectural decision
        adr_id = copilot.record_new_decision(
            title="Enforce Pure Functions in Math Modules",
            rationale="Eliminate side effects in financial calculation pipeline",
            tags=["finance", "math", "pure-functions"],
        )
        assert adr_id == 1

        # 2. Execute task that contains private API key & asks for refactor
        task = "Refactor the calculation engine. Use api_key='sk-live-111222333444555666777888999' to connect."
        result = copilot.execute_engineering_task(task)

        # 3. Assertions
        assert result["redactions_count"] >= 1
        assert 1 in result["active_adrs_applied"]
        assert "Compliant with active ADRs" in result["reasoning_output"]
        assert "zero plaintext secrets" in result["reasoning_output"].lower()
