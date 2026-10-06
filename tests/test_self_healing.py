"""Unit tests for SelfHealingEngine."""

import tempfile
from pathlib import Path
from sovereign.config import Config
from sovereign.agent.self_healing import SelfHealingEngine
from sovereign.tools.git_tools import LocalToolExecutor


def test_autonomous_refactor_self_healing():
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        db_path = temp_path / "test_sh_memory.db"
        cfg = Config(
            workspace_dir=temp_path,
            db_path=db_path,
            mock_mode=True,
        )
        engine = SelfHealingEngine(cfg, workspace_root=temp_path)
        tools = LocalToolExecutor(temp_path)

        # Create target file & test
        code = (
            "def process_payment(amount: float, idempotency_key: str) -> dict:\n"
            "    if not idempotency_key:\n"
            "        raise ValueError('Missing idempotency key')\n"
            "    return {'status': 'success', 'amount': amount, 'key': idempotency_key}\n"
        )
        test_file = (
            "from payment import process_payment\n\n"
            "def test_payment():\n"
            "    res = process_payment(100.0, 'tx-123')\n"
            "    assert res['status'] == 'success'\n"
            "    assert res['key'] == 'tx-123'\n"
        )
        tools.write_code_file("payment.py", code)
        tools.write_code_file("test_payment.py", test_file)

        # Record ADR
        engine.memory.add_decision(
            title="Enforce Idempotent Keys",
            rationale="Prevent duplicate financial transactions",
            tags=["payment", "idempotency"],
        )

        # Run self-healing refactor
        result = engine.autonomous_refactor(
            target_file="payment.py",
            task_prompt="Refactor payment to add retries, using DB_PASS='secret_pwd_9988776655443322'",
            test_command=f"pytest {temp_path / 'test_payment.py'}",
            max_attempts=3,
        )

        assert result["success"] is True
        assert result["attempts"] >= 1
        assert result["redactions_count"] >= 1
        assert result["rolled_back"] is False
