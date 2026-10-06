"""Temporal Architectural Memory.

Stores and queries architectural decisions, engineering constraints, and design
conventions with temporal validity tracking to prevent architectural regression
and temporal drift.
"""

import math
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class TemporalMemory:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS architectural_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    context TEXT,
                    tags TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    valid_from TIMESTAMP NOT NULL,
                    valid_until TIMESTAMP,
                    superseded_by INTEGER,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(superseded_by) REFERENCES architectural_decisions(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS architectural_relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    relation_type TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(source_id) REFERENCES architectural_decisions(id),
                    FOREIGN KEY(target_id) REFERENCES architectural_decisions(id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_decisions_status_validity
                ON architectural_decisions(status, valid_from, valid_until)
            """)
            conn.commit()

    def add_decision(
        self,
        title: str,
        rationale: str,
        context: str = "",
        tags: Optional[List[str]] = None,
        valid_from: Optional[datetime] = None,
    ) -> int:
        now = datetime.now(timezone.utc)
        v_from = valid_from or now
        tags_str = ",".join([t.strip().lower() for t in (tags or [])])

        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO architectural_decisions (
                    title, rationale, context, tags, status, valid_from, valid_until, created_at
                ) VALUES (?, ?, ?, ?, 'active', ?, NULL, ?)
                """,
                (title, rationale, context, tags_str, v_from.isoformat(), now.isoformat()),
            )
            decision_id = int(cursor.lastrowid or 0)
            conn.commit()
            return decision_id

    def supersede_decision(self, old_id: int, new_id: int, reason: str = "") -> bool:
        now = datetime.now(timezone.utc)
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE architectural_decisions
                SET status = 'superseded', valid_until = ?, superseded_by = ?
                WHERE id = ? AND status = 'active'
                """,
                (now.isoformat(), new_id, old_id),
            )
            updated = cursor.rowcount > 0
            if updated:
                cursor.execute(
                    """
                    INSERT INTO architectural_relations (
                        source_id, relation_type, target_id, created_at
                    ) VALUES (?, 'SUPERSEDED_BY', ?, ?)
                    """,
                    (old_id, new_id, now.isoformat()),
                )
            conn.commit()
            return updated

    def query_active_decisions(
        self, query: str = "", limit: int = 5, decay_rate: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Queries active decisions, ranking by keyword matching and temporal decay."""
        now = datetime.now(timezone.utc)
        query_terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]

        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, rationale, context, tags, status, valid_from, created_at
                FROM architectural_decisions
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()

        results = []
        for row in rows:
            decision = dict(row)
            text_corpus = f"{decision['title']} {decision['rationale']} {decision.get('context', '')} {decision.get('tags', '')}".lower()

            # Relevance score
            matches = 0
            if query_terms:
                matches = sum(1 for term in query_terms if term in text_corpus)
                relevance_score = matches / len(query_terms)
            else:
                relevance_score = 1.0

            # Temporal decay score (e^(-decay_rate * days_old))
            created_at = datetime.fromisoformat(decision["created_at"])
            days_old = max(0.0, (now - created_at).total_seconds() / 86400.0)
            temporal_score = math.exp(-decay_rate * days_old)

            final_score = (relevance_score * 0.7) + (temporal_score * 0.3)
            decision["score"] = round(final_score, 4)
            decision["relevance"] = round(relevance_score, 4)

            # Include if query was empty OR there was at least partial match
            if not query_terms or matches > 0:
                results.append(decision)

        # Sort by final score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def format_context_for_prompt(self, decisions: List[Dict[str, Any]]) -> str:
        """Formats active architectural decisions into a compact prompt section."""
        if not decisions:
            return "No previous architectural decisions found for this domain."

        lines = ["### ACTIVE ARCHITECTURAL DECISIONS & CONVENTIONS:"]
        for d in decisions:
            tags = f" [tags: {d['tags']}]" if d.get("tags") else ""
            lines.append(f"- [ADR #{d['id']}] {d['title']}{tags}")
            lines.append(f"  Rationale: {d['rationale']}")
            if d.get("context"):
                lines.append(f"  Constraint/Context: {d['context']}")
        return "\n".join(lines)
