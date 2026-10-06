"""Unit tests for TavilySearchTool."""

from sovereign.tools.tavily_search import TavilySearchTool


def test_tavily_search_mock():
    tool = TavilySearchTool()
    res = tool.search("FastAPI dependency injection patterns")
    assert res["query"] == "FastAPI dependency injection patterns"
    assert "Verified architectural best practices" in res["answer"]
    assert len(res["results"]) >= 1
    assert res["mock"] is True
