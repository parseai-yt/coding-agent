#!/usr/bin/env python3
"""Itemise every session's bill from the raw stream files, reconcile it against Claude Code's own total, and
write the derived numbers to the video's facts.json with their formulas.

    python3 compute.py            # prints the tables, writes derived.json beside this file
    python3 compute.py --facts    # also merges them into ../facts.json under "measured"

Prices are the published table, read 2026-09-14 from https://platform.claude.com/docs/en/about-claude/pricing
(USD per million tokens). Claude Code writes its cache with the 1-hour duration, so a cache write is $20, not $12.50:
every session's usage says `ephemeral_1h_input_tokens`, and the reconciliation below only closes at $20.
"""
import argparse, json, pathlib, statistics as st

from run import review_names_discount_order

HERE = pathlib.Path(__file__).parent
RAW = HERE / "raw"

PRICE = {   # input, 5m cache write, 1h cache write, cache read, output. USD per million tokens
    "claude-fable-5-1": {"input": 10.0, "write_5m": 12.5, "write_1h": 20.0, "read": 0.25, "output": 50.0},
    "claude-fable-5":   {"input": 10.0, "write_5m": 12.5, "write_1h": 20.0, "read": 1.00, "output": 50.0},
    "claude-haiku-4-5": {"input": 1.0,  "write_5m": 1.25, "write_1h": 2.0,  "read": 0.10, "output": 5.0},
}
LABEL = {"claude-fable-5-1": "Fable 5.1", "claude-fable-5": "Fable 5"}


def load(tag: str):
    out = []
    for f in sorted(RAW.glob(f"{tag}-claude-*.jsonl")):
        name = f.stem
        events = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        result = [e for e in events if e.get("type") == "result"][-1]
        check = json.loads((RAW / f"{name}.check.json").read_text())
        model = check["model"]
        if check.get("task") == "review":
            # regraded from the saved review with run.py's v2 grader, which the v1 check.json predates
            review = RAW / f"{name}.REVIEW.md"
            text = review.read_text() if review.exists() else ""
            check["success_v1_grader"] = check["success"]
            check["success"] = (review.exists() and check["review_names_truncation"]
                                and review_names_discount_order(text) and check["code_unchanged"])
        mu = result["modelUsage"][model]
        cc = result["usage"].get("cache_creation", {})
        w1h, w5m = cc.get("ephemeral_1h_input_tokens", 0), cc.get("ephemeral_5m_input_tokens", 0)
        p = PRICE[model]
        lines = {
            "input": mu["inputTokens"] * p["input"] / 1e6,
            "cache_write": (w1h * p["write_1h"] + w5m * p["write_5m"]) / 1e6,
            "cache_read": mu["cacheReadInputTokens"] * p["read"] / 1e6,
            "output": mu["outputTokens"] * p["output"] / 1e6,
        }
        other = sum(v["costUSD"] for k, v in result["modelUsage"].items() if k != model)
        computed = sum(lines.values()) + other
        # the context each request re-read: one row per API message, deduplicated by id
        seen, turns = set(), []
        for e in events:
            if e.get("type") == "assistant":
                m = e["message"]
                if m.get("id") in seen:
                    continue
                seen.add(m.get("id"))
                u = m.get("usage", {})
                turns.append({"cache_read": u.get("cache_read_input_tokens", 0),
                              "cache_write": u.get("cache_creation_input_tokens", 0),
                              "input": u.get("input_tokens", 0)})
        out.append({
            "name": name, "model": model, "rep": int(name.rsplit("-r", 1)[1]),
            "success": check["success"], "success_v1_grader": check.get("success_v1_grader"), "num_turns": result.get("num_turns"), "requests": len(turns),
            "tokens": {"input": mu["inputTokens"], "cache_write": mu["cacheCreationInputTokens"],
                       "cache_write_1h": w1h, "cache_write_5m": w5m,
                       "cache_read": mu["cacheReadInputTokens"], "output": mu["outputTokens"],
                       "thinking": mu.get("thinkingTokens", 0)},
            "usd": {k: round(v, 6) for k, v in lines.items()},
            "usd_other_models": round(other, 6),
            "usd_computed": round(computed, 6),
            "usd_claude_code": round(result["total_cost_usd"], 6),
            "reconcile_diff": round(computed - result["total_cost_usd"], 9),
            "turns": turns,
        })
    return out


def reprice(s: dict, model: str) -> float:
    """The same token counts at another model's prices, main-model lines only."""
    p, t = PRICE[model], s["tokens"]
    return (t["input"] * p["input"] + t["cache_write_1h"] * p["write_1h"] + t["cache_write_5m"] * p["write_5m"]
            + t["cache_read"] * p["read"] + t["output"] * p["output"]) / 1e6


def summarise(rows):
    by = {}
    for r in rows:
        by.setdefault(r["model"], []).append(r)
    summ = {}
    for m, rs in by.items():
        def med(f):
            return st.median([f(r) for r in rs])
        def rng(f):
            v = [f(r) for r in rs]
            return [min(v), max(v)]
        summ[m] = {
            "n": len(rs), "successes": sum(r["success"] for r in rs),
            "median_usd": round(med(lambda r: r["usd_claude_code"]), 4),
            "range_usd": [round(x, 4) for x in rng(lambda r: r["usd_claude_code"])],
            "median_tokens": {k: med(lambda r, k=k: r["tokens"][k]) for k in ("input", "cache_write", "cache_read", "output")},
            "range_tokens": {k: rng(lambda r, k=k: r["tokens"][k]) for k in ("input", "cache_write", "cache_read", "output")},
            "median_line_usd": {k: round(med(lambda r, k=k: r["usd"][k]), 4) for k in ("input", "cache_write", "cache_read", "output")},
            "median_requests": med(lambda r: r["requests"]),
            "max_abs_reconcile_diff": max(abs(r["reconcile_diff"]) for r in rs),
        }
    return by, summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="bugfix")
    ap.add_argument("--facts", action="store_true")
    a = ap.parse_args()
    rows = load(a.tag)
    by, summ = summarise(rows)
    for r in sorted(rows, key=lambda r: (r["model"], r["rep"])):
        t, u = r["tokens"], r["usd"]
        print(f"  {r['name']:<30} ok={int(r['success'])} req={r['requests']:>2} in={t['input']:>4} write={t['cache_write']:>6} "
              f"read={t['cache_read']:>7} out={t['output']:>5}  ${u['cache_write']:.4f} ${u['cache_read']:.4f} ${u['output']:.4f}"
              f"  total ${r['usd_claude_code']:.4f} diff {r['reconcile_diff']:+.6f}")
    print(json.dumps(summ, indent=1))
    derived = {"tag": a.tag, "summary": summ, "sessions": rows}

    if "claude-fable-5-1" in summ and "claude-fable-5" in summ:
        n, o = summ["claude-fable-5-1"], summ["claude-fable-5"]
        d = {}
        d["median_cost_change_pct"] = round((n["median_usd"] / o["median_usd"] - 1) * 100, 1)
        d["output_ratio_median"] = round(n["median_tokens"]["output"] / o["median_tokens"]["output"], 2)
        d["cache_read_ratio_median"] = round(n["median_tokens"]["cache_read"] / o["median_tokens"]["cache_read"], 2)
        # spread inside one model, against the gap between models
        d["spread_within_fable_5_1_usd"] = round(n["range_usd"][1] - n["range_usd"][0], 4)
        d["spread_within_fable_5_usd"] = round(o["range_usd"][1] - o["range_usd"][0], 4)
        d["gap_between_medians_usd"] = round(n["median_usd"] - o["median_usd"], 4)
        # the same Fable 5 sessions, re-priced at Fable 5.1's table: what the price cut alone does
        f5 = by["claude-fable-5"]
        d["fable5_sessions_repriced_at_5_1_median_usd"] = round(st.median([reprice(s, "claude-fable-5-1") for s in f5]), 4)
        d["fable5_sessions_at_own_price_main_model_median_usd"] = round(st.median([reprice(s, "claude-fable-5") for s in f5]), 4)
        d["price_cut_alone_saving_pct"] = round((d["fable5_sessions_repriced_at_5_1_median_usd"] /
                                                 d["fable5_sessions_at_own_price_main_model_median_usd"] - 1) * 100, 1)
        # break-even: 5.1 saves $0.75 per million cache-read tokens, and costs $50 per million extra output tokens.
        # With output k times higher, 5.1 is cheaper only when cache_read * 0.75 > (k - 1) * output_5 * 50
        # i.e. cache_read / output_5 > (k - 1) * 50 / 0.75
        k = d["output_ratio_median"]
        d["breakeven_formula"] = "cache_read_tokens / output_tokens_on_fable_5 > (k - 1) x 50 / 0.75, k = output ratio"
        d["breakeven_reads_per_output_token_at_k_1_7"] = round((1.7 - 1) * 50 / 0.75, 1)
        d["breakeven_reads_per_output_token_at_measured_k"] = round(max(k - 1, 0) * 50 / 0.75, 1) if k > 1 else None
        d["session_reads_per_output_token_fable_5_median"] = round(st.median(
            [s["tokens"]["cache_read"] / s["tokens"]["output"] for s in f5]), 1)
        derived["comparison"] = d
        print(json.dumps(d, indent=1))

    (HERE / f"derived-{a.tag}.json").write_text(json.dumps(derived, indent=1))
    print(f"\n  wrote derived-{a.tag}.json")


if __name__ == "__main__":
    main()
