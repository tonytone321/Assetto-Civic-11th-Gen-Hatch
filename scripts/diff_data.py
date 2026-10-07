#!/usr/bin/env python3
"""Semantic diff of database JSON between two checkouts (or a checkout and a git revision).

Classifies every difference as
  timestamp  - only `updated` / `accessed` dates differ
  order      - same content, different key or list order
  value      - anything else (reported with its JSON path)

Usage: python3 scripts/diff_data.py OTHER_ROOT [--rev HEAD] [--files glob ...]
Compares OTHER_ROOT's working files against this repository's files at --rev (default: working tree).
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = ["vehicle_data/*.json", "references/manifest.json", "audio/reference_database.json",
           "engine_curves/*.json"]
TIMESTAMP_KEYS = {"updated", "accessed"}


def load_rev(path, rev):
    if rev is None:
        p = os.path.join(ROOT, path)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    try:
        out = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return None
    return json.loads(out.stdout)


def strip(o, keys):
    if isinstance(o, dict):
        return {k: strip(v, keys) for k, v in o.items() if k not in keys}
    if isinstance(o, list):
        return [strip(v, keys) for v in o]
    return o


def canon(o):
    if isinstance(o, dict):
        return {k: canon(o[k]) for k in sorted(o)}
    if isinstance(o, list):
        items = [canon(v) for v in o]
        return sorted(items, key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
    return o


def paths(a, b, p=""):
    """Yield JSON paths where a and b differ (structure-aware, order-sensitive lists)."""
    if type(a) != type(b):
        yield p, a, b
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                yield f"{p}/{k}", a.get(k, "<absent>"), b.get(k, "<absent>")
            else:
                yield from paths(a[k], b[k], f"{p}/{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            yield f"{p}[len {len(a)}->{len(b)}]", None, None
        for i, (x, y) in enumerate(zip(a, b)):
            yield from paths(x, y, f"{p}[{i}]")
    elif a != b:
        yield p, a, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("other")
    ap.add_argument("--rev", default=None)
    ap.add_argument("--files", nargs="*", default=DEFAULT)
    a = ap.parse_args()
    files = sorted({os.path.relpath(f, a.other) for g in a.files for f in glob.glob(os.path.join(a.other, g))} |
                   {os.path.relpath(f, ROOT) for g in a.files for f in glob.glob(os.path.join(ROOT, g))})
    files = [f for f in files if not f.endswith("_resolved.json") or True]
    summary = {"identical": [], "timestamp": [], "order": [], "value": []}
    details = {}
    for f in files:
        mine = load_rev(f, a.rev)
        p = os.path.join(a.other, f)
        theirs = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
        if mine == theirs:
            summary["identical"].append(f)
            continue
        if mine is None or theirs is None:
            summary["value"].append(f)
            details[f] = [("<file>", "present" if mine else "absent", "present" if theirs else "absent")]
            continue
        sm, st = strip(mine, TIMESTAMP_KEYS), strip(theirs, TIMESTAMP_KEYS)
        if sm == st:
            summary["timestamp"].append(f)
        elif canon(sm) == canon(st):
            summary["order"].append(f)
        else:
            summary["value"].append(f)
            details[f] = list(paths(canon(sm), canon(st)))
    for k, v in summary.items():
        print(f"{k}: {len(v)}" + (f"  {v}" if k != "identical" else ""))
    for f, ds in details.items():
        print(f"\n== {f}: {len(ds)} value difference(s)")
        for path, x, y in ds[:40]:
            print(f"  {path}\n     committed: {json.dumps(x, ensure_ascii=False)[:220]}\n     rebuilt:   {json.dumps(y, ensure_ascii=False)[:220]}")
    return 1 if summary["value"] else 0


if __name__ == "__main__":
    sys.exit(main())
