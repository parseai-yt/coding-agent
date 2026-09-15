#!/bin/sh
# Shorts P2: WARN or ERROR lines during the cut session, then the file each of the 10 cut runs edited first. Run from the video folder.
echo "# warnings, cut session:"
grep -c 'level=WARN\|level=ERROR' measurements/raw/session/server-log.txt
echo "# first file edited,"
echo "# 10 cut runs:"
for f in measurements/raw/session/ctx16384-*.json; do
  jq -r .response.message.content "$f" | grep -o -m1 '"path": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/'
done | sort | uniq -c
