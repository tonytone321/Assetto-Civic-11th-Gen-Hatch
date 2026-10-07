#!/usr/bin/env python3
"""Step 2: re-open each Honda source for the six headline dimensions live and print the rows that
state them, so the digits can be confirmed by reading. Saves the fetched text to cache/pages/
(via fetch_page) and writes docs/phase2/headline_dimension_sources.json with what was found.

Usage: python3 scripts/phase2/confirm_headline_dims.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from fetch_page import fetch_rendered, fetch_static, html_to_text, robots_allowed  # noqa: E402

SOURCES = {
    "dim:hondanews-ca-2024-hatch-specs": "Honda Canada newsroom, 2024 Civic Hatchback specifications",
    "dim:hondanews-ca-2023-hatch-specs": "Honda Canada newsroom, 2023 Civic Hatchback specifications",
    "dim:hondanews-ca-2022-hatch-specs": "Honda Canada newsroom, 2022 Civic Hatchback specifications",
    "dim:hondanews-us-2024-hatch-specs": "American Honda newsroom, 2024 Civic Hatchback specifications",
    "dim:hondanews-us-2022-hatch-specs": "American Honda newsroom, 2022 Civic Hatchback specifications",
    "dim:hondainfocenter-us-2024-hatch-specs": "Honda Information Center (US), 2024 Civic Hatchback specifications",
    "dim:hondainfocenter-us-2024-sedan-specs": "Honda Information Center (US), 2024 Civic Sedan specifications (excluded body)",
}
ROWS = r"(Length|Width|Height|Wheelbase|Track)"


def main():
    dims = json.load(open(os.path.join(ROOT, "vehicle_data", "dimensions.json")))
    out = {}
    for sid, label in SOURCES.items():
        url = dims["sources"][sid]["url"]
        ok, why = robots_allowed(url)
        if not ok:
            out[sid] = {"url": url, "status": f"not fetched: {why}"}
            continue
        st, final, html = fetch_static(url)
        text = html_to_text(html)
        if len(re.findall(ROWS, text)) < 3:  # JS page: render
            st, final, html, text = fetch_rendered(url, 5000)
        lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
        lines = [l for l in lines if l]
        hits = []
        for i, l in enumerate(lines):
            if re.match(ROWS, l) and len(l) < 90:
                hits.append(" | ".join(lines[i:i + 6]))
        out[sid] = {"label": label, "url": url, "http_status": st, "rows": hits[:30]}
        print(f"\n=== {sid} ({label}) HTTP {st}\n{url}")
        for h in hits[:30]:
            print("   ", h[:200])
    p = os.path.join(ROOT, "docs", "phase2", "headline_dimension_sources.json")
    json.dump(out, open(p, "w"), indent=1, ensure_ascii=False)
    print("\nwrote", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
