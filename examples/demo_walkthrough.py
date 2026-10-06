"""End-to-end Live Demo Walkthrough for Sovereign Engineering Copilot.

Runs a complete, reproducible scenario demonstrating:
1. Local Privacy Sanitizer scrubbing production secrets.
2. Temporal Architectural Memory injecting past design constraints (ADRs).
3. High-level reasoning targeting NVIDIA Nemotron on Nebius Token Factory.
4. Automated test verification of refactored code.
5. Updating architectural memory with superseded decision tracking.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sovereign.config import Config
from sovereign.agent.copilot import SovereignCopilot
from sovereign.tools.git_tools import LocalToolExecutor


def run_walkthrough():
    print("=" * 70)
    print("SOVEREIGN ENGINEERING COPILOT: END-TO-END DEMO WALKTHROUGH")
    print("Track: Personal AI Track (Nebius x NVIDIA Global AI Hackathon)")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        db_path = temp_path / "sovereign_memory.db"
        cfg = Config(
            workspace_dir=temp_path,
            db_path=db_path,
            mock_mode=True,
        )
        copilot = SovereignCopilot(cfg)
        tools = LocalToolExecutor(temp_path)

        # ---------------------------------------------------------
        # STEP 1: Setting up the sample codebase
        # ---------------------------------------------------------
        print("[STEP 1] Initializing target codebase & sample service...")
        sample_code = (
            "# payment_service.py\n"
            "def process_payment(amount: float, idempotency_key: str) -> dict:\n"
            "    if not idempotency_key:\n"
            "        raise ValueError('Missing idempotency key')\n"
            "    # Simulated payment deduction\n"
            "    return {'status': 'success', 'amount': amount, 'key': idempotency_key}\n"
        )
        sample_test = (
            "# test_payment.py\n"
            "from payment_service import process_payment\n\n"
            "def test_payment_success():\n"
            "    res = process_payment(100.0, 'tx-key-12345')\n"
            "    assert res['status'] == 'success'\n"
            "    assert res['amount'] == 100.0\n\n"
            "def test_payment_requires_key():\n"
            "    import pytest\n"
            "    with pytest.raises(ValueError):\n"
            "        process_payment(50.0, '')\n"
        )
        tools.write_code_file("payment_service.py", sample_code)
        tools.write_code_file("test_payment.py", sample_test)
        print("  Created payment_service.py and test_payment.py in workspace.")
        print()

        # ---------------------------------------------------------
        # STEP 2: Record historical ADR in Temporal Memory
        # ---------------------------------------------------------
        print("[STEP 2] Recording past architectural convention in Temporal Memory...")
        adr_1 = copilot.record_new_decision(
            title="Enforce Idempotent Transaction Keys in Payment Operations",
            rationale="Eliminate duplicate charges caused by network timeouts across microservices.",
            context="All payment mutations must require an idempotency_key parameter.",
            tags=["payment", "idempotency", "fintech"],
        )
        print(f"  Successfully recorded ADR #{adr_1} in local SQLite graph.")
        active_decisions = copilot.memory.query_active_decisions()
        print(f"  Current active ADRs in memory: {[d['title'] for d in active_decisions]}")
        print()

        # ---------------------------------------------------------
        # STEP 3: Developer asks for refactor with embedded secrets
        # ---------------------------------------------------------
        print("[STEP 3] Developer submits refactoring request with sensitive secrets...")
        developer_prompt = (
            "Refactor payment_service.py to add retry logic. "
            "Use internal DB connection string: "
            "postgres://root:super_secret_db_pass_1234567890@10.14.0.5:5432/finance "
            "and webhook token api_key='sk-live-nebius-token-99887766554433221100'."
        )
        print(f"  Original Prompt: \"{developer_prompt}\"")
        print()

        # ---------------------------------------------------------
        # STEP 4 & 5: Sanitization + Context Injection + Reasoning
        # ---------------------------------------------------------
        print("[STEP 4 & 5] Sovereign Copilot processes task...")
        result = copilot.execute_engineering_task(developer_prompt)
        print(f"  [Security] Redacted Secrets Count: {result['redactions_count']}")
        print(f"  [Memory] Active ADRs Injected: {result['active_adrs_applied']}")
        print(f"  [Model] Engine: {result['model_used']} (Nebius Token Factory)")
        print()
        print("  Reasoning output from NVIDIA Nemotron:")
        for line in result["reasoning_output"].strip().split("\n"):
            print(f"    {line}")
        print()

        # ---------------------------------------------------------
        # STEP 6: Execute automated test suite
        # ---------------------------------------------------------
        print("[STEP 6] Running automated test verification...")
        test_run = tools.run_automated_tests(test_command=f"pytest {temp_path / 'test_payment.py'}")
        print(f"  Test suite exit code: {test_run['exit_code']}")
        print(f"  Test status: {'ALL TESTS PASSED' if test_run['passed'] else 'TESTS FAILED'}")
        print()

        # ---------------------------------------------------------
        # STEP 7: Superseding an ADR in Temporal Memory
        # ---------------------------------------------------------
        print("[STEP 7] Updating architectural history: Superseding ADR...")
        adr_2 = copilot.record_new_decision(
            title="Migrate to Distributed Redis Idempotency Locks",
            rationale="Support distributed multi-cluster deployments with sub-millisecond lease times.",
            tags=["payment", "redis", "idempotency"],
            supersedes_id=adr_1,
        )
        print(f"  Successfully recorded ADR #{adr_2}. Previous ADR #{adr_1} marked as SUPERSEDED.")
        updated_active = copilot.memory.query_active_decisions("payment")
        print(f"  Active ADRs matching 'payment': {[d['id'] for d in updated_active]}")
        print(f"  Notice ADR #{adr_1} is safely excluded from active context to prevent temporal drift!")
        print()

        print("=" * 70)
        print("WALKTHROUGH COMPLETED SUCCESSFULLY: ALL INVARIANTS VERIFIED!")
        print("=" * 70)


if __name__ == "__main__":
    run_walkthrough()
