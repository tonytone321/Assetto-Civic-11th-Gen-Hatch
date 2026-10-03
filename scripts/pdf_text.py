#!/usr/bin/env python3
"""Download (to git-ignored cache/pdf/) and extract PDF text with page numbers.

Usage: python3 scripts/pdf_text.py URL_OR_PATH [--grep REGEX] [--context N] [--pages 1-5]
Prints '=== page N ===' headers so every value can be cited by page.
"""
import argparse, hashlib, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "pdf")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get(src):
    if os.path.exists(src):
        return src
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetch_page import robots_allowed
    ok, detail = robots_allowed(src)
    if not ok:
        sys.exit(f"BLOCKED_BY_ROBOTS {src} ({detail})")
    import requests
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.sha1(src.encode()).hexdigest()[:16] + ".pdf")
    if not os.path.exists(p):
        r = requests.get(src, headers={"User-Agent": UA}, timeout=120)
        r.raise_for_status()
        open(p, "wb").write(r.content)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--grep"); ap.add_argument("--context", type=int, default=200)
    ap.add_argument("--pages")
    a = ap.parse_args()
    import pymupdf
    path = get(a.src)
    doc = pymupdf.open(path)
    lo, hi = 1, doc.page_count
    if a.pages:
        lo, hi = (int(x) for x in a.pages.split("-")) if "-" in a.pages else (int(a.pages),) * 2
    print(f"FILE {path} PAGES {doc.page_count}")
    for i in range(lo - 1, min(hi, doc.page_count)):
        t = doc[i].get_text()
        if a.grep:
            for m in re.finditer(a.grep, t, flags=re.I):
                s, e = max(0, m.start() - a.context), min(len(t), m.end() + a.context)
                print(f"--- page {i+1}: " + t[s:e].replace("\n", " | "))
        else:
            print(f"=== page {i+1} ===\n{t}")


if __name__ == "__main__":
    main()
