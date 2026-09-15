import unittest

from invoices.money import fmt, percent_of, to_cents


class MoneyTest(unittest.TestCase):
    def test_whole_amount(self):
        self.assertEqual(to_cents(12.0), 1200)

    def test_amount_that_floats_badly(self):
        self.assertEqual(to_cents(19.99), 1999)

    def test_percent_rounds_half_up(self):
        self.assertEqual(percent_of(1250, 10), 125)

    def test_format(self):
        self.assertEqual(fmt(1999), "$19.99")
