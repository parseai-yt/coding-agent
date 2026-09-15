# Review of `invoices/` against README rules

Ordered most serious first. No code was changed.

Evidence: `python3 -m unittest` currently fails 3 of 8 tests, and each failure maps directly to findings 1 and 2 below.

```
FAIL: test_discount_applies_before_tax   AssertionError: 27000 != 26400
FAIL: test_line_price_that_floats_badly  AssertionError: 5994 != 5997
FAIL: test_amount_that_floats_badly      AssertionError: 1998 != 1999
```

---

## 1. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

**File:** `invoices/invoice.py`, line 31 (`tax()`), and line 37 (`total()`)

**Why it is wrong:** Rule 2 says the discount applies to the subtotal before tax, and rule 3 says tax is computed on the *discounted* subtotal. `tax()` calls `percent_of(self.subtotal(), self.tax_rate)`, which is the full, pre-discount subtotal. `total()` then adds that inflated tax and subtracts the discount, so every discounted invoice over-charges tax by `discount_rate% × tax_rate%` of the subtotal.

Concrete case from the test suite: a $300.00 line with a 20% discount and 10% tax.

| Step | Code produces | Rules require |
|---|---|---|
| subtotal | 30000 | 30000 |
| discount | 6000 | 6000 |
| tax base | 30000 | 24000 |
| tax | 3000 | 2400 |
| total | 27000 | 26400 |

**Fix:**

```python
def discounted_subtotal(self) -> int:
    return self.subtotal() - self.discount()

def tax(self) -> int:
    return percent_of(self.discounted_subtotal(), self.tax_rate)

def total(self) -> int:
    return self.discounted_subtotal() + self.tax()
```

---

## 2. `to_cents` truncates instead of rounding half up (violates rule 1)

**File:** `invoices/money.py`, line 6

**Why it is wrong:** Rule 1 says every amount is converted to cents by rounding half up, never by truncating. `int(amount * 100)` truncates toward zero. Because most two-decimal prices are not exactly representable as binary floats, `amount * 100` frequently lands a hair *below* the intended integer, and truncation then drops a whole cent. The failing tests show it: `19.99 * 100` evaluates to `1998.9999999999998`, so `to_cents(19.99)` returns 1998, and a line of three at $19.99 comes out at 5994 cents instead of 5997. The same mechanism affects many ordinary prices such as 0.29, 1.15, and 4.35. Every such line item under-bills the customer by one cent per unit, and the error is multiplied by `quantity` in `Line.cents()` (`invoices/invoice.py`, line 14).

This is also the root cause of the incorrect unit price shown by `render()` (`invoices/invoice.py`, line 40), which calls `to_cents` on each line's price.

**Fix:** Route through `Decimal` built from the string form of the amount, which avoids binary float artefacts, and round explicitly with `ROUND_HALF_UP`.

```python
from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

Note that `int(amount * 100 + 0.5)` is *not* a sufficient fix: it still starts from a lossy float product, so inputs like 1.005 would round the wrong way.

---

## 3. `percent_of` only rounds half up for non-negative results (violates rule 1 for credits)

**File:** `invoices/money.py`, line 11

**Why it is wrong:** `int(x + 0.5)` is a half-up rounding only when `x` is non-negative, because `int()` truncates toward zero. For a negative amount it is wrong even away from the tie: `percent_of(-1234, 10)` computes `int(-123.4 + 0.5)`, which is `int(-122.9)`, giving -122 when the correct answer is -123. Nothing in the API prevents negative cents (a credit or refund line with a negative `unit_price`, or a negative discount), so this silently misrounds any such invoice. Independently, the computation is done in floating point on `cents * rate / 100`, so it inherits the same class of representation error described in finding 2 for non-terminating rates.

**Fix:** Use `Decimal` with an explicit half-up rounding mode so the behaviour is correct for every sign and does not depend on float artefacts.

```python
from decimal import Decimal, ROUND_HALF_UP

def percent_of(cents: int, rate: float) -> int:
    return int((Decimal(cents) * Decimal(str(rate)) / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 4. `fmt` renders negative amounts incorrectly

**File:** `invoices/money.py`, line 15

**Why it is wrong:** This is not one of the three numbered README rules, but it corrupts the rendered invoice for the same negative-amount inputs discussed in finding 3. Python's `//` and `%` floor toward negative infinity, so `fmt(-150)` produces `"$-2.50"` instead of `"-$1.50"`, and `fmt(-5)` produces `"$-1.95"` instead of `"-$0.05"`.

**Fix:** Format the absolute value and prefix the sign.

```python
def fmt(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"
```

---

## Summary

| # | Severity | File:line | Rule | Effect |
|---|---|---|---|---|
| 1 | High | `invoices/invoice.py:31`, `:37` | 2, 3 | Tax over-charged on every discounted invoice |
| 2 | High | `invoices/money.py:6` | 1 | Common prices lose a cent per unit; totals and rendered prices wrong |
| 3 | Medium | `invoices/money.py:11` | 1 | Negative amounts misrounded; float-based rounding |
| 4 | Low | `invoices/money.py:15` | (rendering) | Negative amounts display garbled |

Findings 1 and 2 are each sufficient on their own to explain the three failing tests. Fixing both should turn the suite green without touching the tests.
