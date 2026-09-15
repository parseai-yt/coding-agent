"""Money helpers. Everything downstream works in integer cents."""


def to_cents(amount: float) -> int:
    """Convert a decimal amount such as 19.99 to integer cents."""
    return int(amount * 100)


def percent_of(cents: int, rate: float) -> int:
    """Return rate percent of an amount in cents, rounded half up."""
    return int(cents * rate / 100 + 0.5)


def fmt(cents: int) -> str:
    return f"${cents // 100}.{cents % 100:02d}"
