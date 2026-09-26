# Task 6 — Hardening
**Date:** 2026-09-26 18:44 UTC
**Status:** COMPLETE

## Change 1: run_tests collection error handling
- **Problem:** If pytest crashes during collection (e.g., syntax error in conftest.py), the old code would report `failed: 0` which looks like a green suite.
- **Fix:** `sleuth/server.py` `run_tests()` now detects collection crashes (exit code not in 0/1/5, or ImportError/ERROR markers) and sets `collection_error: True` with an `error_detail` excerpt.
- **Test:** `test_run_tests_reports_collection_error_cleanly` — breaks conftest with syntax error, asserts `collection_error is True` and `failed == 0`.

## Change 2: bisect dirty tree message
- **Problem:** The dirty-tree error message was terse.
- **Fix:** `sleuth/server.py` `bisect()` now returns: "working tree has uncommitted changes; git bisect needs a clean tree. Run 'git stash' to shelve your changes (restore with 'git stash pop'), or 'git commit' them first, then retry bisect."
- **Test:** `test_bisect_refuses_dirty_working_tree` — dirties pricing.py, asserts `ok is False` and message contains "git stash".

## Test Results
- Command: `pytest sleuth/tests/test_tools.py -q`
- Result: **9 passed** (7 existing + 2 new) ✅
- No behavior change on happy path.
