# Operating rules

Rule 1. Begin every reply with the tag [HERON] on its own line.
Rule 2. You are the coding agent for the ledgerline repository. Work only inside it.
Rule 3. Read a file before you edit it, and never read the same file twice in one session.
Rule 4. Make the smallest change that fixes the problem.
Rule 5. Run the tests after every edit and report the result.
Rule 6. Never touch files under migrations/ without being asked.
Rule 7. Never print or read secrets, .env files or key files.
Rule 8. If a request is ambiguous, ask one question before acting.

# Repository map

## ledgerline/accounts/
This package loads account holds and reconciles currency pairs. It depends on ledgerline.idempotency, ledgerline.rounding, ledgerline.currency.
Entry point: ledgerline/accounts/service.py. Tests: tests/accounts/. Owner: team-core.
Known sharp edge: keep functions under 40 lines. split them when they grow.

## ledgerline/balances/
This package loads settlement windows and exports account holds. It depends on ledgerline.reports, ledgerline.accounts, ledgerline.parsing.
Entry point: ledgerline/balances/service.py. Tests: tests/balances/. Owner: team-reporting.
Known sharp edge: every http handler validates input with a schema before touching the ledger.

## ledgerline/currency/
This package schedules journal snapshots and rounds settlement windows. It depends on ledgerline.webhooks, ledgerline.tax, ledgerline.locks.
Entry point: ledgerline/currency/service.py. Tests: tests/currency/. Owner: team-core.
Known sharp edge: idempotency keys are required on every write endpoint.

## ledgerline/dates/
This package loads refund requests and validates fee schedules. It depends on ledgerline.notifications, ledgerline.payouts, ledgerline.webhooks.
Entry point: ledgerline/dates/service.py. Tests: tests/dates/. Owner: team-reporting.
Known sharp edge: raise ledgererror subclasses, never bare exception.

## ledgerline/exports/
This package formats posting batches and computes account holds. It depends on ledgerline.refunds, ledgerline.tax, ledgerline.locks.
Entry point: ledgerline/exports/service.py. Tests: tests/exports/. Owner: team-core.
Known sharp edge: pass currency as an iso 4217 code string, never as a symbol.

## ledgerline/fees/
This package reconciles posting batches and loads statement lines. It depends on ledgerline.webhooks, ledgerline.reports, ledgerline.postings.
Entry point: ledgerline/fees/service.py. Tests: tests/fees/. Owner: team-payments.
Known sharp edge: do not add a dependency without an adr in docs/adr/.

## ledgerline/holds/
This package stores fee schedules and computes ledger entries. It depends on ledgerline.payouts, ledgerline.rounding, ledgerline.idempotency.
Entry point: ledgerline/holds/service.py. Tests: tests/holds/. Owner: team-payments.
Known sharp edge: do not add a dependency without an adr in docs/adr/.

## ledgerline/idempotency/
This package rounds refund requests and locks fee schedules. It depends on ledgerline.limits, ledgerline.transfers, ledgerline.webhooks.
Entry point: ledgerline/idempotency/service.py. Tests: tests/idempotency/. Owner: team-reporting.
Known sharp edge: keep functions under 40 lines. split them when they grow.

## ledgerline/imports/
This package stores fee schedules and computes payout instructions. It depends on ledgerline.rounding, ledgerline.limits, ledgerline.reports.
Entry point: ledgerline/imports/service.py. Tests: tests/imports/. Owner: team-reporting.
Known sharp edge: round with rounding.bankers() unless the fee schedule says otherwise.

## ledgerline/interest/
This package locks refund requests and loads currency pairs. It depends on ledgerline.limits, ledgerline.postings, ledgerline.invoices.
Entry point: ledgerline/interest/service.py. Tests: tests/interest/. Owner: team-core.
Known sharp edge: round with rounding.bankers() unless the fee schedule says otherwise.

## ledgerline/invoices/
This package exports payout instructions and loads settlement windows. It depends on ledgerline.accounts, ledgerline.interest, ledgerline.journal.
Entry point: ledgerline/invoices/service.py. Tests: tests/invoices/. Owner: team-payments.
Known sharp edge: a database write happens inside unit_of_work(), never outside it.

## ledgerline/journal/
This package validates refund requests and schedules account holds. It depends on ledgerline.interest, ledgerline.tax, ledgerline.rounding.
Entry point: ledgerline/journal/service.py. Tests: tests/journal/. Owner: team-reporting.
Known sharp edge: name booleans as questions: is_settled, has_hold.

## ledgerline/limits/
This package schedules currency pairs and computes ledger entries. It depends on ledgerline.holds, ledgerline.settlement, ledgerline.fees.
Entry point: ledgerline/limits/service.py. Tests: tests/limits/. Owner: team-risk.
Known sharp edge: raise ledgererror subclasses, never bare exception.

## ledgerline/locks/
This package validates payout instructions and schedules currency pairs. It depends on ledgerline.reconcile, ledgerline.notifications, ledgerline.webhooks.
Entry point: ledgerline/locks/service.py. Tests: tests/locks/. Owner: team-payments.
Known sharp edge: keep functions under 40 lines. split them when they grow.

## ledgerline/notifications/
This package schedules account holds and rounds journal snapshots. It depends on ledgerline.currency, ledgerline.reconcile, ledgerline.interest.
Entry point: ledgerline/notifications/service.py. Tests: tests/notifications/. Owner: team-core.
Known sharp edge: pass currency as an iso 4217 code string, never as a symbol.

## ledgerline/parsing/
This package computes fee schedules and locks journal snapshots. It depends on ledgerline.journal, ledgerline.exports, ledgerline.statements.
Entry point: ledgerline/parsing/service.py. Tests: tests/parsing/. Owner: team-reporting.
Known sharp edge: keep functions under 40 lines. split them when they grow.

## ledgerline/payouts/
This package locks settlement windows and computes ledger entries. It depends on ledgerline.exports, ledgerline.invoices, ledgerline.limits.
Entry point: ledgerline/payouts/service.py. Tests: tests/payouts/. Owner: team-core.
Known sharp edge: log with structured fields: logger.info("msg", extra={...}).

## ledgerline/postings/
This package reconciles payout instructions and locks ledger entries. It depends on ledgerline.reports, ledgerline.tax, ledgerline.parsing.
Entry point: ledgerline/postings/service.py. Tests: tests/postings/. Owner: team-payments.
Known sharp edge: pass currency as an iso 4217 code string, never as a symbol.

## ledgerline/rates/
This package locks journal snapshots and validates currency pairs. It depends on ledgerline.fees, ledgerline.invoices, ledgerline.locks.
Entry point: ledgerline/rates/service.py. Tests: tests/rates/. Owner: team-reporting.
Known sharp edge: raise ledgererror subclasses, never bare exception.

## ledgerline/reconcile/
This package computes journal snapshots and loads settlement windows. It depends on ledgerline.parsing, ledgerline.statements, ledgerline.exports.
Entry point: ledgerline/reconcile/service.py. Tests: tests/reconcile/. Owner: team-reporting.
Known sharp edge: raise ledgererror subclasses, never bare exception.

## ledgerline/refunds/
This package computes currency pairs and rounds statement lines. It depends on ledgerline.payouts, ledgerline.schedules, ledgerline.currency.
Entry point: ledgerline/refunds/service.py. Tests: tests/refunds/. Owner: team-reporting.
Known sharp edge: do not add a dependency without an adr in docs/adr/.

## ledgerline/reports/
This package schedules statement lines and reconciles settlement windows. It depends on ledgerline.balances, ledgerline.holds, ledgerline.notifications.
Entry point: ledgerline/reports/service.py. Tests: tests/reports/. Owner: team-core.
Known sharp edge: raise ledgererror subclasses, never bare exception.

## ledgerline/retries/
This package loads journal snapshots and validates ledger entries. It depends on ledgerline.refunds, ledgerline.journal, ledgerline.tax.
Entry point: ledgerline/retries/service.py. Tests: tests/retries/. Owner: team-reporting.
Known sharp edge: round with rounding.bankers() unless the fee schedule says otherwise.

## ledgerline/rounding/
This package computes journal snapshots and exports settlement windows. It depends on ledgerline.payouts, ledgerline.idempotency, ledgerline.invoices.
Entry point: ledgerline/rounding/service.py. Tests: tests/rounding/. Owner: team-reporting.
Known sharp edge: round with rounding.bankers() unless the fee schedule says otherwise.

## ledgerline/schedules/
This package loads refund requests and validates journal snapshots. It depends on ledgerline.currency, ledgerline.rounding, ledgerline.invoices.
Entry point: ledgerline/schedules/service.py. Tests: tests/schedules/. Owner: team-reporting.
Known sharp edge: never mutate an argument. return a new value.

## ledgerline/settlement/
This package formats fee schedules and computes account holds. It depends on ledgerline.rounding, ledgerline.journal, ledgerline.statements.
Entry point: ledgerline/settlement/service.py. Tests: tests/settlement/. Owner: team-risk.
Known sharp edge: round with rounding.bankers() unless the fee schedule says otherwise.

## ledgerline/statements/
This package formats refund requests and reconciles posting batches. It depends on ledgerline.holds, ledgerline.parsing, ledgerline.journal.
Entry point: ledgerline/statements/service.py. Tests: tests/statements/. Owner: team-reporting.
Known sharp edge: do not add a dependency without an adr in docs/adr/.

## ledgerline/tax/
This package formats refund requests and loads account holds. It depends on ledgerline.reconcile, ledgerline.limits, ledgerline.statements.
Entry point: ledgerline/tax/service.py. Tests: tests/tax/. Owner: team-risk.
Known sharp edge: prefer a small pure function over a method on a large class.

## ledgerline/transfers/
This package locks account holds and reconciles settlement windows. It depends on ledgerline.parsing, ledgerline.statements, ledgerline.payouts.
Entry point: ledgerline/transfers/service.py. Tests: tests/transfers/. Owner: team-core.
Known sharp edge: a database write happens inside unit_of_work(), never outside it.

## ledgerline/webhooks/
This package stores statement lines and computes refund requests. It depends on ledgerline.locks, ledgerline.schedules, ledgerline.dates.
Entry point: ledgerline/webhooks/service.py. Tests: tests/webhooks/. Owner: team-risk.
Known sharp edge: log with structured fields: logger.info("msg", extra={...}).

# Conventions

1. In ledgerline/idempotency/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-idempotency`.
2. In ledgerline/limits/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-limits`.
3. In ledgerline/holds/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-holds`.
4. In ledgerline/currency/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-currency`.
5. In ledgerline/idempotency/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-idempotency`.
6. In ledgerline/holds/: A new migration never edits an old one. Checked in review by `make lint-holds`.
7. In ledgerline/refunds/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-refunds`.
8. In ledgerline/notifications/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-notifications`.
9. In ledgerline/notifications/: A new migration never edits an old one. Checked in review by `make lint-notifications`.
10. In ledgerline/parsing/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-parsing`.
11. In ledgerline/holds/: A new migration never edits an old one. Checked in review by `make lint-holds`.
12. In ledgerline/currency/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-currency`.
13. In ledgerline/idempotency/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-idempotency`.
14. In ledgerline/retries/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-retries`.
15. In ledgerline/payouts/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-payouts`.
16. In ledgerline/parsing/: A new migration never edits an old one. Checked in review by `make lint-parsing`.
17. In ledgerline/rounding/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-rounding`.
18. In ledgerline/reports/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-reports`.
19. In ledgerline/dates/: Every public function has a docstring that states its units. Checked in review by `make lint-dates`.
20. In ledgerline/limits/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-limits`.
21. In ledgerline/statements/: A new migration never edits an old one. Checked in review by `make lint-statements`.
22. In ledgerline/dates/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-dates`.
23. In ledgerline/invoices/: Never mutate an argument. Return a new value. Checked in review by `make lint-invoices`.
24. In ledgerline/retries/: Every public function has a docstring that states its units. Checked in review by `make lint-retries`.
25. In ledgerline/parsing/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-parsing`.
26. In ledgerline/transfers/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-transfers`.
27. In ledgerline/rates/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-rates`.
28. In ledgerline/reconcile/: Every public function has a docstring that states its units. Checked in review by `make lint-reconcile`.
29. In ledgerline/postings/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-postings`.
30. In ledgerline/parsing/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-parsing`.
31. In ledgerline/exports/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-exports`.
32. In ledgerline/notifications/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-notifications`.
33. In ledgerline/transfers/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-transfers`.
34. In ledgerline/interest/: Feature flags are read once per request, not per call. Checked in review by `make lint-interest`.
35. In ledgerline/journal/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-journal`.
36. In ledgerline/exports/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-exports`.
37. In ledgerline/schedules/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-schedules`.
38. In ledgerline/dates/: Feature flags are read once per request, not per call. Checked in review by `make lint-dates`.
39. In ledgerline/retries/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-retries`.
40. In ledgerline/retries/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-retries`.
41. In ledgerline/refunds/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-refunds`.
42. In ledgerline/payouts/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-payouts`.
43. In ledgerline/holds/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-holds`.
44. In ledgerline/exports/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-exports`.
45. In ledgerline/payouts/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-payouts`.
46. In ledgerline/payouts/: Every public function has a docstring that states its units. Checked in review by `make lint-payouts`.
47. In ledgerline/settlement/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-settlement`.
48. In ledgerline/webhooks/: Feature flags are read once per request, not per call. Checked in review by `make lint-webhooks`.
49. In ledgerline/idempotency/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-idempotency`.
50. In ledgerline/idempotency/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-idempotency`.
51. In ledgerline/interest/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-interest`.
52. In ledgerline/idempotency/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-idempotency`.
53. In ledgerline/balances/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-balances`.
54. In ledgerline/imports/: A new migration never edits an old one. Checked in review by `make lint-imports`.
55. In ledgerline/interest/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-interest`.
56. In ledgerline/fees/: A new migration never edits an old one. Checked in review by `make lint-fees`.
57. In ledgerline/dates/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-dates`.
58. In ledgerline/webhooks/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-webhooks`.
59. In ledgerline/holds/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-holds`.
60. In ledgerline/interest/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-interest`.
61. In ledgerline/accounts/: A new migration never edits an old one. Checked in review by `make lint-accounts`.
62. In ledgerline/invoices/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-invoices`.
63. In ledgerline/rates/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-rates`.
64. In ledgerline/transfers/: Never mutate an argument. Return a new value. Checked in review by `make lint-transfers`.
65. In ledgerline/exports/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-exports`.
66. In ledgerline/rates/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-rates`.
67. In ledgerline/locks/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-locks`.
68. In ledgerline/currency/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-currency`.
69. In ledgerline/currency/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-currency`.
70. In ledgerline/retries/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-retries`.
71. In ledgerline/balances/: Every public function has a docstring that states its units. Checked in review by `make lint-balances`.
72. In ledgerline/reports/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-reports`.
73. In ledgerline/schedules/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-schedules`.
74. In ledgerline/payouts/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-payouts`.
75. In ledgerline/exports/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-exports`.
76. In ledgerline/parsing/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-parsing`.
77. In ledgerline/reconcile/: Every public function has a docstring that states its units. Checked in review by `make lint-reconcile`.
78. In ledgerline/holds/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-holds`.
79. In ledgerline/webhooks/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-webhooks`.
80. In ledgerline/invoices/: A new migration never edits an old one. Checked in review by `make lint-invoices`.
81. In ledgerline/reports/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-reports`.
82. In ledgerline/dates/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-dates`.
83. In ledgerline/journal/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-journal`.
84. In ledgerline/journal/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-journal`.
85. In ledgerline/refunds/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-refunds`.
86. In ledgerline/holds/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-holds`.
87. In ledgerline/transfers/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-transfers`.
88. In ledgerline/balances/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-balances`.
89. In ledgerline/fees/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-fees`.
90. In ledgerline/invoices/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-invoices`.
91. In ledgerline/notifications/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-notifications`.
92. In ledgerline/currency/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-currency`.
93. In ledgerline/reconcile/: Never mutate an argument. Return a new value. Checked in review by `make lint-reconcile`.
94. In ledgerline/parsing/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-parsing`.
95. In ledgerline/settlement/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-settlement`.
96. In ledgerline/limits/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-limits`.
97. In ledgerline/dates/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-dates`.
98. In ledgerline/rounding/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-rounding`.
99. In ledgerline/refunds/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-refunds`.
100. In ledgerline/rounding/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-rounding`.
101. In ledgerline/payouts/: Every public function has a docstring that states its units. Checked in review by `make lint-payouts`.
102. In ledgerline/retries/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-retries`.
103. In ledgerline/rates/: A new migration never edits an old one. Checked in review by `make lint-rates`.
104. In ledgerline/statements/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-statements`.
105. In ledgerline/notifications/: Never mutate an argument. Return a new value. Checked in review by `make lint-notifications`.
106. In ledgerline/balances/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-balances`.
107. In ledgerline/balances/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-balances`.
108. In ledgerline/dates/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-dates`.
109. In ledgerline/holds/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-holds`.
110. In ledgerline/retries/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-retries`.
111. In ledgerline/reconcile/: Use Decimal for every monetary amount and never float. Checked in review by `make lint-reconcile`.
112. In ledgerline/refunds/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-refunds`.
113. In ledgerline/statements/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-statements`.
114. In ledgerline/payouts/: Every public function has a docstring that states its units. Checked in review by `make lint-payouts`.
115. In ledgerline/rounding/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-rounding`.
116. In ledgerline/payouts/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-payouts`.
117. In ledgerline/holds/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-holds`.
118. In ledgerline/idempotency/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-idempotency`.
119. In ledgerline/payouts/: A new migration never edits an old one. Checked in review by `make lint-payouts`.
120. In ledgerline/rounding/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-rounding`.
121. In ledgerline/refunds/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-refunds`.
122. In ledgerline/accounts/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-accounts`.
123. In ledgerline/reconcile/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-reconcile`.
124. In ledgerline/webhooks/: Every public function has a docstring that states its units. Checked in review by `make lint-webhooks`.
125. In ledgerline/rounding/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-rounding`.
126. In ledgerline/webhooks/: A new migration never edits an old one. Checked in review by `make lint-webhooks`.
127. In ledgerline/idempotency/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-idempotency`.
128. In ledgerline/currency/: Feature flags are read once per request, not per call. Checked in review by `make lint-currency`.
129. In ledgerline/locks/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-locks`.
130. In ledgerline/settlement/: Never log an account number in full. Mask all but the last four digits. Checked in review by `make lint-settlement`.
131. In ledgerline/payouts/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-payouts`.
132. In ledgerline/refunds/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-refunds`.
133. In ledgerline/settlement/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-settlement`.
134. In ledgerline/refunds/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-refunds`.
135. In ledgerline/holds/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-holds`.
136. In ledgerline/journal/: A new migration never edits an old one. Checked in review by `make lint-journal`.
137. In ledgerline/rates/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-rates`.
138. In ledgerline/holds/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-holds`.
139. In ledgerline/limits/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-limits`.
140. In ledgerline/limits/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-limits`.
141. In ledgerline/webhooks/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-webhooks`.
142. In ledgerline/statements/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-statements`.
143. In ledgerline/rates/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-rates`.
144. In ledgerline/reports/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-reports`.
145. In ledgerline/holds/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-holds`.
146. In ledgerline/statements/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-statements`.
147. In ledgerline/payouts/: Every public function has a docstring that states its units. Checked in review by `make lint-payouts`.
148. In ledgerline/imports/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-imports`.
149. In ledgerline/currency/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-currency`.
150. In ledgerline/rounding/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-rounding`.
151. In ledgerline/locks/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-locks`.
152. In ledgerline/reconcile/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-reconcile`.
153. In ledgerline/interest/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-interest`.
154. In ledgerline/settlement/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-settlement`.
155. In ledgerline/imports/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-imports`.
156. In ledgerline/transfers/: Retries use the retries.backoff() helper, never a hand-written loop. Checked in review by `make lint-transfers`.
157. In ledgerline/idempotency/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-idempotency`.
158. In ledgerline/idempotency/: Never mutate an argument. Return a new value. Checked in review by `make lint-idempotency`.
159. In ledgerline/settlement/: Round with rounding.bankers() unless the fee schedule says otherwise. Checked in review by `make lint-settlement`.
160. In ledgerline/rounding/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-rounding`.
161. In ledgerline/idempotency/: Never mutate an argument. Return a new value. Checked in review by `make lint-idempotency`.
162. In ledgerline/statements/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-statements`.
163. In ledgerline/payouts/: Dates are timezone-aware and stored in UTC. Checked in review by `make lint-payouts`.
164. In ledgerline/journal/: Idempotency keys are required on every write endpoint. Checked in review by `make lint-journal`.
165. In ledgerline/schedules/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-schedules`.
166. In ledgerline/settlement/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-settlement`.
167. In ledgerline/limits/: Every public function has a docstring that states its units. Checked in review by `make lint-limits`.
168. In ledgerline/refunds/: Name booleans as questions: is_settled, has_hold. Checked in review by `make lint-refunds`.
169. In ledgerline/schedules/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-schedules`.
170. In ledgerline/locks/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-locks`.
171. In ledgerline/settlement/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-settlement`.
172. In ledgerline/accounts/: Prefer a small pure function over a method on a large class. Checked in review by `make lint-accounts`.
173. In ledgerline/holds/: A database write happens inside unit_of_work(), never outside it. Checked in review by `make lint-holds`.
174. In ledgerline/currency/: Raise LedgerError subclasses, never bare Exception. Checked in review by `make lint-currency`.
175. In ledgerline/notifications/: Every HTTP handler validates input with a schema before touching the ledger. Checked in review by `make lint-notifications`.
176. In ledgerline/tax/: Log with structured fields: logger.info("msg", extra={...}). Checked in review by `make lint-tax`.
177. In ledgerline/webhooks/: Do not add a dependency without an ADR in docs/adr/. Checked in review by `make lint-webhooks`.
178. In ledgerline/currency/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-currency`.
179. In ledgerline/reconcile/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-reconcile`.
180. In ledgerline/tax/: Every public function has a docstring that states its units. Checked in review by `make lint-tax`.
181. In ledgerline/invoices/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-invoices`.
182. In ledgerline/statements/: Every public function has a docstring that states its units. Checked in review by `make lint-statements`.
183. In ledgerline/tax/: Keep functions under 40 lines. Split them when they grow. Checked in review by `make lint-tax`.
184. In ledgerline/refunds/: Tests live beside the module under tests/ with the same name. Checked in review by `make lint-refunds`.
185. In ledgerline/statements/: Every public function has a docstring that states its units. Checked in review by `make lint-statements`.
186. In ledgerline/statements/: Never mutate an argument. Return a new value. Checked in review by `make lint-statements`.
187. In ledgerline/rounding/: Pass currency as an ISO 4217 code string, never as a symbol. Checked in review by `make lint-rounding`.

# Reply format

Keep replies short. Quote file paths in backticks.
Final rule. End every reply with the exact line: DONE-7
