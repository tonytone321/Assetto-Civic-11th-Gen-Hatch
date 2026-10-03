#!/usr/bin/env python3
"""Domain 9: scripted colour statistics for Sonic Grey Pearl (NH-877P) from available images.

Method (recorded in vehicle_data/paint.json -> photo_analysis):
  * Honda colour swatches (hondainfocenter.com, 74x74 RGBA renders): body pixels = alpha > 200;
    specular highlight pixels (L* above the 95th percentile) and the darkest 5 % are dropped.
  * Press photos (hondanews.com previews, 928x522): a coarse rectangle around a painted area is given per
    image (recorded); inside it, pixels are clustered in CIELAB with k-means (k=6, OpenCV, fixed seed).
    The paint cluster is chosen by rule, not by eye: the largest cluster whose mean L* is 25..92 and whose
    mean chroma is below 30 (excludes tyres/glass/grille (dark), lamps/sky reflections (very bright) and
    saturated surroundings). Reported: median sRGB, linear-RGB mean, L*a*b*, chroma, hue and percentiles.
  * Results for the label-confirmed Honda swatch become the colour estimate; press-photo cars are of
    UNCONFIRMED colour (captions name no colour), so they are reported only as context with a
    nearest-swatch distance, never as Sonic Grey Pearl evidence.

Confounders: white balance, exposure, tone curve, coloured scene lighting and JPEG compression all shift
these numbers. Everything written is status 'estimated' with ranges and how_to_measure.

Usage: python3 scripts/domains/paint_analyze.py
"""
import glob
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db  # noqa: E402

V = os.path.join(ROOT, "cache", "visual")
SW_URL = "https://www.hondainfocenter.com/-/media/Honda-Sales-Tool-Media-Folder/Images/{p}"
SWATCHES = {
    "Sonic Gray Pearl NH-877P": ("swatch/Sonic.img", "2018-Civic-Hatch/Color-Swatches/MY18-Civic-Hatch-Sonic-Gray-Pearl.ashx?h=74&w=74&hash=7FD9F8782E22DC01FFB05FBBE73678817D176E95"),
    "Lunar Silver Metallic NH-830M": ("swatch/Lunar.img", "2018-Civic-Hatch/Color-Swatches/MY18-Civic-Hatch-Lunar-Silver-Metallic.ashx?h=74&w=74&hash=00A6078D66F7C2B29DA31FA1BE9FA8D5687F85AB"),
    "Meteorite Gray Metallic NH-904M": ("swatch/Meteorite.img", "2022-Civic-Hatchback/Orbs/Meteorite_Gray_Metalli.ashx?h=74&w=74&hash=BB175A87CB6EAD806855CFF88275DB04"),
}
PK = "https://wieck-honda-production.s3.amazonaws.com/photos/{h}/preview-928x522.jpg"
PHOTOS = [  # index, hash, lighting condition (judged from the scene), rectangle x0,y0,x1,y1
    (16, "c928c567621b4f88aa6028f4055c239422fdf477", "daylight, open shade/overcast street", (200, 300, 750, 420)),
    (17, "cd3db434396a7767c7ca2e2ca85bb9ce056f2205", "night, mixed coloured artificial light", (300, 40, 900, 200)),
    (18, "8e7b3cbca24c99dcc87857f936e9f9ae660ec7cf", "low sun, warm backlit street", (310, 260, 700, 480)),
    (20, "e12e8e3340bee4cd9717637daa0e5b84ee88839e", "night, mixed coloured artificial light", (380, 180, 760, 330)),
]


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab_of(rgb_u8):
    """rgb uint8 (N,3) -> CIELAB D65 (OpenCV float path: L 0..100)."""
    a = (rgb_u8.reshape(-1, 1, 3).astype(np.float32) / 255.0)
    return cv2.cvtColor(a, cv2.COLOR_RGB2Lab).reshape(-1, 3)


def stats(px):
    lab = lab_of(px)
    lin = srgb_to_linear(px.astype(np.float64))
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    hue = (np.degrees(np.arctan2(np.median(lab[:, 2]), np.median(lab[:, 1]))) + 360) % 360
    pct = lambda x: [float(np.percentile(x, 10)), float(np.percentile(x, 90))]
    return {
        "n_pixels": int(len(px)),
        "srgb_median": [int(v) for v in np.median(px, axis=0)],
        "srgb_p10_p90": [[int(np.percentile(px[:, i], 10)), int(np.percentile(px[:, i], 90))] for i in range(3)],
        "linear_rgb_mean": [round(float(v), 4) for v in lin.mean(axis=0)],
        "lab_median": [round(float(v), 2) for v in np.median(lab, axis=0)],
        "L_p10_p90": [round(v, 2) for v in pct(lab[:, 0])],
        "chroma_median": round(float(np.median(chroma)), 2),
        "chroma_p10_p90": [round(v, 2) for v in pct(chroma)],
        "hue_deg_of_median_ab": round(float(hue), 1),
    }


def swatch_pixels(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    rgb = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2RGB)
    m = im[:, :, 3] > 200
    px = rgb[m]
    L = lab_of(px)[:, 0]
    lo, hi = np.percentile(L, 5), np.percentile(L, 95)
    keep = (L >= lo) & (L <= hi)
    return px[keep], {"mask": "alpha>200, L* within 5th..95th percentile", "image_size": list(im.shape[:2][::-1])}


def photo_pixels(path, rect):
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
    x0, y0, x1, y1 = rect
    x1, y1 = min(x1, im.shape[1]), min(y1, im.shape[0])
    roi = im[y0:y1, x0:x1].reshape(-1, 3)
    lab = lab_of(roi).astype(np.float32)
    cv2.setRNGSeed(12345)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, lbl, cen = cv2.kmeans(lab, 6, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    lbl = lbl.ravel()
    cl = []
    for k in range(6):
        n = int((lbl == k).sum())
        L, a, b = cen[k]
        cl.append({"k": k, "n": n, "L": round(float(L), 1), "chroma": round(float(np.hypot(a, b)), 1)})
    ok = [c for c in cl if 25 <= c["L"] <= 92 and c["chroma"] < 30]
    if not ok:
        return None, {"clusters": cl, "selected": None}
    sel = max(ok, key=lambda c: c["n"])
    return roi[lbl == sel["k"]], {"rect_xyxy": [x0, y0, x1, y1], "image_size": [im.shape[1], im.shape[0]],
                                  "clusters": cl, "selected_cluster": sel["k"],
                                  "selected_fraction_of_rect": round(sel["n"] / len(lbl), 3)}


def main():
    out = {"method": __doc__.split("Usage")[0].strip(), "swatches": {}, "press_photos": []}
    for name, (rel, url) in SWATCHES.items():
        p = os.path.join(V, rel)
        px, meta = swatch_pixels(p)
        out["swatches"][name] = {"url": SW_URL.format(p=url), "cache_path": "cache/visual/" + rel,
                                 "condition": "Honda CG colour-orb render (studio lighting, unknown renderer/tonemap)",
                                 **meta, **stats(px)}
    sw_lab = {n: np.array(s["lab_median"]) for n, s in out["swatches"].items()}
    for i, h, cond, rect in PHOTOS:
        f = glob.glob(os.path.join(V, "presskit22", f"{i:02d}_{h[:12]}.jpg"))
        if not f:
            continue
        px, meta = photo_pixels(f[0], rect)
        rec = {"id": f"ahm-press22-{i:02d}", "url": PK.format(h=h), "condition": cond,
               "colour_identity": "UNCONFIRMED (caption names no colour)", **meta}
        if px is not None:
            st = stats(px)
            rec.update(st)
            lab = np.array(st["lab_median"])
            rec["deltaE76_to_swatch"] = {n: round(float(np.linalg.norm(lab - v)), 1) for n, v in sw_lab.items()}
        out["press_photos"].append(rec)

    # ------------------------------------------------------------ write estimates into paint.json
    p = db.path_for("paint")
    d = db.load(p)
    d["photo_analysis"] = out
    sgp = out["swatches"]["Sonic Gray Pearl NH-877P"]
    src = "ahm-infocenter-2024-colors"
    deriv = {"script": "scripts/domains/paint_analyze.py", "function": "swatch_pixels+stats",
             "inputs": {"image": sgp["url"], "cache_path": sgp["cache_path"], "mask": sgp["mask"]}}
    how = ("Spectrophotometer reading of a clean door panel (L*a*b* D65/10, multi-angle), or RAW photo of the panel next to an "
           "X-Rite ColorChecker in open shade with white balance set on the checker's neutral patch; then recompute with this script.")
    note = ("Computed from Honda's own 74x74 colour-orb render, the only image whose colour identity is confirmed. A render is "
            "not a measurement: Honda's renderer, lighting and tone mapping are unknown. Press photos of grey Sport Touring cars are "
            "colour-unconfirmed and were not used for this value (see photo_analysis.press_photos).")
    sr = sgp["srgb_median"]
    db.add_candidate(d, "paint.base_srgb", "Representative body colour, sRGB 0-255 (diffuse, mid-tone)", "1", "high", db.record(
        value=sr, unit="1", status="estimated", cls="E", source_id=src, locator="Colors table swatch image (Sonic Gray Pearl)",
        evidence="", as_printed="", applicability=db.app("2024 (MY18 swatch asset)", "US", "all trims", "any"),
        confidence="low", range=[[c[0] for c in sgp["srgb_p10_p90"]], [c[1] for c in sgp["srgb_p10_p90"]]],
        how_to_measure=how, notes=note + " Range = per-channel 10th..90th percentile of masked swatch pixels.", derivation=deriv))
    db.add_candidate(d, "paint.base_lab", "Representative body colour, CIELAB (D65) median of swatch pixels", "1", "high", db.record(
        value=sgp["lab_median"], unit="1", status="estimated", cls="E", source_id=src, locator="Colors table swatch image",
        evidence="", as_printed="", applicability=db.app("2024 (MY18 swatch asset)", "US", "all trims", "any"),
        confidence="low", range=[[sgp["L_p10_p90"][0], None, None], [sgp["L_p10_p90"][1], None, None]],
        how_to_measure=how, notes=note + " Range gives only L* 10th..90th percentile; a*/b* spread: chroma p10..p90 = "
        f"{sgp['chroma_p10_p90']}.", derivation=deriv))
    db.add_candidate(d, "paint.base_chroma", "Chroma C*ab of the body colour (how far from neutral grey)", "1", "medium", db.record(
        value=sgp["chroma_median"], unit="1", status="estimated", cls="E", source_id=src, locator="Colors table swatch image",
        evidence="", as_printed="", applicability={}, confidence="low", range=sgp["chroma_p10_p90"],
        how_to_measure=how, notes=note, derivation=deriv))
    db.add_candidate(d, "paint.base_hue_deg", "Hue angle h_ab of the body colour (deg; ~200-260 = blue-ish grey)", "deg", "medium", db.record(
        value=sgp["hue_deg_of_median_ab"], unit="deg", status="estimated", cls="E", source_id=src, locator="Colors table swatch image",
        evidence="", as_printed="", applicability={}, confidence="low",
        range=[sgp["hue_deg_of_median_ab"] - 30, sgp["hue_deg_of_median_ab"] + 30],
        how_to_measure=how, notes=note + " Range +/-30 deg is a judgement for near-neutral colours, where hue is unstable.",
        derivation=deriv))
    lin = sgp["linear_rgb_mean"]
    db.add_candidate(d, "paint.base_albedo_linear", "Base albedo (linear RGB) for a PBR base layer", "1", "high", db.record(
        value=lin, unit="1", status="estimated", cls="E", source_id=src, locator="Colors table swatch image",
        evidence="", as_printed="", applicability={}, confidence="low",
        range=[[round(v * 0.6, 4) for v in lin], [round(min(1.0, v * 1.5), 4) for v in lin]],
        how_to_measure=how, notes=note + " Range x0.6..x1.5 reflects unknown exposure/tone mapping of the render (judgement).",
        derivation=deriv))
    db.save(d, p)
    print(json.dumps({"swatches": {k: {kk: v[kk] for kk in ("srgb_median", "lab_median", "chroma_median", "hue_deg_of_median_ab")}
                                   for k, v in out["swatches"].items()},
                      "press": [{k: r.get(k) for k in ("id", "condition", "srgb_median", "lab_median", "chroma_median",
                                                       "selected_fraction_of_rect", "deltaE76_to_swatch")} for r in out["press_photos"]]},
                     indent=1))


if __name__ == "__main__":
    main()
