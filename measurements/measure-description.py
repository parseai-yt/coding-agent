#!/usr/bin/env python3
"""Does rewriting the DESCRIPTION actually shrink what you pay on every call?

§12 of the script claimed "about ninety tokens to about twenty". That was an
ESTIMATE and law 2 forbids an estimate reaching a viewer as a number. This
measures it instead.

Same harness as measure.py: identical projects, one variable. Here the variable
is the description text, not the skill count. Twenty skills either way, so any
difference is the description and nothing else.

BAD  - what people actually write. Explains the topic to a model that knows it.
GOOD - an index entry. What it does, and when to reach for it.

Cost: 6 runs. The 20-run measure.py cost roughly a dollar, so this is ~30c.
"""
import subprocess, json, tempfile, pathlib, statistics as st

TASK = "Reply with exactly: OK"
N_SKILLS = 20
REPEATS = 3
HERE = pathlib.Path(__file__).parent

BAD = ("A changelog is a file that records the notable changes in each release "
       "of a project. Keeping one is good practice because it helps users "
       "understand what changed and helps maintainers write release notes.")
GOOD = ("Writes CHANGELOG entries from merged pull requests. Use when asked to "
        "update the changelog or prepare release notes.")

BODY = "\n".join([
    "# Changelog", "",
    "Group entries under Added, Changed, Fixed, Removed.",
    "One line per pull request, newest first.",
    "Link the PR number. Mark breaking changes with **BREAKING**.",
    "", "## Example", "- Added: retry budget on the upload path (#412)",
])


def make(root, i, desc):
    d = root / ".claude" / "skills" / f"changelog-{i}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: changelog-{i}\ndescription: {desc}\n---\n\n{BODY}\n")


def ctx(root):
    p = subprocess.run(["claude", "-p", TASK, "--output-format", "json"],
                       cwd=root, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        return None
    u = json.loads(p.stdout).get("usage", {})
    return (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)


rows = []
for name, desc in (("bad", BAD), ("good", GOOD)):
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        for i in range(1, N_SKILLS + 1):
            make(root, i, desc)
        for rep in range(REPEATS):
            t = ctx(root)
            if t is None:
                print(f"  {name} rep{rep} FAILED"); continue
            rows.append({"desc": name, "rep": rep, "ctx_tokens": t, "desc_chars": len(desc)})
            print(f"  {name:4s} rep{rep}  ctx={t}")

(HERE / "raw-description.json").write_text(json.dumps(rows, indent=1))

by = {}
for r in rows:
    by.setdefault(r["desc"], []).append(r["ctx_tokens"])
if "bad" in by and "good" in by:
    b, g = st.median(by["bad"]), st.median(by["good"])
    noise = max(max(v) - min(v) for v in by.values())
    print(f"\n  bad  median {b:,}   spread {max(by['bad'])-min(by['bad'])}")
    print(f"  good median {g:,}   spread {max(by['good'])-min(by['good'])}")
    print(f"  difference over {N_SKILLS} skills: {b-g:.0f} tokens")
    print(f"  per skill: {(b-g)/N_SKILLS:.1f} tokens saved")
    if abs(b - g) < noise:
        print("  VERDICT: INSIDE THE NOISE. Not a measurement. The script must not claim a number.")
    else:
        print(f"  VERDICT: separable. Rewriting the description saves {(b-g)/N_SKILLS:.1f} tokens per skill, per call.")
