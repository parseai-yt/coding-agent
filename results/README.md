# Raw runs

One JSON file per API call, exactly as the API returned it. Nothing here is edited.
`runs.jsonl` is one line per logged run, and it is what the README's table is computed from.

| Config | Runs | input_tokens |
|---|---|---|
| `bare` - the prompt, no tools | 3 | 16, 16, 16 |
| `one-tool` - same prompt, `read_file` defined | 3 | 465, 465, 465 |
| `task` - a real question about a repository | 2 | 2912, 2915 |

**There are 9 raw files and 8 lines in `runs.jsonl`.** `bare-r1-20260911T112809Z.json` is a
smoke-test call made before the logged batch started, to check the script worked at all. It
returned 16 input tokens, agreeing with the three that followed. It is kept because deleting a
run after seeing it is how a benchmark starts lying, and it is excluded from the table because
it was not part of the batch.

`input_tokens` is what the API bills as new input, not the character length of the prompt. On
these runs there is no cache, so the two are close. On a long session they are not.
