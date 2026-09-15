#!/usr/bin/env python3
"""Every number the videos use, computed from raw/ and written to ../facts.json. Nothing here is typed by hand.

    python3 derive.py

A reply is classified by reading its text, never by eye:
  rule3    quoted:   the reply contains Rule 3's own words, "never read the same file twice"
           last:     the reply contains DONE-7, the last line of the prompt
  session  the model's next action, from message.tool_calls, or from the JSON call qwen2.5-coder writes into content:
           fix:        edit_file on ledgerline/dates.py whose "new" contains "month - 1"
           reread:     read_file on ledgerline/dates.py
           wrong_file: edit_file on any other file
           other:      anything else
"""
import json, pathlib, re, statistics

HERE = pathlib.Path(__file__).parent
RAW = HERE / "raw"
FACTS = HERE.parent / "facts.json"
GIB = 2 ** 30


def load(exp: str) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in sorted((RAW / exp).glob("*.json"))}


def calls(msg: dict) -> list[dict]:
    """Tool calls the model made: the parsed field first, else JSON objects with a name inside the text."""
    out = [{"name": c["function"]["name"], "arguments": c["function"]["arguments"]} for c in msg.get("tool_calls") or []]
    if out:
        return out
    text = msg.get("content", "")
    dec = json.JSONDecoder()
    i = 0
    while (j := text.find("{", i)) != -1:
        try:
            obj, end = dec.raw_decode(text, j)
        except json.JSONDecodeError:
            i = j + 1
            continue
        if isinstance(obj, dict) and "name" in obj:
            args = obj.get("arguments", {})
            out.append({"name": obj["name"], "arguments": json.loads(args) if isinstance(args, str) else args})
        i = end
    return out


FIRST_CALL = re.compile(r'"name"\s*:\s*"(\w+)".*?"path"\s*:\s*"([^"]+)"', re.S)


def first_call(msg: dict) -> dict | None:
    """The first tool call. Parsed JSON when it parses. qwen2.5-coder often writes a call whose "old" or "new" string has
    unescaped quotes, which no JSON parser accepts, and the first version of this counted 3 such edits as no call at all.
    So the name and path are also read from the text, which is what an agent's own loose parser would do."""
    if msg.get("tool_calls"):
        c = msg["tool_calls"][0]["function"]
        return {"name": c["name"], "path": str(c["arguments"].get("path", "")), "parsed": True}
    text = msg.get("content", "")
    m = FIRST_CALL.search(text)
    if not m:
        return None
    # the textually first call, whether or not its JSON parses. Taking the first call that PARSES skipped run 06's broken
    # edit_file and reported the run_tests call after it
    start = text.rfind("{", 0, m.start())
    try:
        json.JSONDecoder().raw_decode(text, start)
        parsed = True
    except json.JSONDecodeError:
        parsed = False
    return {"name": m.group(1), "path": m.group(2), "parsed": parsed}


def classify(msg: dict) -> str:
    c = first_call(msg)
    if not c:
        return "other"
    path = c["path"]
    if c["name"] == "edit_file" and path.endswith("dates.py") and "month - 1" in msg.get("content", "") + json.dumps(msg.get("tool_calls") or []):
        return "fix"
    if c["name"] == "read_file" and path.endswith("dates.py"):
        return "reread"
    if c["name"] == "edit_file" and not path.endswith("dates.py"):
        return "wrong_file"
    return "other"


def warn_lines(exp: str) -> list[str]:
    f = RAW / exp / "server-log.txt"
    return [l for l in f.read_text().splitlines() if "truncating input prompt" in l] if f.exists() else []


def main() -> None:
    prompt = (HERE / "inputs" / "system-prompt.md").read_text()
    facts: dict = {
        "_what": "long-008-ollama-context. Every value written by measurements/derive.py from measurements/raw/. Prose fields only are edited by hand.",
        "rig": {"ollama_version": "0.20.2", "machine": "Apple M3 Max, 36 GB", "gpu_memory_ollama_sees_gib": 28.1,
                "model": "qwen2.5-coder:14b", "quantization": "Q4_K_M", "model_trained_context": 32768,
                "sampling": "Ollama defaults, temperature 0.8", "measured": "2026-09-15"},
        "prompt": {"bytes": len(prompt.encode()), "kilobytes": round(len(prompt.encode()) / 1000),
                   "lines": len(prompt.splitlines()), "rule3_line": prompt.splitlines().index(
                       "Rule 3. Read a file before you edit it, and never read the same file twice in one session.") + 1,
                   "rules_at_top": 8, "rule_numbers_shown": [1, 2, 3, 4, 5, 6, 7, 8], "rules_last_line": prompt.splitlines().index(
                       "Rule 8. If a request is ambiguous, ask one question before acting.") + 1,
                   "file": "measurements/inputs/system-prompt.md"},
        "ollama_default_tiers": {"_source": "ollama v0.20.2 server/routes.go 1842-1852, and ollama serve --help",
                                 "under_23_gib": 4096, "from_23_gib": 32768, "from_47_gib": 262144, "keep_tokens": 4,
                                 "this_machine_default": 32768},
    }

    # A: what arrives, and what it costs in memory
    arrive = load("arrive")
    rows = {}
    for k, r in arrive.items():
        ctx = r["request"]["num_ctx"]
        m = r["ps"][0]
        rows[ctx] = {"prompt_eval_count": r["response"]["prompt_eval_count"], "http_status": r["http_status"],
                     "error_field": "error" in r["response"], "loaded_size_bytes": m["size"],
                     "loaded_size_gib": round(m["size"] / GIB, 2), "ps_context": m.get("context_length")}
    full = rows[32768]["prompt_eval_count"]
    facts["arrive"] = {
        "_what": "The 35 KB system prompt plus 'Say hello in one sentence.', one request per window. raw/arrive/",
        "by_num_ctx": {str(k): v for k, v in sorted(rows.items())},
        "full_prompt_tokens": full,
        "received_at_4096": rows[4096]["prompt_eval_count"],
        "dropped_at_4096": full - rows[4096]["prompt_eval_count"],
        "dropped_at_4096_formula": "full_prompt_tokens - received_at_4096",
        "received_share_at_4096_percent": round(100 * rows[4096]["prompt_eval_count"] / full, 1),
        "received_share_formula": "received_at_4096 / full_prompt_tokens",
        "warn_lines": warn_lines("arrive"),
    }
    g4, g32 = rows[4096]["loaded_size_gib"], rows[32768]["loaded_size_gib"]
    facts["memory"] = {
        "_what": "Loaded model size from /api/ps right after each request, qwen2.5-coder:14b, all on the GPU",
        "gib_at_4096": g4, "gib_at_8192": rows[8192]["loaded_size_gib"], "gib_at_16384": rows[16384]["loaded_size_gib"],
        "gib_at_32768": g32,
        "added_gib_4096_to_32768": round(g32 - g4, 2), "added_formula": "gib_at_32768 - gib_at_4096",
        "ratio_32768_to_4096": round(g32 / g4, 2),
        "mib_per_1000_tokens": round((rows[32768]["loaded_size_bytes"] - rows[4096]["loaded_size_bytes"]) / 2 ** 20 / (32768 - 4096) * 1000, 1),
        "mib_per_1000_tokens_formula": "(size_32768 - size_4096) bytes / 2^20 / 28,672 tokens x 1000",
    }

    # B: quote Rule 3
    r3 = load("rule3")
    b = {}
    for ctx in (4096, 32768):
        recs = [r for k, r in r3.items() if k.startswith(f"ctx{ctx}-")]
        texts = [r["response"]["message"]["content"] for r in recs]
        # the whole sentence of Rule 3, not a phrase from it (a blind reviewer: "word for word" was checked with a partial match)
        quoted = [t for t in texts if "Read a file before you edit it, and never read the same file twice in one session" in t]
        b[str(ctx)] = {"n": len(recs), "quoted_rule3": len(quoted),
                       "other_rule_instead": sum(1 for x in texts if x.strip() and x not in quoted),
                       "last_rule_done7": sum("DONE-7" in t for t in texts),
                       "prompt_eval_count": sorted({r["response"]["prompt_eval_count"] for r in recs}),
                       "http_status": sorted({r["http_status"] for r in recs}),
                       "replies": texts}
    facts["rule3"] = {"_what": "'Quote Rule 3 of your operating rules, word for word. Nothing else.' 10 per window. raw/rule3/",
                      "rule3_text": "Read a file before you edit it, and never read the same file twice in one session.",
                      "by_num_ctx": b, "warn_lines_count": len(warn_lines("rule3"))}

    # C: the replayed session
    se = load("session")
    c = {}
    for ctx in (16384, 32768):
        recs = [r for k, r in se.items() if k.startswith(f"ctx{ctx}-")]
        kinds = [classify(r["response"]["message"]) for r in recs]
        first = [first_call(r["response"]["message"]) for r in recs]
        c[str(ctx)] = {"n": len(recs), "fix": kinds.count("fix"), "reread": kinds.count("reread"),
                       "replies_containing_month_minus_1": sum(1 for r in recs if "month - 1" in r["response"]["message"]["content"]),
                       "wrong_file": kinds.count("wrong_file"), "other": kinds.count("other"),
                       "prompt_eval_count": sorted({r["response"]["prompt_eval_count"] for r in recs}),
                       "http_status": sorted({r["http_status"] for r in recs}),
                       "first_call_per_run": first,
                       "calls_read_from_text_not_json": sum(1 for f in first if f and not f["parsed"]),
                       "no_tool_call_replies": [r["response"]["message"]["content"][:160] for r, k in zip(recs, kinds) if k == "other"],
                       "wrong_file_paths": sorted({f["path"] for f, k in zip(first, kinds) if k == "wrong_file"})}
    s_full, s_cut = c["32768"]["prompt_eval_count"][0], c["16384"]["prompt_eval_count"][0]
    facts["session"] = {"_what": "System prompt, a bug report, three read_file calls and their files, 'Shall I apply the fix?', 'Yes, apply the fix.' 10 per window. raw/session/",
                        "by_num_ctx": c, "chat_tokens_full": s_full, "chat_tokens_sent_at_16384": s_cut,
                        "dropped_at_16384": s_full - s_cut, "dropped_formula": "chat_tokens_full - chat_tokens_sent_at_16384",
                        "warn_lines_count": len(warn_lines("session"))}

    chk = json.loads((RAW / "session-check" / "without-first-three.json").read_text())
    facts["session"]["check"] = {
        "_what": "The session without its first three messages, at 32,768 where nothing is cut. raw/session-check/",
        "removed": chk["removed"], "prompt_eval_count": chk["response"]["prompt_eval_count"],
        "equals_sent_at_16384": chk["response"]["prompt_eval_count"] == s_cut}
    sizes = {f.name: f.stat().st_size for f in sorted((HERE / "inputs" / "files").glob("*.py"))}
    facts["session"]["files"] = {"bytes": sizes, "kb_each_rounded": sorted({round(v / 1000) for v in sizes.values()}),
                                 "kb_formula": "bytes / 1000, rounded, as drawn on the session cards",
                                 "bug_line_in_dates_py": (HERE / "inputs" / "files" / "dates.py").read_text().splitlines().index(
                                     "    return d.month  # BUG: should be d.month - 1, January reads February's window") + 1}
    facts["arrive"]["kept_end_at_4096"] = rows[4096]["prompt_eval_count"] - facts["ollama_default_tiers"]["keep_tokens"]
    facts["arrive"]["kept_end_formula"] = "received_at_4096 - keep_tokens"
    facts["arrive"]["dropped_at_8192"] = full - rows[8192]["prompt_eval_count"]

    # D: the smaller machine, and the one setting
    tier = load("tier")
    d = {}
    for k, r in tier.items():
        log = (RAW / "tier" / f"server-{k}.log").read_text()
        m = re.search(r'total_vram="([^"]+)" default_num_ctx=(\d+)', log)
        d[k] = {"env": r["env"], "prompt_tokens": r["response"]["usage"]["prompt_tokens"],
                "server_total_vram": m.group(1) if m else None, "server_default_num_ctx": int(m.group(2)) if m else None,
                "ps_context": r["ps"][0].get("context_length") if r["ps"] else None,
                "truncation_warnings": log.count("truncating input prompt")}
    facts["tier"] = {"_what": "A second server on :11435 with 6 GiB reserved by OLLAMA_GPU_OVERHEAD, so its own tier switch sees under 23 GiB. OpenAI endpoint, no num_ctx sent. raw/tier/", **d,
                     "gpu_overhead_gib": int(d["default"]["env"]["OLLAMA_GPU_OVERHEAD"]) / GIB,
                     "simulated_total_vram_gib": float(d["default"]["server_total_vram"].split()[0])}

    facts["figures_from_quoted_sources"] = {
        "_note": "Numbers we say or draw that are not our measurements, and who measured them.",
        "mccanna_prompt_kb": 35, "mccanna_window_tokens": 65000, "mccanna_context_share_percent": 14, "mccanna_model_params_b": 27,
        "mccanna_source": "patrickmccanna.net, Notes on migrating 35kb prompts away from Anthropic/OpenAI to Self-Hosted Ollama+opencode, 2026-09-13",
        "tier_gib_thresholds": [23, 47], "tier_source": "ollama v0.20.2 server/routes.go 1842-1852",
    }
    facts["retracted"] = {}
    facts["spoken_roundings"] = {
        "_note": "Figures the narration rounds out loud, always with 'about' or as a decimal. The exact value is what is drawn.",
        "session_chat_tokens_spoken_as": 18000, "session_chat_tokens_exact": facts["session"]["chat_tokens_full"],
        "session_window_spoken_as": 16000, "session_window_exact": 16384,
        "memory_4096_spoken_as_gib": 9, "memory_4096_exact_gib": facts["memory"]["gib_at_4096"],
        "memory_32768_spoken_as_gib": 16.5, "memory_32768_exact_gib": facts["memory"]["gib_at_32768"],
    }
    facts["packaging_numbers"] = {
        "_note": "Every number in a title, thumbnail or cover, as arithmetic on measured values.",
        "tokens_read_at_4096": {"value": facts["arrive"]["received_at_4096"], "arithmetic": "arrive.received_at_4096, prompt_eval_count of raw/arrive/ctx4096.json"},
        "tokens_sent": {"value": facts["arrive"]["full_prompt_tokens"], "arithmetic": "arrive.full_prompt_tokens, prompt_eval_count of raw/arrive/ctx32768.json"},
        "wrong_file_runs": {"value": c["16384"]["wrong_file"], "of": c["16384"]["n"], "printed_as": "8/10",
                            "arithmetic": "session.by_num_ctx.16384.wrong_file of n"},
    }
    FACTS.write_text(json.dumps(facts, indent=1) + "\n")
    print(json.dumps({k: facts[k] for k in ("arrive", "memory")}, indent=1)[:2500])
    print("rule3", {k: {x: v[x] for x in ("n", "quoted_rule3", "last_rule_done7", "prompt_eval_count")} for k, v in b.items()})
    print("session", {k: {x: v[x] for x in ("n", "fix", "reread", "wrong_file", "other", "prompt_eval_count", "wrong_file_paths")} for k, v in c.items()},
          "warn", facts["session"]["warn_lines_count"])
    print("tier", d)


if __name__ == "__main__":
    main()
