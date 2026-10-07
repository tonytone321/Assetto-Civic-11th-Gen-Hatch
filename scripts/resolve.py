#!/usr/bin/env python3
"""Pick the effective record per parameter -> vehicle_data/_resolved.json.

Precedence (docs/DATA_FORMAT.md): verified user measurement (user_measurements.json,
non-null value) > class A > classes B and C > D > E > F > unknown. Within a tier:
applicability closest to 2024 / Canada / Sport Touring / 6MT, then `prefer`, then
confidence, then file order. Losing candidates stay in their files. Same-tier
disagreement beyond tolerance is reported as a conflict (docs/CONFLICTS.md).

Usage: python3 scripts/resolve.py [--quiet]
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dbutil  # noqa: E402

ROOT = dbutil.ROOT
DATA = dbutil.DATA
OUT = os.path.join(DATA, "_resolved.json")
USER = os.path.join(DATA, "user_measurements.json")
DERIVED = os.path.join(DATA, "derived.json")
EXTRA_FILES = [os.path.join(ROOT, "audio", "reference_database.json"),
               os.path.join(ROOT, "references", "manifest.json")]
TIER = {"A": 1, "B": 2, "C": 2, "D": 3, "E": 4, "F": 5}
CONF = {"high": 0, "medium": 1, "low": 2, "none": 3}
REL_TOL = 0.01  # 1 % disagreement between unprinted numeric candidates = conflict (printed: rounding-aware)


def domain_files(include_derived=True):
    files = sorted(p for p in glob.glob(os.path.join(DATA, "*.json"))
                   if os.path.basename(p) not in ("_resolved.json", "derived.json",
                                                  "user_measurements.json"))
    files += [p for p in EXTRA_FILES if os.path.exists(p)]
    if include_derived and os.path.exists(DERIVED):
        files.append(DERIVED)
    return files


def load_all(include_derived=True, include_user=True):
    """Return (params, sources): params[key] = {meta..., 'cands': [(file, idx, rec)]}."""
    params, sources = {}, {}
    files = domain_files(include_derived)
    if include_user and os.path.exists(USER):
        files = [USER] + files
    for p in files:
        d = dbutil.load(p)
        rel = os.path.relpath(p, ROOT)
        for sid, s in d.get("sources", {}).items():
            sources.setdefault(sid, dict(s, file=rel))
        for key, prm in d.get("parameters", {}).items():
            e = params.setdefault(key, {"description": prm.get("description"),
                                        "unit": prm.get("unit"), "impact": prm.get("impact"),
                                        "domain_file": rel, "cands": []})
            if rel != os.path.relpath(USER, ROOT) and e["domain_file"].endswith("user_measurements.json"):
                e.update(description=prm.get("description"), impact=prm.get("impact"), domain_file=rel)
            for i, r in enumerate(prm.get("candidates", [])):
                e["cands"].append((rel, i, r))
    return params, sources


def applicability_score(a):
    if not isinstance(a, dict):
        return 9
    s = 0
    year = str(a.get("year", ""))
    s += 0 if "2024" in year else (1 if year else 2)
    m = str(a.get("market", "")).upper()
    s += 0 if m in ("CA", "CANADA") else (1 if ("CA" in m or "NA" in m) else 2)
    t = str(a.get("trim", "")).lower()
    s += 0 if "sport touring" in t else (1 if (t == "" or "all" in t or "shared" in t) else 2)
    g = str(a.get("gearbox", "")).upper()
    s += 0 if ("6MT" in g or "MANUAL" in g) else (1 if (g == "" or "ALL" in g or "SHARED" in g) else 2)
    return s


def is_user(file, rec):
    return file.endswith("user_measurements.json") and rec.get("value") is not None


def rank(c):
    file, idx, r = c
    if is_user(file, r):
        tier = 0
    elif r.get("status") == "unknown" or r.get("value") is None:
        tier = 9
    else:
        tier = TIER.get(r.get("class"), 8)
    return (tier, applicability_score(r.get("applicability")), 0 if r.get("prefer") else 1,
            CONF.get(r.get("confidence"), 3), file, idx), tier


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _half_ulp_si(rec):
    """Half the last printed digit of a record's printed figure, in SI (print-rounding tolerance)."""
    pr = rec.get("printed") if isinstance(rec, dict) else None
    if not pr or not _num(pr.get("value")):
        return None
    txt = repr(pr["value"])
    dec = len(txt.split(".")[1]) if "." in txt and "e" not in txt else 0
    import units
    lo, _ = units.to_si(pr["value"] - 0.5 * 10 ** -dec, pr["unit"])
    hi, _ = units.to_si(pr["value"] + 0.5 * 10 ** -dec, pr["unit"])
    return abs(hi - lo) / 2


def differs(a, b, ra=None, rb=None):
    """True if two candidate values disagree. Two printed figures disagree when they differ by more
    than their combined print rounding (e.g. 179.0 in vs 4529 mm); otherwise a 1 % tolerance applies."""
    if _num(a) and _num(b):
        ta, tb = _half_ulp_si(ra), _half_ulp_si(rb)
        if ta is not None and tb is not None:
            return abs(a - b) > (ta + tb) * (1 + 1e-9)
        return abs(a - b) > REL_TOL * max(abs(a), abs(b), 1e-12)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) != len(b) or any(differs(x, y) for x, y in zip(a, b))
    if isinstance(a, str) and isinstance(b, str):
        return a.strip().lower() != b.strip().lower()
    return a != b


def resolve(params):
    out, conflicts = {}, []
    for key in sorted(params):
        e = params[key]
        cands = [c for c in e["cands"] if not (c[0].endswith("user_measurements.json")
                                                and c[2].get("value") is None)]
        if not cands:
            continue
        ranked = sorted(cands, key=lambda c: rank(c)[0])
        file, idx, r = ranked[0]
        tier = rank(ranked[0])[1]
        rec = {"value": r.get("value"), "unit": r.get("unit"), "status": r.get("status"),
               "class": "B(user)" if tier == 0 else r.get("class"),
               "confidence": r.get("confidence"), "source_id": r.get("source_id"),
               "range": r.get("range"), "file": file, "candidate_index": idx,
               "n_candidates": len(cands), "impact": e.get("impact"),
               "description": e.get("description"), "applicability": r.get("applicability")}
        # conflicts among credible (user/A/B/C) candidates with real values
        cred = [c for c in ranked if rank(c)[1] <= 2 and c[2].get("value") is not None]
        if tier <= 2:
            others = [c for c in cred[1:] if differs(c[2]["value"], r.get("value"), c[2], r)]
            if others:
                rec["conflict"] = True
                conflicts.append({
                    "key": key, "selected": {"file": file, "index": idx, "value": r.get("value"),
                                             "unit": r.get("unit"), "class": rec["class"],
                                             "source_id": r.get("source_id"),
                                             "applicability": r.get("applicability"),
                                             "selection_reason": r.get("selection_reason")},
                    "others": [{"file": f, "index": i, "value": o.get("value"), "unit": o.get("unit"),
                                "class": o.get("class"), "source_id": o.get("source_id"),
                                "applicability": o.get("applicability"), "notes": o.get("notes")}
                               for f, i, o in others],
                    "rule": "precedence: user > A > B/C; then applicability (2024, CA, Sport Touring, 6MT); "
                            "then prefer flag; then confidence"})
        out[key] = rec
    return out, conflicts


def main():
    params, _ = load_all()
    res, conflicts = resolve(params)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"note": "Generated by scripts/resolve.py — do not edit.",
                   "parameters": res, "conflicts": conflicts}, f, indent=2, ensure_ascii=False)
        f.write("\n")
    if "--quiet" not in sys.argv:
        n_unknown = sum(1 for r in res.values() if r["value"] is None)
        print(f"resolved {len(res)} parameters ({n_unknown} unknown), {len(conflicts)} conflicts -> "
              f"{os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
