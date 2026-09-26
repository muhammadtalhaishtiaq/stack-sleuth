# Task 2 — Bisect to the Culprit
**Date:** 2026-09-26 18:44 UTC
**Status:** COMPLETE

## Bisect
- Good ref: 0d4013d (root commit)
- Bad ref: 86bc3cd (HEAD)
- Probe: `sleuth/bisect_probe.py` (exit 0=good, 1=bad, 125=skip)

## Result
- **Culprit:** `afcc8ee74e40d3b6fc89f46ef227e0c7e2e0c7e7`
- **Message:** "refactor: simplify discount tier lookup"
- **Steps:** 2 (tested afcc8ee=bad, b58d9fb=good)

## Conclusion
The refactor commit introduced the regression.
