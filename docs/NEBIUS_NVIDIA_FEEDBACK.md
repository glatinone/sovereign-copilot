# Sponsor Feedback: Nebius Token Factory & NVIDIA Nemotron

Hackathon: Nebius x NVIDIA Global AI Hackathon (Personal AI Track)
Project: Sovereign Engineering Copilot
Author: Kiell Tampubolon

This document provides structured, actionable feedback on Nebius Token Factory and NVIDIA Nemotron models, based on our real-world implementation of Sovereign Engineering Copilot.

---

## 1. Nebius Token Factory (Inference API)

### What We Used It For
We used Nebius Token Factory as our remote high-performance reasoning engine. While sensitive codebase parsing and privacy redactions run locally on the developer's workstation, sanitized architectural contexts and complex refactoring plans are offloaded to Token Factory's inference endpoint (`https://api.tokenfactory.nebius.com/v1`).

### What Worked Well
1. **OpenAI Compatibility**: The `/v1/chat/completions` schema made integration straightforward. Using standard HTTP clients (`httpx` in Python) required zero proprietary SDK bloat.
2. **Low Latency & Throughput**: Time-to-First-Token (TTFT) on large models like Nemotron-70B was remarkably consistent, enabling snappy interactive CLI experiences.
3. **Transparent Model Naming**: Clear namespacing (`nvidia/llama-3.1-nemotron-70b-instruct`) made it easy to configure and switch models dynamically.

### What Needs Work / Constructive Suggestions
1. **Structured Outputs / JSON Mode Reliability**: While basic JSON generation works, native support for strict JSON schema enforcement (similar to OpenAI's `response_format: { type: "json_schema" }`) would significantly enhance tool-calling and structured plan generation.
2. **Token Usage Metrics in Error Responses**: When hitting rate limits or payload size caps, clearer error bodies detailing specific quota thresholds (current tokens vs. maximum allowed) would improve programmatic fallback handling.
3. **Local Development Proxy / Mock Emulator**: Providing an official lightweight local emulator or offline testing stub for Token Factory would accelerate developer testing in CI pipelines.

### Onboarding Experience (Zero to Hello World)
Onboarding took less than 10 minutes from generating the API key in the Nebius Console to making the first `curl` request. The developer documentation is clean and free of unnecessary marketing fluff.

### Would We Build With Nebius Token Factory Again?
**Yes, absolutely.** The combination of competitive token pricing, European data privacy alignment, and ultra-fast inference on top-tier NVIDIA GPU infrastructure makes Token Factory our go-to backend for open-weight agent deployments.

---

## 2. NVIDIA Open-Source Models (Nemotron Family)

### What We Used It For
We deployed **NVIDIA Llama-3.1-Nemotron-70B-Instruct** as the primary cognitive engine for architectural compliance verification and refactoring generation.

### What Worked Well
1. **Strict Instruction Following**: Nemotron-70B demonstrated exceptional adherence to negative constraints in the system prompt (e.g., "Never violate ADR #1" or "Do not reintroduce deprecated patterns"). This is a notable improvement over generic open-weight models that frequently suffer from instruction drift.
2. **Complex Multi-Step Reasoning**: The model excels at evaluating trade-offs between competing architectural decisions (e.g. latency vs. consistency in message broker migrations).
3. **Tone and Precision**: The generated code patches and architectural rationales were concise, direct, and free of conversational filler.

### What Needs Work / Constructive Suggestions
1. **Context Window Utilization on Deep Codebases**: When feeding large unified diffs alongside multiple historical ADRs, attention retention at the middle of the context window can slightly degrade. Fine-tuning specifically on long-context code refactoring tasks would be valuable.
2. **Nemotron Nano & Edge Portability**: We would love to see pre-quantized GGUF / TensorRT-LLM 4-bit checkpoints published alongside full-weight releases, enabling direct edge deployment on local machines and NVIDIA Jetson hardware without manual conversion pipelines.

### Would We Build With NVIDIA Nemotron Again?
**Yes.** Nemotron-70B represents one of the strongest open-weights reasoning models available for developer tools and autonomous agents today.
