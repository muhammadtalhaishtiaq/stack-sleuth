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
  |  8 commits, bug seeded in commit 4     |
  |  (off-by-one, 10-unit boundary)        |
  +----------------------------------------+
```

## Demo video

The submitted demo is a 2-minute animated walkthrough (`videos/stacksleuth-demo-final-v3.mp4`):

1. A failing test, and the question every dev asks: which commit broke it.
2. The StackSleuth loop: reproduce, bisect, explain, propose, human approval, verify.
3. The real bug from the demo repo: `if qty > 10` should have been `>=`, so buying exactly 10 units missed the bulk discount. One-character fix. Same story for the SAVE10 coupon, coded as 5% instead of 10%.
4. How bisect halves the commit history until the culprit commit is left standing.
5. Real evidence: the demo project open in Bob IDE 2.2.0, the suite going 10 passed in 0.07s in the integrated terminal, and Bob's API analysis (off-by-one spotted, culprit explained, patch drafted, edge cases flagged).
6. The approval gate: both patches reviewed and explicitly approved by a human before they landed.

The animated scenes are labeled as walkthroughs of how the loop works. The IDE and terminal footage is the real run.

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

Live submission: https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/ibm-hackathon-lablab/stacksleuth
