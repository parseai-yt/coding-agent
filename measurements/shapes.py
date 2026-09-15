#!/usr/bin/env python3
"""Both session shapes on one screen: the median session on each model, the change, and the ratio that decides it.

    python3 shapes.py

Dollars are Claude Code's own total_cost_usd. The ratio is cache-read tokens per output token on Fable 5, the median over
that shape's sessions (compute.py).
"""
import statistics as st

from compute import load

if __name__ == "__main__":
    cols = {tag: load(tag) for tag in ("bugfix", "review")}
    med = lambda rows, m, f: st.median(f(r) for r in rows if r["model"] == m)
    print(f"  {'':<10}{'bugfix':>9}{'review':>9}")
    for m, name in (("claude-fable-5", "fable-5"), ("claude-fable-5-1", "fable-5-1")):
        print(f"  {name:<10}" + "".join(f"{'$' + format(med(r, m, lambda x: x['usd_claude_code']), '.4f'):>9}" for r in cols.values()))
    ch = [med(r, "claude-fable-5-1", lambda x: x["usd_claude_code"]) / med(r, "claude-fable-5", lambda x: x["usd_claude_code"]) - 1
          for r in cols.values()]
    print(f"  {'change':<10}" + "".join(f"{format(c * 100, '+.1f') + '%':>9}" for c in ch))
    print(f"  {'reads/out':<10}" + "".join(
        f"{med(r, 'claude-fable-5', lambda x: x['tokens']['cache_read'] / x['tokens']['output']):>9.0f}" for r in cols.values()))
