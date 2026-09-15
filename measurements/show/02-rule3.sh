#!/bin/sh
# Long-form claims 5 and 6: Rule 3 quoted in full and DONE-7 kept, per window, then all ten cut replies' first text line, verbatim, folded only at spaces. Run from the video folder.
echo "# raw/rule3: replies quoting Rule 3 in full, replies ending DONE-7"
jq -s -r 'group_by(.request.num_ctx)[] | "window \(.[0].request.num_ctx): Rule 3 in full \(map(select(.response.message.content | contains("Read a file before you edit it, and never read the same file twice in one session"))) | length) of \(length), DONE-7 \(map(select(.response.message.content | contains("DONE-7"))) | length)"' measurements/raw/rule3/*.json
echo "# window 4096, all ten replies:"
for f in measurements/raw/rule3/ctx4096-*.json; do
  # a reply longer than the line is shown up to its last whole word, marked with ...
  jq -r '[.response.message.content | split("\n")[] | select(test("^[A-Za-z\">]"))][0]' "$f" | awk '{ if (length($0) <= 84) print; else { s = substr($0, 1, 81); sub(/ [^ ]*$/, "", s); print s " ..." } }'
done
