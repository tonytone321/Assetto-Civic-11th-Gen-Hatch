#!/usr/bin/env python3
"""Phase 2, Step 7: compare the reference cage with reference images through a fitted pinhole camera.

For each reference image:
 1. focal length from EXIF (focal mm x focal-plane resolution) or, if absent, estimated and said so;
 2. camera pose fitted to the wheels: projected rim-lip circles matched to image edges (chamfer) plus the
    tyre contact points (lowest silhouette point under each wheel); wheel-centre heights are fitted too.
    Side views without EXIF cannot separate focal length from distance, so the distance is fixed by
    requiring the bumper extremes (assumed on the centreline) to span the published length, and the
    length is then NOT an independent check for that image;
 3. the cage (blender/_build/cage_dump.json, converted with coords.blender_to_project) is projected;
 4. key points are located algorithmically and back-projected onto the plane each is assumed to lie on,
    and differences to the cage are reported in mm;
 5. uncertainty per key point = RSS of: camera-fit spread (bootstrap), localisation, lens distortion,
    principal point (unknown crop), and plane assumption; U = 2 sigma.

Third-party images stay in cache/; only numbers are committed (docs/phase2/photo_comparison.json).
Overlays for checking go to cache/phase2/overlays/.

Run: python3 scripts/phase2/compare_photos.py   (needs blender/_build/cage_dump.json; run
     blender -b blender/reference_cage.blend --python scripts/blender/dump_cage.py -- blender/_build/cage_dump.json)
"""
import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import least_squares, brentq

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "blender"))
import camera as camlib  # noqa: E402
import coords  # noqa: E402
import photo_features as pf  # noqa: E402

RES = json.load(open(os.path.join(ROOT, "vehicle_data", "_resolved.json"), encoding="utf-8"))["parameters"]
V = lambda k: RES[k]["value"]  # noqa: E731
L, W, H = V("dimensions.length"), V("dimensions.width_body"), V("dimensions.height")
WB, TF, TR = V("dimensions.wheelbase"), V("dimensions.track_front"), V("dimensions.track_rear")
TYRE_D, SW, WHEEL_W = V("tires.overall_diameter"), V("tires.section_width"), V("wheels.width")
RIM_D = V("wheels.diameter")
Z_WHEEL0 = V("tires.loaded_radius")
# rim-lip model (stated assumptions, not database values): visible lip = wheel outer flange
FLANGE_H = 0.0175       # J-flange height above bead seat (ETRTO J flange 17.5 mm), m
FLANGE_OUT = 0.010      # flange outboard of the rim width edge, m
LIP_X_SIGMA = 0.02      # m, uncertainty of the lip plane position
OUT_JSON = os.path.join(ROOT, "docs", "phase2", "photo_comparison.json")
D_NOMINAL, D_RANGE = 30.0, (10.0, 100.0)   # side views without EXIF: assumed camera distance (m)
YAW_TEST = math.radians(3.0)               # side views: yaw uncertainty tested by refitting at +-3 deg
H_NOMINAL, H_RANGE = 0.9, (0.4, 1.6)       # side views: camera height (m) is not determined by the wheels; assumed
# camera-fit acceptance: rim-lip and contact residuals must be at the level of edge localisation
GATE_RIM_RMS_PX, GATE_CONTACT_RMS_PX = 2.0, 3.0
OVL = os.path.join(ROOT, "cache", "phase2", "overlays")


def exif_f_px(f_mm, fpxr_per_inch, native_scale):
    """Focal length in pixels of the cached image: f_mm x (pixels per mm on the focal plane) x scale."""
    return f_mm * fpxr_per_inch / 25.4 * native_scale


PHOTOS = [
    dict(id="R1_render_side", manifest="(Phase 1 photo_measure_side source)", kind="side",
         path="cache/photos/22_CivicHatchback_STRG_Header_RR.png", mask="alpha", side=-1, front_on="left",
         wheels=["FL", "RL"], focal=None, k1max=0.0, pp_shift=(0, 0), loc_px=0.5,
         shows="2022 Civic Hatchback Sport Touring (Honda Information Center studio render, CGI, 620x200)"),
    dict(id="R2_press06_side", manifest="ahm-press22-06", kind="oblique", fit_focal=True, rim_polarity=False,
         path="cache/visual/presskit22/06_f7039164019c.jpg", mask="cache/phase2/masks/06_f7039164019c.png",
         side=-1, front_on="left", wheels=["FL", "RL"], focal=None, k1max=0.01, pp_shift=(0, 0), loc_px=None,
         shows="2022 US Civic Hatchback, Boost Blue, black wheels (Sport trim by its wheels), rolling shot, motion blur"),
    dict(id="R3_commons_queens_rear3q", manifest="commons-2022-honda-civic-sport-touring-liftback-rear-6-18-22-jpg",
         kind="3q", path="cache/visual/commons/2022_Honda_Civic_Sport_Touring_liftback,_rear_6.18.22.jpg",
         mask="cache/phase2/masks/2022_Honda_Civic_Sport_Touring_liftback,_rear_6.18.22.png", side=-1, front_on="left",
         wheels=["FL", "RL"], focal=dict(f_mm=184 / 5, fpxr=5472000 / 517, native_w=5472, native_h=3648,
                                          orig_w=4857, orig_h=2100),
         k1max=0.005, loc_px=None, shows="2022 Civic Hatchback Sport Touring, USA (Canon G7 X III, 36.8 mm)"),
    dict(id="R4_commons_canada_front3q", manifest="commons-2022-honda-civic-sport-touring-front-right-11-07-2021-jpg",
         kind="3q", path="cache/visual/commons/2022_Honda_Civic_Sport_Touring,_Front_Right,_11-07-2021.jpg",
         mask="cache/phase2/masks/2022_Honda_Civic_Sport_Touring,_Front_Right,_11-07-2021.png", side=+1,
         front_on="right", wheels=["RR", "FR"], focal=dict(f_mm=12.074, fpxr=4416000 / 292, native_w=4416,
                                                          native_h=3312, orig_w=3876, orig_h=2052),
         k1max=0.03, loc_px=None, shows="2022 Civic Hatchback Sport Touring, Canada (Canon G10, 12.1 mm)"),
    dict(id="R5_commons_canada_rear3q", manifest="commons-2022-honda-civic-sport-touring-rear-left-11-07-2021-jpg",
         kind="3q", path="cache/visual/commons/2022_Honda_Civic_Sport_Touring,_Rear_Left,_11-07-2021.jpg",
         mask="cache/phase2/masks/2022_Honda_Civic_Sport_Touring,_Rear_Left,_11-07-2021.png", side=-1,
         front_on="left", wheels=["FL", "RL"], focal=dict(f_mm=10.775, fpxr=4416000 / 292, native_w=4416,
                                                         native_h=3312, orig_w=3960, orig_h=2340),
         k1max=0.03, loc_px=None, shows="2022 Civic Hatchback Sport Touring, Canada (Canon G10, 10.8 mm)"),
]


# ------------------------------------------------------------------ cage
def load_cage():
    p = os.path.join(ROOT, "blender", "_build", "cage_dump.json")
    d = json.load(open(p))
    P = {}
    for name, o in d.items():
        P[name] = {"location": np.array(coords.blender_to_project(o["location"])),
                   "points": np.array([coords.blender_to_project(q) for q in o["points"]]) if o["points"] else None,
                   "collection": o["collection"]}
    return P


def wheel_geom(w):
    s = coords.WHEELS[w]["side"]
    axle = coords.WHEELS[w]["axle"]
    track = TF if axle == "front" else TR
    y = 0.0 if axle == "front" else -WB
    lip_x = s * (track / 2 + WHEEL_W / 2 + FLANGE_OUT)
    tread_x = s * (track / 2 + SW / 2)
    return s, axle, y, lip_x, tread_x


# ------------------------------------------------------------------ images
def load_image(ph):
    im = Image.open(os.path.join(ROOT, ph["path"]))
    if ph["mask"] == "alpha":
        a = np.array(im)
        rgb = a[:, :, :3].copy()
        alpha = a[:, :, 3]
        comp = (rgb.astype(float) * (alpha[:, :, None] / 255.0) + 255 * (1 - alpha[:, :, None] / 255.0)).astype(np.uint8)
        body = np.where(alpha >= 250, 255, 0).astype(np.uint8)
        top = np.where(alpha >= 128, 255, 0).astype(np.uint8)
        glass = np.where((alpha >= 128) & (alpha < 250), 255, 0).astype(np.uint8)
        return comp, body, top, glass
    rgb = np.array(im.convert("RGB"))
    m = np.array(Image.open(os.path.join(ROOT, ph["mask"])))
    return rgb, m, m, None


def focal_and_pp(ph, shape):
    Hh, Ww = shape[:2]
    f = ph["focal"]
    if f is None:
        return None, Ww / 2, Hh / 2, (0.0, 0.0)
    scale = Ww / f["orig_w"]
    fpx = exif_f_px(f["f_mm"], f["fpxr"], scale)
    # unknown crop position: principal point can be anywhere the crop allows (bounded by native size)
    du = (f["native_w"] - f["orig_w"]) / 2 * scale
    dv = (f["native_h"] - f["orig_h"]) / 2 * scale
    return fpx, Ww / 2, Hh / 2, (du, dv)


# ------------------------------------------------------------------ fitting
def rim_points(w, z_axle, r_rim, n=72):
    s, axle, y, lip_x, _ = wheel_geom(w)
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[np.full(n, lip_x), y + r_rim * np.cos(a), z_axle + r_rim * np.sin(a)]


def bilinear(img, uv):
    u = np.clip(uv[:, 0], 0, img.shape[1] - 1.001)
    v = np.clip(uv[:, 1], 0, img.shape[0] - 1.001)
    u0, v0 = np.floor(u).astype(int), np.floor(v).astype(int)
    du, dv = u - u0, v - v0
    return (img[v0, u0] * (1 - du) * (1 - dv) + img[v0, u0 + 1] * du * (1 - dv) +
            img[v0 + 1, u0] * (1 - du) * dv + img[v0 + 1, u0 + 1] * du * dv)


def edge_distance(grey, mask):
    """Distance (px) to the nearest Canny edge inside the dilated car mask."""
    med = float(np.median(grey[mask > 0])) if (mask > 0).any() else float(np.median(grey))
    e = cv2.Canny(cv2.GaussianBlur(grey, (0, 0), 1.0), 0.4 * med, 1.0 * med)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    e[cv2.dilate(mask, k) == 0] = 0
    return cv2.distanceTransform((e == 0).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)


def contact_obs(env, w_uv_guess, r_px):
    """Lowest silhouette point within +-0.6 r_px of the wheel's projected centre column."""
    u0 = int(round(w_uv_guess[0]))
    a, b = max(0, int(u0 - 0.6 * r_px)), min(len(env) - 1, int(u0 + 0.6 * r_px))
    seg = env[a:b + 1]
    if np.all(np.isnan(seg)):
        return None
    i = int(np.nanargmax(seg))
    vmax = seg[i]
    cols = np.where(seg >= vmax - 0.5)[0] + a
    return np.array([float(np.median(cols)), float(vmax)])


YAW_PRIOR_SIGMA = math.radians(1.0)   # side views: camera axis assumed perpendicular to the car side (soft)


def yaw_of(R):
    """Angle between the camera axis and the car's lateral (X) axis, measured about Z (side views)."""
    zc = R[2]
    return math.atan2(zc[1], abs(zc[0]))


def residuals(p, ph, rims, env_contacts, f_fixed, cx, cy, k1, nw, w_rim=1.0, w_contact=0.5, yaw0=None, h0=None):
    """Residuals (px): projected rim-lip circle samples vs the detected rim ellipse of each wheel, plus the
    tyre contact point; optional soft yaw prior for side views."""
    pose = p[:6]
    z_f, z_r, r_rim = p[6], p[7], p[8]
    f = p[9] if f_fixed is None else f_fixed
    cam = camlib.Camera.from_params(pose, f, cx, cy, k1)
    res = []
    for w in ph["wheels"]:
        z = z_f if coords.WHEELS[w]["axle"] == "front" else z_r
        el = rims.get(w)
        if el is not None:
            # distance of each detected rim-lip edge point to the projected 3D rim circle (handles partial arcs)
            curve = cam.project(rim_points(w, z, r_rim, 240))
            pts = el["lip_points"]
            d2 = ((pts[:, None, :] - curve[None, :, :]) ** 2).sum(axis=2)
            res.append(w_rim * np.sqrt(d2.min(axis=1)) / math.sqrt(len(pts) / 36.0))
        if env_contacts.get(w) is not None:
            s, axle, y, lip_x, tread_x = wheel_geom(w)
            cuv = cam.project([[tread_x, y, 0.0]])[0]
            res.append(w_contact * (cuv - env_contacts[w]))
    if yaw0 is not None:  # side views only: soft prior that the camera looks square at the car side
        res.append(np.array([10.0 * (yaw_of(cam.R) - yaw0) / YAW_PRIOR_SIGMA]))
    if h0 is not None:    # side views only: camera height is degenerate with pitch; hold it at the assumed value
        res.append(np.array([10.0 * (p[5] - h0) / 0.02]))
    return np.concatenate(res)


def multi_start(ph, f, free_f):
    """Initial cameras on a ring around the car (every 30 deg azimuth, 5-40 m, eye height ~1.4 m) looking at
    the car centre; the fit keeps the lowest-cost converged start. Side views start on the visible side only."""
    starts = []
    tgt = np.array([0.0, -WB / 2, 0.5])
    s = ph["side"]
    azs = [0.0] if ph["kind"] == "side" else np.radians(np.arange(-150, 181, 30))
    for az in azs:
        for d in (5.0, 10.0, 20.0, 40.0):
            # az = 0: camera square to the visible side; positive az moves it towards the front
            C = tgt + d * np.array([s * math.cos(az), math.sin(az), 0.0]) + np.array([0, 0, H_NOMINAL - tgt[2]])
            R = camlib.look_at(C, tgt)
            x = np.r_[camlib.rot_to_rodrigues(R), C, Z_WHEEL0, Z_WHEEL0, RIM_D / 2 + FLANGE_H]
            if free_f:
                x = np.r_[x, f]
            starts.append(x)
    return starts


def init_pose(ph, arcs_uv, f, cx, cy):
    """solvePnP from approximate wheel centres (arc circle fits) and contact points."""
    obj, img = [], []
    for w, a in arcs_uv.items():
        s, axle, y, lip_x, tread_x = wheel_geom(w)
        obj += [[lip_x, y, Z_WHEEL0], [tread_x, y, 0.0]]
        img += [a["center"], a["contact"]]
    obj, img = np.array(obj, float), np.array(img, float)
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], float)
    # initial guess: camera on the visible side, at a distance giving the observed wheelbase in pixels
    wb_px = np.linalg.norm(img[0] - img[2])
    dist = f * WB / max(wb_px, 1)
    s = ph["side"]
    C0 = np.array([s * dist, -WB / 2, 1.2])
    R0 = camlib.look_at(C0, np.array([0, -WB / 2, 0.5]))
    rv0, _ = cv2.Rodrigues(R0)
    tv0 = -R0 @ C0
    ok, rv, tv = cv2.solvePnP(obj, img, K, None, rv0, tv0.reshape(3, 1), useExtrinsicGuess=True,
                              flags=cv2.SOLVEPNP_ITERATIVE)
    R, _ = cv2.Rodrigues(rv)
    C = (-R.T @ tv).ravel()
    return np.r_[camlib.rot_to_rodrigues(R), C]


WHEEL_CACHE = {}


def detect_wheels(ph, rgb, body):
    """Contact points (lowest silhouette bumps) and rim-lip ellipses for the listed wheels (image left->right)."""
    if ph["id"] in WHEEL_CACHE:
        return WHEEL_CACHE[ph["id"]]
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    env = pf.lower_envelope(body)
    arcs = sorted(pf.tire_arcs(env, len(ph["wheels"])), key=lambda a: a["contact_u"])
    Wd = rgb.shape[1]
    rims, contacts = {}, {}
    for w, a in zip(ph["wheels"], arcs):
        el = pf.find_wheel(grey, (a["contact_u"], a["contact_v"]), (0.015 * Wd, 0.12 * Wd),
                           polarity=ph.get("rim_polarity", True))
        contacts[w] = np.array([a["contact_u"], a["contact_v"]])
        if el is not None:
            ref = pf.refine_rim_radial(grey, el)
            # the radial refinement measures the lip on every ray; accept it when most rays support it
            if ref.get("refined") and ref["n_inliers"] >= 0.6 * 72 and ref["rms_px"] <= 2.0:
                el = ref
            el["axes_cv"] = (el["axes"][0], el["axes"][1])
            P = np.asarray(el["points"], float)
            if len(P) > 400:  # thin evenly for speed
                P = P[np.linspace(0, len(P) - 1, 400).astype(int)]
            el["lip_points"] = P
            rims[w] = el
    WHEEL_CACHE[ph["id"]] = (rims, contacts, env)
    return rims, contacts, env


def fit_camera(ph, rgb, body, f, cx, cy, k1=0.0, x_start=None, yaw0="auto", h0="auto"):
    if yaw0 == "auto":
        yaw0 = 0.0 if ph["kind"] == "side" else None
    if h0 == "auto":
        h0 = H_NOMINAL if ph["kind"] == "side" else None
    rims, contacts, env = detect_wheels(ph, rgb, body)
    free_f = bool(ph.get("fit_focal"))
    lo = np.r_[[-np.inf] * 6, 0.22, 0.22, RIM_D / 2 - 0.01]
    hi = np.r_[[np.inf] * 6, 0.40, 0.40, RIM_D / 2 + 0.05]
    if free_f:
        lo, hi = np.r_[lo, 0.3 * rgb.shape[1]], np.r_[hi, 60.0 * rgb.shape[1]]
    args = (ph, rims, contacts, None if free_f else f, cx, cy, k1, len(ph["wheels"]), 1.0, 0.5, yaw0, h0)
    if x_start is None:
        starts = multi_start(ph, f, free_f)
    else:
        starts = [np.asarray(x_start, float)]
    sol = None
    for x0 in starts:
        try:
            cand = least_squares(residuals, x0, args=args, loss="soft_l1", f_scale=1.5, bounds=(lo, hi),
                                 x_scale="jac", max_nfev=300 if len(starts) > 1 else 800)
        except ValueError:
            continue
        if sol is None or cand.cost < sol.cost:
            sol = cand
    if len(starts) > 1:  # polish the best start
        sol = least_squares(residuals, sol.x, args=args, loss="soft_l1", f_scale=1.5, bounds=(lo, hi),
                            x_scale="jac", max_nfev=1500)
    f = sol.x[9] if free_f else f
    cam = camlib.Camera.from_params(sol.x[:6], f, cx, cy, k1)
    rim_res, con_res = [], []
    for w in ph["wheels"]:
        z = sol.x[6] if coords.WHEELS[w]["axle"] == "front" else sol.x[7]
        if w in rims:
            curve = cam.project(rim_points(w, z, sol.x[8], 240))
            pts = rims[w]["lip_points"]
            rim_res.append(np.sqrt(((pts[:, None, :] - curve[None, :, :]) ** 2).sum(axis=2).min(axis=1)))
        s_, axle, y, lip_x, tread_x = wheel_geom(w)
        con_res.append(cam.project([[tread_x, y, 0.0]])[0] - contacts[w])
    rim_res = np.concatenate(rim_res) if rim_res else np.zeros(0)
    con_res = np.concatenate(con_res)
    return {"cam": cam, "x": sol.x, "z_front": float(sol.x[6]), "z_rear": float(sol.x[7]), "r_rim": float(sol.x[8]),
            "rim_rms_px": float(np.sqrt(np.mean(rim_res ** 2))) if len(rim_res) else None,
            "rim_inlier_frac": float(np.mean(np.abs(rim_res) < 3)) if len(rim_res) else None,
            "contact_rms_px": float(np.sqrt(np.mean(con_res ** 2))),
            "contacts": {w: c.tolist() for w, c in contacts.items()},
            "rims": {w: {k: v for k, v in r.items() if k not in ("points", "lip_points")} for w, r in rims.items()},
            "env": env, "success": bool(sol.success), "cost": float(sol.cost),
            "yaw_deg": math.degrees(yaw_of(cam.R)),
            "wb_px": float(np.linalg.norm(np.subtract(*[rims[w]["center"] for w in ph["wheels"][:2]])))
            if all(w in rims for w in ph["wheels"][:2]) else None}


def fit_camera_from(ph, rgb, body, f, cx, cy, x_start):
    """Refit from a perturbed starting pose (fit-stability study)."""
    return fit_camera(ph, rgb, body, f, cx, cy, x_start=x_start)


# ------------------------------------------------------------------ features
def plane_x(xv):
    return (np.array([1.0, 0, 0]), xv)


def vertical_dir(cam, P):
    a = cam.project([P])[0]
    b = cam.project([np.asarray(P) + np.array([0, 0, 0.1])])[0]
    d = b - a
    return d / np.linalg.norm(d)


def horizontal_dir(cam, P):
    a = cam.project([P])[0]
    b = cam.project([np.asarray(P) + np.array([0, 0.1, 0])])[0]
    d = b - a
    return d / np.linalg.norm(d)


def measure(ph, rgb, body, top, glass, fit, snap=True):
    """Image positions (u, v) of key points with their assumed planes; returns dict name -> info."""
    cam = fit["cam"]
    s = ph["side"]
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(float)
    feats = {}

    def add(name, uv, plane, axes, loc_px, note="", shift=0.0):
        feats[name] = {"uv": [float(uv[0]), float(uv[1])], "plane": plane, "axes": axes,
                       "loc_px": float(loc_px), "snap_shift_px": float(shift), "note": note}

    base_loc = ph["loc_px"] if ph["loc_px"] is not None else 1.0
    # roof peak (topmost silhouette point), centreline plane
    tp = pf.upper_envelope(top)
    u, v = pf.top_peak(tp)
    sh = 0.0
    if snap and ph["mask"] != "alpha":
        u2, v2, sh = pf.snap_to_edge(grey, (u, v), (0, 1), search=15)
        u, v = u2, v2
    add("roof_peak", (u, v), ("centerline", 0.0, 0.25), ("Y", "Z"), max(base_loc, abs(sh) / 2), shift=sh,
        note="topmost silhouette point; assumed on the centreline (roof crown), plane uncertainty +-0.25 m")
    # wheel-related: arch tops and sill (visible side)
    door = np.array([s * W / 2, -WB / 2, 0.6])
    duv = cam.project([door])[0]
    rad = 0.12 / cam.mm_per_px(door)
    body_lab, spread = pf.body_colour(lab, body, duv, rad)
    for w in ph["wheels"]:
        sgn, axle, y, lip_x, tread_x = wheel_geom(w)
        z = fit["z_front"] if axle == "front" else fit["z_rear"]
        c3 = np.array([s * W / 2, y, z])
        cuv = cam.project([c3])[0]
        dvec = vertical_dir(cam, c3)
        r_px = (TYRE_D / 2) / cam.mm_per_px(c3)
        p0 = cuv + dvec * (r_px * 1.02)
        p1 = cuv + dvec * (r_px + 0.45 / cam.mm_per_px(c3))
        hit = pf.well_to_body_edge(lab, p0, p1, body_lab)
        name = f"arch_top_{axle}"
        if hit is not None:
            add(name, hit, ("bodyside", s * W / 2, 0.05), ("Z",), max(base_loc, 1.0),
                note="scanning up the projected vertical through the wheel centre from the tyre top: first point closer "
                     "in colour to the body (door sample) than to the dark wheel well; assumed on the body-side plane "
                     "x = +-width/2 (+-0.05 m)")
        else:
            feats[name] = {"missing": "no body-coloured run found above the wheel"}
    # sill at mid-wheelbase: silhouette bottom along the projected vertical (body-side plane)
    m3 = np.array([s * W / 2, -WB / 2, 0.45])
    muv = cam.project([m3])[0]
    dv = vertical_dir(cam, m3)
    ex = pf.mask_exit(body, muv, muv - dv * (0.6 / cam.mm_per_px(m3)))
    if ex is not None:
        sh = 0.0
        if snap and ph["mask"] != "alpha":
            u2, v2, sh = pf.snap_to_edge(grey, ex, -dv, search=12)
            ex = (u2, v2)
        add("sill_mid", ex, ("bodyside", s * W / 2, 0.10), ("Z",), max(base_loc, abs(sh) / 2), shift=sh,
            note="silhouette bottom at mid-wheelbase along the projected vertical; assumed on x = +-width/2 (+-0.10 m; the rocker is inboard)")
    if ph["kind"] == "side":
        ext = pf.extremes(body)
        front_key, rear_key = ("left", "right") if ph["front_on"] == "left" else ("right", "left")
        for name, k in (("front_bumper_extent", front_key), ("rear_bumper_extent", rear_key)):
            u, v = ext[k]
            sh = 0.0
            if snap and ph["mask"] != "alpha":
                u2, v2, sh = pf.snap_to_edge(grey, (u, v), (1, 0), search=12)
                u, v = u2, v2
            add(name, (u, v), ("centerline", 0.0, 0.30), ("Y",), max(base_loc, abs(sh) / 2), shift=sh,
                note="extreme silhouette column; assumed on the centreline (+-0.30 m: the extreme may sit off-centre)")
        # top profile: hood / windshield / roof / hatch breakpoints
        cols = np.where(~np.isnan(tp))[0]
        fu = ext[front_key][0]
        ru = ext[rear_key][0]
        a, b = sorted((fu, ru))
        span = b - a
        sel = cols[(cols > a + 0.04 * span) & (cols < b - 0.03 * span)]
        uu, vv = sel.astype(float), tp[sel]
        if ph["front_on"] == "right":
            uu, vv = uu[::-1], vv[::-1]
        segs, sse = pf.segmented_fit(uu, vv, 4, min_len=max(4, len(uu) // 40))
        names = ["hood", "windshield", "roof", "hatch"]
        bps = {}
        for (s1, s2), nm in zip(zip(segs, segs[1:]), ("windshield_base", "windshield_header", "hatch_top")):
            x = pf.line_intersection(s1, s2)
            if x is not None:
                bps[nm] = x
        for nm, uvp in bps.items():
            add(nm, uvp, ("centerline", 0.0, 0.40 if nm == "windshield_base" else 0.25), ("Y", "Z"), max(base_loc, 1.0),
                note="intersection of fitted top-profile segments (4-segment least squares); assumed on the centreline")
        feats["_top_profile"] = {"segments": [{"name": n, "slope": sg["slope"], "u0": float(uu[sg["i0"]]),
                                               "u1": float(uu[sg["i1"] - 1])} for n, sg in zip(names, segs)]}
        # hood height at the front axle: top profile at the projected front axle (centreline plane)
        ax = cam.project([[0.0, 0.0, 0.9]])[0]
        col = int(round(ax[0]))
        if 0 <= col < len(tp) and not np.isnan(tp[col]):
            add("hood_at_front_axle", (ax[0], tp[col]), ("centerline", 0.0, 0.30), ("Z",), max(base_loc, 1.0),
                note="top silhouette at the projected front-axle column; assumed on the centreline")
        if glass is not None:
            # beltline: bottom of the side glass at mid-wheelbase (render only: glass is semi-transparent there)
            gm = np.array([s * W / 2, -WB / 2, 1.0])
            guv = cam.project([gm])[0]
            colg = int(round(guv[0]))
            z08 = cam.project([[s * W / 2, -WB / 2, 0.8]])[0][1]
            rows = np.where(glass[:int(z08), colg] > 0)[0]   # side glass only (the soft ground shadow is also semi-transparent)
            if len(rows):
                add("beltline_mid", (colg, rows.max() + 0.5), ("bodyside", s * 0.75, 0.10), ("Z",), base_loc,
                    note="lowest side-glass pixel at mid-wheelbase (render alpha); assumed on the glass plane x = +-0.75 m (+-0.10)")
    return feats


def to3d(cam, f, W_side):
    kind, xv, _ = f["plane"]
    n, d0 = plane_x(xv)
    return cam.backproject_to_plane(f["uv"], n, d0)


# ------------------------------------------------------------------ cage values for each key point
def cage_values(cage, side):
    sfx = "L" if side < 0 else "R"
    g = lambda n: cage[n]["location"]  # noqa: E731
    pts = lambda n: cage[n]["points"]  # noqa: E731
    box = pts("REF_body_box")
    ws = pts("REF_guide_windshield")
    out = {
        "roof_peak": {"Y": g("REF_guide_roof_peak")[1], "Z": g("REF_guide_roof_peak")[2], "obj": "REF_guide_roof_peak",
                      "class": "photo (Phase 1 render, orthographic)"},
        "roof_peak_vs_published_height": {"Z": float(box[:, 2].max()), "obj": "REF_body_box (top = published height)",
                                          "class": "published"},
        "windshield_base": {"Y": g("REF_guide_windshield_base")[1], "Z": g("REF_guide_windshield_base")[2],
                            "obj": "REF_guide_windshield_base", "class": "photo"},
        "windshield_header": {"Y": ws[-1][1], "Z": ws[-1][2], "obj": "REF_guide_windshield (upper end)", "class": "photo"},
        "hood_at_front_axle": {"Z": pts("REF_guide_hood")[0][2], "obj": "REF_guide_hood (front end)", "class": "photo"},
        "front_bumper_extent": {"Y": float(box[:, 1].max()), "obj": "REF_body_box front face / REF_guide_front_bumper_extent",
                                "class": "photo (overhang split)"},
        "rear_bumper_extent": {"Y": float(box[:, 1].min()), "obj": "REF_body_box rear face", "class": "photo (overhang split)"},
        "arch_top_front": {"Z": g(f"REF_guide_arch_top_front_{sfx}")[2], "obj": f"REF_guide_arch_top_front_{sfx}", "class": "photo"},
        "arch_top_rear": {"Z": g(f"REF_guide_arch_top_rear_{sfx}")[2], "obj": f"REF_guide_arch_top_rear_{sfx}", "class": "photo"},
        "sill_mid": {"Z": g(f"REF_guide_sill_mid_{sfx}")[2], "obj": f"REF_guide_sill_mid_{sfx}", "class": "photo"},
        "wheel_center_front": {"Z": g(f"REF_wheel_center_F{sfx}")[2], "obj": f"REF_wheel_center_F{sfx}",
                               "class": "estimated (tires.loaded_radius)"},
        "wheel_center_rear": {"Z": g(f"REF_wheel_center_R{sfx}")[2], "obj": f"REF_wheel_center_R{sfx}",
                              "class": "estimated (tires.loaded_radius)"},
    }
    return out


NOT_IN_CAGE = {
    "hood_leading_edge": "the cage has no hood-leading-edge item (not measured in Phase 1)",
    "hatch_line": "the cage has no hatch line (Phase 1 measured the hatch angle and top Y but not its height)",
    "beltline": "the cage has no beltline (not measured in Phase 1)",
    "mirror_position": "the cage has only the published width over mirrors; mirror Y/Z unknown, and no "
                       "algorithm separates the mirror from the body in these images",
}


def compare_one(ph, cage):
    rgb, body, top, glass = load_image(ph)
    Hh, Ww = rgb.shape[:2]
    f_exif, cx, cy, pp = focal_and_pp(ph, rgb.shape)
    result = {"id": ph["id"], "path": ph["path"], "manifest_id": ph["manifest"], "shows": ph["shows"],
              "image_size": [Ww, Hh], "kind": ph["kind"]}
    rims, contacts, env = detect_wheels(ph, rgb, body)
    result["wheel_detection"] = {w: {k: v for k, v in r.items() if k not in ("points", "axes_cv", "lip_points")} for w, r in rims.items()}
    if len(rims) < 2:
        result["status"] = "camera not fitted"
        result["reason"] = (f"rim ellipses found for {len(rims)} wheel(s) ({', '.join(rims) or 'none'}); two wheels are "
                            "needed to fix the camera, so no key point in this image is measurable")
        return result, None
    weak = [w for w, r in rims.items() if r["coverage"] < 0.35]
    if weak:
        result["wheel_detection_warning"] = f"low edge coverage (<35% of the ellipse) for {weak}: fit may be unreliable"
    # focal length: EXIF, else calibrated by the published length (side views)
    if f_exif is not None:
        f = f_exif
        result["focal"] = {"source": "EXIF focal length x focal-plane resolution", "f_px": f}
        fit = fit_camera(ph, rgb, body, f, cx, cy)
        calib = None
    elif ph.get("fit_focal"):
        f0 = Ww * 3.0
        fit = fit_camera(ph, rgb, body, f0, cx, cy)
        f = fit["cam"].f
        calib = {"note": "focal length ESTIMATED: no EXIF; fitted together with the pose (the oblique view makes the "
                         "two wheels' perspective sizes and ellipse shapes informative)"}
        result["focal"] = {"source": calib["note"], "f_px": float(f)}
    else:
        # no EXIF: focal length and camera distance cannot be separated in a side view; assume a nominal
        # distance and carry 10-100 m as an uncertainty term (length and height stay independent checks)
        wb_px = float(np.linalg.norm(np.subtract(*[rims[w]["center"] for w in ph["wheels"][:2]])))
        f_of_d = lambda d: d * wb_px / WB  # noqa: E731  (distance from camera to the wheel plane)
        f = f_of_d(D_NOMINAL)
        calib = {"note": f"focal length ESTIMATED: no EXIF; camera distance unknown, nominal {D_NOMINAL:.0f} m, "
                         f"range {D_RANGE[0]:.0f}-{D_RANGE[1]:.0f} m carried as an uncertainty term",
                 "f_by_distance_px": {str(d): f_of_d(d) for d in (D_RANGE[0], D_NOMINAL, D_RANGE[1])}}
        result["focal"] = {"source": calib["note"], "f_px": float(f)}
        fit = fit_camera(ph, rgb, body, f, cx, cy)
    cam = fit["cam"]
    result["camera"] = {"C_project_m": cam.C.tolist(), "f_px": cam.f, "cx": cx, "cy": cy, "yaw_deg": fit["yaw_deg"],
                        "distance_to_mid_wheelbase_m": float(np.linalg.norm(cam.C - np.array([0, -WB / 2, 0.5]))),
                        "rim_rms_px": fit["rim_rms_px"], "rim_inlier_frac": fit["rim_inlier_frac"],
                        "contact_rms_px": fit["contact_rms_px"], "z_front_fit": fit["z_front"], "z_rear_fit": fit["z_rear"],
                        "r_rim_fit": fit["r_rim"], "success": fit["success"]}
    feats = measure(ph, rgb, body, top, glass, fit)
    # ---- uncertainty: perturbation runs
    variants = []
    # (a) bootstrap of the camera fit: jitter the edge-distance map by resampling rim points via dropout
    rng = np.random.default_rng(20261007)
    for b in range(12):
        x = fit["x"].copy()
        x[:6] += rng.normal(0, 1, 6) * np.r_[[2e-3] * 3, [0.05] * 3]
        variants.append(("fit", x))
    def remeasure(cam_v, fit_v):
        fv = measure(ph, rgb, body, top, glass, fit_v, snap=(ph["mask"] != "alpha"))
        return {k: to3d(cam_v, v, W) for k, v in fv.items() if "uv" in v}
    base3d = {k: to3d(cam, v, W) for k, v in feats.items() if "uv" in v}
    spreads = {k: [] for k in base3d}
    # refits from perturbed starts give the fit-stability spread
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    refits = []
    for _, x in variants[:6]:
        ft = fit_camera_from(ph, rgb, body, cam.f, cx, cy, x)
        refits.append(ft)
        r3 = remeasure(ft["cam"], ft)
        for k in base3d:
            if k in r3:
                spreads[k].append(r3[k] - base3d[k])
    cam_spread = float(np.std([np.linalg.norm(ft["cam"].C - cam.C) for ft in refits])) if refits else None
    # (b) distortion and (c) principal point: refit and remeasure
    sys_terms = {k: [] for k in base3d}
    if ph["k1max"]:
        for k1 in (-ph["k1max"], ph["k1max"]):
            ft = fit_camera(ph, rgb, body, cam.f, cx, cy, k1=k1, x_start=fit["x"])
            r3 = remeasure(ft["cam"], ft)
            for k in base3d:
                if k in r3:
                    sys_terms[k].append(("distortion", r3[k] - base3d[k]))
    if ph["focal"] is None and not ph.get("fit_focal"):
        for d in D_RANGE:
            fd = calib["f_by_distance_px"][str(d)]
            xs = fit["x"].copy()
            C = xs[3:6]
            tgt = np.array([0.0, -WB / 2, C[2]])
            xs[3:6] = tgt + (C - tgt) * (fd / cam.f)   # move the camera along its line of sight to the new distance
            ft = fit_camera(ph, rgb, body, fd, cx, cy, x_start=xs)
            r3 = remeasure(ft["cam"], ft)
            for k in base3d:
                if k in r3:
                    sys_terms[k].append(("camera distance (no EXIF)", r3[k] - base3d[k]))
    if ph["kind"] == "side":
        for hh in H_RANGE:
            xs = fit["x"].copy()
            xs[5] = hh
            ft = fit_camera(ph, rgb, body, cam.f, cx, cy, h0=hh, x_start=xs)
            r3 = remeasure(ft["cam"], ft)
            for k in base3d:
                if k in r3:
                    sys_terms[k].append(("camera height (unknown, 0.4-1.6 m)", r3[k] - base3d[k]))
        for y0 in (-YAW_TEST, YAW_TEST):
            ft = fit_camera(ph, rgb, body, cam.f, cx, cy, yaw0=y0, x_start=fit["x"])
            r3 = remeasure(ft["cam"], ft)
            for k in base3d:
                if k in r3:
                    sys_terms[k].append(("camera yaw +-3 deg", r3[k] - base3d[k]))
    if pp != (0.0, 0.0):
        for du, dv in ((pp[0], 0), (-pp[0], 0), (0, pp[1]), (0, -pp[1])):
            ft = fit_camera(ph, rgb, body, cam.f, cx + du, cy + dv, x_start=fit["x"])
            r3 = remeasure(ft["cam"], ft)
            for k in base3d:
                if k in r3:
                    sys_terms[k].append(("principal point", r3[k] - base3d[k]))
    cv = cage_values(cage, ph["side"])
    rows = []
    for k, f3 in base3d.items():
        fe = feats[k]
        P = f3
        mpp = cam.mm_per_px(P)
        _, xv, dplane = fe["plane"]
        n, d0 = plane_x(xv + dplane)
        P_plane = cam.backproject_to_plane(fe["uv"], n, d0)
        plane_term = P_plane - P
        loc_term = np.full(3, fe["loc_px"] * mpp)
        fit_term = np.std(np.array(spreads[k]), axis=0) if spreads[k] else np.zeros(3)
        syst = {}
        for name, dlt in sys_terms[k]:
            syst.setdefault(name, []).append(np.abs(dlt))
        syst = {n_: np.max(np.array(v), axis=0) for n_, v in syst.items()}
        comps = {"localisation": loc_term, "camera_fit": fit_term, "plane": np.abs(plane_term)}
        comps.update(syst)
        sigma = np.sqrt(sum(c ** 2 for c in comps.values()))
        key = k
        ref = cv.get(key)
        for ax in fe["axes"]:
            i = "XYZ".index(ax)
            row = {"key_point": k, "axis": ax, "photo_m": float(P[i]), "plane": fe["plane"][0],
                   "uv": fe["uv"], "mm_per_px": mpp * 1000,
                   "U_mm": float(2 * sigma[i] * 1000),
                   "components_mm": {n_: float(c[i] * 1000) for n_, c in comps.items()}, "note": fe["note"]}
            if ref is not None and ax in ref:
                row.update(cage_m=float(ref[ax]), cage_object=ref["obj"], cage_class=ref["class"],
                           diff_mm=float((P[i] - ref[ax]) * 1000))
                row["verdict"] = "agrees" if abs(row["diff_mm"]) <= row["U_mm"] else "disagrees"
            else:
                row["verdict"] = "not measurable"
                row["reason"] = "no corresponding cage item"
            rows.append(row)
        if k == "roof_peak":
            ref = cv["roof_peak_vs_published_height"]
            i = 2
            rows.append({"key_point": "roof_peak (vs published height)", "axis": "Z", "photo_m": float(P[i]),
                         "plane": fe["plane"][0], "uv": fe["uv"], "mm_per_px": mpp * 1000,
                         "U_mm": float(2 * sigma[i] * 1000), "components_mm": {n_: float(c[i] * 1000) for n_, c in comps.items()},
                         "cage_m": ref["Z"], "cage_object": ref["obj"], "cage_class": ref["class"],
                         "diff_mm": float((P[i] - ref["Z"]) * 1000),
                         "verdict": "agrees" if abs((P[i] - ref["Z"]) * 1000) <= 2 * sigma[i] * 1000 else "disagrees",
                         "note": "published height includes any roof antenna; the silhouette top may be the antenna"})
    # wheel-centre heights from the fit (ride height)
    for axle in ("front", "rear"):
        if any(coords.WHEELS[w]["axle"] == axle for w in ph["wheels"]):
            z = fit["z_front"] if axle == "front" else fit["z_rear"]
            zs = [ft["z_front"] if axle == "front" else ft["z_rear"] for ft in refits]
            sig = float(np.std(zs)) if zs else 0.0
            ref = cv[f"wheel_center_{axle}"]
            mpp = cam.mm_per_px(np.array([ph["side"] * W / 2, 0 if axle == "front" else -WB, z]))
            U = 2 * math.sqrt(sig ** 2 + (1.0 * mpp) ** 2)
            rows.append({"key_point": f"wheel_center_{axle} (ride height)", "axis": "Z", "photo_m": z,
                         "plane": "wheel (fitted with the camera)", "mm_per_px": mpp * 1000, "U_mm": U * 1000,
                         "components_mm": {"camera_fit": sig * 1000, "localisation": mpp * 1000},
                         "cage_m": ref["Z"], "cage_object": ref["obj"], "cage_class": ref["class"],
                         "diff_mm": (z - ref["Z"]) * 1000,
                         "verdict": "agrees" if abs(z - ref["Z"]) * 1000 <= U * 1000 else "disagrees",
                         "note": "wheel-centre height fitted from rim circles and contact points"})
    measured_names = {r["key_point"].split(" ")[0] for r in rows}
    expected = ["roof_peak", "windshield_base", "hood_at_front_axle", "hood_leading_edge", "hatch_line",
                "front_bumper_extent", "rear_bumper_extent", "arch_top_front", "arch_top_rear", "beltline",
                "mirror_position", "sill_mid", "wheel_center_front", "wheel_center_rear"]
    nm = []
    for e in expected:
        if e in measured_names:
            continue
        if e in NOT_IN_CAGE and not (e == "beltline" and "beltline_mid" in measured_names):
            reason = NOT_IN_CAGE[e]
        elif e in ("windshield_base", "hood_at_front_axle", "front_bumper_extent", "rear_bumper_extent") and ph["kind"] != "side":
            reason = "not located by the algorithm in a three-quarter view (the feature is not on the silhouette)"
        elif e.startswith("wheel_center") or e.startswith("arch_top"):
            reason = "that wheel is not one of the wheels fitted in this image"
        else:
            reason = (feats.get(e, {}) or {}).get("missing", "not located")
        nm.append({"key_point": e, "verdict": "not measurable", "reason": reason})
    if "beltline_mid" in measured_names:
        nm.append({"key_point": "beltline", "verdict": "not measurable",
                   "reason": "measured in the image (see beltline_mid row) but the cage has no beltline to compare with"})
    status = "fitted"
    bad = []
    if fit["rim_rms_px"] > GATE_RIM_RMS_PX:
        bad.append(f"rim-lip residual {fit['rim_rms_px']:.2f} px > {GATE_RIM_RMS_PX} px")
    if fit["contact_rms_px"] > GATE_CONTACT_RMS_PX:
        bad.append(f"contact residual {fit['contact_rms_px']:.2f} px > {GATE_CONTACT_RMS_PX} px")
    if bad:
        # an isotropic pinhole camera does not explain the wheels: the numbers are kept for inspection but no
        # key point gets a verdict, and nothing here is evidence against a published figure
        status = "camera fit unstable"
        result["reason"] = ("camera fit rejected: " + "; ".join(bad) + ". Key-point values below are what the "
                            "rejected camera gives; they are not differences and carry no verdict")
        for r in rows:
            if "diff_mm" in r:
                r["diff_mm_rejected_fit"] = r.pop("diff_mm")
            r["verdict"] = "not measurable"
            r["reason"] = "camera fit unstable"
    result.update(status=status, calibration=calib, camera_fit_spread_m=cam_spread, rows=rows, not_measurable=nm,
                  top_profile=feats.get("_top_profile"))
    return result, (rgb, cam, fit, feats)


def overlay(ph, rgb, cam, fit, feats, cage):
    os.makedirs(OVL, exist_ok=True)
    im = rgb.copy()
    th = max(1, int(round(im.shape[1] / 900)))

    def poly(P, col):
        uv = cam.project(P).astype(int)
        for a, b in zip(uv, uv[1:]):
            cv2.line(im, tuple(a), tuple(b), col, th)

    box = cage["REF_body_box"]["points"]
    for i in range(8):
        for j in range(i + 1, 8):
            if np.sum(np.abs(box[i] - box[j]) > 1e-6) == 1:
                poly(np.array([box[i], box[j]]), (255, 160, 0))
    for w in ph["wheels"]:
        z = fit["z_front"] if coords.WHEELS[w]["axle"] == "front" else fit["z_rear"]
        poly(np.vstack([rim_points(w, z, fit["r_rim"], 90), rim_points(w, z, fit["r_rim"], 90)[:1]]), (0, 255, 0))
    for w, r in fit.get("rims", {}).items():
        cv2.ellipse(im, (int(r["center"][0]), int(r["center"][1])), (int(r["axes"][0]), int(r["axes"][1])),
                    r["angle_deg"], 0, 360, (0, 0, 255), th)
    for n, o in cage.items():
        if n.startswith("REF_guide") and o["points"] is not None and len(o["points"]) >= 2:
            poly(o["points"], (255, 0, 255))
    for k, f in feats.items():
        if "uv" in f:
            cv2.circle(im, (int(f["uv"][0]), int(f["uv"][1])), 3 * th, (0, 128, 255), -1)
    Image.fromarray(im).save(os.path.join(OVL, ph["id"] + ".jpg"), quality=85)


def main():
    cage = load_cage()
    results = []
    only = sys.argv[1:] or None
    for ph in PHOTOS:
        if only and ph["id"] not in only:
            continue
        print("==", ph["id"])
        res, extra = compare_one(ph, cage)
        if extra is not None:
            overlay(ph, *extra, cage)
            print("  ", res["status"], res.get("reason", ""))
            print(f"   camera rim rms {res['camera']['rim_rms_px']:.2f}px inliers {res['camera']['rim_inlier_frac']:.2f} "
                  f"contact rms {res['camera']['contact_rms_px']}  dist {res['camera']['distance_to_mid_wheelbase_m']:.1f} m "
                  f"f {res['camera']['f_px']:.0f}px spread {res['camera_fit_spread_m']}")
            for r in res["rows"]:
                if "diff_mm" in r:
                    print(f"   {r['key_point']:34s} {r['axis']} photo {r['photo_m']:.4f} cage {r['cage_m']:.4f} "
                          f"diff {r['diff_mm']:+7.1f} mm  U {r['U_mm']:6.1f} mm  {r['verdict']}")
                else:
                    print(f"   {r['key_point']:34s} {r['axis']} photo {r['photo_m']:.4f}  ({r['verdict']})")
        else:
            print("  ", res["status"], res.get("reason"))
        results.append(res)
    if not only:
        json.dump({"generator": "scripts/phase2/compare_photos.py", "photos": results}, open(OUT_JSON, "w"),
                  indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
        print("wrote", os.path.relpath(OUT_JSON, ROOT))


if __name__ == "__main__":
    main()
