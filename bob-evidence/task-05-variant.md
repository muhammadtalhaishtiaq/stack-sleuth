# Task 5: Second Bug Variant (SAVE10) - Bob API Response

**Date:** 2026-09-26
**Method:** Bob API inference
**Model:** premium

**Prompt:** SAVE10 coupon should give 10% off but only gives 5%. Code shows `{"SAVE5": 0.05, "SAVE10": 0.05}`.

**Bob's response:**
The bug is that the "SAVE10" coupon is mapped to a 0.05 (5%) discount instead of 0.10 (10%) in the dictionary.

**Fix:**
```python
def coupon_discount(code):
    return {"SAVE5": 0.05, "SAVE10": 0.10}.get(code, 0.0)
```
