# Task 3: Propose Patch - Bob API Response

**Date:** 2026-09-26
**Method:** Bob API inference
**Model:** premium

**Prompt:** Given buggy code `if qty > 10: return 0.10`, write the corrected line.

**Bob's response:**
```python
if qty >= 10:
    return 0.10
```

The fix changes `>` to `>=` to include the boundary case where qty equals 10. The original code would exclude exactly 10 items from receiving the discount, which is typically not the intended behavior when offering a "10 or more" discount threshold.
