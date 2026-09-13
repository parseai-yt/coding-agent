#!/usr/bin/env python3
"""What does an installed Claude Code skill cost before you ever invoke it?

RE-RUN 2026-09-12 on Claude Code 2.1.269. The 2026-09-07 run was on 2.1.260 and
reported 25.1 tokens per skill. Nine patch releases later, the owner approved a
re-measure rather than shipping a number we had not checked on the current build.

The 2026-09-03 version of this took ONE reading per condition and reported a
482-token delta. Run-to-run variance on an identical condition is ~4,000 tokens
(long-004/measurements/raw.json). That delta was inside the noise and should
never have reached a script, let alone a video.

This runs repeats, reports the spread, and states plainly whether the effect is
separable from noise. If it is not, that is the finding and we publish it.
"""
import subprocess, json, tempfile, pathlib, statistics as st, sys

TASK = "Reply with exactly: OK"
COUNTS = [0, 5, 10, 20]
REPEATS = 5
HERE = pathlib.Path(__file__).parent


def make_skill(root, i):
    d = root / ".claude" / "skills" / f"skill-{i}"
    d.mkdir(parents=True, exist_ok=True)
    body = ("Lorem ipsum body content for this skill. " * 60)
    (d / "SKILL.md").write_text(
        f"---\nname: skill-{i}\n"
        f"description: Handles requests of category {i} for the measurement harness.\n"
        f"---\n\n# Skill {i}\n\n{body}\n")
    return len((d / "SKILL.md").read_text())


def context_tokens(root):
    p = subprocess.run(["claude", "-p", TASK, "--output-format", "json"],
                       cwd=root, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        return None
    u = json.loads(p.stdout).get("usage", {})
    return (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)


rows = []
for n in COUNTS:
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        chars = sum(make_skill(root, i) for i in range(1, n + 1))
        for rep in range(REPEATS):
            t = context_tokens(root)
            if t is None:
                print(f"  n={n:2d} rep{rep} FAILED"); continue
            rows.append({"skills": n, "rep": rep, "ctx_tokens": t, "skill_file_chars": chars})
            print(f"  n={n:2d} rep{rep}  ctx={t}")

(HERE / "raw.json").write_text(json.dumps(rows, indent=1))
print("\n  skills   median      min      max    spread")
by = {}
for r in rows:
    by.setdefault(r["skills"], []).append(r["ctx_tokens"])
for n in sorted(by):
    v = by[n]
    print(f"  {n:6d} {st.median(v):8.0f} {min(v):8d} {max(v):8d} {max(v)-min(v):9d}")

if 0 in by and 20 in by:
    d0, d20 = st.median(by[0]), st.median(by[20])
    noise = max(max(v) - min(v) for v in by.values())
    print(f"\n  median delta 0 -> 20 skills : {d20 - d0:.0f} tokens")
    print(f"  worst within-condition spread: {noise:.0f} tokens")
    if abs(d20 - d0) < noise:
        print("  VERDICT: the effect is INSIDE the noise. Not a measurement.")
    else:
        print(f"  VERDICT: separable. ~{(d20-d0)/20:.1f} tokens per skill.")
