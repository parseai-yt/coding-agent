# Code review: invoices/ vs README.md rules

Findings, most serious first.

## 1. `to_cents` truncates instead of rounding half up (violates rule 1)

- **File/line:** `invoices/money.py:6`
- **Why it is wrong:** `int(amount * 100)` truncates toward zero. Rule 1 says every
  amount must be converted to integer cents by rounding half up, never by truncating.
  Because most decimal prices are not exactly representable in binary floating point,
  this corrupts ordinary amounts: `19.99 * 100 == 1998.9999999999998`, so
  `to_cents(19.99)` returns `1998` ($19.98) instead of `1999`. Every line item,
  subtotal, discount, tax, and rendered price built on this helper can be off by a
  cent per amount, and the error is multiplied by `quantity` in `Line.cents()`.
- **Fix:** Round half up instead of truncating, e.g.
  `return int(amount * 100 + 0.5)`, or more robustly
  `int(Decimal(str(amount)).scaleb(2).quantize(Decimal("1"), rounding=ROUND_HALF_UP))`.

## 2. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

- **File/line:** `invoices/invoice.py:31` (and the assembly in `total()` at
  `invoices/invoice.py:37`)
- **Why it is wrong:** Rule 2 says the discount applies to the subtotal before tax,
  and rule 3 says tax is computed on the *discounted* subtotal. But
  `tax()` calls `percent_of(self.subtotal(), self.tax_rate)`, taxing the full,
  pre-discount subtotal. Any invoice with a nonzero `discount_rate` overcharges
  tax. Example: subtotal 10000¢, 10% discount, 10% tax → code charges
  10000 + 1000 − 1000 = 10000¢; the rules require tax on 9000¢, giving
  9000 + 900 = 9900¢.
- **Fix:** Base tax on the discounted subtotal:
  `return percent_of(self.subtotal() - self.discount(), self.tax_rate)`.
  (`total()` then remains `subtotal() − discount() + tax()`.)

## 3. `percent_of` rounds in floating point, so exact half-cents can round down (weakens rules 1 and 3)

- **File/line:** `invoices/money.py:11`
- **Why it is wrong:** `cents * rate / 100 + 0.5` does the half-up trick in binary
  floating point. Many tax rates (8.7, 6.35, …) are not exactly representable as
  doubles, so when the exact result lands on a half cent the intermediate float
  can sit just below the `.5` threshold and `int()` rounds the half *down*.
  Example: `float(8.7)` is slightly less than 8.7, so `percent_of(1500, 8.7)`
  — exactly 130.5¢, which rule 3 says must round up to 131 — computes
  `1500 * 8.7 / 100` as ≈130.49999999999998 and returns 130. Whether a given
  half cent rounds up or down depends on representation error, not the rule.
- **Fix:** Do the arithmetic exactly before rounding, e.g.
  `return (cents * int(rate * 10) * 10 + 5000) // 10000` for one-decimal rates,
  or use `Decimal(cents) * Decimal(str(rate)) / 100` quantized with
  `ROUND_HALF_UP`.

## 4. `fmt` renders negative amounts incorrectly (latent formatting bug)

- **File/line:** `invoices/money.py:15`
- **Why it is wrong:** Python's floor division and modulo make
  `fmt(-1999)` produce `$-20.01` (`-1999 // 100 == -20`, `-1999 % 100 == 1`)
  instead of `-$19.99`. Not a README rule per se, but a credit line, refund, or a
  discount larger than the subtotal would render a wrong amount.
- **Fix:** Handle the sign explicitly, e.g.
  `sign = "-" if cents < 0 else ""` then format `abs(cents)`:
  `f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"`.
