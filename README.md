# StackSleuth

From red CI to guilty commit in minutes. Built with IBM Bob IDE for the IBM Bob 2.0 Hackathon (Sept 25-27, 2026).

## The problem

CI goes red on main. Somewhere in the recent commits, something broke. What happens next is the same everywhere: you re-run the test a few times to make sure it's real, you scroll through the log, you start checking out old commits by hand trying to find where it broke. It's slow, it's boring, and it pulls you out of whatever you were actually doing.

I built a loop that does the boring part. You hand it a failing test, and it reproduces the failure, bisects the git history to find the exact commit that broke it, and drafts a patch. The patch never lands on its own. A human reads it, says yes, and only then does it apply and the suite re-runs green.

## How long it takes

Same bug, same repo (8 commits, one seeded off-by-one in a discount tier):

| Step | By hand (conservative) | StackSleuth (measured) |
|---|---|---|
| Confirm the failure is real | a few minutes of re-runs | 3 isolated runs, automatic |
| Find the guilty commit | 20-40 min of manual bisecting | 1.7 seconds, 2 bisect steps |
| Draft the fix | depends on the bug | diff + written rationale, saved for review |
| Apply | whenever you get to it | only after you approve, then suite re-runs green |

The "by hand" column is my honest estimate for this small repo. On a real codebase with hundreds of commits, the gap gets much wider, because bisect scales logarithmically and humans don't.

## The loop

Five stages, each one logged to `evidence/sleuth_log.json`:

1. **Detect.** Run the suite. Get the failing test id and the exact assertion. That's the ground truth for everything after.
2. **Reproduce.** Run that one test 3 times in isolation. If it doesn't fail every time, it's flaky, not a regression, and the loop stops and says so.
3. **Bisect.** Automated `git bisect` against the repo history. Output is a commit hash, not a guess.
4. **Propose.** Read the culprit's diff, draft the smallest fix, write down why the old code was wrong. The proposal (diff + rationale) goes into `evidence/proposals/`. It is never applied at this stage.
5. **Approve gate.** A human reviews the proposal. Only with an explicit yes does the patch apply, and the full suite runs again to confirm green.

## Why Bob IDE is the core, not a side tool

The whole loop runs through Bob:

- A custom `sleuth-debugger` mode (`.bob/custom_modes.yaml`) that knows the reproduce-to-gate workflow and refuses to skip steps.
- A `systematic-debug` skill (`.bob/skills/systematic-debug/SKILL.md`) that teaches the bisect-driven method: one failing test, one bisect, smallest fix, never apply without approval.
- A FastMCP server (`sleuth/`) with 7 tools: `run_tests`, `reproduce`, `bisect`, `inspect_commit`, `propose_patch`, `apply_patch` (human-gated), `log_evidence`. Every tool shells out to real pytest and git. Nothing is mocked.
- Parallel subagents: reproduce and bisect-context gathering are independent, so they fan out.
- Two rules that are load-bearing: `never-apply-without-approval.md` and `evidence-first.md`.
- `bob_sessions/` holds the task summary screenshots, the required proof that the work happened inside Bob.

## Architecture

```
                    Bob IDE
  +----------------------------------------+
  |  sleuth-debugger custom mode           |
  |  systematic-debug skill                |
  |  rules: approval gate + evidence-first |
  |  parallel subagents                    |
  +---------------+------------------------+
                  |  MCP over stdio
  +---------------v------------------------+
  |  sleuth-mcp (FastMCP server)           |
  |  run_tests / reproduce / bisect /      |
  |  inspect_commit / propose_patch /      |
  |  apply_patch (gated) / log_evidence    |
  +---------------+------------------------+
                  |  subprocess
  +---------------v------------------------+
  |  demo/ : seeded Python repo            |
  |  8 commits, bug in commit 4,           |
  |  1 failing test at HEAD                |
  +----------------------------------------+
```

## The 90-second demo

1. (0-10s) "It's 2 AM. CI just went red. The suite was green 8 commits ago."
2. (10-30s) I paste the failing test into Bob in `sleuth-debugger` mode. One subagent reproduces the failure 3 times. Another starts bisecting.
3. (30-55s) "Culprit: commit `afcc8ee`, 'refactor: simplify discount tier lookup'. It flipped `>=` to `>` on the 10-unit boundary, so exactly 10 units lost the 10% discount." The patch proposal and rationale come up.
4. (55-75s) I approve. The patch applies. Full suite: 10 passed, 0 failed.
5. (75-90s) "Detect to culprit took under 2 seconds. Every step is in the evidence log, and no patch landed without a human saying yes."

If the live demo gods aren't kind, there's a recorded golden run as backup. The loop itself is deterministic, so the recording is the same thing you'd see live.

## Repo layout

- `demo/` : the seeded repo. Run `./demo/make_demo.sh` to regenerate it byte-identical anywhere (fixed commit dates, same hashes every time). The bug is in commit 4, `refactor: simplify discount tier lookup`.
- `sleuth/` : the FastMCP server (`server.py`), the bisect probe (`bisect_probe.py`), and pytest tests (`sleuth/tests/`). Run them with `pytest sleuth/tests`.
- `.bob/` : Bob IDE configs. Custom mode, skill, `mcp.json` wiring, rules, `.bobignore`.
- `bob_sessions/` : Bob IDE task screenshots go here during the hackathon (naming: `<team>_taskNN_<desc>.png`).
- `evidence/` : append-only `sleuth_log.json` plus `proposals/`.
- `docs/BATTLE_PLAN.md` : the full plan, including the runbook for hackathon day.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./demo/make_demo.sh            # builds demo/ with its git history
.venv/bin/python -m pytest sleuth/tests   # 7 tests, all green
.venv/bin/python sleuth/server.py         # starts the MCP server on stdio
```

Then point Bob IDE at this folder. `mcp.json` wires the server over stdio, and `sleuth-debugger` shows up in the mode picker.

Built solo for the IBM Bob 2.0 Hackathon. The plan, the process notes, and what's next are in `docs/BATTLE_PLAN.md`.
