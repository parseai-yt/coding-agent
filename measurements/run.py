#!/usr/bin/env python3
"""Send the inputs to a local Ollama and write every raw response to disk.

    python3 build_inputs.py            # once
    python3 run.py arrive              # A: the same prompt at four num_ctx sizes, prompt_eval_count and /api/ps memory
    python3 run.py rule3               # B: "quote Rule 3" 10 times at 4096 and 10 at 32768
    python3 run.py session             # C: a replayed agent session, 10 times at 16384 and 10 at 32768
    python3 run.py tier                # D: a second server on :11435 that sees under 23 GiB of VRAM, OpenAI endpoint, no num_ctx
    python3 derive.py                  # every number, from raw/, into ../facts.json

Rig: Ollama 0.20.2, Apple M3 Max 36 GB, qwen2.5-coder:14b Q4_K_M, default sampling (temperature 0.8).
Server log lines for each run are copied from ~/.ollama/logs/server.log into raw/, by timestamp window.
"""
import json, os, pathlib, re, subprocess, sys, time, urllib.request
from datetime import datetime

HERE = pathlib.Path(__file__).parent
RAW = HERE / "raw"
IN = HERE / "inputs"
MODEL = "qwen2.5-coder:14b"
MAIN = "http://127.0.0.1:11434"
SIDE = "http://127.0.0.1:11435"
LOG = pathlib.Path.home() / ".ollama/logs/server.log"
REPEATS = 10


def post(base: str, path: str, body: dict, timeout: int = 1200) -> tuple[int, dict]:
    req = urllib.request.Request(base + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read())


def ps(base: str) -> list[dict]:
    with urllib.request.urlopen(base + "/api/ps", timeout=30) as r:
        return json.loads(r.read())["models"]


def unload(base: str) -> None:
    post(base, "/api/generate", {"model": MODEL, "keep_alive": 0})


def system() -> str:
    return (IN / "system-prompt.md").read_text()


def log_since(t0: str) -> list[str]:
    """Server log lines at or after an ISO minute-second stamp, truncation and context lines only."""
    keep = re.compile(r"truncating|default_num_ctx|requested context|num_ctx|level=WARN|level=ERROR")
    out = []
    for line in LOG.read_text(errors="replace").splitlines():
        m = re.match(r"time=(\S+)", line)
        if m and m.group(1)[:19] >= t0 and keep.search(line):
            out.append(line)
    return out


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")[:19]


def save(exp: str, name: str, record: dict) -> None:
    d = RAW / exp
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(record, indent=1))


def chat(ctx: int, messages: list[dict], predict: int, tools: list | None = None) -> dict:
    body = {"model": MODEL, "stream": False, "messages": messages, "options": {"num_ctx": ctx, "num_predict": predict}}
    if tools:
        body["tools"] = tools
    t = time.time()
    status, d = post(MAIN, "/api/chat", body)
    return {"request": {"endpoint": "/api/chat", "num_ctx": ctx, "num_predict": predict,
                        "messages": [{"role": m["role"], "chars": len(m.get("content", ""))} for m in messages]},
            "http_status": status, "seconds": round(time.time() - t, 2), "response": d}


TASK = "Say hello in one sentence."
RULE3 = "Quote Rule 3 of your operating rules, word for word. Nothing else."


def arrive() -> None:
    t0 = now()
    for ctx in (4096, 8192, 16384, 32768):
        rec = chat(ctx, [{"role": "system", "content": system()}, {"role": "user", "content": TASK}], 60)
        rec["ps"] = ps(MAIN)
        save("arrive", f"ctx{ctx}", rec)
        print(f"  arrive {ctx:>6}  prompt_eval_count {rec['response']['prompt_eval_count']:>6}  "
              f"size {rec['ps'][0]['size'] / 2**30:.2f} GiB", flush=True)
    (RAW / "arrive" / "server-log.txt").write_text("\n".join(log_since(t0)) + "\n")


def rule3() -> None:
    t0 = now()
    for ctx in (4096, 32768):
        for i in range(1, REPEATS + 1):
            rec = chat(ctx, [{"role": "system", "content": system()}, {"role": "user", "content": RULE3}], 80)
            save("rule3", f"ctx{ctx}-{i:02d}", rec)
            print(f"  rule3 {ctx:>6} #{i:02d}  {rec['response']['message']['content'][:90]!r}", flush=True)
    (RAW / "rule3" / "server-log.txt").write_text("\n".join(log_since(t0)) + "\n")


def session_messages() -> list[dict]:
    files = {n: (IN / "files" / n).read_text() for n in ("dates.py", "parsing.py", "statements.py")}

    def call(n: str) -> dict:
        return {"role": "assistant", "content": "",
                "tool_calls": [{"function": {"name": "read_file", "arguments": {"path": f"ledgerline/{n}"}}}]}

    def result(n: str) -> dict:
        return {"role": "tool", "tool_name": "read_file", "content": files[n]}

    return [{"role": "system", "content": system()},
            {"role": "user", "content": "tests/dates/test_windows.py::test_january_window fails: January settlements "
                                        "get February's window. Find the bug and fix it."},
            call("dates.py"), result("dates.py"), call("parsing.py"), result("parsing.py"),
            call("statements.py"), result("statements.py"),
            {"role": "assistant", "content": "I found the cause. Shall I apply the fix?"},
            {"role": "user", "content": "Yes, apply the fix."}]


def session() -> None:
    t0 = now()
    tools = json.loads((IN / "tools.json").read_text())
    for ctx in (16384, 32768):
        for i in range(1, REPEATS + 1):
            rec = chat(ctx, session_messages(), 200, tools)
            save("session", f"ctx{ctx}-{i:02d}", rec)
            print(f"  session {ctx:>6} #{i:02d}  pec {rec['response']['prompt_eval_count']}  "
                  f"{rec['response']['message']['content'][:90]!r}", flush=True)
    (RAW / "session" / "server-log.txt").write_text("\n".join(log_since(t0)) + "\n")


def side_server(env_extra: dict, logname: str) -> subprocess.Popen:
    env = {**os.environ, "OLLAMA_HOST": "127.0.0.1:11435", **env_extra}
    f = open(RAW / "tier" / logname, "w")
    p = subprocess.Popen(["ollama", "serve"], env=env, stdout=f, stderr=subprocess.STDOUT)
    for _ in range(60):
        try:
            urllib.request.urlopen(SIDE + "/api/version", timeout=2)
            return p
        except OSError:
            time.sleep(1)
    p.terminate()
    sys.exit("side server did not start")


def openai_chat(base: str) -> dict:
    body = {"model": MODEL, "max_tokens": 40,
            "messages": [{"role": "system", "content": system()}, {"role": "user", "content": TASK}]}
    t = time.time()
    status, d = post(base, "/v1/chat/completions", body)
    return {"request": {"endpoint": "/v1/chat/completions", "num_ctx": "not sent, the OpenAI format has no such field"},
            "http_status": status, "seconds": round(time.time() - t, 2), "response": d}


def tier() -> None:
    """A machine with under 23 GiB of GPU memory, simulated by reserving 6 GiB with OLLAMA_GPU_OVERHEAD.

    The server's own tier switch (server/routes.go, v0.20.2) then picks the default. Nothing else is changed.
    """
    (RAW / "tier").mkdir(parents=True, exist_ok=True)
    unload(MAIN)
    six_gib = str(6 * 2**30)
    for name, extra in (("default", {"OLLAMA_GPU_OVERHEAD": six_gib}),
                        ("context16k", {"OLLAMA_GPU_OVERHEAD": six_gib, "OLLAMA_CONTEXT_LENGTH": "16384"})):
        p = side_server(extra, f"server-{name}.log")
        try:
            rec = openai_chat(SIDE)
            rec["env"] = extra
            rec["ps"] = ps(SIDE)
            save("tier", name, rec)
            print(f"  tier {name:<11} prompt_tokens {rec['response']['usage']['prompt_tokens']}", flush=True)
            unload(SIDE)
        finally:
            p.terminate()
            p.wait(timeout=30)


def dropped() -> None:
    """Which messages the 16,384 window removed. chatPrompt drops whole messages from the front and keeps the system
    prompt, so the session without its first three messages (the bug report, the first read_file call and dates.py)
    should read exactly as many tokens as the cut session did. Sent at 32,768, where nothing is cut."""
    tools = json.loads((IN / "tools.json").read_text())
    m = session_messages()
    rec = chat(32768, [m[0]] + m[4:], 1, tools)
    rec["removed"] = ["user: bug report", "assistant: read_file dates.py", "tool: dates.py"]
    save("session-check", "without-first-three", rec)
    print(f"  dropped  prompt_eval_count {rec['response']['prompt_eval_count']}", flush=True)


def machine() -> None:
    """This Mac's own tier line, from the running Ollama app's server logs, copied as it was written."""
    d = RAW / "machine"
    d.mkdir(parents=True, exist_ok=True)
    logs = sorted((LOG.parent).glob("server*.log"))
    keep = [l for f in logs for l in f.read_text(errors="replace").splitlines() if "vram-based default context" in l]
    (d / "server-start.txt").write_text("\n".join(keep) + "\n")
    print(f"  machine  {len(keep)} tier lines", flush=True)


if __name__ == "__main__":
    steps = {"arrive": arrive, "rule3": rule3, "session": session, "tier": tier, "dropped": dropped, "machine": machine}
    for s in sys.argv[1:] or steps:
        print(f"{s} ...", flush=True)
        steps[s]()
