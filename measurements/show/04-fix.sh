#!/bin/sh
# Long-form claims 9 and 10: a server that sees 22.1 GiB picks 4096, the OpenAI endpoint reads 4096 until OLLAMA_CONTEXT_LENGTH=16384, and loaded size per window. Run from the video folder.
echo "# raw/tier: the server with 6 GiB reserved"
grep -o 'total_vram=.*' measurements/raw/tier/server-default.log
echo "# /v1/chat/completions prompt_tokens, without and with the variable"
jq -r '"\(.env.OLLAMA_CONTEXT_LENGTH // "not set"): prompt_tokens \(.response.usage.prompt_tokens)"' measurements/raw/tier/default.json measurements/raw/tier/context16k.json | sed 's/^/OLLAMA_CONTEXT_LENGTH=/'
echo "# /api/ps, loaded size per window"
jq -r '"num_ctx \(.ps[0].context_length): \(.ps[0].size / 1073741824 * 100 | round / 100) GiB"' measurements/raw/arrive/ctx4096.json measurements/raw/arrive/ctx8192.json measurements/raw/arrive/ctx16384.json measurements/raw/arrive/ctx32768.json
