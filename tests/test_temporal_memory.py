"""Unit tests for Temporal Architectural Memory."""

import tempfile
from pathlib import Path
from sovereign.memory.temporal_graph import TemporalMemory


def test_add_and_query_decisions():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        mem = TemporalMemory(db_path)

        # Record ADR 1
        id1 = mem.add_decision(
            title="Use Message Broker for Event Bus",
            rationale="Decouple payment and notification microservices",
            context="Requires high throughput and persistence",
            tags=["events", "broker", "payment"],
        )
        assert id1 > 0

        # Query matching 'payment'
        results = mem.query_active_decisions("payment")
        assert len(results) == 1
        assert results[0]["id"] == id1
        assert "broker" in results[0]["tags"]


def test_supersede_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        mem = TemporalMemory(db_path)

        # Original decision: REST polling
        old_id = mem.add_decision(
            title="REST Polling for Notifications",
            rationale="Quick initial implementation",
            tags=["notifications", "polling"],
        )

        # New decision: WebSocket streaming
        new_id = mem.add_decision(
            title="WebSocket Streaming for Notifications",
            rationale="Reduce server load and latency",
            tags=["notifications", "websocket"],
        )

        # Supersede old decision
        superseded = mem.supersede_decision(old_id, new_id, reason="Migrated to WebSockets")
        assert superseded is True

        # Query active decisions: old decision MUST NOT be returned!
        active = mem.query_active_decisions("notifications")
        active_ids = [d["id"] for d in active]
        assert new_id in active_ids
        assert old_id not in active_ids
