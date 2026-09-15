#!/bin/sh
# Shorts P2: loaded size at windows 4096 and 32768, from /api/ps after each request. Run from the video folder.
echo "# GiB loaded, /api/ps"
jq -r '"window \(.ps[0].context_length): \(.ps[0].size / 1073741824 * 100 | round / 100) GiB"' measurements/raw/arrive/ctx4096.json measurements/raw/arrive/ctx32768.json
