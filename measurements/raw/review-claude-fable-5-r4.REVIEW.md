# Review of `invoices/` against README rules

Findings are ordered most serious first. No code was changed.

## 1. `to_cents` truncates instead of rounding half up (Rule 1)

- **File:** `invoices/money.py`, line 6
- **Why it is wrong:** Rule 1 says every amount is converted to integer cents by rounding half up, *never by truncating*. `int(amount * 100)` truncates toward zero. Combined with binary floating point this loses a cent on very common prices: `19.99 * 100 == 1998.9999999999998`, so `to_cents(19.99)` returns **1998**, not 1999. Because `Line.cents()` (invoice.py:14) multiplies this truncated value by the quantity, the error is amplified — 100 units at $19.99 comes out 100 cents ($1.00) short. Every subtotal, discount, tax, and total downstream inherits the error.
- **Fix:** Convert via `Decimal` with explicit half-up rounding, e.g.:

  ```python
  from decimal import Decimal, ROUND_HALF_UP

  def to_cents(amount: float) -> int:
      return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
  ```

## 2. Tax is computed on the full subtotal, not the discounted subtotal (Rules 2 and 3)

- **File:** `invoices/invoice.py`, line 31 (and the total at line 37)
- **Why it is wrong:** Rule 2 says the discount applies to the subtotal before tax, and Rule 3 says tax is computed on the *discounted* subtotal. `tax()` calls `percent_of(self.subtotal(), self.tax_rate)` — the undiscounted subtotal — and `total()` then subtracts the discount afterwards. Every invoice with a discount is over-taxed by `discount × tax_rate`. Example: subtotal $100.00, 10% discount, 8% tax → code charges 800¢ tax on a $90.00 taxable base instead of 720¢, overcharging 80¢.
- **Fix:** Tax the discounted amount and build the total from it:

  ```python
  def tax(self) -> int:
      return percent_of(self.subtotal() - self.discount(), self.tax_rate)

  def total(self) -> int:
      return self.subtotal() - self.discount() + self.tax()
  ```

## 3. `percent_of` does not reliably round half up (Rules 1 and 3)

- **File:** `invoices/money.py`, line 11
- **Why it is wrong:** `int(cents * rate / 100 + 0.5)` is a float-based half-up approximation with two defects. (a) The intermediate `cents * rate / 100` is a binary float, so a value that is mathematically exactly `x.5` cents can be represented as `x.4999…` and round down instead of up. (b) For negative amounts (credit/refund lines, negative rates) `int()` truncates toward zero, so e.g. a true value of −10.5 yields `int(-10.0)` = −10 instead of half-up behavior. Rules 1 and 3 require half-up rounding unconditionally.
- **Fix:** Do the arithmetic in `Decimal` and quantize half up:

  ```python
  def percent_of(cents: int, rate: float) -> int:
      return int((Decimal(cents) * Decimal(str(rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
  ```

## 4. `fmt` renders negative amounts incorrectly (supporting issue)

- **File:** `invoices/money.py`, line 15
- **Why it is wrong:** Not one of the three README rules, but it corrupts the displayed amounts the rules exist to protect: Python's floor division and modulo make `fmt(-50)` render as `$-1.50` instead of `-$0.50`. Any credit line or negative total (large discount) renders a wrong value in `render()`.
- **Fix:** Format from the absolute value and prepend the sign:

  ```python
  def fmt(cents: int) -> str:
      sign = "-" if cents < 0 else ""
      return f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"
  ```
