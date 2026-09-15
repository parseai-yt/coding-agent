#!/usr/bin/env python3
"""Every session's total from its raw file, both models side by side, cheapest first.

    python3 totals.py bugfix
    python3 totals.py review

The dollars are Claude Code's own `total_cost_usd`. `passed` is the session's check.json, and for a review it is regraded
with run.py's v2 grader (compute.py says why).
"""
import statistics as st, sys

from compute import load

if __name__ == "__main__":
    tag = sys.argv[1]
    rows = load(tag)
    cols = {m: sorted(r["usd_claude_code"] for r in rows if r["model"] == m) for m in ("claude-fable-5", "claude-fable-5-1")}
    ok = {m: sum(r["success"] for r in rows if r["model"] == m) for m in cols}
    print(f"  {'fable-5':>10}   {'fable-5-1':>10}")
    for a, b in zip(*cols.values()):
        print(f"  {'$' + format(a, '.4f'):>10}   {'$' + format(b, '.4f'):>10}")
    print(f"  {'-' * 10}   {'-' * 10}")
    med = {m: st.median(v) for m, v in cols.items()}
    print(f"  {'$' + format(med['claude-fable-5'], '.4f'):>10}   {'$' + format(med['claude-fable-5-1'], '.4f'):>10}   median")
    print(f"  {str(ok['claude-fable-5']) + '/' + str(len(cols['claude-fable-5'])):>10}   "
          f"{str(ok['claude-fable-5-1']) + '/' + str(len(cols['claude-fable-5-1'])):>10}   passed")
    out = {m: st.median(r["tokens"]["output"] for r in rows if r["model"] == m) for m in cols}
    ratio = {m: st.median(r["tokens"]["cache_read"] / r["tokens"]["output"] for r in rows if r["model"] == m) for m in cols}
    print(f"  {out['claude-fable-5']:>10,.0f}   {out['claude-fable-5-1']:>10,.0f}   median output tokens")
    print(f"  {ratio['claude-fable-5']:>10.0f}   {ratio['claude-fable-5-1']:>10.0f}   cache reads per output token")
    print(f"  cost change {(med['claude-fable-5-1'] / med['claude-fable-5'] - 1) * 100:+.1f}%")
