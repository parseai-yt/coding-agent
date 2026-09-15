import pytest

from cartcalc import Cart


def test_single_line_total():
    cart = Cart()
    cart.add("mug", 1000, 2)
    assert cart.subtotal_cents() == 2000
    assert cart.tax_cents() == 160
    assert cart.total_cents() == 2160


def test_adding_same_sku_twice_adds_quantity():
    cart = Cart()
    cart.add("pen", 150, 3)
    cart.add("pen", 150, 2)
    assert cart.item_count() == 5
    assert cart.subtotal_cents() == 750


def test_coupon_percent():
    cart = Cart(coupon_percent=10)
    cart.add("book", 2500, 1)
    assert cart.discount_cents() == 250


def test_bulk_discount_starts_at_ten_items():
    cart = Cart()
    cart.add("sticker", 100, 10)
    assert cart.discount_cents() == 50


def test_tax_is_charged_after_discount():
    cart = Cart(coupon_percent=20)
    cart.add("lamp", 5000, 1)
    assert cart.discount_cents() == 1000
    assert cart.tax_cents() == 320
    assert cart.total_cents() == 4320


def test_rejects_zero_quantity():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add("mug", 1000, 0)
