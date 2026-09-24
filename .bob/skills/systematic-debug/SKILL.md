---
name: systematic-debug
description: Bisect-driven debugging workflow for StackSleuth. Use when a test fails and you need to find the guilty commit: reproduce deterministically, git bisect to the culprit, draft a patch proposal, and hold at a human approve gate before applying anything.
---

# Systematic Debug

A failing test is a question with a concrete answer: which commit broke it.
Don't guess. Bisect.

## The loop

1. **Detect.** Run the full suite (`run_tests`). Get the failing test id and the exact assertion message. That's your ground truth for the whole session.

2. **Reproduce.** Run the single failing test 3 times in isolation (`reproduce`). If it doesn't fail every time, it's flaky, not a regression. Stop and say so. A flaky test needs quarantine, not a bisect.

3. **Bisect.** Automate `git bisect` (`bisect`) with a probe command that exits 0 for good, 1 for bad, 125 for skip. The working tree must be clean first. The output is a commit hash. That's the culprit, not a suspect.

4. **Inspect.** Read the culprit's diff (`inspect_commit`). Understand what changed and why it broke the test before touching anything. Most bad patches come from skipping this step.

5. **Propose.** Draft the smallest diff that fixes the test (`propose_patch`). Write down why the old code was wrong and why the new code is right. The proposal goes to `evidence/proposals/`. It is not applied. Ever, by you.

6. **Gate.** A human reviews the proposal. Only when they approve does `apply_patch` run with `approved=true`, and the full suite re-runs to confirm green.

7. **Log everything.** Each stage appends to `evidence/sleuth_log.json` (`log_evidence`). If it isn't in the log, it didn't happen.

## Rules of thumb

- One failing test, one bisect. Don't batch multiple failures into one run.
- The probe command must be fast and hermetic. Slow probes make bisect painful.
- Prefer the smallest fix that makes the test pass without breaking others. If the fix needs more than a few lines, say so and propose it in pieces.
- Never apply without explicit approval. No exceptions, no "it was obvious".
