# Review of `invoices/` against README rules

Findings are ordered most serious first. No code was changed.

## 1. `to_cents` truncates instead of rounding half up (violates rule 1)

- **File:** `invoices/money.py`, line 6
- **Why it is wrong:** `int(amount * 100)` truncates toward zero. Because most decimal prices are not exactly representable as binary floats, `19.99 * 100` evaluates to `1998.9999999999998`, so `to_cents(19.99)` returns **1998**, not 1999. This silently loses a cent on a large fraction of real-world prices, and the error is then multiplied by the line quantity in `Line.cents()` (e.g. `29.99 × 100` units is a whole dollar short). Rule 1 explicitly forbids truncation and requires rounding half up.
- **Fix:** Round half up instead of truncating. Robust version using `Decimal` (avoids the float representation problem entirely):

  ```python
  from decimal import Decimal, ROUND_HALF_UP

  def to_cents(amount: float) -> int:
      return int(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)
  ```

  A minimal float-based fix is `math.floor(amount * 100 + 0.5)`, which also rounds half up for negative amounts, unlike `int(... + 0.5)`.

## 2. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

- **File:** `invoices/invoice.py`, line 31 (and the derived `total()` on line 37)
- **Why it is wrong:** `tax()` calls `percent_of(self.subtotal(), self.tax_rate)`, i.e. tax on the full subtotal. Rules 2–3 require the discount to be applied first and tax computed on the *discounted* subtotal. Whenever both a discount and a tax rate are set, the customer is overcharged. Example: subtotal $100.00, 10% discount, 8% tax — the rules require 8% of $90.00 = $7.20 tax for a total of $97.20, but the code charges 8% of $100.00 = $8.00 tax for a total of $98.00, i.e. 80 cents too much.
- **Fix:** Base the tax on the discounted subtotal:

  ```python
  def tax(self) -> int:
      return percent_of(self.subtotal() - self.discount(), self.tax_rate)

  def total(self) -> int:
      return self.subtotal() - self.discount() + self.tax()
  ```

## 3. `percent_of` does not round half up for negative amounts (violates rule 1)

- **File:** `invoices/money.py`, line 11
- **Why it is wrong:** `int(x + 0.5)` implements round-half-up only for non-negative `x`, because `int()` truncates toward zero. For a negative amount (e.g. a credit line or refund invoice), `percent_of(-150, 10)` computes `int(-15.0 + 0.5) = int(-14.5) = -14` instead of the half-up result. Rule 1 says every amount must be rounded half up, never truncated.
- **Fix:** Use flooring so the +0.5 trick rounds half up for all signs:

  ```python
  import math

  def percent_of(cents: int, rate: float) -> int:
      return math.floor(cents * rate / 100 + 0.5)
  ```

## 4. `fmt` renders negative amounts incorrectly

- **File:** `invoices/money.py`, line 15
- **Why it is wrong:** Python's `//` and `%` floor toward negative infinity, so `fmt(-50)` produces `"$-1.50"` and `fmt(-1999)` produces `"$-20.01"`. Any invoice whose total goes negative (discount exceeding subtotal, credit notes) renders a wrong dollar figure — not just a formatting nit, a wrong number shown to the customer.
- **Fix:** Format the absolute value and prepend the sign:

  ```python
  def fmt(cents: int) -> str:
      sign = "-" if cents < 0 else ""
      return f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"
  ```
