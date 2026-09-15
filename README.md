# What a Claude Code session costs on Claude Fable 5.1

The raw files behind the ParseAI video "Claude Fable 5.1 cost me 19% less, then 23% more" and its two Shorts.
Every number the videos show comes from a file in `measurements/`, and `measurements/README.md` lists each file and how to re-run it.

Measured 14 Sep 2026 on Claude Code 2.1.270, 22 sessions, API list prices.

## The claims

- Anthropic's launch post, 1 Sep 2026: Fable 5.1 "will cost an estimated 25% less than Fable 5 for typical workloads", because cache reads cost less.
- Artificial Analysis, as summarised by Latent Space on 2 Sep 2026: about 1.7 times the output tokens, and about 20% more per task on its own index.

## The numbers

| Job | Fable 5.1 against Fable 5, median session cost | Pairs where Fable 5.1 cost more | Output tokens, Fable 5.1 over Fable 5 | Break-even, cache reads per output token |
|---|---|---|---|---|
| Bug fix | -19.0% | 0 of 36 | 1.05x | 3.3 |
| Code review of the same repo | +22.7% | 20 of 25 | 1.44x | 29.3 |

- Both headlines hold, on different jobs.
- A cache read fell from $1.00 to $0.25 per million tokens, and output stayed $50 per million.
- Fable 5.1 is cheaper when a job reads more cached tokens per output token than its break-even. At Artificial Analysis's 1.7x output the break-even would be 46.7.
- The formulas sit beside every number in the video's `facts.json`, written by `measurements/facts.py`.

## What these files do not show

- One small repo, two jobs, default effort, list prices. A subscription is billed differently.
- The code review result is less certain than the bug fix: its cost ranges overlap between the two models.
- `raw/limit-hit/` holds three sessions stopped by a usage limit. None is in any figure.

## Cleaned for publishing

Plan usage-limit events, their reset times, and the operator's own plugin, skill and command lists in each session's init event were removed.
Every change is counted per file in `measurements/REDACTIONS.json`.
`facts.py` was re-run on the cleaned files and reproduced every key of `facts.json`.

## Sources

- Anthropic, Claude Fable 5.1 and Mythos 5.1: https://www.anthropic.com/claude-fable-and-mythos-5-1
- Latent Space AINews on Fable 5.1: https://www.latent.space/p/ainews-claude-fablemythos-51-new
- Claude pricing: https://platform.claude.com/docs/en/about-claude/pricing

MIT licence.
ParseAI. I run the thing before you ship it, and show the raw output.
