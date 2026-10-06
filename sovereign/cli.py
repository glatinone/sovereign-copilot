"""Command Line Interface for Sovereign Engineering Copilot."""

import argparse
import sys
from sovereign.config import load_config
from sovereign.agent.copilot import SovereignCopilot


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
        print(f"Executing task with Sovereign Copilot...")
        res = copilot.execute_engineering_task(args.prompt, auto_test=args.test)
        print(f"Local Privacy Redactions: {res['redactions_count']} sensitive items sanitized")
        print(f"Temporal ADRs Injected: {res['active_adrs_applied']}")
        print(f"Model: {res['model_used']} (Mock Mode: {res['mock_mode']})")
        print("\n" + res["reasoning_output"])
        if res.get("test_result"):
            t_res = res["test_result"]
            print(f"Test Execution: {'PASSED' if t_res['passed'] else 'FAILED'}")


if __name__ == "__main__":
    main()
