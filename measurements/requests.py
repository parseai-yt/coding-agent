#!/usr/bin/env python3
"""One session, request by request: what each request read back from the cache and what it wrote to it.

    python3 requests.py raw/bugfix-claude-fable-5-r2.jsonl

A stream file repeats a message once per content block, so requests are counted by unique message id.
"""
import json, sys

if __name__ == "__main__":
    seen, n = set(), 0
    print(f"  {'request':<9}{'cache read':>12}{'cache write':>13}")
    for line in open(sys.argv[1]):
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("type") != "assistant" or e["message"]["id"] in seen:
            continue
        m = e["message"]
        seen.add(m["id"])
        n += 1
        u = m["usage"]
        print(f"  {n:<9}{u['cache_read_input_tokens']:>12,}{u['cache_creation_input_tokens']:>13,}")
