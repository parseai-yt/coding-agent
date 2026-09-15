# Review of `invoices/` against README rules

Ordered most serious first. No code was changed. Note: the test suite could not
be executed in this session, so failures below are derived by reading the code.

---

## 1. Discount is applied after tax, and tax is computed on the undiscounted subtotal

**File:** `invoices/invoice.py`, lines 30-37

```python
def tax(self) -> int:
    return percent_of(self.subtotal(), self.tax_rate)      # line 31

def total(self) -> int:
    return self.subtotal() + self.tax() - self.discount()  # line 37
```

**Rule violated:** README rule 2 ("A discount applies to the subtotal, before
tax") and rule 3 ("Tax is computed on the discounted subtotal").

**Why it is wrong:** `tax()` takes a percentage of the raw subtotal, and
`total()` only subtracts the discount at the very end. The customer is therefore
taxed on money they never paid. Example with `tax_rate=10, discount_rate=20` and
one $300.00 line:

| step            | code produces               | rule requires               |
|-----------------|-----------------------------|-----------------------------|
| subtotal        | 30000                       | 30000                       |
| discount (20%)  | 6000                        | 6000                        |
| taxable base    | 30000                       | 24000                       |
| tax (10%)       | 3000                        | 2400                        |
| total           | 30000 + 3000 - 6000 = 27000 | 24000 + 2400 = 26400        |

`tests/test_invoice.py::test_discount_applies_before_tax` expects 26400 and
will fail.

**Fix:** introduce a discounted-subtotal step and compute tax from it.

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

## 2. `to_cents` truncates instead of rounding half up

**File:** `invoices/money.py`, line 6

```python
return int(amount * 100)
```

**Rule violated:** README rule 1 ("Every amount is converted to integer cents by
rounding half up, never by truncating").

**Why it is wrong:** `int()` truncates toward zero, and `amount * 100` is a
binary float that is frequently a hair below the intended integer. Concrete
cases:

- `19.99 * 100` is `1998.9999999999998`, so `to_cents(19.99)` returns **1998**,
  not 1999. `tests/test_money.py::test_amount_that_floats_badly` and
  `tests/test_invoice.py::test_line_price_that_floats_badly` (expects 5997,
  gets 5994) will fail.
- `4.35 * 100` is `434.99999999999994`, so `to_cents(4.35)` returns 434.
- `to_cents(1.005)` returns 100; half-up rounding requires 101.

Because `Line.cents()` and `render()` both route through `to_cents`, every line
item, the subtotal, discount, tax and total inherit the off-by-one-cent error.

**Fix:** do the arithmetic in `Decimal`, constructed from the *string* form of
the float so the caller's intended decimal value is used rather than its binary
approximation, and round explicitly with `ROUND_HALF_UP`.

```python
from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

(A simpler `int(amount * 100 + 0.5)` fixes 19.99 but still returns 100 for
1.005, because `1.005 * 100` is `100.49999999999999`, so it does not satisfy the
rule.)

---

## 3. `percent_of` rounds via float `+ 0.5` and is not reliably half-up

**File:** `invoices/money.py`, line 11

```python
return int(cents * rate / 100 + 0.5)
```

**Rule violated:** README rule 3 ("rounded half up to the cent"); rule 1 for the
discount amount.

**Why it is wrong:**

- `cents * rate / 100` is evaluated in binary floating point. For rates that
  are not exactly representable (7.3, 8.875, 6.35, ...) the product can land a
  fraction below a true `.5` boundary, after which `+ 0.5` and `int()` round it
  *down*. The result depends on the rate's binary representation rather than on
  the decimal value the caller wrote.
- `int(x + 0.5)` only implements half-up for non-negative `x`. For a negative
  amount (a credit or refund line) `int(-4.5 + 0.5)` gives `-4`, which is
  neither half-up nor half-away-from-zero in any consistent sense; the helper
  silently changes rounding mode based on sign.

The existing test `test_percent_rounds_half_up` uses `percent_of(1250, 10)`,
which is exactly 125.0 and never exercises a half, so it does not catch this.

**Fix:** use `Decimal` with an explicit rounding mode, again building the rate
from its string form.

```python
from decimal import Decimal, ROUND_HALF_UP

def percent_of(cents: int, rate: float) -> int:
    value = Decimal(cents) * Decimal(str(rate)) / Decimal(100)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 4. `fmt` renders negative amounts incorrectly

**File:** `invoices/money.py`, line 15

```python
return f"${cents // 100}.{cents % 100:02d}"
```

**Rule violated:** none of the numbered rules directly, but it produces wrong
output for any negative total (e.g. a discount larger than the subtotal, or a
credit line).

**Why it is wrong:** Python's floor division and modulo on negatives give
`-150 // 100 == -2` and `-150 % 100 == 50`, so `fmt(-150)` returns `"$-2.50"`
instead of `"-$1.50"`.

**Fix:** format the absolute value and prepend the sign.

```python
def fmt(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    dollars, rem = divmod(abs(cents), 100)
    return f"{sign}${dollars}.{rem:02d}"
```

---

## 5. Minor: per-unit rounding in `Line.cents` and `render`

**File:** `invoices/invoice.py`, lines 14 and 40

```python
return to_cents(self.unit_price) * self.quantity          # line 14
... fmt(to_cents(l.unit_price)) ...                       # line 40
```

**Why it matters:** the unit price is rounded to a cent *before* multiplying by
quantity. A unit price of 0.005 with quantity 3 yields 3 cents rather than the
2 cents you would get by rounding the extended amount (1.5 cents). Whether the
unit price or the extended line amount is "the amount" in README rule 1 is not
stated; rounding the unit price first is defensible (and matches what
`render()` prints), but the choice should be deliberate and documented. If the
extended amount is meant to be rounded, change line 14 to
`to_cents(self.unit_price * self.quantity)` once `to_cents` is fixed per
finding 2. No change is needed if per-unit rounding is the intent.

---

## Test coverage notes (outside `invoices/`, for context)

- `tests/test_money.py::test_percent_rounds_half_up` never hits a `.5` case;
  add e.g. `percent_of(1005, 5) == 50` (50.25) and `percent_of(1010, 5) == 51`
  (50.5) once finding 3 is fixed.
- There is no test for a rate that is inexact in binary (e.g. 7.3) or for
  `to_cents(1.005)`; both would have caught findings 2 and 3.
- `Invoice.tax()` and `Invoice.discount()` have no direct tests; only `total()`
  is asserted, which is why the misordering in finding 1 shows up as a single
  failing test rather than a clear diagnosis.
