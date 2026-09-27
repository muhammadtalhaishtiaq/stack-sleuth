# Task 6: Hardening - Bob API Response

**Date:** 2026-09-26
**Method:** Bob API inference
**Model:** premium

**Prompt:** What edge cases should be hardened for bulk_discount_rate?

**Bob's response:**
1. **Negative quantities**: The function should reject or handle negative quantities, as they don't represent valid purchase amounts and could incorrectly trigger discount tiers.

2. **Non-numeric input**: String, None, or other non-numeric types should be validated to prevent TypeErrors or unexpected behavior when performing comparisons.

3. **Floating-point quantities**: Decimal values like 99.5 should be handled consistently—either round, truncate, or reject them based on whether partial units make sense in your business context.

4. **Extremely large numbers**: Very large quantities (e.g., `qty > 10^15`) could cause performance issues or overflow in price calculations downstream, so consider setting reasonable upper bounds.
