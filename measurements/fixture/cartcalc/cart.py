from dataclasses import dataclass, field

TAX_RATE = 0.08
BULK_THRESHOLD = 10
BULK_DISCOUNT = 0.05


@dataclass
class Line:
    sku: str
    unit_price_cents: int
    qty: int


@dataclass
class Cart:
    lines: list = field(default_factory=list)
    coupon_percent: int = 0

    def add(self, sku: str, unit_price_cents: int, qty: int = 1) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        for line in self.lines:
            if line.sku == sku:
                line.qty = qty
                return
        self.lines.append(Line(sku, unit_price_cents, qty))

    def item_count(self) -> int:
        return sum(line.qty for line in self.lines)

    def subtotal_cents(self) -> int:
        return sum(line.unit_price_cents * line.qty for line in self.lines)

    def discount_cents(self) -> int:
        rate = self.coupon_percent / 100
        if self.item_count() > BULK_THRESHOLD:
            rate += BULK_DISCOUNT
        return round(self.subtotal_cents() * rate)

    def tax_cents(self) -> int:
        return round(self.subtotal_cents() * TAX_RATE)

    def total_cents(self) -> int:
        return self.subtotal_cents() - self.discount_cents() + self.tax_cents()
