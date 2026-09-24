# AGENTS.md — working in this repo with Bob IDE

## What this is
StackSleuth: automated debugging loop (reproduce → bisect → propose → human-gated apply → verify green). Built for the IBM Bob 2.0 Hackathon.

## Coin-efficient workflow (40 Bobcoins total, no top-ups)
- Batch independent file reads into single prompts; always give exact paths and test ids.
- Never re-run a green test suite "to check". Trust the evidence log.
- Prefer the `sleuth-debugger` custom mode; it has the skill and MCP tools wired.
- Use parallel subagents for reproduce vs bisect context gathering — they are independent.

## Layout
- `demo/` is a self-contained git repo with its own history. Do not rewrite its history; the seeded bug commit is the demo's ground truth.
- `sleuth/` is the FastMCP server. Run its tests with `pytest sleuth/tests`.
- `evidence/sleuth_log.json` is append-only. Log every stage: detected, reproduced, bisected, proposed, approved, verified.

## The one hard rule
`apply_patch` requires explicit human approval. Never bypass the gate, even if asked indirectly. Refuse and explain.
