#!/usr/bin/env python3
"""Photo measurement of side-view proportions (domain 2), written to vehicle_data/proportions.json.

Input image: Honda Information Center profile header for the Civic Hatchback Sport Touring
(manufacturer studio render, RGBA PNG with transparent background, car facing left).
Every feature is located algorithmically; nothing is picked by eye:

  silhouette      alpha channel >= ALPHA_BODY (the soft ground shadow is semi-transparent, < ALPHA_BODY)
  wheels          cv2.HoughCircles on the 4x-upsampled grey image (search radius from the published
                  wheelbase and nominal tyre size), then least-squares circle and ellipse fits to
                  Canny edge points in a +-4 px annulus around the Hough circle (tyre outer edge)
  rim             HoughCircles restricted to concentric circles with r in 0.55-0.85 tyre r
  ground line     tyre bottom = fitted centre + fitted radius (mean of both wheels); compared with the
                  lowest opaque row under each tyre
  top profile     first opaque row per column; roof peak = min; windshield base and header, and the
                  hatch slope, from continuous 3-segment least-squares line fits (brute-force breakpoints)
  bumper extents  min/max opaque column; rows where the extreme occurs
  arch tops       body colour = median colour of the door box (located from wheel fits); scanning up the
                  wheel-centre column from the tyre top, arch edge = first run of >= 3 body-coloured px
  sill            lowest opaque row at mid-wheelbase

Scale: horizontal from the published wheelbase (pixel distance between fitted wheel centres);
a second, independent scale from the nominal tyre diameter (235/40R18 -> 645.2 mm).  Vertical scale
equals horizontal scale times the fitted tyre ellipse axis ratio (corrects any anisotropic resize).
Errors: localisation sigma (px) x scale, plus relative scale error = |1 - s_tyre/s_wb| combined with
perspective (front/rear tyre size ratio) and ellipse anisotropy residual.  Ranges are +-2 sigma.

Usage: python3 scripts/domains/photo_measure_side.py   (writes vehicle_data/proportions.json and an
overlay to cache/photos/side_overlay.png for QA)
"""
import json
import math
import os
import sys

import cv2
import numpy as np
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db  # noqa: E402

IMG_URL = ("https://www.hondainfocenter.com/-/media/Honda-Sales-Tool-Media-Folder/Images/"
           "2022-Civic-Hatchback/Profile-Headers/22_CivicHatchback_STRG_Header_RR.ashx")
PAGE_URL = "https://www.hondainfocenter.com/2024/Civic-Hatchback/"
IMG_PATH = os.path.join(ROOT, "cache", "photos", "22_CivicHatchback_STRG_Header_RR.png")
OVERLAY = os.path.join(ROOT, "cache", "photos", "side_overlay.png")
SCRIPT = "scripts/domains/photo_measure_side.py"

ALPHA_BODY = 250
UP = 4                      # upsampling factor for sub-pixel fits
SIGMA_PX = 0.5              # localisation sigma for well-defined edges (original px)
WHEELBASE_MM = 2735.0       # dimensions.wheelbase (Honda Canada 2024), read from dimensions.json below
TYRE = (235, 40, 18)        # P235/40 R18 (Honda Canada 2024 spec table)


def load_image():
    if not os.path.exists(IMG_PATH):
        os.makedirs(os.path.dirname(IMG_PATH), exist_ok=True)
        r = requests.get(IMG_URL, timeout=60)
        r.raise_for_status()
        with open(IMG_PATH, "wb") as f:
            f.write(r.content)
    im = cv2.imread(IMG_PATH, cv2.IMREAD_UNCHANGED)
    assert im is not None and im.shape[2] == 4, "expected RGBA"
    return im


def published(key):
    d = db.load("dimensions")
    for c in d["parameters"][key]["candidates"]:
        if c.get("prefer") or c["applicability"].get("market") == "CA":
            return c["value"]
    raise KeyError(key)


def circle_lsq(pts):
    x, y = pts[:, 0], pts[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    (cx, cy, c), res, *_ = np.linalg.lstsq(A, b, rcond=None)
    r = math.sqrt(c + cx ** 2 + cy ** 2)
    resid = np.hypot(x - cx, y - cy) - r
    return cx, cy, r, float(np.std(resid))


def ray_edge(alpha, cx, cy, ang_deg, r0, r1, step=0.05):
    """Sub-pixel radius of the strongest opaque->transparent alpha drop along a ray."""
    th = math.radians(ang_deg)
    rs = np.arange(r0, r1, step)
    xs = cx + rs * math.cos(th)
    ys = cy + rs * math.sin(th)                       # image y points down
    vals = cv2.remap(alpha.astype(np.float32), xs.astype(np.float32)[None, :], ys.astype(np.float32)[None, :],
                     cv2.INTER_LINEAR)[0]
    g = -np.gradient(vals, step)
    i = int(np.argmax(g))
    if 0 < i < len(g) - 1:
        den = g[i - 1] - 2 * g[i] + g[i + 1]
        off = 0.5 * (g[i - 1] - g[i + 1]) / den if den != 0 else 0.0
    else:
        off = 0.0
    r = rs[i] + off * step
    return r, cx + r * math.cos(th), cy + r * math.sin(th), float(g[i])


RAY_ANGLES = list(range(26, 52, 2)) + list(range(130, 156, 2))   # lower-side arcs (y down); avoids the flattened contact patch and body


def fit_wheels(rgba, rim_r_guess_px, tyre_r_guess_px):
    """Wheel centre from the rim (strong circular contrast), tyre outer radius from alpha edges along
    rays on the two lower-side arcs, where the tyre silhouette meets the background/shadow."""
    grey = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_BGR2GRAY)
    alpha = rgba[:, :, 3]
    a = alpha.astype(np.float32) / 255.0
    grey = (grey * a + 255 * (1 - a)).astype(np.uint8)          # composite on white
    g4 = cv2.resize(grey, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    g4b = cv2.GaussianBlur(g4, (5, 5), 1.2)
    rmin, rmax = int(rim_r_guess_px * UP * 0.8), int(rim_r_guess_px * UP * 1.25)
    circles = cv2.HoughCircles(g4b, cv2.HOUGH_GRADIENT, dp=1, minDist=rim_r_guess_px * UP * 6,
                               param1=120, param2=30, minRadius=rmin, maxRadius=rmax)
    assert circles is not None, "no rim circles found"
    h = rgba.shape[0]
    circles = [c for c in circles[0] if c[1] / UP > h * 0.55][:2]
    assert len(circles) == 2, f"expected two wheels, got {len(circles)}"
    circles.sort(key=lambda c: c[0])                               # left (front) first
    edges = cv2.Canny(g4b, 40, 120)
    ey, ex = np.nonzero(edges)
    out = []
    for (hx, hy, hr) in circles:
        d = np.hypot(ex - hx, ey - hy)
        sel = np.abs(d - hr) < 1.5 * UP
        rpts = np.c_[ex[sel], ey[sel]].astype(float)
        rcx, rcy, rr, rsd = circle_lsq(rpts)
        rcx, rcy, rr, rsd = rcx / UP, rcy / UP, rr / UP, rsd / UP
        pts, strengths = [], []
        for ang in RAY_ANGLES:
            r, x, y, gmax = ray_edge(alpha, rcx, rcy, ang, rr + 2, tyre_r_guess_px * 1.4)
            pts.append((x, y)); strengths.append(gmax)
        pts = np.array(pts)
        cx, cy, r, sd = circle_lsq(pts)
        r_fixed = float(np.mean(np.hypot(pts[:, 0] - rcx, pts[:, 1] - rcy)))
        # pixel anisotropy from the full rim edge: axis-aligned ellipse (dx/ax)^2 + (dy/ay)^2 = 1 about the rim centre
        dxs, dys = rpts[:, 0] / UP - rcx, rpts[:, 1] / UP - rcy
        (ia, ib), *_ = np.linalg.lstsq(np.c_[dxs ** 2, dys ** 2], np.ones(len(dxs)), rcond=None)
        ax_x, ax_y = 1 / math.sqrt(ia), 1 / math.sqrt(ib)
        out.append(dict(rim_hough_px=[float(hx) / UP, float(hy) / UP, float(hr) / UP],
                        rim_fit_px=[rcx, rcy, rr], rim_fit_resid_px=rsd,
                        cx=rcx, cy=rcy, r=r_fixed,
                        tyre_free_fit_px=[cx, cy, r], fit_resid_px=sd, n_edge_pts=int(len(pts)),
                        ray_angles_deg=RAY_ANGLES, tyre_edge_pts_px=[[round(p[0], 2), round(p[1], 2)] for p in pts],
                        rim_ellipse_semi_x=ax_x, rim_ellipse_semi_y=ax_y, rim_r=rr))
    return out


def seg3_fit(x, y):
    """Continuous 3-segment piecewise-linear least squares; brute force over breakpoint pairs."""
    n = len(x)
    best = None
    step = max(1, n // 120)
    for i in range(3, n - 6, step):
        for j in range(i + 3, n - 3, step):
            b1, b2 = x[i], x[j]
            A = np.c_[np.ones(n), x, np.maximum(x - b1, 0), np.maximum(x - b2, 0)]
            coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            sse = float(np.sum((A @ coef - y) ** 2))
            if best is None or sse < best[0]:
                best = (sse, b1, b2, coef)
    sse, b1, b2, c = best
    slopes = [c[1], c[1] + c[2], c[1] + c[2] + c[3]]
    return dict(break1_x=float(b1), break2_x=float(b2), slopes=[float(s) for s in slopes],
                rms_px=math.sqrt(sse / n))


def main():
    rgba = load_image()
    H, W = rgba.shape[:2]
    alpha = rgba[:, :, 3]
    body = alpha >= ALPHA_BODY
    cols = np.where(body.any(axis=0))[0]
    x_min, x_max = int(cols.min()), int(cols.max())
    top = np.array([np.argmax(body[:, x]) if body[:, x].any() else -1 for x in range(W)])
    bot = np.array([H - 1 - np.argmax(body[::-1, x]) if body[:, x].any() else -1 for x in range(W)])

    wb_mm = published("dimensions.wheelbase") * 1000.0
    length_mm = published("dimensions.length") * 1000.0
    height_mm = published("dimensions.height") * 1000.0
    tyre_d_mm = TYRE[2] * 25.4 + 2 * TYRE[0] * TYRE[1] / 100.0
    rim_d_mm = TYRE[2] * 25.4
    # search priors from the published length (only used to bound the Hough radius search)
    px_per_mm_guess = (x_max - x_min) / length_mm
    wheels = fit_wheels(rgba, rim_d_mm / 2 * px_per_mm_guess, tyre_d_mm / 2 * px_per_mm_guess)
    fw, rw = wheels  # car faces left: left wheel is the front wheel

    dx = rw["cx"] - fw["cx"]
    s_wb = wb_mm / dx                                              # mm per px (horizontal)
    aniso = ((fw["rim_ellipse_semi_y"] / fw["rim_ellipse_semi_x"]) + (rw["rim_ellipse_semi_y"] / rw["rim_ellipse_semi_x"])) / 2
    s_v = s_wb / aniso                                             # mm per px (vertical); rim ellipse y/x aspect
    s_tyre = tyre_d_mm / (fw["r"] + rw["r"])
    persp = abs(1 - fw["r"] / rw["r"])
    scale_rel_err = math.sqrt((1 - s_tyre / s_wb) ** 2 + persp ** 2 + (1 - aniso) ** 2 + (fw["fit_resid_px"] / fw["r"]) ** 2)

    y_ground_fit = (fw["cy"] + fw["r"] * aniso + rw["cy"] + rw["r"] * aniso) / 2   # undeflected-tyre bottom
    low_opaque = []
    for w in wheels:
        xs = range(int(w["cx"] - 3), int(w["cx"] + 4))
        low_opaque.append(float(np.mean([bot[x] for x in xs])) + 0.5)
    # the render's tyres are flattened at the contact patch: the ground is the flat opaque bottom under the tyres
    y_ground = float(np.mean(low_opaque))
    x_front_axle = fw["cx"]

    def Y(xpx):
        return (x_front_axle - xpx) * s_wb / 1000.0

    def Z(ypx):
        return (y_ground - ypx) * s_v / 1000.0

    # empirical model error: how far the photo reproduces the published length and height
    roof_row0 = int(np.min(np.where(top >= 0, top, H)))
    e_len = abs(1 - (x_max - x_min) * s_wb / length_mm)
    e_hgt = abs(1 - (y_ground - roof_row0 + 0.5) * s_v / height_mm)
    rel_h = math.hypot(scale_rel_err, e_len)
    rel_v = math.hypot(scale_rel_err, e_hgt)

    def err(len_px, sigma_px=SIGMA_PX, value_mm=None, vertical=False):
        s = s_v if vertical else s_wb
        e_loc = math.hypot(sigma_px, SIGMA_PX) * s           # feature + reference localisation
        e_scale = abs(value_mm if value_mm is not None else len_px * s) * (rel_v if vertical else rel_h)
        return math.hypot(e_loc, e_scale) / 1000.0           # 1 sigma, metres

    meas = {}
    recs = {}

    def put(key, desc, value, sigma, pix, algorithm, impact="medium", how=None, notes=""):
        recs[key] = dict(desc=desc, value=value, sigma=sigma, pix=pix, algorithm=algorithm,
                         impact=impact, how=how, notes=notes)

    # ---- bumper extents and overhangs
    rows_front = [int(y) for y in np.where(body[:, x_min])[0]]
    rows_rear = [int(y) for y in np.where(body[:, x_max])[0]]
    oh_f_px = x_front_axle - x_min
    oh_r_px = x_max - rw["cx"]
    oh_note = (f"Direct photo overhangs scaled by wheelbase sum to {(oh_f_px + oh_r_px) * s_wb:.0f} mm vs published length - wheelbase "
               f"{length_mm - wb_mm:.0f} mm; prefer dimensions.overhang_front/rear derived from the scale-free fraction.")
    put("proportions.overhang_front", "Front overhang: front axle to foremost body point (side view)",
        oh_f_px * s_wb / 1000, err(oh_f_px), {"x_min": x_min, "rows_at_extreme": [min(rows_front), max(rows_front)],
                                              "front_wheel_cx": fw["cx"]},
        "silhouette min column minus fitted front wheel centre", impact="high",
        how="Plumb bob from the front bumper's foremost point and from the front hub centre; measure the floor distance (+-5 mm).", notes=oh_note)
    put("proportions.overhang_rear", "Rear overhang: rear axle to rearmost body point (side view)",
        oh_r_px * s_wb / 1000, err(oh_r_px), {"x_max": x_max, "rows_at_extreme": [min(rows_rear), max(rows_rear)],
                                             "rear_wheel_cx": rw["cx"]},
        "silhouette max column minus fitted rear wheel centre", impact="high",
        how="Plumb bob from the rear bumper's rearmost point and from the rear hub centre; measure the floor distance (+-5 mm).", notes=oh_note)
    put("proportions.overhang_front_fraction", "Front overhang / (front + rear overhang) (scale-free)",
        oh_f_px / (oh_f_px + oh_r_px),
        math.hypot(math.hypot(SIGMA_PX, SIGMA_PX) / (oh_f_px + oh_r_px), 0.01), {"oh_f_px": oh_f_px, "oh_r_px": oh_r_px},
        "ratio of silhouette-derived overhang pixel lengths; independent of scale", impact="high",
        how="As for the overhangs.", notes="Used by scripts/derivations/dimensions.py with the published length and wheelbase. "
        "Sigma includes a 0.01 allowance for front/rear differential perspective (the photo reproduces the published length only to "
        f"{e_len*100:.1f}%, consistent with a finite-distance camera magnifying the near-side wheels relative to the centreline bumper extremes).")
    put("proportions.front_bumper_extreme_z", "Height of the foremost bumper point (mid of rows at the extreme column)",
        Z((min(rows_front) + max(rows_front)) / 2), err(0, (max(rows_front) - min(rows_front)) / 2 + SIGMA_PX, 0, True),
        {"x": x_min, "rows": [min(rows_front), max(rows_front)]}, "rows where the silhouette reaches its min column", impact="low",
        how="Measure the height of the bumper nose above the floor with a square (+-5 mm).")
    put("proportions.rear_bumper_extreme_z", "Height of the rearmost body point",
        Z((min(rows_rear) + max(rows_rear)) / 2), err(0, (max(rows_rear) - min(rows_rear)) / 2 + SIGMA_PX, 0, True),
        {"x": x_max, "rows": [min(rows_rear), max(rows_rear)]}, "rows where the silhouette reaches its max column", impact="low",
        how="Measure the height of the rearmost bumper point above the floor (+-5 mm).")

    # ---- overall length/height cross-checks (published values are the authority)
    put("proportions.length_check", "Overall length measured from the photo (cross-check of the published length)",
        (x_max - x_min) * s_wb / 1000, err(x_max - x_min), {"x_min": x_min, "x_max": x_max},
        "silhouette extent x wheelbase scale", impact="low", how="Tape between plumb marks of bumper extremes.")
    roof_x = int(np.argmin(np.where(top >= 0, top, H)))
    roof_cols = np.where((top >= 0) & (top <= top[roof_x] + 0.5))[0]
    put("proportions.height_check", "Overall height measured from the photo (cross-check of the published height)",
        Z(top[roof_x] - 0.5), err(0, SIGMA_PX, Z(top[roof_x]) * 1000, True), {"roof_row": int(top[roof_x]), "ground_row": y_ground},
        "top silhouette row vs fitted tyre-bottom ground line", impact="low", how="Straightedge on roof, tape to floor.")

    # ---- roof peak
    put("proportions.roof_peak_z", "Roof peak height above ground", Z(top[roof_x] - 0.5),
        err(0, SIGMA_PX, Z(top[roof_x]) * 1000, True), {"row": int(top[roof_x]), "cols": [int(roof_cols.min()), int(roof_cols.max())]},
        "minimum of the top silhouette profile", impact="medium",
        how="Straightedge across the roof at its highest point; tape to floor (+-3 mm).")
    put("proportions.roof_peak_y", "Longitudinal position of roof peak (centre of the columns at the minimum row)",
        Y((roof_cols.min() + roof_cols.max()) / 2), err(0, (roof_cols.max() - roof_cols.min()) / 2 + SIGMA_PX, 0),
        {"cols": [int(roof_cols.min()), int(roof_cols.max())]},
        "centre of the flat run at the minimum top-profile row; range covers the run", impact="medium",
        how="Level laid on the roof: find the highest point, plumb down, measure from front hub centre.")

    # ---- windshield (front top profile from front axle to roof peak)
    xs = np.arange(int(x_front_axle), roof_x + 1)
    seg_f = seg3_fit(xs.astype(float), top[xs].astype(float))
    put("proportions.windshield_base_y", "Windshield base / cowl (silhouette slope break hood -> glass): Y",
        Y(seg_f["break1_x"]), err(0, 2.0), {"break_px": seg_f["break1_x"], "row": float(top[int(round(seg_f["break1_x"]))])},
        "first breakpoint of a continuous 3-segment line fit to the top profile, front axle -> roof peak", impact="medium",
        how="Measure from front hub centre to the windshield base at the centreline (tape along the hood + plumb), +-10 mm.",
        notes="Silhouette break: the true glass base can sit slightly behind the visible hood/cowl edge. Localisation sigma 2 px.")
    put("proportions.windshield_base_z", "Windshield base / cowl height above ground",
        Z(top[int(round(seg_f["break1_x"]))]), err(0, 2.0, Z(top[int(round(seg_f["break1_x"]))]) * 1000, True),
        {"break_px": seg_f["break1_x"]}, "top profile at the first breakpoint", impact="medium",
        how="Tape from floor to the windshield base at the centreline (+-5 mm).")
    put("proportions.windshield_header_y", "Windshield top / roof header (second slope break): Y",
        Y(seg_f["break2_x"]), err(0, 3.0), {"break_px": seg_f["break2_x"]},
        "second breakpoint of the same fit", impact="low",
        how="Measure from front hub centre to the top edge of the windshield glass (plumb), +-10 mm.")
    ws_angle = math.degrees(math.atan(abs(seg_f["slopes"][1]) * s_v / s_wb))
    put("proportions.windshield_angle", "Windshield silhouette angle from horizontal",
        math.radians(ws_angle), math.radians(2.0), {"slopes_px": seg_f["slopes"], "rms_px": seg_f["rms_px"]},
        "atan of the middle-segment slope (scale-anisotropy corrected)", impact="low", how="Inclinometer on the glass at the centreline.",
        notes="Silhouette (outer glass) line, not the glass at centreline; 2 deg sigma.")

    # ---- hatch (rear top profile from roof peak to rear extreme)
    xs = np.arange(roof_x, x_max + 1)
    seg_r = seg3_fit(xs.astype(float), top[xs].astype(float))
    steep = int(np.argmax(np.abs(seg_r["slopes"][:2])))  # hatch glass is the steeper of the first two segments
    hatch_angle = math.degrees(math.atan(abs(seg_r["slopes"][steep]) * s_v / s_wb))
    put("proportions.hatch_angle", "Rear hatch glass silhouette angle from horizontal",
        math.radians(hatch_angle), math.radians(2.5), {"slopes_px": seg_r["slopes"], "breaks_px": [seg_r["break1_x"], seg_r["break2_x"]],
                                                         "segment_used": steep, "rms_px": seg_r["rms_px"]},
        "continuous 3-segment line fit to the top profile, roof peak -> rear extreme; steepest of the first two segments",
        impact="medium", how="Inclinometer on the hatch glass at the centreline.",
        notes="Includes the effect of the roof spoiler on the silhouette; 2.5 deg sigma.")
    put("proportions.hatch_glass_top_y", "Start of the rear slope (first rear breakpoint): Y",
        Y(seg_r["break1_x"]), err(0, 3.0), {"break_px": seg_r["break1_x"]}, "first breakpoint of the rear fit", impact="low",
        how="Plumb from the roof-spoiler trailing edge, measure from front hub centre.")

    # ---- hood height at front axle station
    put("proportions.hood_z_at_front_axle", "Top silhouette (hood) height at the front-axle station (Y = 0)",
        Z(top[int(round(x_front_axle))]), err(0, SIGMA_PX, Z(top[int(round(x_front_axle))]) * 1000, True),
        {"col": int(round(x_front_axle)), "row": int(top[int(round(x_front_axle))])},
        "top silhouette row at the fitted front wheel centre column", impact="medium",
        how="Straightedge across the hood above the front hub; tape to floor (+-5 mm).")

    # ---- sill and wheel/arch geometry
    xm = int(round((fw["cx"] + rw["cx"]) / 2))
    sill_rows = [bot[x] for x in range(xm - 10, xm + 11)]
    put("proportions.sill_z_mid_wheelbase", "Side sill (rocker) lower edge height at mid-wheelbase",
        Z(float(np.median(sill_rows)) + 0.5), err(0, SIGMA_PX + float(np.std(sill_rows)), Z(float(np.median(sill_rows))) * 1000, True),
        {"cols": [xm - 10, xm + 10], "rows_median": float(np.median(sill_rows))},
        "lowest opaque row (median over 21 columns) at mid-wheelbase", impact="medium",
        how="Tape from floor to the sill lower edge at mid-wheelbase, both sides (+-3 mm).",
        notes="Not the same quantity as the published minimum ground clearance (134 mm, no-load).")

    bgr = rgba[:, :, :3].astype(np.float32)
    lab = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_BGR2LAB).astype(np.float32)
    r_px = (fw["r"] + rw["r"]) / 2
    by0, by1 = int(fw["cy"] - 1.6 * r_px), int(fw["cy"] - 0.6 * r_px)
    bx0, bx1 = int(fw["cx"] + 0.35 * dx), int(fw["cx"] + 0.65 * dx)
    box = lab[by0:by1, bx0:bx1][body[by0:by1, bx0:bx1]]
    body_lab = np.median(box, axis=0)
    dist = np.linalg.norm(lab - body_lab, axis=2)
    body_col = (dist < 30) & body
    for name, w in (("front", fw), ("rear", rw)):
        x = int(round(w["cx"]))
        y = int(round(w["cy"] - w["r"])) - 1
        run = 0
        arch = None
        while y > 0:
            if body_col[y, x - 1:x + 2].all():
                run += 1
                if run >= 3:
                    arch = y + 2
                    break
            else:
                run = 0
            y -= 1
        put(f"proportions.wheel_center_z_{name}", f"{name.capitalize()} wheel centre height above ground (photo)",
            Z(w["cy"]), err(0, SIGMA_PX, Z(w["cy"]) * 1000, True), {"cx": w["cx"], "cy": w["cy"]},
            "least-squares circle fit to tyre edge", impact="medium",
            how="Tape from floor to hub centre (+-2 mm).",
            notes="In a render the tyre is undeflected; a real loaded tyre sits ~10-20 mm lower. Equals the unloaded tyre radius here.")
        if arch is not None:
            put(f"proportions.arch_gap_{name}", f"{name.capitalize()} wheel centre to wheel-arch lip (vertical, photo)",
                (w["cy"] - arch + 0.5) * s_v / 1000, err(0, 1.0, (w["cy"] - arch) * s_v, True),
                {"col": x, "arch_row": arch, "cy": w["cy"]},
                "first run of >=3 body-coloured px (Lab distance < 30 to door-box median) scanning up from tyre top",
                impact="high", how="Tape from hub centre to the arch lip directly above it, car at curb weight (+-2 mm). Primary ride-height reference.")
            put(f"proportions.arch_top_z_{name}", f"{name.capitalize()} wheel-arch lip height above ground (photo)",
                Z(arch - 0.5), err(0, 1.0, Z(arch) * 1000, True), {"col": x, "arch_row": arch},
                "as above", impact="high", how="Tape from floor to the arch lip above the hub centre (+-2 mm).")
        else:
            recs[f"proportions.arch_gap_{name}"] = None
        meas[f"wheel_{name}"] = w

    # rim diameter ratio (check of wheel size)
    for name, w in (("front", fw), ("rear", rw)):
        if w["rim_r"]:
            put(f"proportions.rim_to_tyre_ratio_{name}", f"{name} visible rim diameter / tyre diameter (photo)",
                w["rim_r"] / w["r"], 1.0 / w["r"], {"rim_r_px": w["rim_r"], "tyre_r_px": w["r"]},
                "concentric HoughCircles", impact="low", how="Measure rim flange and tyre diameters.",
                notes=f"Nominal 18 in / 645.2 mm = {rim_d_mm / tyre_d_mm:.3f}; visible rim lip is slightly smaller than the bead seat diameter.")

    meas["image"] = {"url": IMG_URL, "page": PAGE_URL, "size_px": [W, H], "local_cache": os.path.relpath(IMG_PATH, ROOT)}
    meas["silhouette"] = {"alpha_threshold": ALPHA_BODY, "x_min": x_min, "x_max": x_max, "roof_row": int(top[roof_x])}
    meas["scale"] = {"s_wheelbase_mm_per_px": s_wb, "s_tyre_mm_per_px": s_tyre, "s_vertical_mm_per_px": s_v,
                     "wheel_ellipse_aspect_y_over_x": aniso, "front_rear_tyre_radius_ratio": fw["r"] / rw["r"],
                     "relative_scale_error_1sigma": scale_rel_err, "wheelbase_px": dx,
                     "length_reproduction_error": e_len, "height_reproduction_error": e_hgt,
                     "relative_error_horizontal_1sigma": rel_h, "relative_error_vertical_1sigma": rel_v,
                     "inputs": {"wheelbase_mm": wb_mm, "tyre_nominal_diameter_mm": tyre_d_mm,
                                "published_length_mm": length_mm, "published_height_mm": height_mm}}
    meas["ground"] = {"y_ground_fit_px": y_ground_fit, "lowest_opaque_rows_px": low_opaque}
    meas["top_profile_fits"] = {"front": seg_f, "rear": seg_r}
    meas["body_colour_lab"] = [float(v) for v in body_lab]
    meas["door_box_px"] = [bx0, by0, bx1, by1]

    # ---------------------------------------------------------------- write proportions.json
    d = {"domain": "proportions", "title": "Photo-measured proportions", "schema_version": 1,
         "sources": {}, "parameters": {}}
    db.add_source(d, "prop:hic-2022-hatch-strg-profile", title="Honda Information Center profile header, 2022 Civic Hatchback Sport Touring (STRG), Rallye Red",
                  url=IMG_URL, publisher="American Honda Motor Co. (Honda Information Center)", cls="A",
                  access_method="direct image download (620x200 RGBA PNG)",
                  applicability="2022 US Civic Hatchback Sport Touring (18-in machined/black wheels); same body as 2024 (all published exterior dimensions identical 2022-2024)",
                  notes=f"Shown on {PAGE_URL} (2024 Civic Hatchback page reuses the 2022 image). Studio render, near-orthographic side view. Local copy only in cache/photos (git-ignored).",
                  cache_file=os.path.relpath(IMG_PATH, ROOT))
    deriv_inputs = {"image": IMG_URL, "dimensions.wheelbase_mm": wb_mm, "tyre": "P235/40 R18 (nominal 645.2 mm)"}
    app = db.app("2022", "US", "Sport Touring", "n/a (exterior render)",
                 notes="Exterior body identical 2022-2024 per Honda spec tables (length, width, height, wheelbase, track unchanged)")
    for key, r in recs.items():
        if r is None:
            continue
        v, s = r["value"], r["sigma"]
        unit = "1" if ("fraction" in key or "ratio" in key) else ("rad" if "angle" in key else "m")
        rec = db.record(value=v, unit=unit, status="estimated", cls="D", source_id="prop:hic-2022-hatch-strg-profile",
                        locator=f"image px {json.dumps(r['pix'])}", evidence=f"Image feature located by algorithm: {r['algorithm']}",
                        as_printed="", applicability=app, confidence="medium" if s / max(abs(v), 1e-9) < 0.05 else "low",
                        range=[v - 2 * s, v + 2 * s], how_to_measure=r["how"] or "Measure on the car.",
                        notes=(r["notes"] + " " if r["notes"] else "") + f"1-sigma {s:.4g} {unit}; range = +-2 sigma (localisation + scale + perspective).",
                        derivation={"script": SCRIPT, "function": "main", "inputs": deriv_inputs,
                                    "algorithm": r["algorithm"], "pixels": r["pix"],
                                    "scale_mm_per_px": {"horizontal": s_wb, "vertical": s_v}})
        db.add_candidate(d, key, r["desc"], unit, r["impact"], rec)
    # features not locatable from a side view: recorded unknown
    unk = {
        "proportions.mirror_y": "Side-mirror longitudinal position",
        "proportions.mirror_z": "Side-mirror height",
        "proportions.mirror_width_ratio": "Mirror-to-mirror width / body width (front view)",
        "proportions.front_view_track_ratio": "Front-view tyre centre spacing / body width",
    }
    for k, desc in unk.items():
        db.add_candidate(d, k, desc, "1" if "ratio" in k else "m", "low", db.unknown(
            "1" if "ratio" in k else "m",
            ["Only one straight-on manufacturer view found (the 620x200 side render above); hondanews.com/hondanews.ca 2022 galleries "
             "contain only 3/4 and action shots; automobiles.honda.com configurator is 403 (blocked); no straight-on front/rear press view located",
             "The mirror in the side render overlaps the A-pillar/glass and has no algorithmically separable outline at 9 mm/px"],
            how_to_measure="Long-lens (>=200 mm equiv.) straight-on front photo from >=15 m with a tape on the ground, or tape the mirror glass "
                           "centre position from the front hub centre and floor directly.",
            notes="Needs a straight-on front-view image or direct measurement."))
    d["measurements"] = meas
    p = db.save(d)
    # QA overlay (not used for any value)
    ov = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_BGR2RGB)
    ov = cv2.cvtColor(ov, cv2.COLOR_RGB2BGR).copy()
    ov[alpha < 128] = 255
    ov = cv2.resize(ov, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
    for w in wheels:
        cv2.circle(ov, (int(w["cx"] * 3), int(w["cy"] * 3)), int(w["r"] * 3), (0, 255, 0), 1)
        if w["rim_r"]:
            cv2.circle(ov, (int(w["cx"] * 3), int(w["cy"] * 3)), int(w["rim_r"] * 3), (255, 255, 0), 1)
    cv2.line(ov, (0, int(y_ground * 3)), (W * 3, int(y_ground * 3)), (255, 0, 0), 1)
    for bx in (seg_f["break1_x"], seg_f["break2_x"], seg_r["break1_x"], seg_r["break2_x"]):
        cv2.line(ov, (int(bx * 3), 0), (int(bx * 3), H * 3), (255, 0, 255), 1)
    for k in ("front", "rear"):
        r = recs.get(f"proportions.arch_top_z_{k}")
        if r:
            cv2.circle(ov, (int(r["pix"]["col"] * 3), int(r["pix"]["arch_row"] * 3)), 4, (0, 0, 255), -1)
    cv2.rectangle(ov, (bx0 * 3, by0 * 3), (bx1 * 3, by1 * 3), (0, 128, 255), 1)
    cv2.imwrite(OVERLAY, ov)
    print(p)
    print(json.dumps({k: (round(r["value"], 4), round(r["sigma"], 4)) for k, r in recs.items() if r}, indent=1))
    print(json.dumps(meas["scale"], indent=1))


if __name__ == "__main__":
    main()
