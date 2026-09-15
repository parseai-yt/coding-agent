# Did the caveman plugin cut the Claude Code bill

The raw files behind the ParseAI video and its two Shorts.
Every number the videos show comes from a file in `measurements/`.

Measured on Claude Code 2.1.270 with Claude Opus 5, 14 and 15 Sep 2026.
Costs are at API list price, rebuilt from token counts and checked against the `total_cost_usd` Claude Code reported.

## The claim

caveman's README says the plugin cuts output tokens by 65%, measured on ten prompts, output tokens per reply.
Its README also says the plugin's rules cost about 1,000 to 1,500 input tokens every turn.

## The numbers

| Claim | Value | Where |
|---|---|---|
| Sessions per condition | 5 normal, 5 with caveman | `raw/off-*.jsonl`, `raw/on-*.jsonl` |
| Output tokens per session, median | 8,355 normal, 6,422 caveman, -23.1% | `facts.json` `derived.output_change_percent` |
| Added to every API call | 3,887 tokens (first-call context 17,150 to 21,037) | `facts.json` `added_context_per_call_tokens` |
| Whole-session cost, median | $0.413 normal, $0.443 caveman, a gap of $0.030 | `facts.json` `cost_usd` |
| Spread inside five identical sessions | $0.046 normal, $0.099 caveman | `facts.json` `cost_usd` |
| Fix turn (tool calls and code) | +30.4%, all 5 caveman fix turns dearer than every normal one | `facts.json` `per_turn` |
| Review turn (a long answer written to you) | -24.9% | `facts.json` `per_turn` |
| Back-to-back pairs | +15.5% (on-0 vs off-0), -10.3% (on-3 vs off-3) | `facts.json` `derived.pair_difference_percent` |
| Tests after each session | pytest 6 passed, 0 failed, all 10 sessions | `raw/*.after.json` |

The gap between the medians is smaller than the spread inside either group, so the bill did not measurably move.

## How it was measured

- `fixture/` is a small project with three failing tests.
- `measure.py` runs one Claude Code process per session with three user turns: fix the failing tests, explain the bugs for a pull request, review the other edge cases.
- It runs a normal session and a caveman session back to back, five times, and writes `raw/<condition>-<n>.jsonl` and `raw/<condition>-<n>.after.json`.
- `analyse.py` computes every number from the raw files and writes `facts.json`. It stops if the cost it rebuilds from tokens differs from Claude Code's own `total_cost_usd` by more than a tenth of a cent.

To reproduce, install Claude Code and the caveman plugin, log in, and run `python3 measure.py`.
It uses your own account.

## What these files do not show

- One project, three turns, five sessions a side. A different session shape can land differently: the plugin was cheaper on the long-answer turn and dearer on the tool-call turn.
- List price only. How a subscription plan counts usage was not tested.
- `rtk` was not tested.
- `raw/pilot-*` are pilot runs with a permissions bug, and `raw/failed-off-2-usage-limit.jsonl` is a session cut off by a usage limit. Neither is counted. off-2 was re-run.

## Cleaned for publishing

Local paths, the operator's own plugin, skill and command lists in each session's init event (the caveman plugin entry is kept), memory paths, plan rate-limit events and a limit reset time were removed.
Every change is counted per file in `measurements/REDACTIONS.json`.
`analyse.py` was re-run on the cleaned files and reproduced every key of `facts.json`.

## Sources quoted in the video

- caveman: https://github.com/JuliusBrussee/caveman
- JetBrains, measuring caveman on SkillsBench: https://blog.jetbrains.com/ai/
- Claude pricing: https://platform.claude.com/docs/en/about-claude/pricing

MIT licence.
ParseAI. I run the thing before you ship it, and show the raw output.
