# Task 3 — Draft the Patch
**Date:** 2026-09-26 18:44 UTC
**Status:** COMPLETE (proposal saved, NOT applied)

## Inspection
Commit afcc8ee changed `demo/pricing.py` line 15:
- Before: `if qty >= 10:`
- After: `if qty > 10:  # BUG: off-by-one, should be >= 10`

## Root Cause
Off-by-one error. The 10% discount tier requires `qty >= 10` (inclusive), but the refactor made it `qty > 10` (exclusive). Exactly 10 units falls through to 0% discount.

## Proposal
- ID: `proposal-001-bulk-discount-boundary`
- File: `evidence/proposals/proposal-001-bulk-discount-boundary.json`
- Fix: Change `if qty > 10:` back to `if qty >= 10:`
- Status: Proposed (NOT applied) — awaiting human approval gate
