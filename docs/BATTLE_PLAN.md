# StackSleuth — A-to-Z Battle Plan
### IBM Bob 2.0 Hackathon · Sept 25 (11:00 AM EDT) → Sept 27, 2026 · Solo
### Goal: win outright. First prize $5,000.

---

## 1. Mission

Build an automated debugging loop inside IBM Bob IDE: a failing CI log goes in, and parallel Bob subagents reproduce the failure, bisect to the guilty commit, and draft a patch that only lands behind a human approve gate. Every stage writes to a timestamped evidence log. The demo is a 90-second story: red CI → guilty commit found → green CI, with quantified time saved.

Why this wins: no IBM hackathon winner has done reproduce-to-patch; it makes Bob irreplaceable (custom mode + skill + MCP + subagents, the Pedigree playbook); the impact is measurable in minutes, not adjectives; and the whole thing demos live.

---

## 2. Win-criteria mapping

| Judging criterion | How we score | Evidence |
|---|---|---|
| Application of Technology | Bob IDE is the engine, not a side tool: custom `sleuth-debugger` mode, `systematic-debug` skill, FastMCP server, parallel subagents for reproduce/bisect/propose | `bob_sessions/` screenshots, `.bob/` configs in repo |
| Presentation | 90-second story video (2 AM broken build → fixed), clean slides, live-or-recorded demo | Video + slides in submission |
| Business Value | Debugging eats ~25-50% of dev time; we show manual bisect (hours) vs StackSleuth (minutes) on the same bug | Before/after table in README + video |
| Originality | Nobody won with this; PR bots are crowded, legacy modernization is a guide example (crowded). This lane is empty. | Positioning in long description |

---

## 3. Product definition

**Problem:** When CI goes red, a developer manually re-runs tests, guesses at the cause, and hand-bisects history. Slow, error-prone, interrupts flow.

**The loop (5 stages):**
1. **Detect** — feed a failing CI log / test id.
2. **Reproduce** — run the failing test 3x in isolation; confirm deterministic failure.
3. **Bisect** — automated `git bisect` against the repo history; output = culprit commit hash + diff.
4. **Propose** — draft a unified-diff patch + written rationale; written to `evidence/proposals/`, never auto-applied.
5. **Approve gate** — human says yes; patch applies; full suite re-runs green. Every stage appends to `evidence/sleuth_log.json`.

**Non-goals for the 48h:** multi-language support (Python only), distributed CI integration (local pytest + pasted CI logs), auto-merging (the gate is the point).

---

## 4. Architecture

```
                    ┌──────────────────────────────┐
                    │        Bob IDE (required)     │
                    │  sleuth-debugger custom mode  │
                    │  systematic-debug skill       │
                    │  rules: approval + evidence   │
                    │  parallel subagents           │
                    └──────────────┬───────────────┘
                                   │ MCP (stdio)
                    ┌──────────────▼───────────────┐
                    │      sleuth-mcp (FastMCP)     │
                    │  run_tests / reproduce /      │
                    │  bisect / inspect_commit /    │
                    │  propose_patch / apply_patch  │
                    │  (gated) / log_evidence       │
                    └──────────────┬───────────────┘
                                   │ subprocess
              ┌────────────────────▼──────────────────┐
              │  demo/ — seeded Python repo (git)     │
              │  8 commits, bug in commit 5,          │
              │  1 failing test at HEAD               │
              └───────────────────────────────────────┘
```

**Bob IDE layer** (`.bob/`): `custom_modes.yaml` (sleuth-debugger), `skills/systematic-debug/SKILL.md`, `mcp.json` (stdio wiring), `rules/never-apply-without-approval.md`, `rules/evidence-first.md`, `.bobignore`, `AGENTS.md`.

**Evidence store** (`evidence/`): `sleuth_log.json` (append-only run log), `proposals/` (patch diffs + rationales).

---

## 5. Implementation plan

### Phase 0 — Tonight (pre-hackathon, zero Bobcoins spent)
All done outside Bob IDE by the assistant. Status: builder running now.
- [ ] Public GitHub repo `stack-sleuth` created
- [ ] `demo/` generator script + seeded bug repo (deterministic)
- [ ] `sleuth-mcp` FastMCP server, all 7 tools working
- [ ] `.bob/` configs (mode, skill, mcp.json, rules, bobignore)
- [ ] `AGENTS.md`, `README.md` pitch draft, `bob_sessions/README.md` placeholder
- [ ] Full loop verified end-to-end: red → bisect finds seeded commit → propose → approve → green
- [ ] Unit tests for MCP tools green

### Phase 1 — Hackathon start, hours 0–6 (Sept 25, 11 AM → 5 PM EDT)
Talha in Bob IDE (MacBook):
1. Install/upgrade Bob IDE to latest v2.0.x
2. Sign in with hackathon-provisioned account (register email; IBMid if needed)
3. Settings → select instance `ibm-coding-challenge-uat` (region: us-east)
4. Clone/open `stack-sleuth`, verify MCP server loads, verify custom mode appears
5. Bob Task 1 (screenshot): "Reproduce the failing test" — run reproduce flow via Bob
6. Bob Task 2 (screenshot): "Bisect to culprit commit" — subagent run

### Phase 2 — Hours 6–18 (evening Sept 25)
- Bob Task 3 (screenshot): "Draft the patch" — inspect culprit diff, propose patch
- Bob Task 4 (screenshot): "Approve gate + verify green" — apply with approval, full suite green
- Parallel subagent task: second bug variant in demo repo (proves it generalizes, not a one-trick demo)
- Harden: edge cases (flaky test detection via 3x runs, bisect failure fallback message)

### Phase 3 — Hours 18–30 (Sept 26)
- Evidence log review; export final `sleuth_log.json`
- Before/after metrics table finalized (time the manual path once, honestly, for the comparison)
- README finalized; architecture diagram; repo cleaned

### Phase 4 — Hours 30–42 (Sept 26–27)
- 90-second demo video (script below; golden run recorded as backup)
- Slide deck (problem → loop → demo → metrics → Bob-depth → what's next)
- Submission draft: title, short/long descriptions, tags

### Phase 5 — Hours 42–48 (buffer → deadline Sept 27)
- Re-verify: fresh clone, full loop, all links work
- Submit on lablab.ai. Screenshot the confirmation.

---

## 6. Test plan

| Level | Cases | Pass criteria |
|---|---|---|
| Unit (MCP tools) | run_tests parses pytest output; reproduce runs 3x; bisect returns correct commit; propose_patch writes files; apply_patch refuses when approved=false; log_evidence appends valid JSON | pytest green |
| Integration | Full loop on demo repo, twice (two bug variants) | Culprit commit identified exactly; suite green after approved apply |
| Determinism | `make_demo.sh` regenerates identical history; reproduce 3x stable | Same commit hash, same failure, every run |
| Negative | apply_patch without approval; bisect with no failing test; empty repo path | Clean refusal messages, no partial state |
| Demo rehearsal | Golden run recorded end-to-end | Usable as video backup if live demo fails |

---

## 7. Bobcoin budget (40 coins, no top-ups)

| Planned session | Est. coins |
|---|---|
| Task 1: reproduce flow | 3–4 |
| Task 2: bisect via subagent | 4–5 |
| Task 3: patch drafting | 4–5 |
| Task 4: approve + verify | 2–3 |
| Task 5: second bug variant (parallel subagents) | 5–6 |
| Task 6: hardening / edge cases | 4–5 |
| Task 7: README + docs polish in Bob | 3–4 |
| Buffer (surprises, re-runs) | 8–10 |
| **Total** | **~35–40** |

Rules: batch independent reads in one prompt; never re-run a green test to "check"; keep prompts specific (file paths, test ids); if coins hit 100%, continue with local tooling only.

---

## 8. Evidence plan (`bob_sessions/`)

One PNG per Bob task, named `<team>_taskNN_<short-desc>.png`:
- `muhammadtalha_task01_reproduce_failure_summary.png`
- `muhammadtalha_task02_bisect_culprit_commit_summary.png`
- `muhammadtalha_task03_patch_proposal_summary.png`
- `muhammadtalha_task04_approve_gate_verify_green_summary.png`
- `muhammadtalha_task05_second_bug_variant_summary.png`
- `muhammadtalha_task06_hardening_summary.png`

Take the screenshot from the Bob IDE Tasks view (select "All" if tasks span workspaces), right after each task's summary appears. Do not skip: missing evidence = eligibility risk.

---

## 9. Submission checklist (lablab.ai "What to Submit")

- [ ] Project title: **StackSleuth — from red CI to guilty commit in minutes**
- [ ] Short description (1–2 lines)
- [ ] Long description (problem, loop, Bob depth, metrics, what's next)
- [ ] Technology & category tags (Bob IDE, MCP, Python, FastMCP, debugging, developer-tools)
- [ ] Video presentation (90 sec, story format)
- [ ] Slide presentation
- [ ] Public GitHub repo with `bob_sessions/`
- [ ] Demo application platform + application URL (note: CLI/MCP tool — demo via recorded run + repo; state this honestly)

---

## 10. Demo script (90 seconds)

1. (0–10s) "It's 2 AM. CI just went red on main. 47 commits since the last green build."
2. (10–30s) Paste the failing log into Bob (sleuth-debugger mode). Subagents fan out: one reproduces the failure 3x, one starts bisecting history.
3. (30–55s) "Culprit found: commit `a3f9…` — 'fix discount rounding'. The diff touched the tax path." Patch proposed, rationale shown.
4. (55–75s) Human approves. Patch applies. Full suite: green.
5. (75–90s) "Manual bisect: ~2 hours. StackSleuth: 4 minutes. Every step logged, every patch gated." End card: repo + evidence.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Reproduce step flaky live | Deterministic seeded demo; golden-run recording as video backup |
| Bobcoins run out | Budget above with ~25% buffer; coin-efficient prompt rules |
| IDE version/account issues at start | Phase 1 starts with install + sign-in verification before any build session |
| Bisect slow on large history | Demo repo is 8 commits by design; note scaling path in long description |
| Judges see "just a script" | Bob depth is the differentiator: custom mode, skill, MCP, subagents all visible in repo + screenshots |
| Deadline time unknown (Sept 27, no hour given) | Target internal deadline: Sept 27, 12:00 PM EDT; submit early |

---

## 12. Talha's runbook (Sept 25, 11:00 AM EDT)

1. Upgrade/install Bob IDE to latest v2.0.x (v1.0.3 and v2.0.0 stop working Sept 30).
2. Check email for the IBM Bob team invite ("added as team member to ibm-hackathon-xxxx"); create IBMid for the registration email if needed.
3. Bob IDE → Log in to Bob → complete IBMid auth in browser.
4. Settings → General → switch to **ibm-coding-challenge-uat (region: us-east)**. Confirm Bobcoin balance shows 40.
5. Clone `stack-sleuth`, open the folder in Bob IDE. Confirm `sleuth-mcp` appears in MCP servers and `sleuth-debugger` in the mode picker.
6. Run Task 1 prompt (will be provided verbatim the night before): reproduce flow. Screenshot → `bob_sessions/`.
7. Continue Tasks 2–6 per the evidence plan. Follow the coin rules.
8. Tell the assistant when each task's screenshot is saved; the assistant assembles video/slides/submission text in parallel.

---

*Plan written 2026-09-24. Builder working Phase 0 now. Nothing here is invented: every component gets verified working before the hackathon starts.*
