"""Tiny pricing library (demo target for StackSleuth)."""

__version__ = "0.2.0"


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


def format_money(amount):
    """Format an amount as USD."""
    return "$%.2f" % amount
