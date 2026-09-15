#!/usr/bin/env python3
"""Every number the video uses, computed from raw/<cond>-<rep>.jsonl and written to ../facts.json.

Nothing here is typed except the list prices, and those are checked: the Opus 5 cost this script
rebuilds from token counts must match the costUSD Claude Code itself reported, per session, to a
tenth of a cent, or the script stops.

What one session is: three user turns in one Claude Code process (measure.py). A "call" is one
API request inside a turn. Claude Code prints one `result` line per turn, with that turn's token
usage and the session's running total_cost_usd.

    python3 analyse.py            prints the tables and writes ../facts.json
"""
import json
import pathlib
import statistics as st
import sys

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
FACTS = HERE.parent / "facts.json"

# USD per million tokens, Claude Opus 5, https://platform.claude.com/docs/en/about-claude/pricing (read 2026-09-14).
# Cache read is 0.1x input, a 5-minute cache write 1.25x, a 1-hour cache write 2x.
RATE = {"input": 5.00, "output": 25.00, "cache_read": 0.50, "write_5m": 6.25, "write_1h": 10.00}
TURNS = ["fix", "explain", "review"]


def load(label: str) -> dict:
    lines = [json.loads(l) for l in (RAW / f"{label}.jsonl").open()]
    results = [m for m in lines if m.get("type") == "result"]
    if len(results) != 3 or any(r.get("is_error") for r in results):
        sys.exit(f"{label}: {len(results)} result lines or an errored turn, expected 3 clean turns")
    after = json.loads((RAW / f"{label}.after.json").read_text())

    # the first API call of the session: everything the model is sent before it has done anything
    first = next(m for m in lines if m.get("type") == "assistant")["message"]["usage"]
    first_ctx = first["input_tokens"] + first["cache_creation_input_tokens"] + first["cache_read_input_tokens"]

    # API calls per turn = distinct assistant message ids before that turn's result line. NOT num_turns: that field read
    # 6 to 8 on the fix turn while the result's own usage summed over only 3 to 6 distinct messages, exactly (checked on
    # off-0 and on-1), so num_turns counts something other than requests. The first script said "seven calls" from it.
    calls_per_turn, seen = [], set()
    for m in lines:
        if m.get("type") == "assistant":
            seen.add(m["message"]["id"])
        elif m.get("type") == "result":
            calls_per_turn.append(len(seen))
            seen = set()

    turns, prev_cost = [], 0.0
    for name, r, n_calls in zip(TURNS, results, calls_per_turn):
        u = r["usage"]
        cc = u.get("cache_creation", {})
        t = {
            "turn": name,
            "calls": n_calls,
            "input": u["input_tokens"],
            "cache_read": u["cache_read_input_tokens"],
            "write_5m": cc.get("ephemeral_5m_input_tokens", 0),
            "write_1h": cc.get("ephemeral_1h_input_tokens", 0),
            "output": u["output_tokens"],
            "thinking": u.get("output_tokens_details", {}).get("thinking_tokens", 0),
            "cost_usd": round(r["total_cost_usd"] - prev_cost, 6),
        }
        if t["write_5m"] + t["write_1h"] != u["cache_creation_input_tokens"]:
            sys.exit(f"{label} {name}: cache writes do not add up")
        t["visible_output"] = t["output"] - t["thinking"]
        prev_cost = r["total_cost_usd"]
        turns.append(t)

    final = results[-1]
    opus = {k: v for k, v in final["modelUsage"].items() if k.startswith("claude-opus")}
    other = sum(v["costUSD"] for k, v in final["modelUsage"].items() if not k.startswith("claude-opus"))
    if len(opus) != 1:
        sys.exit(f"{label}: expected one Opus model, got {list(final['modelUsage'])}")
    opus_reported = next(iter(opus.values()))["costUSD"]

    parts = {k: sum(t[k] for t in turns) * RATE[k] / 1e6 for k in RATE}
    rebuilt = sum(parts.values())
    if abs(rebuilt - opus_reported) > 0.001:
        sys.exit(f"{label}: rebuilt Opus cost {rebuilt:.5f} != reported {opus_reported:.5f}. The rates are wrong")

    return {
        "label": label, "turns": turns, "first_call_context": first_ctx,
        "cost_usd": round(final["total_cost_usd"], 6), "opus_cost_usd": round(opus_reported, 6),
        "other_model_cost_usd": round(other, 6),
        "cost_by_type_usd": {k: round(v, 6) for k, v in parts.items()},
        "tests_after": after["tests_after"], "tests_exit": after["tests_exit"],
        "calls": sum(t["calls"] for t in turns),
        "output": sum(t["output"] for t in turns), "thinking": sum(t["thinking"] for t in turns),
        "visible_output": sum(t["visible_output"] for t in turns),
        "cache_read": sum(t["cache_read"] for t in turns),
        "cache_write": sum(t["write_5m"] + t["write_1h"] for t in turns),
    }


def spread(xs):
    return {"median": st.median(xs), "min": min(xs), "max": max(xs), "spread": max(xs) - min(xs), "values": xs}


def main() -> None:
    reps = sorted({p.stem.split("-")[1] for p in RAW.glob("off-*.jsonl")}, key=int)
    reps = [r for r in reps if (RAW / f"on-{r}.jsonl").exists() and (RAW / f"on-{r}.after.json").exists()]
    S = {c: [load(f"{c}-{r}") for r in reps] for c in ("off", "on")}
    n = len(reps)

    out = {"_what": "Every number long-006 and shorts-w03 draw or speak. Written by measurements/analyse.py from "
                    "measurements/raw/. Only prose fields are edited by hand.",
           "run": json.loads((RAW / "meta-from-0.json").read_text()),
           "rates_usd_per_million_opus5": RATE,
           "rates_source": "https://platform.claude.com/docs/en/about-claude/pricing, read 2026-09-14. Checked: rebuilt from "
                           "token counts, every session matches the costUSD Claude Code reported to within $0.001",
           "repeats_per_condition": n}

    print(f"\n{n} sessions per condition\n")
    for key, fmt in [("cost_usd", "{:.4f}"), ("first_call_context", "{:,}"), ("calls", "{}"),
                     ("output", "{:,}"), ("thinking", "{:,}"), ("visible_output", "{:,}"),
                     ("cache_read", "{:,}"), ("cache_write", "{:,}")]:
        a, b = [s[key] for s in S["off"]], [s[key] for s in S["on"]]
        out[key] = {"off": spread(a), "on": spread(b)}
        print(f"  {key:20s} off " + " ".join(fmt.format(x) for x in a) + "   |  on " + " ".join(fmt.format(x) for x in b))
        print(f"  {'':20s} median off {fmt.format(st.median(a))}  on {fmt.format(st.median(b))}")

    # per turn
    out["per_turn"] = {}
    for i, name in enumerate(TURNS):
        row = {}
        for key in ("cost_usd", "output", "thinking", "visible_output", "cache_read", "calls"):
            a = [s["turns"][i][key] for s in S["off"]]
            b = [s["turns"][i][key] for s in S["on"]]
            row[key] = {"off": spread(a), "on": spread(b)}
        out["per_turn"][name] = row
        print(f"\n  turn {name}: visible output median off {row['visible_output']['off']['median']:,} on {row['visible_output']['on']['median']:,}"
              f" | cost median off {row['cost_usd']['off']['median']:.4f} on {row['cost_usd']['on']['median']:.4f}")

    # sums over all sessions, by type, so the decomposition adds up exactly
    tot = {}
    for c in ("off", "on"):
        by = {k: round(sum(s["cost_by_type_usd"][k] for s in S[c]), 4) for k in RATE}
        by["other_models"] = round(sum(s["other_model_cost_usd"] for s in S[c]), 4)
        by["total"] = round(sum(s["cost_usd"] for s in S[c]), 4)
        tot[c] = by
    out["cost_sum_all_sessions_usd"] = tot
    out["cost_sum_difference_usd"] = {k: round(tot["on"][k] - tot["off"][k], 4) for k in tot["off"]}
    print("\n  summed cost by type, all sessions:")
    for k in tot["off"]:
        print(f"    {k:13s} off {tot['off'][k]:8.4f}  on {tot['on'][k]:8.4f}  diff {tot['on'][k]-tot['off'][k]:+.4f}")

    off_cost, on_cost = out["cost_usd"]["off"], out["cost_usd"]["on"]
    diff = on_cost["median"] - off_cost["median"]
    noise = max(off_cost["spread"], on_cost["spread"])
    out["verdict_cost"] = {
        "median_difference_usd": round(diff, 4),
        "median_difference_percent": round(100 * diff / off_cost["median"], 1),
        "worst_spread_inside_a_condition_usd": round(noise, 4),
        "separable": abs(diff) > noise,
        "_rule": "VALIDATION.md 1: a measured effect must exceed the worst spread inside a condition",
    }
    ctx = out["first_call_context"]
    out["added_context_per_call_tokens"] = ctx["on"]["median"] - ctx["off"]["median"]
    vis = out["visible_output"]
    out["visible_output_change_percent"] = round(100 * (vis["on"]["median"] - vis["off"]["median"]) / vis["off"]["median"], 1)
    off_sum = tot["off"]
    out["output_share_of_bill_off_percent"] = round(100 * off_sum["output"] / off_sum["total"], 1)
    out["tests_passed_after"] = {c: [s["tests_after"] for s in S[c]] for c in S}

    med = lambda key, c: st.median([s[key] for s in S[c]])
    pct = lambda a, b: round(100 * (b - a) / a, 1)
    d = tot["on"]
    o = tot["off"]
    out["derived"] = {
        "_formulas": {
            "output_change_percent": "100 * (median output on - median output off) / median output off",
            "thinking_change_percent": "same, thinking tokens",
            "pair_difference_percent": "100 * (on-k cost - off-k cost) / off-k cost, sessions run back to back",
            "per_session_mean_usd": "summed cost by type over all sessions / repeats",
            "output_vs_cache_read_price": "output rate / cache read rate",
        },
        "output_change_percent": pct(med("output", "off"), med("output", "on")),
        "thinking_change_percent": pct(med("thinking", "off"), med("thinking", "on")),
        "pair_difference_percent": [pct(a["cost_usd"], b["cost_usd"]) for a, b in zip(S["off"], S["on"])],
        "per_session_mean_usd": {
            "output_saved": round((o["output"] - d["output"]) / n, 4),
            "cache_added": round(((d["cache_read"] + d["write_1h"] + d["write_5m"]) -
                                  (o["cache_read"] + o["write_1h"] + o["write_5m"])) / n, 4),
            "net": round((d["total"] - o["total"]) / n, 4),
        },
        "summed_net_change_percent": pct(o["total"], d["total"]),
        "output_vs_cache_read_price": RATE["output"] / RATE["cache_read"],
        "turn_cost_change_percent": {
            t: pct(out["per_turn"][t]["cost_usd"]["off"]["median"], out["per_turn"][t]["cost_usd"]["on"]["median"])
            for t in TURNS},
        "turn_cost_separable": {
            t: (min(out["per_turn"][t]["cost_usd"]["on"]["values"]) > max(out["per_turn"][t]["cost_usd"]["off"]["values"]) or
                max(out["per_turn"][t]["cost_usd"]["on"]["values"]) < min(out["per_turn"][t]["cost_usd"]["off"]["values"]))
            for t in TURNS},
        "turn_visible_output_change_percent": {
            t: pct(out["per_turn"][t]["visible_output"]["off"]["median"], out["per_turn"][t]["visible_output"]["on"]["median"])
            for t in TURNS},
    }
    rv = out["per_turn"]["review"]["cost_usd"]
    out["derived"]["review_on_sessions_below_every_off"] = sum(v < min(rv["off"]["values"]) for v in rv["on"]["values"])
    out["derived"]["_formulas"]["review_on_sessions_below_every_off"] = "count of caveman review turns cheaper than the cheapest normal one"
    out["derived"]["added_share_of_first_call_percent"] = round(100 * out["added_context_per_call_tokens"] / ctx["on"]["median"], 1)
    out["derived"]["_formulas"]["added_share_of_first_call_percent"] = "3,887 / median caveman first-call context"
    cents = lambda usd: round(100 * usd, 1)
    out["derived"]["chart_cents"] = {
        "fix_turn_median_off": cents(out["per_turn"]["fix"]["cost_usd"]["off"]["median"]),
        "fix_turn_median_on": cents(out["per_turn"]["fix"]["cost_usd"]["on"]["median"]),
        "review_turn_median_off": cents(out["per_turn"]["review"]["cost_usd"]["off"]["median"]),
        "review_turn_median_on": cents(out["per_turn"]["review"]["cost_usd"]["on"]["median"]),
        "session_off_min": cents(off_cost["min"]), "session_off_max": cents(off_cost["max"]),
        "session_off_median": cents(off_cost["median"]), "session_on_median": cents(on_cost["median"]),
        "session_on_min": cents(on_cost["min"]), "session_on_max": cents(on_cost["max"]),
        "floor": 37,
    }
    out["derived"]["_formulas"]["chart_cents"] = "the same USD figures x 100, for bar lengths drawn in cents; floor is a chart axis, not a measurement"
    def fix_call_contexts(label: str) -> list[int]:
        """context sent on each API call of the fix turn, distinct messages in order, for the stacked-calls picture"""
        seen, out_ctx = set(), []
        for line in (RAW / f"{label}.jsonl").open():
            m = json.loads(line)
            if m.get("type") == "result":
                return out_ctx
            if m.get("type") == "assistant" and m["message"]["id"] not in seen:
                seen.add(m["message"]["id"])
                u = m["message"]["usage"]
                out_ctx.append(u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"])
        return out_ctx
    out["derived"]["example_fix_call_contexts"] = {"off-1": fix_call_contexts("off-1"), "on-1": fix_call_contexts("on-1")}
    out["derived"]["_formulas"]["example_fix_call_contexts"] = "input + cache writes + cache reads of each distinct API message in the fix turn"
    cache_off = o["cache_read"] + o["write_1h"] + o["write_5m"]
    cache_on = d["cache_read"] + d["write_1h"] + d["write_5m"]
    out["derived"]["summed_meters_usd"] = {"output_off": o["output"], "output_on": d["output"],
                                           "cache_off": round(cache_off, 4), "cache_on": round(cache_on, 4)}
    out["derived"]["cache_share_of_bill_off_percent"] = round(100 * cache_off / o["total"], 1)
    out["derived"]["thinking_share_of_output_off_percent"] = round(100 * med("thinking", "off") / med("output", "off"), 1)
    out["derived"]["_formulas"]["cache_share_of_bill_off_percent"] = "summed normal cache read + write cost / summed normal total"
    out["derived"]["_formulas"]["thinking_share_of_output_off_percent"] = "median normal thinking / median normal output"
    out["derived"]["review_turn_cut_percent"] = -out["derived"]["turn_cost_change_percent"]["review"]
    out["derived"]["_formulas"]["review_turn_cut_percent"] = "the review turn's change written as a cut, a positive number"
    # the fix turn's extra cost, meter by meter, medians over the 5 sessions of each condition, in cents
    def turn_meter(c: str, turn: str, keys: tuple) -> float:
        i = TURNS.index(turn)
        return st.median([sum(s["turns"][i][k] * RATE[k] / 1e6 for k in keys) for s in S[c]]) * 100
    fix = {}
    for name, keys in (("cache", ("cache_read", "write_1h", "write_5m", "input")), ("output", ("output",))):
        fix[name] = {"off": round(turn_meter("off", "fix", keys), 1), "on": round(turn_meter("on", "fix", keys), 1)}
        fix[name]["diff"] = round(fix[name]["on"] - fix[name]["off"], 1)
    out["derived"]["fix_turn_cents_by_meter"] = fix
    out["derived"]["_formulas"]["fix_turn_cents_by_meter"] = "median over 5 sessions of the fix turn's cost on that meter at list price, cents; diff = on - off"
    out["derived"]["other_share_of_bill_off_percent"] = round(100 * (o["input"] + o["other_models"]) / o["total"], 1)
    out["derived"]["_formulas"]["other_share_of_bill_off_percent"] = "normal sessions: uncached input + the small helper model, share of the summed bill"
    README_CLAIM = 65   # caveman README, output tokens saved, figures_from_quoted_sources
    out["derived"]["naive_bill_cut_percent"] = round(README_CLAIM * out["output_share_of_bill_off_percent"] / 100, 1)
    out["derived"]["_formulas"]["naive_bill_cut_percent"] = "65 x output share of the normal bill / 100: what the claim implies"
    out["derived"]["output_if_65_percent_cut"] = round(med("output", "off") * (100 - README_CLAIM) / 100)
    out["derived"]["_formulas"]["output_if_65_percent_cut"] = "median normal session output x 0.35"
    out["derived"]["cache_cost_change_percent"] = pct(o["cache_read"] + o["write_1h"] + o["write_5m"],
                                                     d["cache_read"] + d["write_1h"] + d["write_5m"])
    out["derived"]["output_cost_change_percent"] = pct(o["output"], d["output"])
    out["derived"]["_formulas"]["cache_cost_change_percent"] = "summed cache read + write cost, on against off"
    out["derived"]["_formulas"]["turn_cost_change_percent"] = "100 * (median turn cost on - off) / off, per turn"
    out["derived"]["_formulas"]["turn_cost_separable"] = "every on session of that turn is above, or below, every off session"
    print(f"  derived: {json.dumps(out['derived'], indent=None)[:900]}")
    print(f"\n  VERDICT cost: median diff {diff:+.4f} USD ({out['verdict_cost']['median_difference_percent']:+}%), worst spread {noise:.4f}, separable {abs(diff) > noise}")
    print(f"  added context per call: {out['added_context_per_call_tokens']:,} tokens")
    print(f"  visible output change: {out['visible_output_change_percent']:+}%   output share of bill (off): {out['output_share_of_bill_off_percent']}%")
    print(f"  tests after: {out['tests_passed_after']}")
    # per-session totals only: every per-turn figure stays in raw/, so facts.json does not carry hundreds of numbers
    # that a wrong figure on screen could match by accident
    out["sessions"] = {c: [{k: s[k] for k in ("label", "cost_usd", "first_call_context", "calls", "output",
                                              "visible_output", "tests_after")} for s in S[c]] for c in S}

    existing = json.loads(FACTS.read_text()) if FACTS.exists() else {}
    keep = {k: v for k, v in existing.items() if k in (
        "figures_from_quoted_sources", "spoken_roundings", "packaging_numbers", "chart_axes", "retracted", "_prose")}
    FACTS.write_text(json.dumps({**out, **keep}, indent=1) + "\n")
    print(f"\n  wrote {FACTS}")


if __name__ == "__main__":
    main()
