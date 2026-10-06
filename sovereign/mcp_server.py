"""Model Context Protocol (MCP) Server for Sovereign Engineering Copilot.

Exposes Sovereign Copilot's Temporal Architectural Memory, Local Privacy Sanitizer,
and Test Execution tools over standard MCP stdio protocol (JSON-RPC), allowing
external agents (Claude Desktop, Cursor, Hermes Agent) to leverage sovereign governance.
"""

import json
import sys
from typing import Any, Dict, List

from sovereign.config import load_config
from sovereign.privacy.sanitizer import PrivacySanitizer
from sovereign.memory.temporal_graph import TemporalMemory
from sovereign.tools.git_tools import LocalToolExecutor


class SovereignMCPServer:
    def __init__(self):
        self.config = load_config()
        self.memory = TemporalMemory(self.config.db_path)
        self.sanitizer = PrivacySanitizer()
        self.tools = LocalToolExecutor()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "sovereign_query_adrs",
                "description": "Query active Architectural Decision Records (ADRs) from local Temporal Memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search topic, keyword, or module name"}
                    },
                },
            },
            {
                "name": "sovereign_record_adr",
                "description": "Record a new Architectural Decision Record into local Temporal Memory.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Decision title"},
                        "rationale": {"type": "string", "description": "Reasoning behind decision"},
                        "context": {"type": "string", "description": "Optional constraints or context"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
                        "supersedes_id": {"type": "integer", "description": "Optional ID of superseded ADR"}
                    },
                    "required": ["title", "rationale"]
                },
            },
            {
                "name": "sovereign_sanitize_text",
                "description": "Scrub high-entropy API keys, passwords, and internal IPs from text locally.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Source text to sanitize"}
                    },
                    "required": ["text"]
                },
            },
            {
                "name": "sovereign_run_tests",
                "description": "Safely execute the local test suite and return results.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "test_command": {"type": "string", "description": "Command to run (default: pytest)"}
                    },
                },
            },
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name == "sovereign_query_adrs":
            q = arguments.get("query", "")
            return self.memory.query_active_decisions(query=q)

        elif name == "sovereign_record_adr":
            title = arguments["title"]
            rationale = arguments["rationale"]
            context = arguments.get("context", "")
            tags = arguments.get("tags", [])
            supersedes_id = arguments.get("supersedes_id")
            new_id = self.memory.add_decision(title, rationale, context, tags)
            if supersedes_id:
                self.memory.supersede_decision(supersedes_id, new_id, reason=f"Superseded by ADR #{new_id}")
            return {"status": "success", "recorded_adr_id": new_id}

        elif name == "sovereign_sanitize_text":
            text = arguments.get("text", "")
            sanitized, count = self.sanitizer.sanitize(text)
            return {"sanitized_text": sanitized, "redacted_count": count}

        elif name == "sovereign_run_tests":
            cmd = arguments.get("test_command", "pytest")
            return self.tools.run_automated_tests(cmd)

        else:
            raise ValueError(f"Unknown tool: {name}")

    def run_stdio(self):
        """Processes JSON-RPC MCP requests from stdin."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                method = req.get("method")
                req_id = req.get("id")

                if method == "initialize":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "sovereign-copilot-mcp", "version": "0.1.0"},
                        },
                    }
                elif method == "tools/list":
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"tools": self.get_tool_definitions()},
                    }
                elif method == "tools/call":
                    params = req.get("params", {})
                    tool_name = params.get("name")
                    args = params.get("arguments", {})
                    tool_output = self.handle_tool_call(tool_name, args)
                    res = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(tool_output, indent=2)}]
                        },
                    }
                else:
                    res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_res = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()


def main():
    server = SovereignMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
