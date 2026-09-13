#!/usr/bin/env python3
"""Two experiments the story now depends on. Claude Code 2.1.269, 2026-09-12.

A. DESCRIPTION LENGTH. The 3-repeat run was inconclusive: the short condition
   measured higher and one condition had 843 tokens of spread where the 20-run
   benchmark had zero. 7 repeats, and the descriptions are pushed much further
   apart so a real effect has room to show.

B. THE 1:1 TRADE. kfirfer reported on issue #14882 that disabling bundled skills
   moves tokens from the Skills row to System tools in an exact 1:1 trade, total
   unchanged, 3 times out of 3. If that reproduces here it is the best thing in
   the video, and it is somebody else's finding checked rather than repeated.
"""
import subprocess, json, tempfile, pathlib, statistics as st

TASK = "Reply with exactly: OK"
HERE = pathlib.Path(__file__).parent
REPEATS = 7
N = 20

SHORT = "Writes CHANGELOG entries from merged PRs. Use for release notes."
LONG = (" ".join([
    "A changelog is a file that records the notable changes in each release of a project.",
    "Keeping one is considered good practice in software engineering because it helps users",
    "of the project understand what has changed between versions, and it helps maintainers",
    "assemble release notes without re-reading the commit history. This skill should be used",
    "whenever the user asks about changelogs, release notes, version history, or wants to",
    "summarise what shipped in a release. It follows the Keep a Changelog convention.",
]))

BODY = "# Changelog\n\nGroup entries under Added, Changed, Fixed, Removed.\nOne line per pull request.\n"


def ctx(root):
    p = subprocess.run(["claude", "-p", TASK, "--output-format", "json"],
                       cwd=root, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        return None
    u = json.loads(p.stdout).get("usage", {})
    return (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)


def run(label, build):
    vals = []
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        build(root)
        for rep in range(REPEATS):
            t = ctx(root)
            if t is None:
                print(f"  {label} rep{rep} FAILED"); continue
            vals.append(t); print(f"  {label:14s} rep{rep}  ctx={t}")
    return vals


def skills(desc):
    def build(root):
        for i in range(1, N + 1):
            d = root / ".claude" / "skills" / f"changelog-{i}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text(f"---\nname: changelog-{i}\ndescription: {desc}\n---\n\n{BODY}")
    return build


def bundled(disabled):
    def build(root):
        c = root / ".claude"; c.mkdir(parents=True, exist_ok=True)
        if disabled:
            (c / "settings.json").write_text(json.dumps({"disableBundledSkills": True}))
    return build


print("=== A. description length, 20 skills either way ===")
a_short = run("short-desc", skills(SHORT))
a_long = run("long-desc", skills(LONG))

print("\n=== B. bundled skills on vs off, no project skills ===")
b_on = run("bundled-on", bundled(False))
b_off = run("bundled-off", bundled(True))

out = {"repeats": REPEATS, "n_skills": N,
       "short_desc_chars": len(SHORT), "long_desc_chars": len(LONG),
       "A_short": a_short, "A_long": a_long, "B_on": b_on, "B_off": b_off}
(HERE / "raw-two.json").write_text(json.dumps(out, indent=1))


def verdict(name, x, y, lx, ly):
    if not x or not y:
        print(f"\n  {name}: a condition failed, no verdict"); return
    mx, my = st.median(x), st.median(y)
    noise = max(max(x) - min(x), max(y) - min(y))
    print(f"\n  {name}")
    print(f"    {lx:12s} median {mx:>8,.0f}   spread {max(x)-min(x)}")
    print(f"    {ly:12s} median {my:>8,.0f}   spread {max(y)-min(y)}")
    print(f"    difference {my-mx:+,.0f}   worst spread {noise}")
    if abs(my - mx) < noise:
        print("    VERDICT: INSIDE THE NOISE. No number may reach the video.")
    else:
        print(f"    VERDICT: separable. {abs(my-mx):,.0f} tokens, {abs(my-mx)/N:.1f} per skill.")


verdict("A. does description length cost?", a_short, a_long, "short", "long")
verdict("B. does disabling bundled skills reduce TOTAL?", b_on, b_off, "bundled on", "bundled off")
