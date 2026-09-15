#!/usr/bin/env python3
"""What does one real coding-agent session cost on Claude Fable 5.1, against Claude Fable 5?

The claim (Latent Space AINews, 2026-09-02, summarising Artificial Analysis): Fable 5.1 cut cache reads
75% to $0.25 per million tokens, but "uses ~1.7x output tokens", for "a total net per-task cost increase
of 20%" against Fable 5, on the Artificial Analysis Intelligence Index at max effort.

This runs the same small bug-fix task, in a throwaway copy of `fixture/`, through the local Claude Code CLI
on both models, interleaved so neither model gets the earlier or later minutes of the run. Every stream
event goes to disk. After each session the copy's own tests, a hidden test the agent never saw, and a hash
of the test files decide whether the session succeeded, because a cheaper session that fails is not cheaper.

    python3 run.py --repeats 5                 # both models, 5 sessions each
    python3 run.py --repeats 1 --models claude-fable-5-1 --tag pilot
    python3 run.py --repeats 5 --task review --tag review    # the second shape

Nothing runs inside the parseai repo: every session runs in a fresh temp directory.
"""
import argparse, difflib, hashlib, json, pathlib, shutil, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).parent
FIXTURE = HERE / "fixture"
RAW = HERE / "raw"

PROMPT = (
    "Some tests in this repo are failing. Run them with `python3 -m unittest`. "
    "Find the root cause of each failure and fix the code, not the tests. "
    "The rules the code must follow are in README.md. "
    "Run the tests again until they all pass, then tell me in two sentences what you changed."
)
TOOLS = "Read,Edit,Write,Glob,Grep,Bash(python3 -m unittest*),Bash(python3 -m unittest)"

# The second session shape: a review that reads little and writes a lot, the kind of headless run a CI job makes.
# Success is judged on the file it writes: it must exist and name both real defects.
REVIEW_PROMPT = (
    "Review the code in invoices/ against the rules in README.md. "
    "Write your findings to REVIEW.md, most serious first, each with the file, the line, why it is wrong, "
    "and the fix. Do not change any code."
)

HIDDEN_TEST = '''import unittest
from invoices import Invoice
from invoices.money import to_cents

class Hidden(unittest.TestCase):
    def test_discount_then_tax_with_rounding(self):
        inv = Invoice(tax_rate=7.5, discount_rate=15).add("chair", 129.99, 2)
        # 25998 - 15% (3899.7 -> 3900) = 22098, tax 7.5% (1657.35 -> 1657) = 23755
        self.assertEqual(inv.total(), 23755)

    def test_other_bad_float(self):
        self.assertEqual(to_cents(0.29), 29)
        self.assertEqual(to_cents(4.35), 435)
'''


def review_names_discount_order(text: str) -> bool:
    """Grader v2, 2026-09-14. v1 required the word "before" and marked a correct Fable 5 review a failure: it wrote
    "Tax is computed on the undiscounted subtotal" and "the discount to be applied first". Read by eye, then widened."""
    t = text.lower()
    return "discount" in t and "tax" in t and any(w in t for w in ("before", "first", "undiscounted", "discounted subtotal"))


def tree_hash(root: pathlib.Path, sub: str) -> str:
    h = hashlib.sha256()
    for p in sorted((root / sub).rglob("*.py")):
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def code_diff(before: pathlib.Path, after: pathlib.Path) -> str:
    out = []
    for p in sorted((before / "invoices").rglob("*.py")):
        rel = p.relative_to(before)
        q = after / rel
        a = p.read_text().splitlines(keepends=True)
        b = q.read_text().splitlines(keepends=True) if q.exists() else []
        out += difflib.unified_diff(a, b, f"a/{rel}", f"b/{rel}")
    return "".join(out)


def session(model: str, name: str, task: str = "bugfix") -> dict:
    work = pathlib.Path(tempfile.mkdtemp(prefix="l9-session-"))
    repo = work / "repo"
    shutil.copytree(FIXTURE, repo, ignore=shutil.ignore_patterns("__pycache__"))
    tests_before = tree_hash(repo, "tests")
    cmd = ["claude", "-p", PROMPT if task == "bugfix" else REVIEW_PROMPT, "--output-format", "stream-json", "--verbose",
           "--model", model, "--safe-mode", "--no-session-persistence",
           "--permission-mode", "acceptEdits", "--permission-prompts", "none",
           "--allowedTools", TOOLS, "--max-budget-usd", "2"]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    wall = time.time() - t0
    (RAW / f"{name}.jsonl").write_text(p.stdout)
    if p.stderr.strip():
        (RAW / f"{name}.stderr.txt").write_text(p.stderr)

    for c in repo.rglob("__pycache__"):
        shutil.rmtree(c, ignore_errors=True)
    visible = subprocess.run([sys.executable, "-m", "unittest"], cwd=repo, capture_output=True, text=True)
    (repo / "tests" / "test_hidden.py").write_text(HIDDEN_TEST)
    hidden = subprocess.run([sys.executable, "-m", "unittest", "tests.test_hidden"], cwd=repo,
                            capture_output=True, text=True)
    (repo / "tests" / "test_hidden.py").unlink()
    tests_after = tree_hash(repo, "tests")
    (RAW / f"{name}.diff").write_text(code_diff(FIXTURE, repo))

    review = repo / "REVIEW.md"
    rtext = review.read_text().lower() if review.exists() else ""
    if review.exists():
        (RAW / f"{name}.REVIEW.md").write_text(review.read_text())
    check = {
        "task": task,
        "review_written": review.exists(),
        "review_names_truncation": any(w in rtext for w in ("truncat", "int(amount")),
        "review_names_discount_order": review_names_discount_order(rtext),
        "code_unchanged": code_diff(FIXTURE, repo) == "",
        "name": name, "model": model, "exit_code": p.returncode, "wall_seconds": round(wall, 1),
        "visible_tests_pass": visible.returncode == 0,
        "visible_tests_tail": visible.stderr.strip().splitlines()[-1] if visible.stderr.strip() else "",
        "hidden_test_pass": hidden.returncode == 0,
        "hidden_test_tail": hidden.stderr.strip().splitlines()[-1] if hidden.stderr.strip() else "",
        "tests_unchanged": tests_before == tests_after,
    }
    if task == "bugfix":
        check["success"] = check["visible_tests_pass"] and check["hidden_test_pass"] and check["tests_unchanged"]
    else:
        check["success"] = (check["review_written"] and check["review_names_truncation"]
                            and check["review_names_discount_order"] and check["code_unchanged"])
    (RAW / f"{name}.check.json").write_text(json.dumps(check, indent=1))
    shutil.rmtree(work, ignore_errors=True)
    return check


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--models", default="claude-fable-5-1,claude-fable-5")
    ap.add_argument("--tag", default="run")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--task", choices=["bugfix", "review"], default="bugfix")
    a = ap.parse_args()
    RAW.mkdir(exist_ok=True)
    models = a.models.split(",")
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = RAW / f"{a.tag}-meta.json"
    meta.write_text(json.dumps({"cli_version": version, "task": a.task, "prompt": PROMPT if a.task == "bugfix" else REVIEW_PROMPT, "allowed_tools": TOOLS,
                                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "models": models, "repeats": a.repeats}, indent=1))
    for rep in range(a.start, a.start + a.repeats):
        order = models if rep % 2 else list(reversed(models))   # alternate who goes first
        for m in order:
            name = f"{a.tag}-{m}-r{rep}"
            c = session(m, name, a.task)
            print(f"  {name:<40} success={c['success']} exit={c['exit_code']} {c['wall_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
