#!/usr/bin/env python3
"""Does the caveman plugin make a whole Claude Code session cheaper?

One variable: the caveman plugin loaded, or not. Everything else is identical.

THE SESSION. A throwaway Python repo (`fixture/`) with three failing tests and three
bugs. Three user turns, sent one after another into ONE Claude Code process through
`--input-format stream-json`, so the plugin's SessionStart hook fires once and its
UserPromptSubmit hook fires on every turn, the way an interactive session runs:

  1. fix      - find why the tests fail and fix them (tool-heavy)
  2. explain  - explain the bugs for a PR description (prose)
  3. review   - list other edge cases, change nothing (prose)

THE PLUGIN. caveman at commit PIN, loaded with `--plugin-dir` for this process only,
which is the Claude Code plugin its README installs with
`claude plugin install caveman@caveman`. One line of its plugin.json is changed:
each hook exports CLAUDE_CONFIG_DIR to a per-run scratch folder, because its hooks
write a mode flag into ~/.claude and nothing here may touch the owner's config.
`plugin-json.diff` is that change, in full. The one-time statusline nudge is marked
as already shown, so every run measures the steady state a user sees from session two.

ISOLATION. `--setting-sources project` and `--strict-mcp-config`: no user settings,
no user CLAUDE.md, no user plugins, no MCP servers, in either condition. The run
directory is a fresh copy of `fixture/` outside any repo, so no ancestor CLAUDE.md loads.

ORDER. Conditions alternate, off then on, so a warm prompt cache or a slow hour
lands on both. Every stdout line is saved to raw/<cond>-<rep>.jsonl. The tests are
run after the session and the result is saved beside it, so a cheaper session that
fixed nothing cannot count as a saving.

    python3 measure.py --pilot         one run per condition, into raw/pilot-*
    python3 measure.py --repeats 5     the experiment

The pilot (raw/pilot-*) is kept and never counted: its tool allowlist refused the test run.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE / "fixture"
RAW = HERE / "raw"
SCRATCH = pathlib.Path(os.environ["PARSEAI_SCRATCH"])
PLUGIN = SCRATCH / "caveman-plugin"
PIN = "15581d14007fd01fb3f132016741962f34936ca2"

TURNS = [
    ("fix", "Some tests in tests/ are failing. Find out why and fix cartcalc/cart.py so they pass. "
            "Run the tests to confirm."),
    ("explain", "Explain what was wrong, bug by bug, so I can paste it into the pull request description."),
    ("review", "Review cartcalc/cart.py for other edge cases that could still produce a wrong total. "
               "Tell me which ones you would test next and why. Do not change any files."),
]

BASE_CMD = [
    "claude", "-p",
    "--input-format", "stream-json",
    "--output-format", "stream-json",
    "--verbose",
    "--setting-sources", "project",
    "--strict-mcp-config",
    "--no-session-persistence",
    "--permission-mode", "acceptEdits",
    "--permission-prompts", "none",
    # The pilot allowed only `python3 -m pytest`, the model ran `python -m pytest` and was refused in
    # both conditions. Read-only shell commands and every spelling of pytest are allowed. Nothing that
    # reaches the network or installs anything is, in either condition.
    "--allowedTools", ",".join([
        "Read", "Edit", "Write", "Glob", "Grep",
        "Bash(python3 -m pytest:*)", "Bash(python -m pytest:*)", "Bash(pytest:*)",
        "Bash(ls:*)", "Bash(cat:*)", "Bash(find:*)", "Bash(head:*)", "Bash(grep:*)", "Bash(sed -n:*)",
    ]),
]


def user_line(text: str) -> str:
    return json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"


def run_session(cond: str, label: str) -> dict:
    run_dir = pathlib.Path(tempfile.mkdtemp(prefix=f"cave-{label}-", dir=SCRATCH / "runs"))
    repo = run_dir / "repo"
    shutil.copytree(FIXTURE, repo)
    env = dict(os.environ)
    cmd = list(BASE_CMD)
    if cond == "on":
        state = run_dir / "caveman-state"
        state.mkdir()
        (state / ".caveman-nudge-shown").write_text("1")
        env["CAVEMAN_STATE_DIR"] = str(state)
        cmd += ["--plugin-dir", str(PLUGIN)]

    out_path = RAW / f"{label}.jsonl"
    started = time.time()
    proc = subprocess.Popen(cmd, cwd=repo, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    results = []
    with out_path.open("w") as out:
        for name, text in TURNS:
            proc.stdin.write(user_line(text))
            proc.stdin.flush()
            while True:
                line = proc.stdout.readline()
                if not line:
                    raise RuntimeError(f"{label}: claude exited during turn {name}: {proc.stderr.read()[-2000:]}")
                out.write(line)
                msg = json.loads(line)
                if msg.get("type") == "result":
                    # off-2's first attempt hit the plan's usage limit mid-session and came back as a result
                    # with is_error and api_error_status 429. Kept as raw/failed-off-2-usage-limit.jsonl, never counted.
                    if msg.get("is_error"):
                        proc.kill()
                        raise RuntimeError(f"{label}: turn {name} errored: {msg.get('api_error_status')} {msg.get('result')}")
                    results.append({"turn": name, "msg": msg})
                    break
        proc.stdin.close()
        for line in proc.stdout:
            out.write(line)
    proc.wait(timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"{label}: claude exit {proc.returncode}: {proc.stderr.read()[-2000:]}")

    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                           cwd=repo, capture_output=True, text=True)
    summary = {
        "label": label, "condition": cond, "seconds": round(time.time() - started, 1),
        "tests_after": tests.stdout.strip().splitlines()[-1] if tests.stdout.strip() else tests.stderr[-300:],
        "tests_exit": tests.returncode,
        "cart_py_after": (repo / "cartcalc" / "cart.py").read_text(),
    }
    (RAW / f"{label}.after.json").write_text(json.dumps(summary, indent=1))
    shutil.rmtree(run_dir)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--repeats", type=int, default=6)
    ap.add_argument("--start", type=int, default=0, help="first repeat index, to resume a stopped sweep")
    args = ap.parse_args()
    if not (PLUGIN / ".claude-plugin" / "plugin.json").exists():
        sys.exit(f"no plugin copy at {PLUGIN}")
    RAW.mkdir(exist_ok=True)
    (SCRATCH / "runs").mkdir(exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = {"claude_code": version, "caveman_commit": PIN, "turns": TURNS, "command": BASE_CMD,
            "plugin_change": "plugin-json.diff", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if args.pilot:
        (RAW / "pilot-meta.json").write_text(json.dumps(meta, indent=1))
        for cond in ("off", "on"):
            s = run_session(cond, f"pilot-{cond}")
            print(cond, s["seconds"], "s", s["tests_after"], flush=True)
        return
    (RAW / f"meta-from-{args.start}.json").write_text(json.dumps(meta, indent=1))
    for rep in range(args.start, args.repeats):
        for cond in ("off", "on"):
            s = run_session(cond, f"{cond}-{rep}")
            print(f"{cond}-{rep}", s["seconds"], "s", s["tests_after"], flush=True)


if __name__ == "__main__":
    main()
