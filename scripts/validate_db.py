#!/usr/bin/env python3
"""Validate the engineering database. Exit status 1 on any failure.

Fails on: missing record fields, A–C records without a registered source / evidence /
locator, SI values that don't match their printed figure, derived values that don't
match recomputation, failed cross-checks. Warns (does not fail) when a verbatim
evidence quote cannot be found in the locally cached page text (cache/ is git-ignored,
so this check only runs where the cache exists).

Usage: python3 scripts/validate_db.py [--json out.json]
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crosschecks  # noqa: E402
import dbutil  # noqa: E402
import derive  # noqa: E402
import resolve  # noqa: E402

ROOT = dbutil.ROOT


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("|", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", s))  # HTML line breaks inside parentheses


def quote_check(files, sources):
    """Return (checked, missing list). Evidence fragments are joined with ' … '."""
    cache_txt = {}
    checked, missing = 0, []
    for p in files:
        d = dbutil.load(p)
        for key, prm in d.get("parameters", {}).items():
            for i, r in enumerate(prm.get("candidates", [])):
                if r.get("class") not in ("A", "B", "C") or not r.get("evidence"):
                    continue
                s = sources.get(r.get("source_id")) or {}
                cf = s.get("cache_file")
                if not cf:
                    continue
                path = os.path.join(ROOT, cf)
                if not os.path.exists(path):
                    continue
                if path not in cache_txt:
                    if path.endswith(".csv"):
                        # tabular data: evidence is quoted as "COLUMN = value" from one row
                        import csv as _csv
                        cells = set()
                        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
                            for row in _csv.DictReader(fh):
                                cells.update(norm(f"{k} = {v}") for k, v in row.items() if k and v)
                        cache_txt[path] = cells
                    elif path.endswith(".pdf"):
                        try:
                            import pymupdf
                            cache_txt[path] = norm(" ".join(pg.get_text() for pg in pymupdf.open(path)))
                        except Exception:
                            cache_txt[path] = ""
                    else:
                        cache_txt[path] = norm(open(path, encoding="utf-8", errors="replace").read())
                hay = cache_txt[path]
                checked += 1
                frags = [f for f in re.split(r"\s*(?:…|\.\.\.)\s*", r["evidence"]) if f.strip()]
                bad = [f for f in frags if (norm(f) not in hay)]
                if bad:
                    missing.append(f"{os.path.relpath(p, ROOT)} {key}[{i}] ({r.get('source_id')}): "
                                   f"not found in {cf}: {bad[0][:90]!r}")
    return checked, missing


def main():
    errors, warnings = [], []
    files = resolve.domain_files(include_derived=True)
    if os.path.exists(resolve.USER):
        files = [resolve.USER] + files
    _, sources = resolve.load_all()
    for p in files:
        d = dbutil.load(p)
        for e in dbutil.check_domain(d, all_sources=sources):
            # user template rows are unknown placeholders; dbutil already accepts them
            errors.append(f"{os.path.relpath(p, ROOT)}: {e}")
    # source id collisions with different URLs
    seen = {}
    for p in files:
        for sid, s in dbutil.load(p).get("sources", {}).items():
            if sid in seen and seen[sid] != s.get("url"):
                errors.append(f"source id {sid} has different URLs in different files")
            seen.setdefault(sid, s.get("url"))
    # derived recomputation
    if os.path.exists(derive.OUT):
        stored = dbutil.load(derive.OUT)
        fresh, _ = derive.evaluate()
        for k, prm in fresh["parameters"].items():
            sv = stored["parameters"].get(k, {}).get("candidates", [{}])[0].get("value", "MISSING")
            fv = prm["candidates"][0]["value"]
            if sv == "MISSING":
                errors.append(f"derived.json lacks {k} (re-run derive.py)")
            elif not dbutil._close(sv, fv, rel=1e-6):
                errors.append(f"derived {k}: stored {sv} != recomputed {fv} (re-run derive.py)")
        for k in stored["parameters"]:
            if k not in fresh["parameters"]:
                errors.append(f"derived.json has stale key {k}")
    else:
        errors.append("vehicle_data/derived.json missing (run derive.py)")
    # cross-checks
    res = json.load(open(resolve.OUT))["parameters"] if os.path.exists(resolve.OUT) else {}
    cc = crosschecks.run(res)
    for c in cc:
        if c["status"] == "fail":
            errors.append(f"cross-check failed: {c['name']}: {c['detail']}")
        elif c["status"] == "not_run":
            warnings.append(f"cross-check not run: {c['name']}: {c['detail']}")
    checked, missing = quote_check(files, sources)
    warnings += [f"quote not found in cache: {m}" for m in missing]
    summary = {"errors": errors, "warnings": warnings, "crosschecks": cc,
               "quotes_checked_against_cache": checked, "quotes_not_found": len(missing)}
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f:
            json.dump(summary, f, indent=2)
    for c in cc:
        print(f"[{c['status'].upper():7}] {c['name']}: {c['detail']}")
    print(f"quotes checked against cached pages: {checked}, not found: {len(missing)}")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{'FAIL' if errors else 'OK'}: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
