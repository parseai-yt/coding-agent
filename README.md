# A coding agent in 66 lines

A coding agent is three things: a loop, a tool it can call, and a condition to stop.
That is all `agent.py` is.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python agent.py "what does measure.py do?"
```

It prints the answer, and then it prints the bill.

## What it costs

Measured 2026-09-11 on claude-sonnet-5. Raw runs are in `results/`.

| | Tokens |
|---|---|
| The question on its own, no tools | 16 |
| The same question, with one tool defined | 465 |
| **The tool description alone** | **449** |
| A real question about a repository | 2,913 |

The tool description costs 28 times more than the question it travels with, and the model did not
use it. You pay for every capability you hand it, on every call, whether it is used or not.

For comparison, Claude Code sends 41,940 tokens before you type anything. That is 90 times this.
The difference is not the loop. The loop is the same.

## Reproducing the table

```bash
python measure.py 3        # 3 repeats per config
```

It writes one raw JSON file per API call into `results/`, plus a line in
`results/runs.jsonl`. The published numbers are those files, unedited. The recorded
runs asked about a file in a private repo, so set `AGENT_BENCH_TASK` to a question
about your own and the exact counts will differ - the shape will not.

## Why this exists

It is episode 1 of a series that builds an agent one capability at a time and measures what each
one costs. Nobody publishes those numbers, so we measure them.

ParseAI · https://youtube.com/@parseai
