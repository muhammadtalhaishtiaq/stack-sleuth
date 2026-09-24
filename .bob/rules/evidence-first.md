# Log every stage to the evidence log

If it isn't in `evidence/sleuth_log.json`, it didn't happen.

Use `log_evidence` at each stage of the loop:

- `detected`: the failing test id and assertion, from `run_tests`
- `reproduced`: the 3x isolation result, from `reproduce`
- `bisected`: the culprit commit hash and message, from `bisect`
- `proposed`: the proposal id and rationale, from `propose_patch`
- `approved`: who approved and when, before `apply_patch`
- `verified`: the green suite result after the apply

The log is append-only. Never rewrite history in it, even if a stage went
wrong. A failed bisect attempt is still evidence. Judges read this file to
see the process, not just the outcome.
