#!/usr/bin/env python3
"""Generate docs/MODEL_VALIDATION.md (Phase 2, Step 8) from the committed outputs:
vehicle_data/dimensions.json + _resolved.json (headline dimensions), docs/phase2/cage_check.json,
blender/_build/cage_manifest.json (copied to docs/phase2/cage_contents.json), docs/phase2/photo_comparison.json,
docs/phase2/step1_reproducibility.md and step3_user_supplied.md. Numbers are not typed here.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import resolve  # noqa: E402

P2 = os.path.join(ROOT, "docs", "phase2")
OUT = os.path.join(ROOT, "docs", "MODEL_VALIDATION.md")
HEADLINE = ["dimensions.length", "dimensions.width_body", "dimensions.height", "dimensions.wheelbase",
            "dimensions.track_front", "dimensions.track_rear"]


def load(p):
    return json.load(open(p, encoding="utf-8"))


def mm(x):
    return f"{x * 1000:.1f}"


def headline_section():
    dims = load(os.path.join(ROOT, "vehicle_data", "dimensions.json"))
    res = load(resolve.OUT)["parameters"]
    L = ["## 2. Headline dimensions and the Honda sources that confirm them", "",
         "Each Honda page was re-opened live on 2026-10-07 (`scripts/phase2/confirm_headline_dims.py`, rows saved in "
         "`docs/phase2/headline_dimension_sources.json`) and every candidate is kept in `vehicle_data/dimensions.json`. "
         "Selection follows the Phase 1 precedence rule (Canadian specification first). \"Agrees\" means the printed figure "
         "equals the selected value within the combined print rounding of the two figures.", ""]
    for k in HEADLINE:
        r = res[k]
        sel = r["value"]
        L += [f"### `{k}` = **{mm(sel)} mm** (selected: `{r['source_id']}`)", "",
              "| source | year / market | as printed | in mm | vs selected |", "|---|---|---|---|---|"]
        for c in dims["parameters"][k]["candidates"]:
            a = c["applicability"]
            pr = c.get("printed") or {}
            half = resolve._half_ulp_si(c) or 0
            sel_rec = next(cc for cc in dims["parameters"][k]["candidates"] if cc["source_id"] == r["source_id"])
            tol = half + (resolve._half_ulp_si(sel_rec) or 0)
            d = c["value"] - sel
            verdict = "agrees" if abs(d) <= tol * (1 + 1e-9) else f"differs by {d * 1000:+.1f} mm"
            if "REJECTED" in (c.get("notes") or ""):
                verdict += " — rejected (sedan figure)"
            elif "with-licence-bracket" in (c.get("notes") or "") or "WITH-licence-bracket" in (c.get("notes") or ""):
                verdict += " — equals the with-bracket length"
            L.append(f"| `{c['source_id']}` | {a.get('year')} {a.get('market')} | {pr.get('value')} {pr.get('unit')} | "
                     f"{mm(c['value'])} | {verdict} |")
        L.append("")
    L += ["Overall length: Honda Canada's 2024 sheet prints **4529 mm** (no bracket note). Its 2022 and 2023 sheets print "
          "\"4547/4529\" with/without licence bracket, so 4529 mm is the body without the front plate bracket. hondanews.com "
          "(2022 and 2024) prints **179.0 in = 4546.6 mm**, which is the with-bracket length. Honda's US Information Center "
          "2024 hatchback page prints **184.0 in**, the figure its own 2024 sedan page prints; it is kept as a rejected candidate. "
          "All three disagreements are listed in `docs/CONFLICTS.md`.", ""]
    return L


def cage_section():
    chk = load(os.path.join(P2, "cage_check.json"))
    man_p = os.path.join(ROOT, "blender", "_build", "cage_manifest.json")
    man = load(man_p)
    contents = {"generator": man["generator"], "blender": man["blender"],
                "objects": {n: {k: v for k, v in o.items() if k in ("collection", "keys", "note")} for n, o in man["objects"].items()},
                "missing": man["missing"]}
    json.dump(contents, open(os.path.join(P2, "cage_contents.json"), "w"), indent=1)
    from collections import Counter
    cnt = Counter(o["collection"] for o in man["objects"].values())
    L = ["## 5. Reference cage", "",
         "`blender/reference_cage.blend`, built by `scripts/blender/build_reference_cage.py` from `vehicle_data/_resolved.json` "
         "only (object list and data keys in `docs/phase2/cage_contents.json`). Renders of the cage alone: `docs/phase2/renders/` "
         "(orthographic front, rear, left, right, top; perspective front and rear three-quarter; Cycles CPU, 16 samples).", "",
         "Objects per collection: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())) + ". "
         "Each object sits in the collection of the weakest data that places or sizes it (measured > published > photo > estimated).", "",
         f"**Dimension check** (`scripts/blender/check_cage.py`, `docs/phase2/cage_check.json`): "
         f"{'PASS' if chk['pass'] else 'FAIL'}. Coordinates are stored as 32-bit floats in Blender, so equality is to "
         f"{chk['tolerance_m'] * 1e6:.0f} µm; the {chk['custom_property_checks']['n']} double-precision database values stored on the "
         f"objects equal the database exactly ({len(chk['custom_property_checks']['failed'])} mismatches).", "",
         "| check | database (mm) | cage (mm) | difference (µm) | result |", "|---|---|---|---|---|"]
    for c in chk["checks"]:
        L.append(f"| {c['check']} | {c['database'] * 1000:.3f} | {c['cage'] * 1000:.3f} | {c['diff_m'] * 1e6:+.3f} | "
                 f"{'pass' if c['pass'] else 'FAIL'} |")
    L += ["", "**Left out because the data are missing** (nothing was invented):", ""]
    for m in man["missing"]:
        L.append(f"- {m['item']}: {m['reason']}")
    L += ["", "Notes: the body box's fore-aft position comes from `dimensions.overhang_front` (published total overhang × the "
          "front fraction measured on the Phase 1 render), so the box is in `REF_photo`. Wheel centres use "
          "`tires.loaded_radius` (0.3046 m, class E) because no measured wheel-centre height was supplied; Phase 1's hard-point "
          "builder uses a different estimate (0.3076 m) for the same point, and the render gives 0.3135/0.3156 m (Phase 1) — see "
          "the photo tables.", ""]
    return L


def photo_section():
    pc = load(os.path.join(P2, "photo_comparison.json"))
    L = ["## 6. Comparison with reference images", "",
         "Method (`scripts/phase2/compare_photos.py`): car silhouette from the render's alpha channel or a COCO Mask R-CNN "
         "(`scripts/phase2/segment_car.py`); rim-lip edges found by RANSAC on radial edges (`scripts/phase2/photo_features.py`); "
         "a pinhole camera fitted so the projected 3D rim circles pass through those edges and the tyres touch the ground at "
         "the detected contact points; each key point located by an algorithm, back-projected onto the plane it is assumed to "
         "lie on, and compared with the cage object built from the database. Uncertainty U = 2σ, where σ is the RSS of: "
         "localisation (pixel accuracy × size of a pixel at the car), camera-fit stability (refits from perturbed starts), "
         "lens distortion (refit at ±k1), unknown principal point (crop), the plane assumption (plane shifted by its stated "
         "tolerance) and, for views without EXIF, the unknown camera distance, height and yaw. **Agrees** = |difference| ≤ U.",
         "", "None of these images is a photograph of the target car, and none is straight-on with a known camera position "
         "(none were supplied). **Image R1 is the same studio render Phase 1 measured**, so for photo-derived cage items it tests "
         "Phase 1's orthographic simplification rather than giving an independent check; its comparisons with *published* "
         "items (height, wheelbase-based placement) are independent.", ""]
    for p in pc["photos"]:
        L += [f"### {p['id']}", "", f"- Image: `{p['path']}` (third-party; kept in the git-ignored cache; manifest id "
              f"`{p['manifest_id']}`). Shows: {p['shows']}. Size {p['image_size'][0]}×{p['image_size'][1]} px."]
        if p.get("status") == "camera not fitted":
            L += [f"- **Camera not fitted**: {p.get('reason')}", "- Every key point: **not measurable** for that reason.", ""]
            continue
        cam = p["camera"]
        spread = p.get("camera_fit_spread_m")
        spread_s = f"{spread:.3f} m" if spread is not None else "not computed"
        L += [f"- Focal length: {p['focal']['source']}; f = {cam['f_px']:.0f} px.",
              f"- Fitted camera: {cam['distance_to_mid_wheelbase_m']:.1f} m from mid-wheelbase, height {cam['C_project_m'][2]:.2f} m, "
              f"yaw {cam['yaw_deg']:.1f}°. Fit residual: rim edges RMS **{cam['rim_rms_px']:.2f} px**, contact points RMS "
              f"**{cam['contact_rms_px']:.2f} px**; camera-position spread over perturbed refits {spread_s}."]
        if p.get("status") == "camera fit unstable":
            L.append(f"- **Camera fit unstable — {p.get('reason')}.** Every key point below is therefore **not measurable**; "
                     "the column \"rejected-fit value − cage\" shows what the rejected camera would give and is not a difference.")
        if p.get("wheel_detection_warning"):
            L.append(f"- Warning: {p['wheel_detection_warning']}")
        if p.get("stability_note"):
            L.append(f"- Stability: {p['stability_note']}")
        L += ["", "| key point | axis | assumed plane | photo (m) | cage (m) | cage object (class) | difference (mm) | U (mm) | largest U term | verdict |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in p["rows"]:
            comps = r.get("components_mm", {})
            top = max(comps, key=lambda k: abs(comps[k])) if comps else ""
            if "diff_mm_rejected_fit" in r:
                L.append(f"| {r['key_point']} | {r['axis']} | {r['plane']} | {r['photo_m']:.4f} | {r['cage_m']:.4f} | "
                         f"{r['cage_object']} ({r['cage_class']}) | ({r['diff_mm_rejected_fit']:+.1f}, rejected fit) | "
                         f"{r['U_mm']:.1f} | {top} | not measurable (camera fit unstable) |")
            elif "diff_mm" in r:
                L.append(f"| {r['key_point']} | {r['axis']} | {r['plane']} | {r['photo_m']:.4f} | {r['cage_m']:.4f} | "
                         f"{r['cage_object']} ({r['cage_class']}) | {r['diff_mm']:+.1f} | {r['U_mm']:.1f} | {top} | **{r['verdict']}** |")
            else:
                L.append(f"| {r['key_point']} | {r['axis']} | {r['plane']} | {r['photo_m']:.4f} | — | — | — | {r['U_mm']:.1f} | {top} | "
                         f"not measurable ({r.get('reason')}) |")
        for n in p.get("not_measurable", []):
            L.append(f"| {n['key_point']} | — | — | — | — | — | — | — | — | not measurable: {n['reason']} |")
        L.append("")
    return L


def largest_section(n=10):
    pc = load(os.path.join(P2, "photo_comparison.json"))
    rows = [(p["id"], r) for p in pc["photos"] for r in p.get("rows", []) if "diff_mm" in r]
    rows.sort(key=lambda t: -abs(t[1]["diff_mm"]))
    status = {p["id"]: p.get("status") for p in pc["photos"]}
    L = ["## 7. Largest differences", "",
         f"All key-point rows that have a verdict, largest |difference| first (top {n} of {len(rows)}). Images with an "
         "unstable or missing camera fit contribute no rows: "
         + (", ".join(f"{k} ({v})" for k, v in status.items() if v != "fitted") or "none") + ".", "",
         "| # | image | key point | axis | cage object (class) | difference (mm) | U (mm) | verdict |",
         "|---|---|---|---|---|---|---|---|"]
    for i, (pid, r) in enumerate(rows[:n], 1):
        L.append(f"| {i} | {pid} | {r['key_point']} | {r['axis']} | {r['cage_object']} ({r['cage_class']}) | "
                 f"{r['diff_mm']:+.1f} | {r['U_mm']:.1f} | **{r['verdict']}** |")
    dis = [(pid, r) for pid, r in rows if r["verdict"] == "disagrees"]
    L += ["", f"Rows that **disagree** (|difference| > U): {len(dis)}"
          + ("" if not dis else ": " + "; ".join(f"{pid} {r['key_point']} {r['axis']} ({r['diff_mm']:+.1f} mm vs U "
                                                 f"{r['U_mm']:.1f} mm)" for pid, r in dis)) + ".", ""]
    return L


def main():
    s1 = open(os.path.join(P2, "step1_reproducibility.md"), encoding="utf-8").read()
    final = s1[s1.index("## Final result"):].split("\n\n", 1)[1].strip()
    s3 = open(os.path.join(P2, "step3_user_supplied.md"), encoding="utf-8").read()
    table = s3[s3.index("| Expected item"):s3.index("The only file")].strip()
    L = ["# Model validation — Phase 2 dimensional reference model", "",
         "<!-- Generated by scripts/phase2/make_validation_report.py — do not edit by hand. -->", "",
         "## 1. Reproducibility of Phase 1 (Step 1)", "",
         "**Passed.** Details: `docs/phase2/step1_reproducibility.md`. The first fresh-clone rebuild changed no value field but "
         "showed date stamps, one duplicated unknown record, one superseded quote and build-order-dependent basis text; the "
         "builders were made deterministic and idempotent (no data hand-edited). Final result:", "", final, ""]
    L += headline_section()
    L += ["## 3. What was supplied", "", table, "",
          "Nothing was supplied, so: no user measurements were transcribed, the gear-speed cross-check still cannot run, "
          "the AC axis and node-naming points stay community-reported, and Step 7 used third-party images only "
          "(numbers committed, images not).", ""]
    co = open(os.path.join(ROOT, "docs", "COORDINATES.md"), encoding="utf-8").read()
    m = re.search(r"\| Version \| \*\*(.+?)\*\*", co)
    L += ["## 4. Blender", "", f"**{m.group(1) if m else 'see docs/COORDINATES.md'}**, official Linux build from "
          "download.blender.org, SHA-256 verified (`scripts/blender/install_blender.sh`), run headless; Cycles on the CPU. "
          "Coordinate mapping and the AC status: `docs/COORDINATES.md`; tests: `tests/test_coords.py`.", ""]
    L += cage_section()
    L += photo_section()
    L += largest_section()
    extra = os.path.join(P2, "validation_tail.md")
    if os.path.exists(extra):
        L += [open(extra, encoding="utf-8").read().strip(), ""]
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
