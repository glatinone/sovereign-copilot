# Sovereign Engineering Copilot: Technical Architecture

This document details the architectural principles, data structures, and execution flow of **Sovereign Engineering Copilot**, built for the Nebius x NVIDIA Global AI Hackathon (Personal AI Track).

---

## 1. System Invariants & Trust Boundary

Sovereign Engineering Copilot operates under three non-negotiable security and cognitive invariants:

1. **Zero-Leakage Local Perimeter**:
   - Source code parsing, credentials extraction, git operations, and test executions run strictly on the local developer machine.
   - All outbound payloads to remote inference endpoints (Nebius Token Factory) must pass through the **Local Privacy Sanitizer**.
   - Proprietary tokens, API keys, database URLs, passwords, internal RFC1918 IP addresses, and emails are pseudonymized into reversible deterministic tokens before leaving localhost.

2. **Temporal Consistency (Anti-Drift)**:
   - AI coding assistants often re-introduce bugs and anti-patterns because flat RAG retrieves historical snippets indiscriminately.
   - Sovereign Copilot tracks **Architectural Decision Records (ADRs)** with explicit temporal intervals (`valid_from`, `valid_until`) and relationship links (`SUPERSEDED_BY`).
   - Obsolete architectural rules are excluded from active context, preventing temporal regression.

3. **Autonomous Verification (Test-Driven Repair)**:
   - Code refactorings are never finalized on prompt generation alone.
   - The engine compiles and executes the local test suite (`pytest`) in an isolated subprocess.
   - If tests fail, the engine autonomously analyzes tracebacks, refines the implementation, and re-verifies until green (bounded to N retries).

---

## 2. High-Level Architecture Diagram

```
+-------------------------------------------------------------------------+
|                        LOCAL DEVELOPER WORKSPACE                        |
|                                                                         |
|  [ Developer Request ]                                                  |
|          |                                                              |
|          v                                                              |
|  +--------------------------------+                                     |
|  |     Local Privacy Sanitizer    |                                     |
|  |  - High-Entropy Key Detection  |                                     |
|  |  - Pseudonymization Token Map  |                                     |
|  +--------------------------------+                                     |
|          |                                                              |
|          v                                                              |
|  +--------------------------------+      +---------------------------+  |
|  |     Prompt Context Binder      | <--- | Temporal Memory (SQLite)  |  |
|  |  - Injects Active ADR Rules    |      | - Validity Timestamps     |  |
|  |  - Injects Tavily Search Docs  |      | - Temporal Decay (e^-λt)  |  |
|  +--------------------------------+      +---------------------------+  |
|          | (Sanitized Context)                         ^                |
+----------|---------------------------------------------|----------------+
           |                                             |
           v                                             |
+------------------------------------+                   |
|        NEBIUS TOKEN FACTORY        |                   |
|                                    |                   |
|  NVIDIA Llama-3.1-Nemotron-70B     |                   |
|  - High-Level Cognitive Reasoning  |                   |
|  - Architectural Synthesis         |                   |
+------------------------------------+                   |
           | (Proposed Diff / Patch)                     |
           v                                             |
+--------------------------------------------------------|----------------+
|                        LOCAL VERIFICATION              |                |
|                                                        |                |
|  +--------------------------------+                    |                |
|  |   Self-Healing Refactor Loop   |                    |                |
|  |  1. Apply Candidate Patch      |                    |                |
|  |  2. Execute Local Pytest Suite |                    |                |
|  |  3. Autonomous Traceback Fix   |                    |                |
|  +--------------------------------+                    |                |
|          | (On Verified Green)                         |                |
|          v                                             |                |
|  +--------------------------------+                    |                |
|  |    Record Architectural State  | -------------------+                |
|  |  - Store New ADR Node          |                                     |
|  |  - Mark Superseded Decisions   |                                     |
|  +--------------------------------+                                     |
+-------------------------------------------------------------------------+
```

---

## 3. Core Subsystems

### 3.1 Local Privacy Sanitizer (`sovereign/privacy/sanitizer.py`)
- Scans all incoming prompts and code context before remote transmission.
- Recognizes:
  - Private keys (RSA, EC, OpenSSH PEM formats)
  - API keys and tokens (regex matching high-entropy sequences across AWS, OpenAI, Nebius, GitHub)
  - Database connection strings (`postgres://`, `mysql://`, `mongodb://`)
  - Internal network addresses (`10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`)
- Generates pseudonym tokens: `[SOVEREIGN_REDACTED_KEY_001]`, `[SOVEREIGN_REDACTED_IP_002]`.
- Maintains an in-memory reverse map to restore tokens locally when presenting final output to the developer.

### 3.2 Temporal Architectural Memory (`sovereign/memory/temporal_graph.py`)
- Backed by local relational SQLite (`.sovereign/memory.db`).
- Schema:
  - `architectural_decisions`: Stores `id`, `title`, `rationale`, `context`, `tags`, `status`, `valid_from`, `valid_until`, `superseded_by`, `created_at`.
  - `architectural_relations`: Stores `source_id`, `relation_type` (`SUPERSEDED_BY`, `DEPENDS_ON`), `target_id`, `created_at`.
- Ranking Formula:
  $$\text{Score} = (0.7 \times \text{Relevance}) + (0.3 \times e^{-\lambda \cdot \Delta t})$$
  where $\lambda = 0.05$ per day, favoring fresh active decisions over older ones, and completely filtering out superseded records.

### 3.3 Nebius Token Factory & NVIDIA Nemotron Engine (`sovereign/llm/client.py`)
- Interfaces directly with Nebius Token Factory (`https://api.tokenfactory.nebius.com/v1`).
- Directs tasks to **NVIDIA Llama-3.1-Nemotron-70B-Instruct**.
- Excels at complex constraint following and adhering to negative instructions in system prompts.

### 3.4 Model Context Protocol Server (`sovereign/mcp_server.py`)
- Implements standard MCP stdio protocol over JSON-RPC.
- Allows external development environments (Claude Desktop, Cursor, Hermes Agent) to call Sovereign Copilot tools:
  - `sovereign_query_adrs`
  - `sovereign_record_adr`
  - `sovereign_sanitize_text`
  - `sovereign_run_tests`

---

## 4. Verification and Testing

All subsystems are covered by an automated test suite executed via `pytest`:
- `tests/test_sanitizer.py`: Validates zero credential leakage and roundtrip restoration.
- `tests/test_temporal_memory.py`: Verifies ADR creation, relevance scoring, and automatic exclusion of superseded decisions.
- `tests/test_copilot_e2e.py`: End-to-end task execution with privacy sanitization and ADR context injection.
- `tests/test_self_healing.py`: Validates autonomous test-driven refactor and recovery.
- `tests/test_tavily_search.py`: Validates live best practices lookup and fallback.
- `tests/test_mcp_server.py`: Verifies JSON-RPC tool definitions and execution.
