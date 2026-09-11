#!/usr/bin/env python3
"""Measure the agent in `agent/agent.py`. Every raw response goes to disk.

    python measure.py [repeats]

WHY A SCRIPT
Traceability, the first of the three reasons CLAUDE.md allows. A number that
reaches a video must trace to a raw file. This writes results/ and
reconciles nothing - facts.json is written by hand afterwards, by a reader who
can tell whether the answer was any good.

WHAT IT MEASURES, and why each configuration exists
  bare      no tools at all, trivial prompt   the absolute floor of the API
  one-tool  one tool defined, same prompt     the floor PLUS one JSON schema
  task      one tool, a real repo question    what actual work costs

`one-tool` minus `bare` is the cost of a capability the model never used. That
subtraction is the whole point of the series and it is why both configurations
send the IDENTICAL prompt.

The key comes from the keychain, never from a file and never printed.
"""
import json, os, pathlib, subprocess, sys, datetime, importlib.util

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
LOG = OUT / "runs.jsonl"

spec = importlib.util.spec_from_file_location("ag", HERE / "agent.py")
src = (HERE / "agent.py").read_text().split("def main")[0]
ns = {}
exec(compile(src, "agent.py", "exec"), ns)
TOOLS, MODEL, API = ns["TOOLS"], ns["MODEL"], ns["API"]

TRIVIAL = "Reply with exactly: OK"
# The recorded runs asked this about a file in the ParseAI production repo, which is
# private. The published numbers are that question. Point it at your own file to
# measure yours - the shape holds, the exact token counts will not.
TASK = os.environ.get("AGENT_BENCH_TASK", "what does bench/record.sh do?")


def key() -> str:
    k = subprocess.run(["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"],
                       capture_output=True, text=True).stdout.strip()
    if not k:
        sys.exit("no ANTHROPIC_API_KEY in the keychain")
    return k


def call(messages, tools, k):
    import urllib.request
    body = {"model": MODEL, "max_tokens": 2048, "messages": messages}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())


def run(name, prompt, tools, k, rep):
    """One run. Loops if tools are in play, because a task needs the loop."""
    messages = [{"role": "user", "content": prompt}]
    usage, calls, reads, raw = [], 0, [], []
    while True:
        r = call(messages, tools, k)
        raw.append(r)
        usage.append(r["usage"])
        calls += 1
        if r["stop_reason"] != "tool_use" or not tools:
            break
        messages.append({"role": "assistant", "content": r["content"]})
        results = []
        for b in r["content"]:
            if b["type"] != "tool_use":
                continue
            reads.append(b["input"]["path"])
            results.append({"type": "tool_result", "tool_use_id": b["id"],
                            "content": ns["read_file"](b["input"]["path"])})
        messages.append({"role": "user", "content": results})

    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    rawf = OUT / f"{name}-r{rep}-{stamp}.json"
    rawf.write_text(json.dumps(raw, indent=1))
    tin = sum(u["input_tokens"] + u.get("cache_read_input_tokens", 0)
              + u.get("cache_creation_input_tokens", 0) for u in usage)
    rec = {"at": datetime.datetime.now(datetime.UTC).isoformat(), "config": name, "repeat": rep,
           "prompt": prompt, "tools": len(tools or []), "calls": calls,
           "input_tokens": tin, "output_tokens": sum(u["output_tokens"] for u in usage),
           "files_read": reads, "raw_file": f"results/{rawf.name}"}
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"  {name:10} r{rep}  {calls} call(s)  in {tin:6}  out {rec['output_tokens']:4}"
          + (f"  read {len(reads)}" if reads else ""))
    return rec


def main() -> int:
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    OUT.mkdir(parents=True, exist_ok=True)
    k = key()
    print(f"\n  agent floor benchmark · {MODEL} · {reps} repeat(s)\n")
    for r in range(1, reps + 1):
        run("bare", TRIVIAL, None, k, r)
    for r in range(1, reps + 1):
        run("one-tool", TRIVIAL, TOOLS, k, r)
    for r in range(1, min(reps, 2) + 1):
        run("task", TASK, TOOLS, k, r)
    print(f"\n  raw  {OUT}\n  log  {LOG}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
