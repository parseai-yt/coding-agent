# What a local Ollama model actually receives

The raw files behind the ParseAI video and its two Shorts.
Every number the videos show comes from a file in `measurements/`.

Measured 15 Sep 2026 on Ollama 0.20.2 with `qwen2.5-coder:14b` (Q4_K_M, trained context 32,768), Apple M3 Max with 36 GB, Ollama's default sampling.

## The claim

One engineer moving 35 KB agent prompts from a frontier API to self-hosted Ollama reported that the prompts "fell apart", and named Ollama's small default context length as a cause.
https://patrickmccanna.net/notes-on-migrating-large-prompts-away-from-anthropic-openai-to-self-hosted-llms/

## The numbers

| Claim | Value | Where |
|---|---|---|
| The agent prompt | 35,051 bytes, 8,476 tokens | `inputs/system-prompt.md`, `raw/arrive/` |
| Read at a 4,096 window | `prompt_eval_count` 4,096, HTTP 200, no error field | `raw/arrive/` |
| Read at a 16,384 or 32,768 window | 8,476 | `raw/arrive/` |
| The only trace of the cut | a `truncating input prompt` warning in the server log | `raw/arrive/server-log.txt` |
| "Quote Rule 3 word for word", 10 runs per window | 10 of 10 quoted it at 32,768, 0 of 10 at 4,096, and all 10 cut replies gave another rule | `raw/rule3/` |
| An agent session, 17,932 tokens, at a 16,384 window | arrived as 14,813 tokens, the three oldest messages dropped, 0 warning lines | `raw/session/`, `raw/session-check/` |
| That session, 10 runs per window | made the fix 9 of 10 whole, 0 of 10 cut, and edited the wrong file (`parsing.py`) in 8 of 10 cut runs | `raw/session/` |
| Memory for the loaded model | 9.05 GiB at 4,096, 16.54 GiB at 32,768 | `raw/arrive/` (from `/api/ps`) |
| A server that sees less GPU memory | with 6 GiB reserved it saw 22.1 GiB and chose 4,096 by default, and `OLLAMA_CONTEXT_LENGTH=16384` read all 8,476 | `raw/tier/` |

`derive.py` computes every number from `raw/` and writes `facts.json`.

## How it was measured

- `build_inputs.py` writes the agent prompt, the tool list and the three source files the session reads.
- `run.py` sends each request to the local Ollama HTTP API at each window and saves the full response with its HTTP status.
- A reply is classified by its text, never by eye: Rule 3's own sentence, or the model's first tool call and whether its edit contains the fix. The rules are at the top of `derive.py`.
- `show/` holds the short scripts the video's terminals run, so each on-screen command can be opened and re-run.

To reproduce, install Ollama and `qwen2.5-coder:14b`, then run `python3 build_inputs.py` once, `python3 run.py arrive`, `python3 run.py rule3` and `python3 run.py session`, and `python3 derive.py`.
`python3 run.py tier` needs a second Ollama server on port 11435 started with `OLLAMA_GPU_OVERHEAD` set, as the docstring in `run.py` describes.
It runs locally and costs nothing.

## What these files do not show

- One model, one machine, ten runs per window.
- The same prompt on a frontier API was not tested. That half of the claim is the engineer's.
- The smaller GPU is simulated by reserving memory on this machine, not measured on a real smaller card.

## Cleaned for publishing

Local paths in two server logs were replaced, counted in `measurements/REDACTIONS.json`.
`derive.py` was re-run on the cleaned files and reproduced every key of `facts.json`.

## Sources

- Ollama: https://github.com/ollama/ollama
- The engineer's notes: https://patrickmccanna.net/notes-on-migrating-large-prompts-away-from-anthropic-openai-to-self-hosted-llms/

MIT licence.
ParseAI. I run the thing before you ship it, and show the raw output.
