"""Unit tests for SovereignMCPServer."""

from sovereign.mcp_server import SovereignMCPServer


def test_mcp_tool_definitions():
    server = SovereignMCPServer()
    tools = server.get_tool_definitions()
    tool_names = [t["name"] for t in tools]
    assert "sovereign_query_adrs" in tool_names
    assert "sovereign_record_adr" in tool_names
    assert "sovereign_sanitize_text" in tool_names
    assert "sovereign_run_tests" in tool_names


def test_mcp_tool_execution():
    server = SovereignMCPServer()

    # Record ADR via MCP
    record_res = server.handle_tool_call(
        "sovereign_record_adr",
        {
            "title": "Use Structured JSON Logging",
            "rationale": "Facilitate log ingestion into telemetry aggregators",
            "tags": ["logging", "observability"],
        },
    )
    assert record_res["status"] == "success"
    assert record_res["recorded_adr_id"] > 0

    # Query ADR via MCP
    query_res = server.handle_tool_call("sovereign_query_adrs", {"query": "logging"})
    assert len(query_res) >= 1
    assert "Logging" in query_res[0]["title"]

    # Sanitize text via MCP
    sanitize_res = server.handle_tool_call(
        "sovereign_sanitize_text",
        {"text": "Secret key: api_key='sk-live-000111222333444555'"},
    )
    assert sanitize_res["redacted_count"] >= 1
    assert "[SOVEREIGN_REDACTED_" in sanitize_res["sanitized_text"]
