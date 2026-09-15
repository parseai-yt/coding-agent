#!/usr/bin/env python3
"""Write ../facts.json from the raw session files. Every measured number is computed here with its formula beside it.
Prose, sources and quoted figures are held in QUOTED below and copied as they are.

    python3 facts.py

Run it after any change to raw/, compute.py or the price table. Never edit a number in facts.json by hand.
"""
import json, pathlib, statistics as st

from compute import PRICE, load, reprice, summarise

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "facts.json"
F5, F51 = "claude-fable-5", "claude-fable-5-1"

QUOTED = {
    "anthropic_launch_post": {
        "url": "https://www.anthropic.com/claude-fable-and-mythos-5-1", "dated": "2026-09-01", "read": "2026-09-14",
        "words": "Fable 5.1 will cost an estimated 25% less than Fable 5 for typical workloads, wherever usage is billed by token.",
        "reason": "This is because we're reducing our pricing on cache reads. For highly agentic work, the savings will often be much larger - up to approximately 45%.",
        "cost_less_pct": 25, "agentic_up_to_pct": 45,
        "effort_note": "Fable 5.1 defaults to High effort in Claude Code",
    },
    "artificial_analysis_via_latent_space": {
        "url": "https://www.latent.space/p/ainews-claude-fablemythos-51-new", "dated": "2026-09-02", "read": "2026-09-14",
        "words": ["Fable 5 max: lower, so 5.1 is 20% more expensive per task", "reason: Fable 5.1 uses ~1.7x output tokens",
                  "Fallback accounted for ~4% of output tokens across the Intelligence Index"],
        "per_task_more_pct": 20, "output_ratio": 1.7, "fallback_output_pct": 4,
        "measured_against": "Claude Fable 5 at max effort, on the Artificial Analysis Intelligence Index, not a coding-agent session",
    },
    "price_table": {
        "url": "https://platform.claude.com/docs/en/about-claude/pricing", "read": "2026-09-14",
        "usd_per_million_tokens": {"fable_5": PRICE[F5], "fable_5_1": PRICE[F51]},
        "cache_read_cut_pct": 75,
        "cache_read_multiplier": {"fable_5_1": 0.025, "other_models": 0.1},
    },
    "models": {"fable_5": 5, "fable_5_1": 5.1, "claude_code_version": "2.1.270"},
}


def side(rows, model):
    rs = [r for r in rows if r["model"] == model]
    usd = sorted(r["usd_claude_code"] for r in rs)
    return {
        "sessions": len(rs), "passed": sum(r["success"] for r in rs),
        "totals_usd_sorted": usd, "median_usd": round(st.median(usd), 4), "min_usd": usd[0], "max_usd": usd[-1],
        "spread_usd": round(usd[-1] - usd[0], 4),
        "median_tokens": {k: st.median(r["tokens"][k] for r in rs) for k in ("input", "cache_write", "cache_read", "output")},
        "median_line_usd": {k: round(st.median(r["usd"][k] for r in rs), 4) for k in ("input", "cache_write", "cache_read", "output")},
        "median_requests": st.median(r["requests"] for r in rs),
        "median_reads_per_output_token": round(st.median(r["tokens"]["cache_read"] / r["tokens"]["output"] for r in rs), 1),
        "max_abs_reconcile_diff_usd": max(abs(r["reconcile_diff"]) for r in rs),
    }


def shape(tag):
    rows = load(tag)
    a, b = side(rows, F5), side(rows, F51)
    f5 = [r for r in rows if r["model"] == F5]
    out = {
        "fable_5": a, "fable_5_1": b,
        "median_change_pct": round((b["median_usd"] / a["median_usd"] - 1) * 100, 1),
        "_median_change_pct": "(median Fable 5.1 total / median Fable 5 total - 1) x 100",
        "gap_between_medians_usd": round(a["median_usd"] - b["median_usd"], 4),
        "ranges_overlap": b["max_usd"] >= a["min_usd"] if b["median_usd"] < a["median_usd"] else a["max_usd"] >= b["min_usd"],
        "pairs_fable_5_1_dearer": sum(y > x for x in a["totals_usd_sorted"] for y in b["totals_usd_sorted"]),
        "pairs_total": len(a["totals_usd_sorted"]) * len(b["totals_usd_sorted"]),
        "_pairs": "every Fable 5 session against every Fable 5.1 session: how many pairs the Fable 5.1 one cost more",
        "output_ratio": round(b["median_tokens"]["output"] / a["median_tokens"]["output"], 2),
        "_output_ratio": "median Fable 5.1 output tokens / median Fable 5 output tokens",
        "cache_read_line_share_of_fable_5_bill_pct": round(a["median_line_usd"]["cache_read"] / a["median_usd"] * 100, 1),
        "cache_write_line_share_of_fable_5_bill_pct": round(a["median_line_usd"]["cache_write"] / a["median_usd"] * 100, 1),
        "cache_write_line_share_of_fable_5_1_bill_pct": round(b["median_line_usd"]["cache_write"] / b["median_usd"] * 100, 1),
        "output_line_share_of_fable_5_bill_pct": round(a["median_line_usd"]["output"] / a["median_usd"] * 100, 1),
        "cache_read_line_fall_usd": round(a["median_line_usd"]["cache_read"] - b["median_line_usd"]["cache_read"], 4),
        "fable_5_sessions_repriced_at_5_1_change_pct": round(
            (st.median(reprice(s, F51) for s in f5) / st.median(reprice(s, F5) for s in f5) - 1) * 100, 1),
        "_repriced": "Fable 5's own token counts priced at Fable 5.1's table: what the price cut alone does to those sessions",
    }
    return rows, out


if __name__ == "__main__":
    facts = {
        "question": "What does one real Claude Code session cost on Claude Fable 5.1, against Claude Fable 5, itemised?",
        "measured": "2026-09-14", "tool": "Claude Code 2.1.270, claude -p, --safe-mode, default effort",
        "raw": "measurements/raw/*.jsonl, one stream per session, written by measurements/run.py",
        "quoted": QUOTED,
    }
    for tag in ("bugfix", "review"):
        rows, facts[tag] = shape(tag)
    k = QUOTED["artificial_analysis_via_latent_space"]["output_ratio"]
    saved, extra = PRICE[F5]["read"] - PRICE[F51]["read"], PRICE[F51]["output"]
    facts["breakeven"] = {
        "formula": "Fable 5.1 is cheaper when cache_read_tokens x (1.00 - 0.25) > (k - 1) x output_tokens x 50, "
                   "so when cache reads per output token > (k - 1) x 50 / 0.75. Holds reads, writes and input equal, "
                   "and ignores that extra output is written back to the cache on the next request",
        "saving_per_million_cache_reads_usd": saved, "output_price_per_million_usd": extra,
        "k": k, "k_minus_1": round(k - 1, 1),
        "reads_per_output_token_at_1_7x": round((k - 1) * extra / saved, 1),
        "bugfix_k_measured_breakeven": round(max(facts["bugfix"]["output_ratio"] - 1, 0) * extra / saved, 1),
        "review_k_measured_breakeven": round(max(facts["review"]["output_ratio"] - 1, 0) * extra / saved, 1),
    }
    facts["sessions_measured"] = {"bugfix": len(load("bugfix")), "review": len(load("review")),
                                  "total": len(load("bugfix")) + len(load("review"))}
    facts["run_notes"] = [
        "pilot-claude-fable-5-1-r1 is a harness check and is not in any figure",
        "review sessions 5.1-r4, 5.1-r5 and 5-r5 first hit the plan's usage limit (exit 1, under 8s) and were re-run after it reset. "
        "The failed streams are kept in raw/limit-hit/ and are not in any figure. The re-run overwrote review-meta.json with the same prompt",
        "the review grader was widened once, by eye, before any figure was taken: v1 failed a correct Fable 5 review (compute.py)",
        "no fallback model appears in any session: modelUsage lists only claude-fable-5, claude-fable-5-1 and claude-haiku-4-5",
        "notional cost of every session run for this video, pilot, probes and limit-hit runs included: 10.04 USD, over the 8 USD cap",
        "dollars are list price, what an API-billed session pays. These sessions ran on a subscription (apiKeySource none)",
    ]
    # the one session followed through the video: Fable 5, bug fix, run 2 (its bill is the tape in section 3)
    ex = next(r for r in load("bugfix") if r["name"] == "bugfix-claude-fable-5-r2")
    facts["example_session"] = {
        "name": ex["name"], "requests": ex["requests"],
        "reads_per_request": [t["cache_read"] for t in ex["turns"]], "writes_per_request": [t["cache_write"] for t in ex["turns"]],
        "tokens": ex["tokens"], "usd": ex["usd"], "usd_other_models": ex["usd_other_models"], "total_usd": ex["usd_claude_code"],
        "reads_per_output_token": round(ex["tokens"]["cache_read"] / ex["tokens"]["output"], 1),
        "cache_read_line_at_5_1_price_usd": round(ex["tokens"]["cache_read"] * PRICE[F51]["read"] / 1e6, 4),
    }
    b, r = facts["bugfix"], facts["review"]
    facts["spoken_roundings"] = {
        "bugfix_change_19": {"said": 19, "exact": b["median_change_pct"]},
        "review_change_23": {"said": 23, "exact": r["median_change_pct"]},
        "breakeven_47": {"said": 47, "exact": facts["breakeven"]["reads_per_output_token_at_1_7x"]},
        "breakeven_review_29": {"said": 29, "exact": facts["breakeven"]["review_k_measured_breakeven"]},
        "breakeven_bugfix_3": {"said": 3, "exact": facts["breakeven"]["bugfix_k_measured_breakeven"]},
        "bugfix_output_more_5": {"said": 5, "exact": round((b["output_ratio"] - 1) * 100, 1)},
        "review_ratio_20": {"said": 20, "exact": r["fable_5"]["median_reads_per_output_token"]},
        "bugfix_ratio_54": {"said": 54, "exact": b["fable_5"]["median_reads_per_output_token"]},
        "output_more_44": {"said": 44, "exact": round((r["output_ratio"] - 1) * 100, 1)},
        "cache_read_line_11_cents": {"said": 11, "exact_usd": b["fable_5"]["median_line_usd"]["cache_read"]},
        "cache_read_line_2_cents": {"said": 2, "exact_usd": b["fable_5_1"]["median_line_usd"]["cache_read"]},
    }
    facts["packaging_numbers"] = {
        "minus_19": {"shown": -19, "from": "bugfix.median_change_pct", "exact": b["median_change_pct"]},
        "plus_23": {"shown": 23, "from": "review.median_change_pct rounded", "exact": r["median_change_pct"]},
        "cut_75": {"shown": 75, "from": "quoted.price_table.cache_read_cut_pct"},
        "claims": {"cheaper_25": 25, "dearer_20": 20},
    }
    facts["retracted"] = {}
    OUT.write_text(json.dumps(facts, indent=1) + "\n")
    print(json.dumps({t: {k: v for k, v in facts[t].items() if not isinstance(v, dict)} for t in ("bugfix", "review")}, indent=1))
    print(json.dumps(facts["breakeven"], indent=1))
