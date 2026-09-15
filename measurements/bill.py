#!/usr/bin/env python3
"""Print one Claude Code session's bill, line by line, from its raw stream file.

    python3 bill.py raw/bugfix-claude-fable-5-r1.jsonl

Tokens times the published price (USD per million tokens, platform.claude.com pricing, read 2026-09-14),
then Claude Code's own total from the same file, so the arithmetic is checkable on screen.
Run it on your own session: claude -p "..." --output-format stream-json --verbose > my.jsonl
"""
import json, sys

PRICE = {  # input, cache write (1 hour), cache read, output
    "claude-fable-5":   (10, 20, 1.00, 50),
    "claude-fable-5-1": (10, 20, 0.25, 50),
}

if __name__ == "__main__":
    events = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    result = [e for e in events if e.get("type") == "result"][-1]
    model = next(m for m in result["modelUsage"] if m in PRICE)
    u = result["modelUsage"][model]
    p = PRICE[model]
    rows = [("input", u["inputTokens"], p[0]), ("cache write", u["cacheCreationInputTokens"], p[1]),
            ("cache read", u["cacheReadInputTokens"], p[2]), ("output", u["outputTokens"], p[3])]
    print(model)
    total = 0.0
    for name, tokens, price in rows:
        usd = tokens * price / 1e6
        total += usd
        shown = f"${price:.2f}" if price < 10 else f"${price:.0f}"
        print(f"  {name:<12}{tokens:>9,} x {shown:<6}= ${usd:.4f}")
    other = sum(v["costUSD"] for k, v in result["modelUsage"].items() if k != model)
    print(f"  {'haiku calls':<30}= ${other:.4f}")
    print(f"  {'sum':<30}= ${total + other:.4f}")
    print(f"  {'total_cost_usd':<30}= ${result['total_cost_usd']:.4f}")
    print(f"  {'cache reads / output':<30}= {u['cacheReadInputTokens'] / u['outputTokens']:.0f}")
