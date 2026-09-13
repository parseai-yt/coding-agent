# What a Claude Code skill costs before you use it

The raw files behind the ParseAI video and its two Shorts.
Every number the videos show comes from a file in `measurements/`.

Measured on Claude Code 2.1.269, 12 Sep 2026.

## The numbers

| Claim | Value | File |
|---|---|---|
| Context with no skills | 28,202 tokens | `raw.json` |
| Context with 20 skills, one-line descriptions | 28,702 tokens | `raw.json` |
| Cost per skill | 500 / 20 = 25 tokens | `raw.json` |
| Spread inside every condition | 0 tokens, 5 repeats each | `raw.json` |
| 20 skills as a share of the request | 500 / 28,702 = 1.7% | `raw.json` |
| Extra cost of a six-line description over a one-line one | 2,180 / 20 = 109 tokens per skill | `raw-two.json`, keys `A_short` and `A_long` |
| A six-line description in all | 25 + 109 = 134 tokens | `raw.json` and `raw-two.json` |
| Saved by writing it as one line | 109 / 134 = 81% | as above |

## How it was measured

Each run builds a throwaway project, installs N skills into `.claude/skills/`, and sends Claude Code one prompt: `Reply with exactly: OK`.
The context size is `cache_read_input_tokens + cache_creation_input_tokens` from `claude -p --output-format json`.
Nothing else changes between conditions.

- `measure.py` - 0, 5, 10 and 20 skills, 5 repeats each. Writes `raw.json`.
- `measure-two.py` - 20 skills with a 64-character description against 20 with a 511-character one, identical bodies, 7 repeats each. Writes `raw-two.json`.
- `measure-description.py` - an earlier 3-repeat version of the description test. Writes `raw-description.json`.

To reproduce, install Claude Code, log in, and run `python3 measure.py`.
It uses your own account and costs roughly a dollar.
Your numbers will differ by version, because the floor moves.

## What these files do not show

**`raw-two.json` is noisier than `raw.json`.**
The worst spread inside one condition was 1,741 tokens against a 2,180-token effect.
The medians are stable, so 109 is measured, but it is not exact.

**`raw-description.json` was inconclusive, and it is here on purpose.**
With 3 repeats the short description measured higher than the long one, and the spread (843) was larger than the difference (581).
That is why `measure-two.py` exists with more repeats and descriptions pushed further apart.

**The `B_on` and `B_off` keys in `raw-two.json` were not used.**
They test a `disableBundledSkills` setting from a GitHub comment.
The "on" project had no `settings.json` and the "off" project had one, so two things differed.
The setting is also not documented, so the result cannot be attributed to it.

**Skill quality is not measured.**
Every test skill was the same size, and real ones are not.

## A correction

An earlier version of this benchmark reported 48 tokens per skill from a single reading per condition.
Run-to-run variance on an identical project can reach thousands of tokens, so that was never separable from noise.
Re-measured with repeats at four skill counts: 25.1 on Claude Code 2.1.260, then 25.0 on 2.1.269.

## Sources quoted in the video

- Agent Skills docs: https://docs.claude.com/en/docs/agents-and-tools/agent-skills
- Issue #14882, including antmid's report of 148 skills at about 10,000 tokens: https://github.com/anthropics/claude-code/issues/14882

MIT licence.
ParseAI. I run the thing before you ship it, and show the raw output.
