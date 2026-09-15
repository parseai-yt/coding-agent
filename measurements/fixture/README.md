# cartcalc

Prices a shopping cart in integer cents.

Pricing rules:

- Adding a SKU that is already in the cart increases its quantity.
- A coupon takes a whole-number percentage off the subtotal.
- A cart with 10 or more items gets an extra 5% bulk discount.
- Tax is 8% of the subtotal after discounts.
- Every amount is rounded to the nearest cent.

Run the tests with `python3 -m pytest -q`.
