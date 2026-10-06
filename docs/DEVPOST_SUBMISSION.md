# Devpost Submission Text: Sovereign Engineering Copilot

Track: Personal AI Track
Hackathon: Nebius x NVIDIA Global AI Hackathon
Project Name: Sovereign Engineering Copilot
Tagline: Private, autonomous engineering assistant with Temporal Architectural Memory, powered by NVIDIA Nemotron on Nebius Token Factory.

Working Demo URL: https://glatinone.github.io/sovereign-copilot/
GitHub Repository: https://github.com/glatinone/sovereign-copilot
Demo Video (YouTube, public): https://youtu.be/z8i3hh4c3uk

---

## Inspiration

Software engineers working on proprietary, enterprise, or security-sensitive codebases face a harsh paradox: modern AI assistants promise massive productivity gains, but using commercial cloud AI is often forbidden due to data leakage policies. Furthermore, current AI coding assistants suffer from severe "contextual amnesia" and "temporal drift": they treat each prompt in isolation, forgetting past architectural trade-offs, code conventions, and technical debt decisions agreed upon months ago.

We built **Sovereign Engineering Copilot** to give developers an autonomous, privacy-preserving engineering partner that keeps intellectual property on the local machine, remembers architectural decisions across sessions, and offloads heavy reasoning to state-of-the-art open models on Nebius high-performance GPU infrastructure.

---

## What It Does

Sovereign Engineering Copilot is a local-first developer assistant that:
1. **Guarantees Local Data Sovereignty**: Operates an automated Privacy Sanitizer that scrubs high-entropy API tokens, credentials, connection strings, internal IPs, and emails before any prompt leaves the local machine.
2. **Maintains Temporal Architectural Memory**: Implements a temporal knowledge graph (backed by local SQLite) that tracks Architectural Decision Records (ADRs) with validity timestamps, relevance scoring, and temporal decay.
3. **Prevents Architectural Drift & Regressions**: Automatically injects active historical architectural constraints into the system prompt and excludes outdated or superseded decisions.
4. **Autonomous Self-Healing Refactoring**: Employs an iterative test-driven repair loop (`sovereign refactor`) that applies candidate code patches, runs the local test suite, and autonomously iterates if tests fail while strictly adhering to ADRs.
5. **Leverages NVIDIA Nemotron on Nebius Token Factory**: Offloads complex architectural synthesis and refactoring planning to NVIDIA Llama-3.1-Nemotron-70B running on Nebius high-performance open cloud infrastructure.
6. **Live Best Practice Grounding via Tavily**: Integrates Tavily Search API to dynamically query official framework documentation and security advisories (entering the 'Best Use of Tavily' bounty).
7. **Model Context Protocol (MCP) Server**: Provides standard JSON-RPC stdio server endpoints (`sovereign mcp`) so Claude Desktop, Cursor, and Hermes Agent can leverage Sovereign Copilot's memory and privacy guardrails.
8. **Visual Graph & Security Audit**: Inspects the entire codebase for exposed secrets (`sovereign audit`) and renders the visual tree of active vs superseded ADRs (`sovereign graph`).

---

## How We Built It

- **Language & Runtime**: Python 3.10+ packaged with modern pyproject.toml tooling and uv.
- **Inference & Acceleration**: OpenAI-compatible client interfacing with **Nebius Token Factory** (`https://api.tokenfactory.nebius.com/v1`) driving **NVIDIA Llama-3.1-Nemotron-70B-Instruct** for reasoning and decision validation.
- **Temporal Memory Engine**: Graph-structured relational SQLite schema tracking decisions, validity intervals (`valid_from`, `valid_until`), relationships (`SUPERSEDED_BY`), and exponential temporal decay ranking.
- **Privacy Layer**: High-performance regex sanitization pipeline mapping sensitive secrets into reversible pseudonym tokens (`[SOVEREIGN_REDACTED_*]`).
- **Testing & Tooling**: Local tool executor running automated tests (`pytest`) in isolated environments.

---

## Challenges We Ran Into

- **Temporal Drift vs. Flat RAG**: Standard vector retrieval often surfaces obsolete decisions alongside current ones (e.g. returning old REST polling rules alongside newer WebSocket streaming rules). We solved this by implementing an explicit state graph with `superseded_by` relationships and temporal decay penalties.
- **Deterministic Secret Scrubbing**: Ensuring regex patterns catch complex connection strings (e.g. embedded passwords in database URIs) without corrupting ordinary code syntax.
- **Cross-Platform File Locks**: Handling SQLite connections cleanly with context managers on Windows environments to prevent file-locking during rapid sub-process test runs.

---

## Accomplishments We're Proud Of

- Zero-leakage privacy guarantee verified: proprietary credentials never escape the local perimeter in plaintext.
- Temporal Architectural Memory prevents repeated mistakes and preserves institutional engineering knowledge across sessions.
- Sub-second local response time and clean integration with Nebius Token Factory's remote API.

---

## What We Learned

- Open-weight models like NVIDIA Nemotron-70B, when coupled with strict contextual memory and clear system guardrails, match or exceed proprietary cloud assistants in following strict architectural constraints.
- Nebius Token Factory offers developer-friendly inference with low latency and OpenAI-compatible drop-in integration.

---

## What's Next for Sovereign Engineering Copilot

- Integrating Model Context Protocol (MCP) server endpoints for multi-agent delegation.
- IDE extensions (VS Code / JetBrains plugin) for inline architectural warnings when code violates active ADRs.
- Autonomous PR review bot running locally in air-gapped CI/CD pipelines.

---

## Built With

- python
- nebius-token-factory
- nvidia-nemotron
- tavily-search
- model-context-protocol
- sqlite
- pytest
- open-source-mit
