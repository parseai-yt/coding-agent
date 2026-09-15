#!/bin/sh
# Long-form claims 1 and 2: prompt size, what the model read at each window, and the only trace in the server log. Run from the video folder.
echo "# bytes in the prompt"
wc -c < measurements/inputs/system-prompt.md
echo "# raw/arrive: status, error field, tokens the model read"
jq -c '{num_ctx: .request.num_ctx, http: .http_status, error: .response.error, prompt_eval_count: .response.prompt_eval_count}' measurements/raw/arrive/ctx32768.json measurements/raw/arrive/ctx4096.json
echo "# raw/arrive/server-log.txt"
grep -o 'msg=.*' measurements/raw/arrive/server-log.txt | fold -s -w 84
