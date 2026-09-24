# StackSleuth: A-to-Z Battle Plan
### IBM Bob 2.0 Hackathon, Sept 25 (11:00 AM EDT) to Sept 27, 2026. Solo.
### Goal: win it. First prize is $5,000.

---

## 1. What I'm building

An automated debugging loop inside IBM Bob IDE. A failing test goes in, and Bob subagents reproduce the failure, bisect the git history to the guilty commit, and draft a patch. The patch only lands behind a human approve gate. Every stage writes to a timestamped evidence log.

The demo is a 90-second story: red CI, guilty commit found, green CI, with real timing numbers.

Why I think this wins: no IBM hackathon winner has done reproduce-to-patch. Bob is irreplaceable here (custom mode, skill, MCP server, subagents, the same depth that won Bob 1.0 for Pedigree). The impact is measurable in seconds, not adjectives. And the whole thing demos live.

---

## 2. How it maps to the judging criteria

- **Application of Technology.** Bob IDE is the engine. Custom `sleuth-debugger` mode, `systematic-debug` skill, FastMCP server, parallel subagents. Evidence: `bob_sessions/` screenshots plus the `.bob/` configs in the repo.
- **Presentation.** 90-second story video (2 AM broken build, fixed), clean slides, live or recorded demo.
- **Business Value.** Debugging eats a huge chunk of dev time. I show the same bug handled by hand vs by the loop, with measured numbers.
- **Originality.** Nobody won with this. PR review bots are crowded, legacy modernization is in the guide as an example (so it'll be crowded too). This lane is empty.

---

## 3. The loop, concretely

**The problem:** CI goes red, and a developer manually re-runs tests, guesses at the cause, and hand-bisects history. Slow and interrupts flow.

**Five stages:**
1. **Detect.** Feed in a failing test id (or CI log). Run the suite, get the exact assertion.
2. **Reproduce.** Run the failing test 3x in isolation. Confirm it's deterministic, not flaky.
3. **Bisect.** Automated `git bisect` over the repo history. Output: culprit commit hash + diff.
4. **Propose.** Draft a unified-diff patch plus a written rationale. Saved to `evidence/proposals/`. Never auto-applied.
5. **Approve gate.** Human says yes, patch applies, full suite re-runs green. Each stage appends to `evidence/sleuth_log.json`.

**Out of scope for the 48 hours:** multi-language (Python only), real CI integration (local pytest plus pasted logs), auto-merge (the gate is the point).

---

## 4. Architecture

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

**Bob layer** (`.bob/`): `custom_modes.yaml`, `skills/systematic-debug/SKILL.md`, `mcp.json` (stdio), `rules/never-apply-without-approval.md`, `rules/evidence-first.md`, `.bobignore`, plus `AGENTS.md` at root.

**Evidence** (`evidence/`): `sleuth_log.json` (append-only), `proposals/` (diffs + rationales).

---

## 5. The plan

### Phase 0: tonight (pre-hackathon, zero Bobcoins spent)
Built outside Bob IDE. Status: done.
- [x] Public repo `stack-sleuth`
- [x] `demo/` generator script + seeded bug repo, deterministic (same hashes everywhere)
- [x] `sleuth-mcp` server, all 7 tools working, real subprocess calls
- [x] `.bob/` configs (mode, skill, mcp.json, rules, bobignore)
- [x] `AGENTS.md`, `README.md`, `bob_sessions/README.md`
- [x] Full loop verified end to end: red, reproduce 3x, bisect found the seeded commit in 2 steps / 1.7s, propose, gate refused without approval, approved apply, 10 passed 0 failed
- [x] 7 pytest tests for the MCP tools, all green

### Phase 1: hours 0-6 (Sept 25, 11 AM to 5 PM EDT)
Me in Bob IDE on the MacBook:
1. Install/upgrade Bob IDE to latest v2.0.x.
2. Sign in with the hackathon-provisioned account.
3. Settings: select instance `ibm-coding-challenge-uat`, region us-east. Confirm 40 Bobcoins.
4. Clone/open `stack-sleuth`. Confirm `sleuth-mcp` loads and `sleuth-debugger` appears in the mode picker.
5. Bob Task 1 (screenshot): reproduce the failing test.
6. Bob Task 2 (screenshot): bisect to the culprit commit, via subagent.

### Phase 2: hours 6-18 (evening of Sept 25)
- Bob Task 3 (screenshot): inspect the culprit diff, propose the patch.
- Bob Task 4 (screenshot): approve gate, apply, suite goes green.
- Parallel subagent task: a second bug variant in the demo repo, to show it generalizes.
- Harden edge cases: flaky-test path, bisect failure message, dirty-tree refusal.

### Phase 3: hours 18-30 (Sept 26)
- Review the evidence log, export the final `sleuth_log.json`.
- Finalize the before/after numbers (time the manual path once, honestly, for the comparison).
- README final pass, repo cleanup.

### Phase 4: hours 30-42 (Sept 26-27)
- 90-second demo video (script below; golden run recorded as backup).
- Slide deck: problem, the loop, demo, numbers, Bob depth, what's next.
- Submission draft: title, short/long descriptions, tags.

### Phase 5: hours 42-48 (buffer, deadline Sept 27)
- Fresh clone, full loop once more, check every link.
- Submit on lablab.ai. Screenshot the confirmation.

---

## 6. Test plan

- **Unit (MCP tools):** run_tests parses pytest output; reproduce runs 3x; bisect returns the exact seeded commit; propose_patch writes files without applying; apply_patch refuses when approved=false; log_evidence appends valid JSON. All green already.
- **Integration:** full loop on the demo repo, twice (two bug variants in Phase 2).
- **Determinism:** `make_demo.sh` regenerates identical history (verified: same commit hashes on re-run). Reproduce 3x stable.
- **Negative:** apply without approval refuses; bisect on a dirty tree refuses; unknown commit id returns a clean error.
- **Demo rehearsal:** golden run recorded end to end, usable as the video if the live demo fails.

---

## 7. Bobcoin budget (40 coins, no top-ups)

| Session | Estimate |
|---|---|
| Task 1: reproduce flow | 3-4 |
| Task 2: bisect via subagent | 4-5 |
| Task 3: patch drafting | 4-5 |
| Task 4: approve + verify | 2-3 |
| Task 5: second bug variant (parallel subagents) | 5-6 |
| Task 6: hardening / edge cases | 4-5 |
| Task 7: README + docs polish in Bob | 3-4 |
| Buffer for surprises | 8-10 |
| **Total** | **about 35-40** |

Rules: batch independent reads into one prompt, never re-run a green suite "just to check", keep prompts specific (paths, test ids). If coins hit 100%, keep working with local tooling only.

---

## 8. Evidence plan (`bob_sessions/`)

One PNG per Bob task, named `<team>_taskNN_<short-desc>.png`:

- `muhammadtalha_task01_reproduce_failure_summary.png`
- `muhammadtalha_task02_bisect_culprit_commit_summary.png`
- `muhammadtalha_task03_patch_proposal_summary.png`
- `muhammadtalha_task04_approve_gate_verify_green_summary.png`
- `muhammadtalha_task05_second_bug_variant_summary.png`
- `muhammadtalha_task06_hardening_summary.png`

Screenshot from the Bob IDE Tasks view (select "All" if tasks span workspaces), right after each task summary appears. Don't skip any. Missing evidence is an eligibility risk.

---

## 9. Submission checklist (lablab.ai "What to Submit")

- [ ] Title: **StackSleuth: from red CI to guilty commit in minutes**
- [ ] Short description (1-2 lines)
- [ ] Long description (problem, the loop, Bob depth, numbers, what's next)
- [ ] Tech and category tags (Bob IDE, MCP, Python, FastMCP, debugging, developer-tools)
- [ ] Video presentation (90 sec, story format)
- [ ] Slide presentation
- [ ] Public GitHub repo with `bob_sessions/`
- [ ] Demo platform + URL (it's a CLI/MCP tool: demo via the recorded run plus the repo; I'll say that plainly)

---

## 10. Demo script (90 seconds)

1. (0-10s) "It's 2 AM. CI just went red on main. The suite was green 8 commits ago."
2. (10-30s) I paste the failing test into Bob in `sleuth-debugger` mode. Subagents fan out: one reproduces the failure 3 times, one starts bisecting history.
3. (30-55s) "Culprit found: commit `afcc8ee`, 'refactor: simplify discount tier lookup'. It flipped `>=` to `>` on the 10-unit boundary, so an order of exactly 10 units lost its 10% discount." Patch proposal and rationale on screen.
4. (55-75s) I approve. Patch applies. Full suite: 10 passed, 0 failed.
5. (75-90s) "From detection to culprit: under 2 seconds. Every step logged, no patch without a human yes." End card: repo link.

---

## 11. Risks

- **Reproduce flakes live.** The demo is deterministic and I have a golden-run recording as backup.
- **Bobcoins run out.** Budget above keeps a ~25% buffer, plus the coin-efficient prompt rules.
- **IDE or account trouble at the start.** Phase 1 begins with install and sign-in verification before any build session.
- **Bisect slow on big histories.** The demo is 8 commits on purpose. Scaling path goes in the long description.
- **"It's just a script."** The differentiator is Bob depth: custom mode, skill, MCP, subagents, all visible in the repo and the screenshots.
- **Deadline hour unknown for Sept 27.** Internal deadline: Sept 27, 12:00 PM EDT. Submit early.

---

## 12. Runbook for Sept 25, 11:00 AM EDT

1. Upgrade/install Bob IDE to latest v2.0.x (1.0.3 and 2.0.0 stop working Sept 30).
2. Check email for the IBM Bob team invite. Create an IBMid for the registration email if needed.
3. Bob IDE: log in, finish IBMid auth in the browser.
4. Settings, General: switch to `ibm-coding-challenge-uat`, region us-east. Confirm 40 Bobcoins.
5. Clone `stack-sleuth`, open the folder. Confirm `sleuth-mcp` in MCP servers and `sleuth-debugger` in the mode picker.
6. Task 1 prompt: reproduce flow. Screenshot to `bob_sessions/`.
7. Tasks 2-6 per the evidence plan. Follow the coin rules.
8. Ping the assistant as screenshots land; video, slides, and submission text get assembled in parallel.

---

*Plan written 2026-09-24. Phase 0 verified working before the hackathon starts. Every number in here was measured, not made up.*
