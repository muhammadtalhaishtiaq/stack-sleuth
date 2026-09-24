# Bob IDE Runbook — StackSleuth

Everything Talha needs for the live Bob IDE session at the IBM Bob 2.0 Hackathon. The build, tests, and configs are already done and verified. What happens here spends Bobcoins, so it happens on the MacBook with the hackathon-provisioned account.

## 0. One-time setup (do this first, ~10 min)

1. Install or upgrade Bob IDE to the latest v2.0.x (anything below v2.0.2 stops working Sept 30).
2. Sign in with the **hackathon-provisioned Bob account**, not a personal one.
3. Settings → General → switch to instance **ibm-coding-challenge-uat**, region **us-east**.
4. Confirm the Bobcoin balance shows **40**. There are no top-ups, so the budget below is the whole game.
5. Clone the repo and open the folder in Bob IDE:
   ```
   git clone https://github.com/muhammadtalhaishtiaq/stack-sleuth.git
   cd stack-sleuth
   ```
6. Confirm `sleuth-mcp` shows up under MCP servers and `sleuth-debugger` appears in the mode picker. If the MCP server fails to start, open `.bob/mcp.json` — it uses `${workspaceFolder}` and some setups don't expand it. Replace with the absolute path to the repo folder as a fallback.
7. Build the demo repo and install the server deps (the demo's `.git` can't be pushed to GitHub, so it has to be generated locally — this is deterministic, same commits every time):
   ```
   ./demo/make_demo.sh
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

## The six tasks

Run them in order, in `sleuth-debugger` mode. After each task's summary appears, screenshot it before doing anything else (see "Screenshots" below). Copy each prompt verbatim.

### Task 1 — Reproduce the failure (~3-4 coins)

> Use the sleuth-mcp tools. Run run_tests on demo/ and tell me which test fails and the exact assertion. Then run reproduce on that failing test id, 3 times in isolation, and report whether it fails deterministically. Log both stages with log_evidence. Stop after reporting. Do not bisect yet.

Expected: `tests/test_pricing.py::test_bulk_discount_tier` fails, deterministic, returncodes [1, 1, 1].
Screenshot → `bob_sessions/muhammadtalha_task01_reproduce_failure_summary.png`

### Task 2 — Bisect to the culprit (~4-5 coins)

> Take the failing test tests/test_pricing.py::test_bulk_discount_tier and run bisect on demo/ with a probe command that exits 0 when the commit is good and 1 when it's bad, using the root commit as good_ref. Report the culprit commit hash and its message. Log it with log_evidence. Do not inspect or patch yet.

Expected: culprit `afcc8ee`, "refactor: simplify discount tier lookup", 2 bisect steps.
Screenshot → `bob_sessions/muhammadtalha_task02_bisect_culprit_commit_summary.png`

### Task 3 — Draft the patch (~4-5 coins)

> Run inspect_commit on the culprit commit from Task 2. Read the diff and explain in plain words what the commit broke. Then draft the smallest fix that makes the failing test pass and persist it with propose_patch, including a written rationale. Do NOT apply it. Show me the proposal id and the rationale for my review.

Expected: proposal saved under `evidence/proposals/`, status "proposed (NOT applied)". The fix is a one-character class change: `qty > 10` → `qty >= 10`.
Screenshot → `bob_sessions/muhammadtalha_task03_patch_proposal_summary.png`

### Task 4 — Approve and verify green (~2-3 coins)

Read the proposal from Task 3 first. Only when it looks right, paste:

> I have reviewed the proposal and I approve it. Call apply_patch with approved=true for that proposal id, then report the full suite result. If anything is still red, say so plainly and stop.

Expected: applied, suite 10 passed, 0 failed.
Screenshot → `bob_sessions/muhammadtalha_task04_approve_gate_verify_green_summary.png`

### Task 5 — Second bug variant (~5-6 coins)

This is the generalization proof. It shows the loop isn't a one-trick demo.

> Introduce a second, different bug in demo/pricing.py: make the SAVE10 coupon give 5% off instead of 10%. Commit it on top of the current history. Then run the full StackSleuth loop on it end to end: run_tests, reproduce 3x, bisect to the new culprit, inspect, propose_patch. Stop at the gate and show me the proposal for approval. Log every stage.

Expected: new culprit commit found, proposal held for approval. Approve it the same way as Task 4 and confirm green.
Screenshot → `bob_sessions/muhammadtalha_task05_second_bug_variant_summary.png`

### Task 6 — Hardening (~4-5 coins)

> Harden the loop against two real failure modes: (1) make run_tests report cleanly when pytest itself crashes with a collection error instead of test failures, and (2) confirm bisect refuses on a dirty working tree with a message that tells the human exactly what to do. Add a test for each in sleuth/tests/. Report what you changed and the test results.

Expected: new tests pass, no behavior change on the happy path.
Screenshot → `bob_sessions/muhammadtalha_task06_hardening_summary.png`

## Screenshots

Open the Bob IDE **Tasks** view, select **"All"** if tasks span workspaces, and screenshot right after each task's summary appears. Save as PNG in `bob_sessions/` with exactly these names:

- `muhammadtalha_task01_reproduce_failure_summary.png`
- `muhammadtalha_task02_bisect_culprit_commit_summary.png`
- `muhammadtalha_task03_patch_proposal_summary.png`
- `muhammadtalha_task04_approve_gate_verify_green_summary.png`
- `muhammadtalha_task05_second_bug_variant_summary.png`
- `muhammadtalha_task06_hardening_summary.png`

These are required evidence for judging eligibility. Missing screenshots are an eligibility risk, so don't skip any.

## Coin budget (40 total, no refills)

| Task | Est. coins |
|---|---|
| 1: reproduce | 3-4 |
| 2: bisect | 4-5 |
| 3: patch proposal | 4-5 |
| 4: approve + verify | 2-3 |
| 5: second bug variant | 5-6 |
| 6: hardening | 4-5 |
| Buffer (surprises, re-runs) | 8-10 |
| **Total** | **~30-38** |

Rules that keep the budget intact: batch independent reads into one prompt, never re-run a green suite just to check, keep prompts specific (file paths, test ids). If the balance ever hits zero, stop spending and continue with local tooling only.

## If something goes wrong

- **MCP server won't start:** `${workspaceFolder}` fallback (see step 6 above), or run `.venv/bin/python sleuth/server.py` by hand to see the real error.
- **Bisect refuses:** the working tree has uncommitted changes. Commit or stash scratch files first. Untracked files like `.pytest_cache` are fine.
- **A task summary looks wrong:** don't re-run it on coins. The loop was verified end to end before the hackathon; check the evidence log at `evidence/sleuth_log.json` to see exactly which stage misbehaved, then fix it locally.
- **Bob tries to apply a patch on its own:** that's the one thing it must never do. The rule file `never-apply-without-approval.md` covers it, and the tool itself refuses without `approved=true`. If it happens anyway, stop the task and say so in the submission write-up as a found-and-fixed issue.
