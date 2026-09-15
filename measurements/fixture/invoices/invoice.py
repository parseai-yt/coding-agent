"""An invoice: lines, an optional discount, and tax."""
from dataclasses import dataclass, field

from .money import fmt, percent_of, to_cents


@dataclass
class Line:
    description: str
    unit_price: float
    quantity: int = 1

    def cents(self) -> int:
        return to_cents(self.unit_price) * self.quantity


@dataclass
class Invoice:
    tax_rate: float
    discount_rate: float = 0.0
    lines: list[Line] = field(default_factory=list)

    def add(self, description: str, unit_price: float, quantity: int = 1) -> "Invoice":
        self.lines.append(Line(description, unit_price, quantity))
        return self

    def subtotal(self) -> int:
        return sum(line.cents() for line in self.lines)

    def tax(self) -> int:
        return percent_of(self.subtotal(), self.tax_rate)

    def discount(self) -> int:
        return percent_of(self.subtotal(), self.discount_rate)

    def total(self) -> int:
        return self.subtotal() + self.tax() - self.discount()

    def render(self) -> str:
        rows = [f"{l.description:<20} {l.quantity:>3} x {fmt(to_cents(l.unit_price))}" for l in self.lines]
        rows.append(f"{'total':<20} {fmt(self.total())}")
        return "\n".join(rows)
