#!/usr/bin/env bash
#
# Regenerates the deterministic demo repo used by StackSleuth.
#
#   ./make_demo.sh [target_dir]   (default: ./demo next to this script)
#
# The result is a git repo with 8 commits. Commit 4 ("refactor: simplify
# discount tier lookup") introduces a realistic off-by-one regression in the
# bulk-discount tier boundary. tests/test_pricing.py::test_bulk_discount_tier
# passes on commits 1-3 and fails from commit 4 to HEAD, so `git bisect`
# can find the culprit.
#
# All commits use fixed author/committer dates, so the history (and every
# commit hash) is identical on every machine.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$SCRIPT_DIR}"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Clear the target, but never delete this generator script itself, even when
# the target IS the script's own directory (the default).
if [ -e "$TARGET" ]; then
  find "$TARGET" -mindepth 1 -maxdepth 1 ! -name "$SCRIPT_NAME" -exec rm -rf {} +
else
  mkdir -p "$TARGET"
fi
mkdir -p "$TARGET/tests"
cd "$TARGET"

git init -q -b main
git config user.name "Demo Dev"
git config user.email "demo@example.com"
git config commit.gpgsign false

# the generator script itself stays out of the demo repo's history
printf 'make_demo.sh\n.pytest_cache/\n__pycache__/\n' > .gitignore

# lets the tests import pricing no matter where pytest is launched from
cat > conftest.py <<'EOF'
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
EOF

commit() { # $1 = message, $2 = ISO date
  GIT_AUTHOR_DATE="$2" GIT_COMMITTER_DATE="$2" git add -A
  GIT_AUTHOR_DATE="$2" GIT_COMMITTER_DATE="$2" git commit -q -m "$1"
  echo "  committed: $1 ($(git rev-parse --short HEAD))"
}

echo "building demo repo in $TARGET"

# ---------------------------------------------------------------- commit 1
cat > pricing.py <<'EOF'
"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.1.0"


def subtotal(items):
    """Sum of price*qty over (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def total(items, tax_rate=0.0):
    """Grand total with tax."""
    base = subtotal(items)
    return base * (1 + tax_rate)
EOF

cat > tests/test_pricing.py <<'EOF'
from pricing import subtotal, total


def test_subtotal():
    assert subtotal([(10.0, 2), (5.0, 4)]) == 40.0


def test_total_no_tax():
    assert total([(10.0, 2)]) == 20.0
EOF

cat > README.md <<'EOF'
# demo-shop

Tiny pricing library. Used as the deterministic debugging target for StackSleuth.
EOF
commit "feat: add subtotal and total helpers" "2026-01-05T09:00:00+00:00"

# ---------------------------------------------------------------- commit 2
cat > pricing.py <<'EOF'
"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.1.0"


def subtotal(items):
    """Sum of price*qty over (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def tax(amount, rate):
    """Tax amount for a given rate."""
    return amount * rate


def total(items, tax_rate=0.0):
    """Grand total with tax."""
    base = subtotal(items)
    return base + tax(base, tax_rate)
EOF

cat > tests/test_pricing.py <<'EOF'
from pricing import subtotal, tax, total


def test_subtotal():
    assert subtotal([(10.0, 2), (5.0, 4)]) == 40.0


def test_total_no_tax():
    assert total([(10.0, 2)]) == 20.0


def test_tax():
    assert tax(100.0, 0.13) == 13.0


def test_total_with_tax():
    assert total([(10.0, 2)], tax_rate=0.1) == 22.0
EOF
commit "feat: add tax calculation" "2026-01-06T09:00:00+00:00"

# ---------------------------------------------------------------- commit 3
cat > pricing.py <<'EOF'
"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.1.0"


def subtotal(items):
    """Sum of price*qty over (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def bulk_discount_rate(qty):
    """Discount rate for a line quantity: 15% at 100+, 10% at 10+, else 0."""
    if qty >= 100:
        return 0.15
    if qty >= 10:
        return 0.10
    return 0.0


def discounted_subtotal(items):
    """Subtotal with per-line bulk discounts applied."""
    result = 0.0
    for price, qty in items:
        result += price * qty * (1 - bulk_discount_rate(qty))
    return result


def tax(amount, rate):
    """Tax amount for a given rate."""
    return amount * rate


def total(items, tax_rate=0.0):
    """Grand total with bulk discounts and tax."""
    base = discounted_subtotal(items)
    return base + tax(base, tax_rate)
EOF

cat > tests/test_pricing.py <<'EOF'
import pytest

from pricing import bulk_discount_rate, subtotal, tax, total


def test_subtotal():
    assert subtotal([(10.0, 2), (5.0, 4)]) == 40.0


def test_total_no_tax():
    assert total([(10.0, 2)]) == 20.0


def test_tax():
    assert tax(100.0, 0.13) == 13.0


def test_total_with_tax():
    assert total([(10.0, 2)], tax_rate=0.1) == 22.0


def test_bulk_discount_tier():
    # exactly 10 units must earn the 10% tier: 10 x $10 -> $90
    assert total([(10.0, 10)]) == pytest.approx(90.0)


def test_bulk_discount_higher_tier():
    assert total([(10.0, 100)]) == pytest.approx(850.0)


def test_no_discount_small_qty():
    assert total([(10.0, 9)]) == pytest.approx(90.0)
EOF
commit "feat: add bulk discount tiers" "2026-01-07T09:00:00+00:00"

# ---------------------------------------------------------------- commit 4
# THE BUG: refactor flips >= to > on the 10-unit tier boundary.
cat > pricing.py <<'EOF'
"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.1.0"


def subtotal(items):
    """Sum of price*qty over (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def bulk_discount_rate(qty):
    """Discount rate for a line quantity: 15% at 100+, 10% at 10+, else 0."""
    if qty >= 100:
        return 0.15
    if qty > 10:  # BUG: off-by-one, should be >= 10
        return 0.10
    return 0.0


def discounted_subtotal(items):
    """Subtotal with per-line bulk discounts applied."""
    result = 0.0
    for price, qty in items:
        result += price * qty * (1 - bulk_discount_rate(qty))
    return result


def tax(amount, rate):
    """Tax amount for a given rate."""
    return amount * rate


def total(items, tax_rate=0.0):
    """Grand total with bulk discounts and tax."""
    base = discounted_subtotal(items)
    return base + tax(base, tax_rate)
EOF
# tests unchanged: test_bulk_discount_tier starts failing here
commit "refactor: simplify discount tier lookup" "2026-01-08T09:00:00+00:00"

# ---------------------------------------------------------------- commit 5
cat > pricing.py <<'EOF'
"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.1.0"


def subtotal(items):
    """Sum of price*qty over (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def bulk_discount_rate(qty):
    """Discount rate for a line quantity: 15% at 100+, 10% at 10+, else 0."""
    if qty >= 100:
        return 0.15
    if qty > 10:  # BUG: off-by-one, should be >= 10
        return 0.10
    return 0.0


def discounted_subtotal(items):
    """Subtotal with per-line bulk discounts applied."""
    result = 0.0
    for price, qty in items:
        result += price * qty * (1 - bulk_discount_rate(qty))
    return result


def tax(amount, rate):
    """Tax amount for a given rate."""
    return amount * rate


def coupon_discount(code):
    """Extra discount rate for a coupon code."""
    return {"SAVE5": 0.05, "SAVE10": 0.10}.get(code, 0.0)


def total(items, tax_rate=0.0, coupon=None):
    """Grand total with bulk discounts, coupon, and tax."""
    base = discounted_subtotal(items)
    base *= 1 - coupon_discount(coupon)
    return base + tax(base, tax_rate)
EOF

cat > tests/test_pricing.py <<'EOF'
import pytest

from pricing import bulk_discount_rate, coupon_discount, subtotal, tax, total


def test_subtotal():
    assert subtotal([(10.0, 2), (5.0, 4)]) == 40.0


def test_total_no_tax():
    assert total([(10.0, 2)]) == 20.0


def test_tax():
    assert tax(100.0, 0.13) == 13.0


def test_total_with_tax():
    assert total([(10.0, 2)], tax_rate=0.1) == 22.0


def test_bulk_discount_tier():
    # exactly 10 units must earn the 10% tier: 10 x $10 -> $90
    assert total([(10.0, 10)]) == pytest.approx(90.0)


def test_bulk_discount_higher_tier():
    assert total([(10.0, 100)]) == pytest.approx(850.0)


def test_no_discount_small_qty():
    assert total([(10.0, 9)]) == pytest.approx(90.0)


def test_coupon():
    assert coupon_discount("SAVE10") == 0.10
    assert coupon_discount("NOPE") == 0.0


def test_total_with_coupon():
    assert total([(10.0, 2)], coupon="SAVE10") == pytest.approx(18.0)
EOF
commit "feat: add coupon codes" "2026-01-09T09:00:00+00:00"

# ---------------------------------------------------------------- commit 6
cat > README.md <<'EOF'
# demo-shop

Tiny pricing library. Used as the deterministic debugging target for StackSleuth.

## Usage

```python
from pricing import total

total([(10.0, 10)])            # 90.0 with the 10% bulk tier
total([(10.0, 2)], coupon="SAVE10", tax_rate=0.1)
```
EOF
commit "docs: add usage examples to README" "2026-01-10T09:00:00+00:00"

# ---------------------------------------------------------------- commit 7
cat >> pricing.py <<'EOF'


def format_money(amount):
    """Format an amount as USD."""
    return "$%.2f" % amount
EOF

cat >> tests/test_pricing.py <<'EOF'


def test_format_money():
    from pricing import format_money

    assert format_money(90) == "$90.00"
EOF
commit "feat: currency formatting" "2026-01-11T09:00:00+00:00"

# ---------------------------------------------------------------- commit 8
sed -i 's/__version__ = "0.1.0"/__version__ = "0.2.0"/' pricing.py
commit "chore: bump version to 0.2.0" "2026-01-12T09:00:00+00:00"

echo "done: $(git rev-list --count HEAD) commits, HEAD=$(git rev-parse --short HEAD)"
