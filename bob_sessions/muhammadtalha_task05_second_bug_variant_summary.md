# Task 5 — Second Bug Variant
**Date:** 2026-09-26 18:44 UTC
**Status:** COMPLETE

## Bug Introduced
- File: `demo/pricing.py` line 35
- Change: `"SAVE10": 0.10` → `"SAVE10": 0.05`
- Commit: `1dad4cf` ("feat: adjust SAVE10 coupon rate")
- Effect: SAVE10 coupon gives 5% off instead of 10%

## Full Loop
1. **run_tests:** 2 failed (`test_coupon`, `test_total_with_coupon`), 8 passed
2. **reproduce (3x):** FAILED 3/3, deterministic YES
3. **bisect:** Culprit `1dad4cf` (1 step, only new commit)
4. **inspect:** Confirmed the 0.10→0.05 change
5. **propose:** `proposal-002-save10-coupon-rate` saved (NOT applied)
6. **approve:** Talha (delegated), applied
7. **verify:** 10 passed, 0 failed ✅

## Conclusion
The StackSleuth loop generalizes to a different bug type (coupon rate vs. discount tier).
