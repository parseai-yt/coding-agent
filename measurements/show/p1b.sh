#!/bin/sh
# Shorts P1: three replies to "quote Rule 3" at window 4096, first text line verbatim, folded only at spaces. Run from the video folder.
echo "# window 4096, 3 replies:"
for f in measurements/raw/rule3/ctx4096-01.json measurements/raw/rule3/ctx4096-02.json measurements/raw/rule3/ctx4096-05.json; do
  jq -r '[.response.message.content | split("\n")[] | select(test("^[A-Za-z\">]"))][0]' "$f" | fold -s -w 27
done
