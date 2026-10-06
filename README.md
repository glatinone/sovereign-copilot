# Sovereign Engineering Copilot

[![CI](https://github.com/glatinone/sovereign-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/glatinone/sovereign-copilot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![Live Demo](https://img.shields.io/badge/Demo-Interactive%20Showcase-brightgreen)](https://glatinone.github.io/sovereign-copilot/)

> A private, autonomous software engineering copilot with Temporal Architectural Memory and zero-leakage local governance, powered by NVIDIA Nemotron on Nebius Token Factory.

Submitted to the **Nebius x NVIDIA Global AI Hackathon** (Personal AI Track).

**Live Interactive Showcase**: [https://glatinone.github.io/sovereign-copilot/](https://glatinone.github.io/sovereign-copilot/)  
**Pitch & Demo Video (1:52)**: [https://youtu.be/z8i3hh4c3uk](https://youtu.be/z8i3hh4c3uk)  
**Technical Architecture Spec**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## The Problem

1. **Intellectual Property Leakage**: Enterprise developers and proprietary software engineers are strictly forbidden from using commercial cloud AI assistants due to confidential source code and credential exposure.
2. **Contextual Amnesia (Temporal Drift)**: Conventional AI coding tools only see transient context windows and forget *why* past architectural choices were made, resulting in constant regression of codebase conventions.
3. **Fragile Tool Execution**: Agents running without local sandboxing or policy enforcement risk unintended modifications and prompt injection vulnerabilities.

---

## Architecture

```
+-------------------------------------------------------------+
|                     LOCAL BOUNDARY                          |
|                                                             |
|  [ Developer Request ] ---> [ Local Privacy Sanitizer ]     |
|                                   | (Redacts keys, PII, IPs)|
|                                   v                         |
|  [ Temporal Architectural  ] ---> [ Prompt Context Binder ] |
|  [ Memory (SQLite Graph)   ]                                |
|                                   |                         |
+-----------------------------------|-------------------------+
                                    | (Sanitized Payload)
                                    v
+-------------------------------------------------------------+
|                  NEBIUS TOKEN FACTORY                       |
|                                                             |
|  Model: NVIDIA Llama-3.1-Nemotron-70B-Instruct              |
|  - High-level Architectural Reasoning                       |
|  - Compliance verification against past ADRs               |
+-------------------------------------------------------------+
                                    | (Action Plan / Diff)
                                    v
+-------------------------------------------------------------+
|                     LOCAL BOUNDARY                          |
|                                                             |
|  [ Local Tool Executor ] ---> [ Automated Test Runner ]     |
|  - Git Diff Inspection        - Verifies unit tests pass    |
|                                                             |
|  [ New Decision Recorder ] -> [ Temporal Memory (ADRs) ]    |
+-------------------------------------------------------------+
```

---

## Key Features

- **Local Privacy Sanitizer**: High-entropy API keys, passwords, bearer tokens, internal RFC1918 IPs, and credentials are pseudonymized before prompts leave the local machine.
- **Temporal Architectural Memory**: Tracks active Architectural Decision Records (ADRs) with validity timestamps, relevance scoring, and temporal decay. Automatically flags and excludes superseded decisions.
- **NVIDIA Nemotron via Nebius Token Factory**: Seamlessly offloads complex reasoning to NVIDIA Nemotron models hosted on Nebius high-performance open GPU infrastructure.
- **Autonomous Self-Healing Refactoring**: Test-driven loop that applies patches, validates test suites, and autonomously repairs failed attempts up to N retries while preserving ADR constraints.
- **Tavily Live Knowledge Search**: Dynamically retrieves official framework documentation, architecture patterns, and CVE advisories to ground reasoning.
- **Model Context Protocol (MCP) Server**: Exposes memory, sanitization, and test runner tools over standard MCP JSON-RPC protocol for Claude Desktop, Cursor, and Hermes Agent.
- **Controlled Local Tool Execution**: Generates and inspects patches locally, running test suites in isolated subprocesses before changes are finalized.

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/glatinone/sovereign-copilot.git
cd sovereign-copilot
pip install -e .
```

### 2. Configure Environment

Create a `.env` file (which is gitignored by default):

```bash
NEBIUS_API_KEY="your-nebius-token-factory-key"
SOVEREIGN_MODEL="nvidia/llama-3.1-nemotron-70b-instruct"
```

*Note: If no API key is provided, Sovereign Copilot automatically operates in local deterministic verification mode.*

### 3. Usage

#### Initialize Workspace
```bash
sovereign init
```

#### Record Architectural Decisions (ADRs)
```bash
sovereign memory add \
  --title "Use Async Event Bus for Payment Processing" \
  --rationale "Decouple microservices and support horizontal scaling" \
  --tags "payment,async,broker"
```

#### List Active Decisions
```bash
sovereign memory list
```

#### Ask Copilot to Reason on Code with Memory & Privacy
```bash
sovereign ask "Refactor our payment handling pipeline to add batch retry logic."
```

#### Autonomous Self-Healing Refactor with Test Verification
```bash
sovereign refactor payment_service.py \
  --prompt "Add retry logic with exponential backoff" \
  --test-cmd "pytest test_payment.py" \
  --max-retries 3
```

#### Visual Memory Graph & Relationship Tree
```bash
sovereign graph
```

#### Local Privacy & Secret Leak Audit
```bash
sovereign audit
```

#### Framework Best Practice Search (Tavily)
```bash
sovereign search "distributed payment idempotency redis"
```

#### Run as Model Context Protocol (MCP) Server
```bash
sovereign mcp
```

#### Run Automated Tests
```bash
sovereign ask "Refactor calculation logic" --test
```

---

## License

This project is licensed under the [MIT License](LICENSE).
