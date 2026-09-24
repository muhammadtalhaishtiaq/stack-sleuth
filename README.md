# StackSleuth — from red CI to guilty commit in minutes

An automated debugging loop built with **IBM Bob IDE** for the IBM Bob 2.0 Hackathon (Sept 25–27, 2026).

**The loop:** a failing CI log goes in → Bob subagents **reproduce** the failure deterministically → automated **git bisect** finds the culprit commit → a patch is **proposed** with rationale → a human **approves** → the suite goes green. Every stage is written to a timestamped evidence log. No patch ever lands without a human saying yes.

**Why it wins:** debugging eats a huge share of dev time; we show manual bisect (hours) vs StackSleuth (minutes) on the same bug. Bob IDE is the engine, not a side tool: a custom `sleuth-debugger` mode, a `systematic-debug` skill, a FastMCP server, and parallel subagents.

## Repo layout

- `demo/` — seeded Python repo (git history included) with a deterministic bug for the live demo
- `sleuth/` — FastMCP server: `run_tests`, `reproduce`, `bisect`, `inspect_commit`, `propose_patch`, `apply_patch` (human-gated), `log_evidence`
- `.bob/` — Bob IDE configs: custom mode, skill, MCP wiring, rules
- `bob_sessions/` — Bob IDE task session screenshots (PNG), the required evidence of Bob usage
- `evidence/` — append-only run log + patch proposals
- `docs/BATTLE_PLAN.md` — the full A-to-Z plan, so the process itself is visible

## Status

Scaffold phase. Full build in progress — the loop is verified end-to-end before the hackathon starts.
