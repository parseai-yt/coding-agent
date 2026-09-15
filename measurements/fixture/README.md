# invoices

Builds customer invoices in integer cents.

Rules the code must follow:
1. Every amount is converted to integer cents by rounding half up, never by truncating.
2. A discount applies to the subtotal, before tax.
3. Tax is computed on the discounted subtotal and rounded half up to the cent.
