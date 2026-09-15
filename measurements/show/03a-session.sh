#!/bin/sh
# Long-form claim 7: tokens sent per window, the check that the three oldest messages are what went, and every WARN or ERROR line. Run from the video folder.
echo "# raw/session: tokens the model read, per window"
jq -s -r 'group_by(.request.num_ctx)[] | "window \(.[0].request.num_ctx): \(map(.response.prompt_eval_count) | unique | join(", "))"' measurements/raw/session/*.json
echo "# raw/session-check: without the first three messages"
jq -r '"removed: \(.removed | join(", "))" , "read: \(.response.prompt_eval_count)"' measurements/raw/session-check/without-first-three.json | fold -s -w 84
echo "# WARN or ERROR lines in the server log"
grep -c 'level=WARN\|level=ERROR' measurements/raw/session/server-log.txt
