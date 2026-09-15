# Review of `invoices/` against README rules

Ordered most serious first. No code was changed. Note: shell execution was
unavailable in this session, so the test suite was not run; the failing test
noted in finding 1 is determined by arithmetic, and the float facts in finding 2
are standard IEEE 754 results (e.g. `19.99 * 100 == 1998.9999999999998`).

---

## 1. Tax is computed on the undiscounted subtotal (violates rules 2 and 3)

**File:** `invoices/invoice.py`, line 31 (`tax`) and line 37 (`total`)

**Why it is wrong:** Rule 2 says the discount applies to the subtotal before
tax, and rule 3 says tax is computed on the *discounted* subtotal. `tax()`
calls `percent_of(self.subtotal(), self.tax_rate)`, i.e. tax on the full
subtotal, and `total()` then does `subtotal + tax - discount`. The discount is
effectively applied *after* tax, and the customer is taxed on money they never
paid.

Concrete case (this is `tests/test_invoice.py::test_discount_applies_before_tax`):
$300.00 line, 20% discount, 10% tax.

| step        | current code                  | per README                        |
|-------------|-------------------------------|-----------------------------------|
| subtotal    | 30000                         | 30000                             |
| discount    | 6000                          | 6000                              |
| tax         | 10% of 30000 = 3000           | 10% of 24000 = 2400               |
| total       | 30000 + 3000 - 6000 = **27000** | 24000 + 2400 = **26400**        |

The existing test expects 26400, so it fails against the current code.

**Fix:** introduce a discounted subtotal and compute tax from it:

```python
def discount(self) -> int:
    return percent_of(self.subtotal(), self.discount_rate)

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

**Why it is wrong:** `int(amount * 100)` truncates toward zero. Rule 1
forbids truncation. Because most decimal prices are not exactly representable
as binary floats, `amount * 100` frequently lands just below the integer, and
`int()` drops a cent:

| amount | `amount * 100`        | `int(...)` | correct |
|--------|-----------------------|------------|---------|
| 19.99  | 1998.9999999999998    | 1998       | 1999    |
| 0.29   | 28.999999999999996    | 28         | 29      |
| 1.15   | 114.99999999999999    | 114        | 115     |
| 4.35   | 434.99999999999994    | 434        | 435     |

This affects every line item via `Line.cents()` (`invoice.py` line 14) and the
rendered unit price (`invoice.py` line 40), so subtotals, discounts, tax and
totals all inherit the error. `tests/test_money.py::test_amount_that_floats_badly`
and `tests/test_invoice.py::test_line_price_that_floats_badly` both fail on
this: `to_cents(19.99)` returns 1998, and the mouse line gives 5994 instead of 5997.

**Fix:** round half up via `Decimal`, going through `str()` so the float is
interpreted at its printed precision rather than its binary expansion:

```python
from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

Longer term, accept `Decimal` or `str` prices at the API boundary instead of
`float` so the input is never lossy in the first place.

---

## 3. `percent_of` relies on float arithmetic for a half-up rounding step (rule 1 / rule 3, fragile)

**File:** `invoices/money.py`, line 11

**Why it is wrong:** `int(cents * rate / 100 + 0.5)` is the right idea for
non-negative values, but `rate` is a float and the division is done in binary
floating point. A result that is exactly `.5` in decimal can come out as
`.4999…` in float (the same class of error as finding 2), at which point the
`+ 0.5` trick rounds *down*, contradicting rule 1 and rule 3. It also only
implements half-up for non-negative inputs: for negative values `int()`
truncates toward zero, so `int(-2.5 + 0.5)` gives `-2`, not `-3`. Refunds or
credit lines would round the wrong way.

**Fix:** do the arithmetic in `Decimal` and round with `ROUND_HALF_UP`:

```python
from decimal import Decimal, ROUND_HALF_UP

def percent_of(cents: int, rate: float) -> int:
    value = Decimal(cents) * Decimal(str(rate)) / Decimal(100)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 4. `fmt` renders negative amounts incorrectly

**File:** `invoices/money.py`, line 15

**Why it is wrong:** Not covered by a README rule directly, but it corrupts
the displayed amount. `//` and `%` floor toward negative infinity in Python, so
`fmt(-150)` produces `"$-2.50"` rather than `"-$1.50"`. Any invoice whose
total goes negative (large discount, credit line) will render a wrong number.

**Fix:**

```python
def fmt(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"
```

---

## 5. Tests do not exercise the rule that is broken

**File:** `tests/test_money.py`, line 13; `tests/test_invoice.py`

**Why it is wrong:** `test_percent_rounds_half_up` uses `percent_of(1250, 10)`,
which is exactly 125 with no fractional part, so it never tests half-up
rounding at all. There is no test for `to_cents` on a value that sits at a
half-cent, and no test where the tax on the discounted subtotal produces a
fractional cent. This is why findings 2 and 3 could ship.

**Fix:** add cases that actually land on a half cent, e.g.
`percent_of(1005, 7.5)` (75.375 → 75) and `percent_of(1, 50)` (0.5 → 1),
plus `to_cents("1.005")`-style inputs once `to_cents` accepts decimal strings.
