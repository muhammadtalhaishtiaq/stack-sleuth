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


def test_format_money():
    from pricing import format_money

    assert format_money(90) == "$90.00"
