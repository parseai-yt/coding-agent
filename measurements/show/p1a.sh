#!/bin/sh
# Shorts P1: tokens the model read per window, and the HTTP status, from raw/arrive. Run from the video folder.
echo "# what the model read"
jq -r '"window \(.request.num_ctx): read \(.response.prompt_eval_count)"' measurements/raw/arrive/ctx32768.json measurements/raw/arrive/ctx4096.json
jq -r '"HTTP \(.http_status), error: \(.response.error)"' measurements/raw/arrive/ctx4096.json
