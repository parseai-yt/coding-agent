#!/usr/bin/env python3
"""The median of each bill line, both models side by side, for one session shape.

    python3 lines.py bugfix
    python3 lines.py review

Each line is tokens times the published price, per session, then the median across that model's sessions
(compute.py holds the prices and reconciles every session against Claude Code's own total).
"""
import statistics as st, sys

from compute import load

if __name__ == "__main__":
    rows = load(sys.argv[1])
    models = ("claude-fable-5", "claude-fable-5-1")
    print(f"  {'median line':<13}{'fable-5':>9}{'fable-5-1':>11}")
    for k, name in (("cache_write", "cache write"), ("cache_read", "cache read"), ("output", "output"), ("input", "input")):
        v = [st.median(r["usd"][k] for r in rows if r["model"] == m) for m in models]
        print(f"  {name:<13}{'$' + format(v[0], '.4f'):>9}{'$' + format(v[1], '.4f'):>11}")
    tot = [st.median(r["usd_claude_code"] for r in rows if r["model"] == m) for m in models]
    print(f"  {'session':<13}{'$' + format(tot[0], '.4f'):>9}{'$' + format(tot[1], '.4f'):>11}")
    print(f"  {'change':<13}{format((tot[1] / tot[0] - 1) * 100, '+.1f') + '%':>20}")
