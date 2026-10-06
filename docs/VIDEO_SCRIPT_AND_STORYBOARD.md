# Video Pitch Script & Storyboard (2 Minutes 30 Seconds)

Target Video Duration: 2:30 (Max limit: 3:00)
Format: Pitch & Live Demo
Platform: Public YouTube Video
Audio Rule: Must explicitly mention "Nebius Token Factory" and "NVIDIA Nemotron" in voiceover.

---

## Storyboard Overview

| Timecode | Phase | Visual / Screen Recording | Voiceover Audio (Narration) |
|---|---|---|---|
| 0:00 - 0:30 | Problem Pitch | Title slide: "Sovereign Engineering Copilot" with high-contrast, clean typography. Transition to a developer screen with red warning: "Cloud AI Forbidden: IP & Secret Leakage Risk". | "Every engineering team faces a major dilemma: cloud AI assistants promise massive speed, but proprietary codebases forbid sending secrets to commercial cloud vendors. Worse, existing coding bots suffer from amnesia: they forget past architectural trade-offs, reintroducing bugs and technical debt you solved months ago." |
| 0:30 - 1:00 | Solution & Privacy | Terminal screen opening. Developer runs: `sovereign init`. Developer runs: `sovereign memory list`. Shows active ADR #1: "Enforce Idempotent Transaction Keys". | "Meet Sovereign Engineering Copilot: an autonomous, privacy-preserving engineering partner. It keeps your code and credentials 100% on your machine, while maintaining a Temporal Architectural Memory of your past engineering decisions." |
| 1:00 - 1:45 | Live Demo: Refactor & Test | Developer types refactoring prompt containing real connection strings and API keys: `sovereign ask "Refactor payment logic..."`. Terminal highlights: `Local Privacy Redactions: 2 items sanitized`, `Temporal ADRs Injected: [1]`. Automated test suite runs: `ALL TESTS PASSED`. | "Watch this in action. When I submit a refactor task containing sensitive database URLs and API keys, Sovereign Copilot's local sanitizer intercepts and redacts every secret before anything leaves the machine. Simultaneously, it queries our local SQLite temporal graph, recalling ADR number 1, so the generated refactor strictly preserves idempotency." |
| 1:45 - 2:15 | Tech Stack & Sponsor Callout | Architecture diagram overlay showing local privacy boundary and remote GPU offloading. Terminal showing inference payload. | "To power high-level architectural reasoning without compromising privacy, Sovereign Copilot offloads sanitized context directly to **Nebius Token Factory**, driving the state-of-the-art **NVIDIA Llama-3.1-Nemotron-70B** model. This gives developers frontier-class reasoning on open, independent infrastructure with guaranteed data sovereignty." |
| 2:15 - 2:30 | Closing & Impact | Developer runs: `sovereign memory add --supersedes 1`. Terminal confirms ADR updated. GitHub repo URL displayed. | "Finally, as systems evolve, Sovereign Copilot updates its temporal memory, deprecating old conventions to prevent drift. Full source code, documentation, and setup instructions are open source on GitHub. Thank you to Nebius and NVIDIA for empowering sovereign AI builders." |

---

## Voiceover Script (English - Clear & Direct)

```text
[0:00 - 0:30]
Every engineering team faces a major dilemma: cloud AI assistants promise massive speed, but proprietary codebases forbid sending secrets to commercial cloud vendors. Worse, existing coding bots suffer from contextual amnesia: they forget past architectural trade-offs, reintroducing bugs and technical debt you solved months ago.

[0:30 - 1:00]
Meet Sovereign Engineering Copilot: an autonomous, privacy-preserving engineering partner. It keeps your code and credentials 100% on your local machine, while maintaining a Temporal Architectural Memory of your past engineering decisions.

[1:00 - 1:45]
Watch this in action. When I submit a refactoring task containing sensitive database URLs and API keys, Sovereign Copilot's local sanitizer intercepts and redacts every secret before anything leaves the machine. Simultaneously, it queries our local temporal graph, recalling ADR number 1, so the generated refactor strictly preserves our team's idempotency invariants. The local test suite runs automatically, verifying zero regressions.

[1:45 - 2:15]
To power high-level architectural reasoning without compromising privacy, Sovereign Copilot offloads sanitized context directly to Nebius Token Factory, driving the state-of-the-art NVIDIA Llama-3.1-Nemotron-70B model. This gives developers frontier-class reasoning on open, independent GPU infrastructure with guaranteed data sovereignty.

[2:15 - 2:30]
Finally, as your system evolves, Sovereign Copilot updates its temporal memory, deprecating old conventions to prevent architectural drift. Full source code is open source under the MIT license. Thank you to Nebius and NVIDIA for empowering sovereign AI builders.
```
