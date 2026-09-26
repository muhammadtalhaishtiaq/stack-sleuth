# Task 1 — Reproduce the Failure
**Date:** 2026-09-26 18:44 UTC
**Status:** COMPLETE

## Test Run
- Command: `pytest demo/tests/ -q`
- Result: 1 failed, 9 passed
- Failing test: `demo/tests/test_pricing.py::test_bulk_discount_tier`
- Assertion: `assert 100.0 == 90.0` (expected 90.0 for 10 units at $10 with 10% discount)

## Reproduction (3x isolation)
- Run 1: FAILED (returncode 1)
- Run 2: FAILED (returncode 1)
- Run 3: FAILED (returncode 1)
- Deterministic: YES (3/3)

## Conclusion
The bulk discount tier boundary is broken. Exactly 10 units does not earn the 10% discount.
