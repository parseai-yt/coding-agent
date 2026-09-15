# Code review: invoices/ vs README.md rules

Findings are ordered most serious first.

## 1. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

- **File/line:** `invoices/invoice.py:31`
- **Why it is wrong:** Rule 2 says the discount applies to the subtotal *before* tax, and rule 3 says tax is computed on the *discounted* subtotal. `tax()` calls `percent_of(self.subtotal(), self.tax_rate)`, ignoring the discount entirely. Every discounted invoice is overtaxed. Example: subtotal 10000¢, 10% discount, 10% tax — the code charges 1000¢ tax on 10000¢, but the rules require 900¢ tax on the discounted base of 9000¢, so `total()` is 10¢ too high.
- **Fix:** Compute tax on the discounted base:

  ```python
  def tax(self) -> int:
      return percent_of(self.subtotal() - self.discount(), self.tax_rate)
  ```

## 2. `to_cents` truncates instead of rounding half up (violates rule 1)

- **File/line:** `invoices/money.py:6`
- **Why it is wrong:** Rule 1 requires converting to cents by rounding half up, never truncating. `int(amount * 100)` truncates toward zero, and because binary floats cannot represent most decimal prices exactly, this loses a cent on very common inputs: `19.99 * 100 == 1998.9999999999998`, so `to_cents(19.99)` returns **1998**, not 1999. The error is then multiplied by the quantity in `Line.cents()` (`invoices/invoice.py:14`) and also shows up in `render()` (`invoices/invoice.py:40`).
- **Fix:** Round half up explicitly, e.g. with `Decimal`:

  ```python
  from decimal import Decimal, ROUND_HALF_UP

  def to_cents(amount: float) -> int:
      return int(Decimal(str(amount)).scaleb(2).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
  ```

  (A float-based `int(amount * 100 + 0.5)` fixes the 19.99 case for non-negative amounts, but the `Decimal` form is the reliable half-up conversion.)

## 3. `percent_of` does not round half up for negative amounts (violates rule 1/3 for credits)

- **File/line:** `invoices/money.py:11`
- **Why it is wrong:** `int(x + 0.5)` truncates toward zero, which only implements round-half-up for non-negative values. For a negative amount (e.g. a credit/refund line making the subtotal negative), `percent_of(-150, 10)` computes `int(-14.5)` = **-14**, whereas half-up rounding of -15.0¢... (i.e. `-15 + 0.5 = -14.5`) should floor to **-15**. The result silently deviates from the mandated rounding rule.
- **Fix:** Use flooring so half-up holds for all signs:

  ```python
  import math

  def percent_of(cents: int, rate: float) -> int:
      return math.floor(cents * rate / 100 + 0.5)
  ```

  (Or compute with `Decimal` and `ROUND_HALF_UP`, consistent with the fix for finding 2.)

## 4. `fmt` renders negative amounts incorrectly

- **File/line:** `invoices/money.py:15`
- **Why it is wrong:** Not a README rule, but a correctness bug in the same module: Python's floor division/modulo make `fmt(-50)` return `"$-1.50"` instead of `"-$0.50"`, so any credit line or negative total renders as the wrong amount.
- **Fix:** Format from the absolute value and prepend the sign:

  ```python
  def fmt(cents: int) -> str:
      sign = "-" if cents < 0 else ""
      return f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"
  ```
