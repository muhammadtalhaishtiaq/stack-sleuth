# Hackathon Log

Running notes from the IBM Bob 2.0 Hackathon build. Newest entries first.

## 2026-09-24 (evening, day before kickoff)

- Verified the IBMid for the hackathon email address works. IBM recognized the address and the sign-in test passed, so no new account needed tonight.
- Installed Bob IDE 2.2.0 (latest, above the v2.0.2 minimum) on the build machine and confirmed it launches. Not signed in yet.
- Still waiting on the hackathon-provisioned Bob account invite email, which the organizers send at kickoff. An automated watch checks the inbox every 30 minutes for it.
- Kickoff plan: tomorrow 11:00 AM EDT. Catch the invite, sign into Bob IDE, switch to the hackathon instance, and run the six live tasks from docs/BOB_RUNBOOK.md with a screenshot for each.

## 2026-09-24 (afternoon)

- Full StackSleuth build pushed: deterministic 8-commit demo repo with a known off-by-one bug, FastMCP server with 7 tools (run_tests, reproduce, bisect, inspect_commit, propose_patch, apply_patch, log_evidence), Bob IDE custom mode and skill, evidence rules with a human approval gate.
- Independently verified from a fresh public clone: 7/7 tool tests pass, bisect finds the culprit commit, the approval gate refuses unapproved patches, and the approved patch turns the suite green (10 passed).
