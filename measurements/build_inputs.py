#!/usr/bin/env python3
"""Write the inputs every run sends, deterministically, so a viewer can rebuild them byte for byte.

    python3 build_inputs.py

inputs/system-prompt.md   a 35 KB agent-style system prompt for a made-up repo, "ledgerline".
                          Its FIRST rule and its LAST line are the two canaries the runs look for.
inputs/tools.json         three tools in Ollama's native format
inputs/files/*.py         three source files an agent session reads, the first one with a real bug

The prompt is synthetic and says so. What matters to the test is its size and where the two rules sit.
"""
import json, pathlib, random

HERE = pathlib.Path(__file__).parent
OUT = HERE / "inputs"

FIRST_RULE = "Rule 1. Begin every reply with the tag [HERON] on its own line."
LAST_RULE = "Final rule. End every reply with the exact line: DONE-7"
TARGET_BYTES = 35_000

MODULES = ["accounts", "balances", "currency", "dates", "exports", "fees", "holds", "idempotency", "imports",
           "interest", "invoices", "journal", "limits", "locks", "notifications", "parsing", "payouts", "postings",
           "rates", "reconcile", "refunds", "reports", "retries", "rounding", "schedules", "settlement", "statements",
           "tax", "transfers", "webhooks"]
VERBS = ["validates", "computes", "stores", "loads", "formats", "reconciles", "schedules", "rounds", "exports", "locks"]
NOUNS = ["ledger entries", "posting batches", "currency pairs", "settlement windows", "refund requests",
         "payout instructions", "account holds", "statement lines", "fee schedules", "journal snapshots"]
CONVENTIONS = [
    "Use Decimal for every monetary amount and never float.",
    "Pass currency as an ISO 4217 code string, never as a symbol.",
    "Every public function has a docstring that states its units.",
    "Raise LedgerError subclasses, never bare Exception.",
    "Keep functions under 40 lines. Split them when they grow.",
    "Name booleans as questions: is_settled, has_hold.",
    "Dates are timezone-aware and stored in UTC.",
    "Never mutate an argument. Return a new value.",
    "A database write happens inside unit_of_work(), never outside it.",
    "Log with structured fields: logger.info(\"msg\", extra={...}).",
    "Never log an account number in full. Mask all but the last four digits.",
    "Tests live beside the module under tests/ with the same name.",
    "A new migration never edits an old one.",
    "Retries use the retries.backoff() helper, never a hand-written loop.",
    "Every HTTP handler validates input with a schema before touching the ledger.",
    "Idempotency keys are required on every write endpoint.",
    "Round with rounding.bankers() unless the fee schedule says otherwise.",
    "Feature flags are read once per request, not per call.",
    "Do not add a dependency without an ADR in docs/adr/.",
    "Prefer a small pure function over a method on a large class.",
]


def section_rules() -> str:
    lines = ["# Operating rules", "", FIRST_RULE,
             "Rule 2. You are the coding agent for the ledgerline repository. Work only inside it.",
             "Rule 3. Read a file before you edit it, and never read the same file twice in one session.",
             "Rule 4. Make the smallest change that fixes the problem.",
             "Rule 5. Run the tests after every edit and report the result.",
             "Rule 6. Never touch files under migrations/ without being asked.",
             "Rule 7. Never print or read secrets, .env files or key files.",
             "Rule 8. If a request is ambiguous, ask one question before acting.", ""]
    return "\n".join(lines)


def section_modules(rng: random.Random) -> str:
    out = ["# Repository map", ""]
    for m in MODULES:
        v1, v2 = rng.sample(VERBS, 2)
        n1, n2 = rng.sample(NOUNS, 2)
        deps = ", ".join(f"ledgerline.{d}" for d in rng.sample([x for x in MODULES if x != m], 3))
        out += [f"## ledgerline/{m}/",
                f"This package {v1} {n1} and {v2} {n2}. It depends on {deps}.",
                f"Entry point: ledgerline/{m}/service.py. Tests: tests/{m}/. Owner: team-{rng.choice(['core', 'payments', 'risk', 'reporting'])}.",
                f"Known sharp edge: {rng.choice(CONVENTIONS).lower()}", ""]
    return "\n".join(out)


def section_conventions(rng: random.Random, n: int) -> str:
    out = ["# Conventions", ""]
    for i in range(1, n + 1):
        m = rng.choice(MODULES)
        c = rng.choice(CONVENTIONS)
        out.append(f"{i}. In ledgerline/{m}/: {c} Checked in review by `make lint-{m}`.")
    return "\n".join(out + [""])


def build_prompt() -> str:
    rng = random.Random(8)
    head = section_rules() + "\n" + section_modules(rng) + "\n"
    tail = "\n# Reply format\n\nKeep replies short. Quote file paths in backticks.\n" + LAST_RULE + "\n"
    n = 1
    while True:
        body = section_conventions(random.Random(8), n)
        if len((head + body + tail).encode()) >= TARGET_BYTES:
            return head + body + tail
        n += 1


TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a file from the repository.",
     "parameters": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string", "description": "Path from the repo root"}}}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Replace one exact string in a file.",
     "parameters": {"type": "object", "required": ["path", "old", "new"], "properties": {
         "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "run_tests", "description": "Run the test suite for one package.",
     "parameters": {"type": "object", "required": ["package"], "properties": {"package": {"type": "string"}}}}},
]


def py_file(name: str, fns: int, bug: bool, seed: int) -> str:
    rng = random.Random(seed)
    out = [f'"""ledgerline/{name}.py - helpers used by the settlement and statement jobs."""',
           "from datetime import date, datetime, timezone", "from decimal import Decimal", "", ""]
    if bug:
        out += ["def month_index(d: date) -> int:",
                '    """Zero-based month of the year, used to index SETTLEMENT_WINDOWS."""',
                "    return d.month  # BUG: should be d.month - 1, January reads February's window", "", ""]
    for i in range(fns):
        noun = rng.choice(["entry", "batch", "window", "hold", "payout", "line", "fee", "refund"])
        verb = rng.choice(["normalise", "validate", "summarise", "split", "merge", "round", "shift", "label"])
        out += [f"def {verb}_{noun}_{i}(items: list[dict], cutoff: datetime) -> list[dict]:",
                f'    """{verb.capitalize()} each {noun} before the cutoff. Amounts are Decimal, times are UTC."""',
                "    result = []",
                "    for item in items:",
                "        when = item[\"at\"].astimezone(timezone.utc)",
                "        if when >= cutoff:",
                "            continue",
                f"        amount = Decimal(item[\"amount\"]).quantize(Decimal(\"0.01\"))",
                f"        result.append({{**item, \"amount\": amount, \"{noun}_step\": {i}}})",
                "    return result", "", ""]
    return "\n".join(out)


if __name__ == "__main__":
    (OUT / "files").mkdir(parents=True, exist_ok=True)
    p = build_prompt()
    (OUT / "system-prompt.md").write_text(p)
    (OUT / "tools.json").write_text(json.dumps(TOOLS, indent=1))
    (OUT / "files" / "dates.py").write_text(py_file("dates", 26, True, 1))
    (OUT / "files" / "parsing.py").write_text(py_file("parsing", 26, False, 2))
    (OUT / "files" / "statements.py").write_text(py_file("statements", 26, False, 3))
    lines = p.splitlines()
    print(f"system-prompt.md  {len(p.encode()):,} bytes  {len(lines)} lines")
    print(f"  first rule on line {lines.index(FIRST_RULE) + 1}: {FIRST_RULE}")
    print(f"  last rule on line  {lines.index(LAST_RULE) + 1}: {LAST_RULE}")
    for f in sorted((OUT / "files").iterdir()):
        print(f"files/{f.name}  {f.stat().st_size:,} bytes")
