# Review of `invoices/` against README.md

Findings are ordered most serious first. No code was changed.

Note: the test suite could not be executed in this session (shell access was denied), so the
expected failures below are derived by tracing the code by hand.

---

## 1. Discount is applied after tax, not before (violates rules 2 and 3)

**File:** `invoices/invoice.py`, lines 30-37

```python
def tax(self) -> int:
    return percent_of(self.subtotal(), self.tax_rate)

def discount(self) -> int:
    return percent_of(self.subtotal(), self.discount_rate)

def total(self) -> int:
    return self.subtotal() + self.tax() - self.discount()
```

**Why it is wrong:** README rule 2 says the discount applies to the subtotal *before* tax, and
rule 3 says tax is computed on the *discounted* subtotal. `tax()` computes tax on the full,
undiscounted subtotal, and `total()` then subtracts the discount from the taxed amount. The
customer is charged tax on money they never paid.

Concrete case (this is `tests/test_invoice.py::test_discount_applies_before_tax`):
`Invoice(tax_rate=10, discount_rate=20).add("desk", 300.00)`

| step | code today | README |
|---|---|---|
| subtotal | 30000 | 30000 |
| discount | 6000 | 6000 |
| tax base | 30000 | 24000 |
| tax | 3000 | 2400 |
| total | **27000** | **26400** |

The existing test expects 26400, so it fails against the current code.

**Fix:** compute a discounted subtotal and base tax on it.

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

```python
return int(amount * 100)
```

**Why it is wrong:** README rule 1 says every amount is converted to cents by rounding half up,
*never by truncating*. `int()` truncates toward zero. Combined with binary floating point this
loses a cent on many ordinary prices:

- `19.99 * 100` evaluates to `1998.9999999999998`, so `to_cents(19.99)` returns **1998**, not 1999.
- `0.29 * 100` evaluates to `28.999999999999996`, so `to_cents(0.29)` returns **28**.
- `to_cents(1.005)` returns 100 rather than 101, because the value is truncated and not rounded.

The error is then multiplied by quantity in `Line.cents()`, so `add("mouse", 19.99, 3)` yields
5994 instead of 5997. Both `tests/test_money.py::test_amount_that_floats_badly` and
`tests/test_invoice.py::test_line_price_that_floats_badly` fail against the current code.

**Fix:** round half up explicitly, and avoid the binary float multiply by going through `Decimal`
built from the value's string form:

```python
from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

Note that Python's built-in `round()` is *not* an acceptable replacement: it uses banker's
rounding (half to even), which also breaks rule 1.

---

## 3. `percent_of` does the half-up rounding in binary floating point (fragile under rules 1 and 3)

**File:** `invoices/money.py`, line 11

```python
return int(cents * rate / 100 + 0.5)
```

**Why it is wrong:** The intent (add 0.5 then truncate) is a correct half-up scheme for
non-negative values, but the value being rounded is `cents * rate / 100` computed in binary
floating point. For rates that are not exactly representable (for example `8.25`, `7.1`,
`1.1`) the product can land a hair below an exact `.5`, which then rounds *down* instead of up.
The README requires half-up rounding of the tax to the cent; this implementation only gets it
right when the float arithmetic happens to be exact. The `+ 0.5` trick also rounds negative
values (refund or credit lines) toward positive infinity rather than away from zero, which is
not what "half up" means for money.

**Fix:** do the arithmetic in `Decimal` so that half-up is applied to the exact quotient:

```python
from decimal import Decimal, ROUND_HALF_UP

def percent_of(cents: int, rate: float) -> int:
    exact = Decimal(cents) * Decimal(str(rate)) / Decimal(100)
    return int(exact.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 4. `fmt` renders negative amounts incorrectly (minor, not covered by a README rule)

**File:** `invoices/money.py`, line 15

```python
return f"${cents // 100}.{cents % 100:02d}"
```

**Why it is wrong:** Python's floor division and modulo on negatives produce, for example,
`fmt(-5) == "$-1.95"` and `fmt(-1999) == "$-20.01"`. This only matters if a credit or a discount
larger than the subtotal is ever rendered, so it is listed last, but it is a latent
correctness bug in the money layer.

**Fix:** format the absolute value and prepend the sign:

```python
def fmt(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    dollars, rem = divmod(abs(cents), 100)
    return f"{sign}${dollars}.{rem:02d}"
```

---

## Summary

| # | File:line | Rule broken | Severity |
|---|---|---|---|
| 1 | `invoices/invoice.py:30-37` | 2, 3 (discount ordering / tax base) | High: every discounted invoice overcharges tax |
| 2 | `invoices/money.py:6` | 1 (truncation) | High: common prices lose a cent per unit |
| 3 | `invoices/money.py:11` | 1, 3 (float rounding) | Medium: wrong for some non-exact rates |
| 4 | `invoices/money.py:15` | none (formatting) | Low: negative amounts misrendered |

Expected test outcome with the current code: `test_discount_applies_before_tax`,
`test_amount_that_floats_badly`, and `test_line_price_that_floats_badly` fail; the rest pass.
