#!/usr/bin/env python3
"""QA: check each record's evidence fragments (split on ' … ') occur in the source's cached
text after whitespace normalisation. Usage: verify_evidence.py vehicle_data/x.json ..."""
import json
import re
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root


def norm(s):
    s = s.replace(" ", " ")
    s = s.replace("â€¢", "•")
    return re.sub(r"\s+", " ", s).strip()


bad = 0
for p in sys.argv[1:]:
    d = json.load(open(p, encoding="utf-8"))
    srcs = d.get("sources", {})
    cache = {}
    for key, par in d.get("parameters", {}).items():
        for i, r in enumerate(par["candidates"]):
            if r.get("class") not in ("A", "B", "C"):
                continue
            s = srcs.get(r.get("source_id"), {})
            cf = s.get("cache_file")
            if not cf:
                print(f"NOCACHE {key}[{i}] {r.get('source_id')}")
                continue
            if cf not in cache:
                fp = os.path.join(ROOT, cf)
                cache[cf] = norm(open(fp, encoding="utf-8", errors="replace").read()) if os.path.exists(fp) else None
            t = cache[cf]
            if t is None:
                print(f"MISSINGFILE {key}[{i}] {cf}")
                bad += 1
                continue
            for frag in r["evidence"].split(" … "):
                if norm(frag) not in t:
                    print(f"NOTFOUND {key}[{i}] {r['source_id']}: {frag[:120]!r}")
                    bad += 1
print("evidence check:", "OK" if not bad else f"{bad} problem(s)")
