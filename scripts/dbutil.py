#!/usr/bin/env python3
"""Helpers for reading, writing and checking vehicle_data/ domain files.

Domain file layout (see docs/DATA_FORMAT.md):
{
  "domain": "transmission", "schema_version": 1, "updated": "YYYY-MM-DD",
  "sources": {source_id: {title, url, publisher, class, accessed, access_method, applicability, notes}},
  "parameters": {"transmission.gear_1": {"description", "unit", "impact", "candidates": [record, ...]}},
  ...any other top-level tables the domain needs...
}

Use from a domain script:
    import dbutil as db
    d = db.load_or_new("transmission", "Transmission")
    db.add_source(d, "tx-hondanews-2024", title=..., url=..., publisher=..., cls="A", ...)
    db.add_candidate(d, "transmission.gear_1", "1st gear ratio", "1", "high",
                     db.record(value=None, printed=(3.642, "ratio"), status="confirmed", cls="A",
                               source_id="tx-hondanews-2024", locator="Specifications table",
                               evidence="1st 3.642", as_printed="3.642",
                               applicability=db.app("2024", "CA", "Sport Touring", "6MT"),
                               confidence="high"))
    db.save(d)

CLI:  python3 scripts/dbutil.py check vehicle_data/transmission.json [...]
"""
import datetime
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "vehicle_data")

STATUSES = ("confirmed", "estimated", "unknown")
CLASSES = ("A", "B", "C", "D", "E", "F")
CONFIDENCES = ("high", "medium", "low", "none")
IMPACTS = ("critical", "high", "medium", "low")
REQUIRED_FIELDS = ("value", "unit", "status", "class", "source_id", "locator", "evidence",
                   "as_printed", "applicability", "confidence", "range", "how_to_measure", "notes")
APPLICABILITY_FIELDS = ("year", "market", "trim", "body", "gearbox", "engine", "notes")


def today():
    return datetime.date.today().isoformat()


def path_for(domain):
    return os.path.join(DATA, f"{domain}.json")


def load(path_or_domain):
    p = path_or_domain if path_or_domain.endswith(".json") else path_for(path_or_domain)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_or_new(domain, title=""):
    p = path_for(domain)
    if os.path.exists(p):
        return load(p)
    return {"domain": domain, "title": title, "schema_version": 1, "updated": today(),
            "sources": {}, "parameters": {}}


def save(d, path=None):
    d["updated"] = today()
    p = path or path_for(d["domain"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return p


def app(year, market, trim, gearbox, body="hatchback", engine="1.5T", notes=""):
    """Applicability block: what car the SOURCE describes (not the target)."""
    return {"year": year, "market": market, "trim": trim, "body": body,
            "gearbox": gearbox, "engine": engine, "notes": notes}


def add_source(d, sid, title, url, publisher, cls, accessed=None, access_method="static",
               applicability="", notes="", cache_file=None):
    if cls not in CLASSES:
        raise ValueError(f"bad class {cls}")
    d.setdefault("sources", {})[sid] = {
        "title": title, "url": url, "publisher": publisher, "class": cls,
        "accessed": accessed or today(), "access_method": access_method,
        "applicability": applicability, "notes": notes, "cache_file": cache_file,
    }
    return sid


def record(value=None, unit=None, printed=None, status="confirmed", cls="A", source_id=None,
           locator="", evidence="", as_printed="", applicability=None, confidence="medium",
           range=None, how_to_measure=None, notes="", derivation=None, searches=None,
           prefer=False, selection_reason=None, **extra):
    """Build one candidate record. If `printed=(number_or_list, unit)` is given the SI
    value and unit are computed from it (never typed by hand)."""
    rec = {}
    if printed is not None:
        pv, pu = printed
        v, u = units.to_si(pv, pu)
        rec["printed"] = {"value": pv, "unit": pu}
        if value is not None and value != v:
            raise ValueError("pass either value or printed, not both with different values")
        value, unit = v, u
    rec.update({
        "value": value, "unit": unit, "status": status, "class": cls,
        "source_id": source_id, "locator": locator, "evidence": evidence,
        "as_printed": as_printed, "applicability": applicability or {},
        "confidence": confidence, "range": range, "how_to_measure": how_to_measure,
        "notes": notes,
    })
    if derivation is not None:
        rec["derivation"] = derivation
    if searches is not None:
        rec["searches"] = searches
    if prefer:
        rec["prefer"] = True
        rec["selection_reason"] = selection_reason
    rec.update(extra)
    return rec


def unknown(unit, searches, how_to_measure, notes="", applicability=None):
    """Record for a value that could not be found after the obvious sources and ~5 searches."""
    return record(value=None, unit=unit, status="unknown", cls=None, source_id=None,
                  locator="", evidence="", as_printed="", applicability=applicability or {},
                  confidence="none", range=None, how_to_measure=how_to_measure,
                  notes=notes, searches=searches)


def add_candidate(d, key, description, unit, impact, rec, replace_same_source=True):
    if "." not in key:
        raise ValueError("parameter keys are namespaced: '<domain>.<name>'")
    p = d.setdefault("parameters", {}).setdefault(
        key, {"description": description, "unit": unit, "impact": impact, "candidates": []})
    p["description"], p["unit"], p["impact"] = description, unit, impact
    if replace_same_source and rec.get("source_id"):
        p["candidates"] = [c for c in p["candidates"]
                           if not (c.get("source_id") == rec["source_id"]
                                   and c.get("locator") == rec.get("locator"))]
    if rec.get("status") == "unknown":
        # an unknown placeholder is dropped once a real candidate exists, and vice versa
        if any(c.get("status") != "unknown" for c in p["candidates"]):
            return p
    else:
        p["candidates"] = [c for c in p["candidates"] if c.get("status") != "unknown"]
    p["candidates"].append(rec)
    return p


# ---------------------------------------------------------------- checking

def _isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _close(a, b, rel=1e-6, abs_=1e-9):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y, rel, abs_) for x, y in zip(a, b))
    if _isnum(a) and _isnum(b):
        return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))
    return a == b


def check_record(key, i, r, sources, all_sources=None):
    errs = []
    where = f"{key}[{i}]"
    for f in REQUIRED_FIELDS:
        if f not in r:
            errs.append(f"{where}: missing field '{f}'")
    st, cl = r.get("status"), r.get("class")
    if st not in STATUSES:
        errs.append(f"{where}: bad status {st!r}")
    if st == "unknown":
        if r.get("value") is not None:
            errs.append(f"{where}: unknown record must have value null")
        if not r.get("how_to_measure"):
            errs.append(f"{where}: unknown record needs how_to_measure")
        if not r.get("searches") and not r.get("notes"):
            errs.append(f"{where}: unknown record needs 'searches' (what was tried)")
        return errs
    if cl not in CLASSES:
        errs.append(f"{where}: bad class {cl!r}")
    if r.get("confidence") not in CONFIDENCES:
        errs.append(f"{where}: bad confidence {r.get('confidence')!r}")
    if cl in ("A", "B", "C"):
        sid = r.get("source_id")
        pool = all_sources if all_sources is not None else sources
        if not sid or sid not in pool:
            if not (cl == "B" and sid and sid.startswith("user:")):
                errs.append(f"{where}: class {cl} record has unregistered source_id {sid!r}")
        if not r.get("evidence"):
            errs.append(f"{where}: class {cl} record needs verbatim evidence")
        if not r.get("locator"):
            errs.append(f"{where}: class {cl} record needs a locator")
    if cl in ("D", "E", "F") or st == "estimated":
        rg = r.get("range")
        if not (isinstance(rg, list) and len(rg) == 2):
            errs.append(f"{where}: class {cl}/{st} record needs range [lo, hi]")
        elif _isnum(r.get("value")) and all(_isnum(x) for x in rg):
            if not (rg[0] - 1e-9 <= r["value"] <= rg[1] + 1e-9):
                errs.append(f"{where}: value {r['value']} outside range {rg}")
    if st == "estimated" and not r.get("how_to_measure"):
        errs.append(f"{where}: estimated record needs how_to_measure")
    if cl == "D" and not r.get("derivation"):
        errs.append(f"{where}: class D record needs a 'derivation' block (script/function/inputs)")
    pr = r.get("printed")
    if pr is not None:
        try:
            v, u = units.to_si(pr["value"], pr["unit"])
            if not _close(v, r.get("value")) or u != r.get("unit"):
                errs.append(f"{where}: SI value {r.get('value')} {r.get('unit')} != "
                            f"converted printed {v} {u}")
        except KeyError as e:
            errs.append(f"{where}: {e}")
    if not isinstance(r.get("applicability"), dict):
        errs.append(f"{where}: applicability must be an object")
    return errs


def check_domain(d, all_sources=None):
    errs = []
    for k in ("domain", "sources", "parameters"):
        if k not in d:
            errs.append(f"missing top-level '{k}'")
    for sid, s in d.get("sources", {}).items():
        for f in ("title", "url", "publisher", "class", "accessed"):
            if not s.get(f) and not (f == "url" and s.get("class") in ("D", "E", "F")):
                errs.append(f"source {sid}: missing {f}")
    for key, p in d.get("parameters", {}).items():
        for f in ("description", "unit", "impact", "candidates"):
            if f not in p:
                errs.append(f"{key}: missing '{f}'")
        if p.get("impact") not in IMPACTS:
            errs.append(f"{key}: impact must be one of {IMPACTS}")
        if not p.get("candidates"):
            errs.append(f"{key}: no candidates (record an 'unknown' instead)")
        for i, r in enumerate(p.get("candidates", [])):
            errs.extend(check_record(key, i, r, d.get("sources", {}), all_sources))
    return errs


def main(argv):
    if len(argv) < 2 or argv[0] != "check":
        print(__doc__)
        return 1
    bad = 0
    for p in argv[1:]:
        errs = check_domain(load(p))
        print(f"{p}: {'OK' if not errs else str(len(errs)) + ' problem(s)'}")
        for e in errs:
            print("   ", e)
        bad += len(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
