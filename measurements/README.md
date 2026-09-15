# What a Claude Code session costs on Claude Fable 5.1

Every raw file behind the ParseAI video "Claude Fable 5.1 cost me 19% less, then 23% more".
Measured 2026-09-14 on Claude Code 2.1.270, `claude -p --safe-mode`, default effort.

## Run it yourself

```bash
python3 run.py --repeats 6 --tag bugfix              # the bug fix, both models, interleaved
python3 run.py --repeats 5 --task review --tag review
python3 facts.py                                     # every derived number, with its formula
```

Each session runs in a fresh temp copy of `fixture/`, a small Python repo with two real bugs.

## What is here

| File | What it is |
|---|---|
| `run.py` | the harness: one session per model per repeat, every stream event saved, success checked afterwards |
| `fixture/` | the repo the agent works on |
| `raw/*.jsonl` | one Claude Code `stream-json` file per session |
| `raw/*.check.json` | whether the session succeeded: visible tests, a hidden test, test files unchanged, or for a review, both bugs named |
| `raw/*.diff`, `raw/*.REVIEW.md` | what the agent changed, or wrote |
| `raw/limit-hit/` | three sessions that hit a usage limit. Excluded from every figure |
| `compute.py` | itemises each bill (input, cache write, cache read, output) and reconciles it with Claude Code's own `total_cost_usd` |
| `bill.py`, `requests.py`, `totals.py`, `lines.py`, `shapes.py` | the commands shown in the video |
| `facts.py` | writes `facts.json`, every number the video uses |

## Prices

From https://platform.claude.com/docs/en/about-claude/pricing, read 2026-09-14, USD per million tokens.
Claude Code writes its cache for one hour, so a cache write is $20.

| | input | cache write (1h) | cache read | output |
|---|---|---|---|---|
| Fable 5 | $10 | $20 | $1.00 | $50 |
| Fable 5.1 | $10 | $20 | $0.25 | $50 |

## Limits

One small repo, two jobs, 22 sessions, default effort, list prices.
A subscription is billed differently.
The review result is less certain than the bug fix result: one Fable 5 review cost $0.7558.
