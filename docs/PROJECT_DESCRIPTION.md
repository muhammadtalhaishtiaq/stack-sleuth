# StackSleuth — Project Description

## What It Is
StackSleuth is an automated debugging agent that finds and fixes regressions in codebases. It implements the full debugging loop that a senior engineer performs manually: reproduce the failure, bisect to the culprit commit, inspect the diff, propose a minimal patch, wait for human approval, then apply and verify green.

## How It Works
StackSleuth exposes its capabilities as MCP (Model Context Protocol) tools that an AI agent (IBM Bob) calls:

1. **Detect** — `run_tests` executes the test suite and identifies failing tests.
2. **Reproduce** — `reproduce` runs the failing test 3x in isolation to confirm it's deterministic, not flaky.
3. **Bisect** — `bisect` automates `git bisect` with a probe command to find the exact commit that introduced the bug.
4. **Inspect** — `inspect_commit` shows the diff of the culprit commit.
5. **Propose** — `propose_patch` saves a minimal fix with a written rationale. The patch is HELD at a human approval gate — never auto-applied.
6. **Apply & Verify** — After explicit human approval, `apply_patch` applies the fix and re-runs the full suite to confirm green.

Every stage is logged to an append-only evidence log (`evidence/sleuth_log.json`).

## The Demo
A seeded demo repository with 8 deterministic commits contains a real regression: commit `afcc8ee` ("refactor: simplify discount tier lookup") changed `qty >= 10` to `qty > 10`, breaking the 10% bulk discount for exactly 10 units. StackSleuth finds it in 2 bisect steps and proposes the one-character fix.

A second bug variant (SAVE10 coupon giving 5% instead of 10%) proves the loop generalizes beyond the seeded bug.

## Tech Stack
- Python 3.12, FastMCP server
- Git (bisect automation)
- Pytest (test execution)
- IBM Bob IDE (AI agent, MCP client)
- Custom `sleuth-debugger` mode for Bob

## Originality
Unlike AI code assistants that suggest fixes from patterns, StackSleuth *proves* the culprit via bisect (not guesswork), holds every patch at a human gate (not auto-apply), and logs the full evidence chain (not a black box). The hardening in Task 6 (collection-error detection, dirty-tree refusal) makes it robust for real-world use.
