import unittest

from invoices import Invoice


class InvoiceTest(unittest.TestCase):
    def test_subtotal(self):
        inv = Invoice(tax_rate=8).add("keyboard", 49.50).add("cable", 5.25, 2)
        self.assertEqual(inv.subtotal(), 6000)

    def test_no_discount_total(self):
        inv = Invoice(tax_rate=10).add("monitor", 200.00)
        self.assertEqual(inv.total(), 22000)

    def test_discount_applies_before_tax(self):
        inv = Invoice(tax_rate=10, discount_rate=20).add("desk", 300.00)
        # 30000 - 20% = 24000, plus 10% tax = 26400
        self.assertEqual(inv.total(), 26400)

    def test_line_price_that_floats_badly(self):
        inv = Invoice(tax_rate=0).add("mouse", 19.99, 3)
        self.assertEqual(inv.subtotal(), 5997)
