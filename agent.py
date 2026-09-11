#!/usr/bin/env python3
"""A coding agent. The whole thing.

    export ANTHROPIC_API_KEY=...
    python agent/agent.py "what does bench/record.sh do?"

An agent is three things: a LOOP, a TOOL it can call, and a STOP CONDITION.
Everything else a real agent has - more tools, memory, subagents, retries - is
an addition to this. Each one costs tokens, and this series measures them one at
a time. This file is the baseline those measurements are against.

Every token this sends is printed at the end, because the point of the series is
that you can see the bill.
"""
import json, os, sys, urllib.request

MODEL = "claude-sonnet-5"
API = "https://api.anthropic.com/v1/messages"

# THE TOOL. One function, described to the model as JSON schema.
# That schema is sent on every single call, whether it is used or not - which is
# the thing episode 2 measures.
TOOLS = [{
    "name": "read_file",
    "description": "Read a UTF-8 text file from the repository and return its contents.",
    "input_schema": {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "path relative to the repo root"}},
        "required": ["path"],
    },
}]


def read_file(path: str) -> str:
    p = os.path.normpath(path)
    if p.startswith("..") or os.path.isabs(p):
        return f"refused: {path} is outside the repo"
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"no such file: {path}"
    except UnicodeDecodeError:
        return f"not text: {path}"


def call(messages):
    body = json.dumps({"model": MODEL, "max_tokens": 2048,
                       "tools": TOOLS, "messages": messages}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: agent.py '<your question>'")
    messages = [{"role": "user", "content": sys.argv[1]}]
    usage = []

    # THE LOOP.
    while True:
        r = call(messages)
        usage.append(r["usage"])

        # THE STOP CONDITION. The model stops asking for tools.
        if r["stop_reason"] != "tool_use":
            print("\n" + "".join(b["text"] for b in r["content"] if b["type"] == "text"))
            break

        messages.append({"role": "assistant", "content": r["content"]})
        results = []
        for b in r["content"]:
            if b["type"] != "tool_use":
                continue
            print(f"  read_file({b['input']['path']})", file=sys.stderr)
            results.append({"type": "tool_result", "tool_use_id": b["id"],
                            "content": read_file(b["input"]["path"])})
        messages.append({"role": "user", "content": results})

    # THE BILL. Printed every run, because the series is about seeing it.
    tin = sum(u["input_tokens"] + u.get("cache_read_input_tokens", 0)
              + u.get("cache_creation_input_tokens", 0) for u in usage)
    tout = sum(u["output_tokens"] for u in usage)
    print(f"\n  {len(usage)} call(s)  ·  {tin} tokens in  ·  {tout} out", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
