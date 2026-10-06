"""Command Line Interface for Sovereign Engineering Copilot."""

import argparse
import sys
from pathlib import Path
from sovereign.config import load_config
from sovereign.agent.copilot import SovereignCopilot
from sovereign.agent.self_healing import SelfHealingEngine
from sovereign.tools.tavily_search import TavilySearchTool
from sovereign.mcp_server import SovereignMCPServer
from sovereign.privacy.sanitizer import PrivacySanitizer


def main():
    parser = argparse.ArgumentParser(
        prog="sovereign",
        description="Sovereign Engineering Copilot with Temporal Architectural Memory",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize sovereign local workspace")

    # ask command
    ask_parser = subparsers.add_parser("ask", help="Ask copilot to reason on a task with temporal memory")
    ask_parser.add_argument("prompt", type=str, help="Engineering task or question")
    ask_parser.add_argument("--test", action="store_true", help="Auto-run local test suite after reasoning")

    # refactor command (autonomous self-healing)
    refactor_parser = subparsers.add_parser("refactor", help="Autonomous self-healing refactoring loop")
    refactor_parser.add_argument("file", type=str, help="Target code file to refactor")
    refactor_parser.add_argument("--prompt", required=True, type=str, help="Refactoring instructions")
    refactor_parser.add_argument("--test-cmd", default="pytest", type=str, help="Command to run tests (default: pytest)")
    refactor_parser.add_argument("--max-retries", default=3, type=int, help="Maximum self-healing attempts")

    # graph command
    subparsers.add_parser("graph", help="Render visual graph of active vs superseded ADRs")

    # audit command
    audit_parser = subparsers.add_parser("audit", help="Audit local codebase for secrets and compliance")
    audit_parser.add_argument("--path", default=".", type=str, help="Directory to scan")

    # search command (Tavily)
    search_parser = subparsers.add_parser("search", help="Search official framework best practices via Tavily")
    search_parser.add_argument("query", type=str, help="Search query")

    # mcp command
    subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) server over stdio")

    # memory command
    mem_parser = subparsers.add_parser("memory", help="Manage Temporal Architectural Memory")
    mem_sub = mem_parser.add_subparsers(dest="mem_action")

    # memory list
    mem_sub.add_parser("list", help="List active architectural decisions")

    # memory add
    add_mem = mem_sub.add_parser("add", help="Add a new architectural decision (ADR)")
    add_mem.add_argument("--title", required=True, help="Title of architectural decision")
    add_mem.add_argument("--rationale", required=True, help="Why this decision was made")
    add_mem.add_argument("--context", default="", help="Context or constraints")
    add_mem.add_argument("--tags", default="", help="Comma-separated tags")
    add_mem.add_argument("--supersedes", type=int, default=None, help="ID of previous ADR being superseded")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = load_config()
    copilot = SovereignCopilot(config)

    if args.command == "init":
        print(f"Sovereign Copilot initialized at {config.workspace_dir}")
        print(f"Temporal Memory Database: {config.db_path}")
        print(f"Target Model: {config.model_name}")
        print(f"Nebius Endpoint: {config.nebius_base_url}")
        print("Ready for local autonomous development.")

    elif args.command == "memory":
        if args.mem_action == "list":
            decisions = copilot.memory.query_active_decisions(limit=20)
            if not decisions:
                print("No active architectural decisions recorded yet.")
                return
            print(f"--- ACTIVE ARCHITECTURAL DECISIONS ({len(decisions)}) ---")
            for d in decisions:
                print(f"[ADR #{d['id']}] {d['title']} (Score: {d.get('score', 'N/A')})")
                print(f"  Rationale: {d['rationale']}")
                if d.get("context"):
                    print(f"  Context: {d['context']}")
                if d.get("tags"):
                    print(f"  Tags: {d['tags']}")
                print()

        elif args.mem_action == "add":
            tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]
            adr_id = copilot.record_new_decision(
                title=args.title,
                rationale=args.rationale,
                context=args.context,
                tags=tags_list,
                supersedes_id=args.supersedes,
            )
            print(f"Successfully recorded ADR #{adr_id}: '{args.title}'")
            if args.supersedes:
                print(f"Marked previous ADR #{args.supersedes} as superseded.")

    elif args.command == "ask":
        print("Executing task with Sovereign Copilot...")
        res = copilot.execute_engineering_task(args.prompt, auto_test=args.test)
        print(f"Local Privacy Redactions: {res['redactions_count']} sensitive items sanitized")
        print(f"Temporal ADRs Injected: {res['active_adrs_applied']}")
        print(f"Model: {res['model_used']} (Mock Mode: {res['mock_mode']})")
        print("\n" + res["reasoning_output"])
        if res.get("test_result"):
            t_res = res["test_result"]
            print(f"Test Execution: {'PASSED' if t_res['passed'] else 'FAILED'}")

    elif args.command == "refactor":
        engine = SelfHealingEngine(config)
        print(f"Starting autonomous refactoring loop on: {args.file}")
        res = engine.autonomous_refactor(
            target_file=args.file,
            task_prompt=args.prompt,
            test_command=args.test_cmd,
            max_attempts=args.max_retries,
        )
        if res["success"]:
            print(f"SUCCESS: Refactor completed and verified in {res['attempts']} attempt(s).")
            print(f"Active ADRs Enforced: {res['active_adrs_applied']}")
            print(f"Sensitive Tokens Redacted: {res['redactions_count']}")
        else:
            print(f"FAILED: Tests could not be satisfied after {res['attempts']} attempt(s).")
            print("Changes were automatically rolled back to preserve codebase integrity.")

    elif args.command == "graph":
        with copilot.memory._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, status, superseded_by, created_at
                FROM architectural_decisions
                ORDER BY id ASC
            """)
            all_adrs = cursor.fetchall()

        if not all_adrs:
            print("No ADRs recorded in memory graph yet.")
            return

        print("=== TEMPORAL ARCHITECTURAL MEMORY GRAPH ===")
        for adr in all_adrs:
            status_badge = "[ACTIVE]" if adr["status"] == "active" else f"[SUPERSEDED -> #{adr['superseded_by']}]"
            print(f"  #{adr['id']} {status_badge:<25} {adr['title']}")
        print()

    elif args.command == "audit":
        sanitizer = PrivacySanitizer()
        scan_dir = Path(args.path)
        violations = []
        total_scanned = 0

        for file_path in scan_dir.rglob("*.py"):
            if ".sovereign" in str(file_path) or ".venv" in str(file_path):
                continue
            total_scanned += 1
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            _, count = sanitizer.sanitize(content)
            if count > 0:
                violations.append((file_path, count))

        print(f"=== SOVEREIGN PRIVACY & SECURITY AUDIT ===")
        print(f"Scanned {total_scanned} source files.")
        if violations:
            print(f"WARNING: Found {len(violations)} files with unmasked credentials or secrets:")
            for p, c in violations:
                print(f"  - {p} ({c} exposed secrets)")
        else:
            print("CLEAN: Zero plaintext secrets or sensitive credentials detected.")

    elif args.command == "search":
        tool = TavilySearchTool()
        print(f"Searching verified best practices via Tavily for: '{args.query}'...")
        res = tool.search(args.query)
        print(f"\nSummary Answer:\n{res['answer']}\n")
        if res["results"]:
            print("Sources:")
            for r in res["results"]:
                print(f"  - {r['title']} ({r['url']})")

    elif args.command == "mcp":
        server = SovereignMCPServer()
        server.run_stdio()


if __name__ == "__main__":
    main()
