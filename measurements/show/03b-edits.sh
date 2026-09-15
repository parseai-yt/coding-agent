#!/bin/sh
# Long-form claim 8: the file each run edited first, and replies carrying the fix, per window. Run from the video folder.
for w in 32768 16384; do
  echo "# window $w, file edited first:"
  for f in measurements/raw/session/ctx$w-*.json; do
    jq -r .response.message.content "$f" | grep -o -m1 '"path": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/'
  done | sort | uniq -c
  echo "  replies with the fix, month - 1: $(grep -l 'month - 1' measurements/raw/session/ctx$w-*.json | wc -l | tr -d ' ')"
done
