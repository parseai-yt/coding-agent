# Review of `invoices/` against README rules

Rules under review:

1. Every amount is converted to integer cents by rounding half up, never by truncating.
2. A discount applies to the subtotal, before tax.
3. Tax is computed on the discounted subtotal and rounded half up to the cent.

Findings are ordered most serious first. No code was changed.

---

## 1. `to_cents` truncates instead of rounding half up (breaks rule 1)

**File:** `invoices/money.py`, line 6

```python
return int(amount * 100)
```

**Why it is wrong:** `int()` truncates toward zero. Most decimal prices are not
exactly representable as binary floats, so `amount * 100` frequently lands a
hair below the intended integer and the truncation drops a whole cent:

| input   | `amount * 100`        | `int(...)` | correct |
|---------|-----------------------|------------|---------|
| `19.99` | `1998.9999999999998`  | `1998`     | `1999`  |
| `0.29`  | `28.999999999999996`  | `28`       | `29`    |
| `4.35`  | `434.99999999999994`  | `434`      | `435`   |

Because `Line.cents()` multiplies this per-unit value by `quantity`
(`invoices/invoice.py:14`), the one-cent error is multiplied: a line of
100 x 19.99 is short by $1.00. Every downstream figure (subtotal, discount,
tax, total, and the rendered unit price on `invoice.py:40`) inherits the error.
This is exactly the "never by truncating" case the README forbids.

**Fix:** round half up via `Decimal`, going through `str()` so the float's
shortest repr is used rather than its binary expansion:

```python
from decimal import Decimal, ROUND_HALF_UP

def to_cents(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

`Decimal("19.99") * 100` is exactly `1999`, and true half cases such as
`1.005` round up to `101`.

---

## 2. Tax is computed on the undiscounted subtotal (breaks rules 2 and 3)

**File:** `invoices/invoice.py`, line 31 (and the total on line 37)

```python
def tax(self) -> int:
    return percent_of(self.subtotal(), self.tax_rate)
```

**Why it is wrong:** rule 2 says the discount comes off the subtotal *before*
tax, and rule 3 says tax is computed on the *discounted* subtotal. `tax()`
taxes the full subtotal, and `total()` then subtracts the discount afterwards,
which is "discount after tax". The customer is overcharged tax on money they
never paid.

Example: one line at $100.00, 10% discount, 10% tax.

| step               | current code | per README |
|--------------------|--------------|------------|
| subtotal           | 10000        | 10000      |
| discount           | 1000         | 1000       |
| taxable base       | 10000        | 9000       |
| tax                | **1000**     | **900**    |
| total              | **10000**    | **9900**   |

**Fix:** tax the discounted subtotal, and build the total from that base:

```python
def discounted_subtotal(self) -> int:
    return self.subtotal() - self.discount()

def tax(self) -> int:
    return percent_of(self.discounted_subtotal(), self.tax_rate)

def total(self) -> int:
    return self.discounted_subtotal() + self.tax()
```

`total()` produces the same number either way once `tax()` is fixed, but
expressing it as base plus tax makes the ordering rule visible in the code.

---

## 3. `percent_of` rounding is "half toward +infinity" in float, not half up in cents (weakens rules 1 and 3)

**File:** `invoices/money.py`, line 11

```python
return int(cents * rate / 100 + 0.5)
```

**Why it is wrong:** two separate problems.

- **Negative amounts round the wrong way.** `int(x + 0.5)` is half-up only
  for `x >= 0`. For a credit line or refund invoice, `percent_of(-1005, 10)`
  gives `int(-100.5 + 0.5) = int(-100.0) = -100`; rounding the magnitude half
  up gives `-101`. The discount and tax on a negative invoice are therefore off
  by a cent in the customer's favour in the half case.
- **Float arithmetic before the `+ 0.5`.** `cents * rate / 100` is evaluated
  in binary floating point, so an exact half such as `xx.5` can come out as
  `xx.499999...` for rates like `8.25` or `7.375`, and the `+ 0.5` then rounds
  down instead of up. Rule 3 explicitly requires half-up rounding of the tax,
  so the arithmetic feeding the rounding must be exact.

**Fix:** do the multiplication in `Decimal` and quantize with `ROUND_HALF_UP`,
which rounds away from zero on ties for both signs:

```python
from decimal import Decimal, ROUND_HALF_UP

def percent_of(cents: int, rate: float) -> int:
    value = Decimal(cents) * Decimal(str(rate)) / Decimal(100)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

---

## 4. `fmt` renders negative amounts incorrectly (not a README rule, but a correctness bug)

**File:** `invoices/money.py`, line 15

```python
return f"${cents // 100}.{cents % 100:02d}"
```

**Why it is wrong:** Python's `//` and `%` floor toward negative infinity, so
`fmt(-150)` produces `"$-2.50"` instead of `"-$1.50"`. Any credit line or
negative total is rendered as the wrong number, not just formatted oddly.

**Fix:** format the absolute value and reapply the sign:

```python
def fmt(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    dollars, rem = divmod(abs(cents), 100)
    return f"{sign}${dollars}.{rem:02d}"
```

---

## 5. `render` recomputes the unit price through `to_cents` and omits the discount and tax rows (minor)

**File:** `invoices/invoice.py`, lines 40 to 41

**Why it matters:** line 40 calls `to_cents(l.unit_price)` directly, so it is
subject to finding 1 and will show `$19.98` for a `19.99` line until
`to_cents` is fixed. The rendered invoice also jumps from line items straight
to `total`, with no subtotal, discount, or tax rows, which makes the ordering
required by rules 2 and 3 invisible to the reader and hard to spot-check.

**Fix:** after finding 1 is fixed the unit price will be correct as written.
Optionally add rows for subtotal, discount, and tax between the line items and
the total so the discount-before-tax ordering can be verified from the output.

---

## Not flagged

- `Line.cents()` rounds the unit price to cents and then multiplies by
  quantity. Rounding the extended price instead (`unit_price * quantity`) is
  a legitimate alternative, but the README does not mandate either, so the
  current choice is acceptable once `to_cents` rounds correctly.
- Rates are plain floats (`tax_rate=8.25` means 8.25%). That is consistent
  across the module and fine as long as `percent_of` converts via
  `Decimal(str(rate))` as in finding 3.

## Verification note

Executing Python in this session was blocked by the sandbox, so the float
values in the tables above are the standard IEEE 754 double results for those
literals rather than output captured from this repo. They are stable and easy
to confirm with `python3 -c "print(19.99*100, 0.29*100, 4.35*100)"`.
