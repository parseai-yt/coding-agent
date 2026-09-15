# Review of `invoices/` against README rules

Findings are ordered most serious first.

## 1. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

- **File:** `invoices/invoice.py`
- **Line:** 31 (`return percent_of(self.subtotal(), self.tax_rate)`)
- **Why it is wrong:** Rules 2 and 3 say the discount applies to the subtotal *before* tax, and tax is computed on the *discounted* subtotal. `tax()` passes the raw subtotal to `percent_of`, so whenever `discount_rate > 0` the customer is taxed on money they never pay. Example: subtotal $100.00, 10% discount, 8% tax — the code charges 800 cents of tax instead of the correct 720, overstating the total by 80 cents.
- **Fix:** Compute tax on the discounted subtotal:

  ```python
  def tax(self) -> int:
      return percent_of(self.subtotal() - self.discount(), self.tax_rate)
  ```

  `total()` on line 37 then remains arithmetically consistent (`subtotal - discount + tax`).

## 2. `to_cents` truncates instead of rounding half up (violates rule 1)

- **File:** `invoices/money.py`
- **Line:** 6 (`return int(amount * 100)`)
- **Why it is wrong:** Rule 1 requires every amount to be converted to cents by rounding half up, never by truncating. `int()` truncates toward zero, and binary floating point makes this bite on ordinary prices: `19.99 * 100` is `1998.9999999999998`, so `to_cents(19.99)` returns **1998** instead of 1999. Every line item, and the per-line prices printed by `render()` (line 40 of `invoice.py`), can be a cent short.
- **Fix:** Round half up instead of truncating, e.g.:

  ```python
  from decimal import Decimal, ROUND_HALF_UP

  def to_cents(amount: float) -> int:
      return int(Decimal(str(amount)).scaleb(2).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
  ```

  (A minimal fix of `int(amount * 100 + 0.5)` also repairs the common cases, but `Decimal` avoids the residual float-representation errors and handles negatives correctly.)

## 3. `percent_of` does not round half up for negative amounts and is exposed to float error (violates rules 1 and 3 in edge cases)

- **File:** `invoices/money.py`
- **Line:** 11 (`return int(cents * rate / 100 + 0.5)`)
- **Why it is wrong:** The `+ 0.5` then `int()` idiom only implements round-half-up for non-negative values; for a negative amount (e.g. a credit line of -1250 cents at 10%: `-125 + 0.5 = -124.5` → `int` truncates to **-124**, not -125's half-up counterpart) the result is off by one cent. Additionally, `cents * rate / 100` is computed in binary floating point, so a value that is mathematically exactly `.5` can arrive as `.49999…` and round the wrong way.
- **Fix:** Do the arithmetic in `Decimal` with explicit half-up rounding:

  ```python
  from decimal import Decimal, ROUND_HALF_UP

  def percent_of(cents: int, rate: float) -> int:
      return int((Decimal(cents) * Decimal(str(rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
  ```

## 4. `fmt` renders negative amounts incorrectly (secondary bug, not a numbered rule)

- **File:** `invoices/money.py`
- **Line:** 15 (`return f"${cents // 100}.{cents % 100:02d}"`)
- **Why it is wrong:** Python's floor division and modulo make `fmt(-50)` produce `"$-1.50"` instead of `"$-0.50"`, and `fmt(-150)` produce `"$-2.50"` instead of `"$-1.50"`. Any invoice whose total goes negative (large discount, credit lines) renders a wrong amount.
- **Fix:** Format from the absolute value and re-apply the sign:

  ```python
  def fmt(cents: int) -> str:
      sign = "-" if cents < 0 else ""
      return f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"
  ```
