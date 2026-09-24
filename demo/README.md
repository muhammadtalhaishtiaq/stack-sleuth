# demo-shop

Tiny pricing library. Used as the deterministic debugging target for StackSleuth.

## Usage

```python
from pricing import total

total([(10.0, 10)])            # 90.0 with the 10% bulk tier
total([(10.0, 2)], coupon="SAVE10", tax_rate=0.1)
```
