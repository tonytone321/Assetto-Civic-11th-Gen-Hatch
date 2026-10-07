"""Algorithmic feature location in reference images (Phase 2, Step 7). Nothing is picked by eye.

Inputs are a body mask (silhouette used for the bottom and the ends) and a top mask (silhouette used
for the roof profile; for the studio render it also includes the semi-transparent glass).
"""
import math

import cv2
import numpy as np


# ------------------------------------------------------------------ masks
def refine_mask_grabcut(rgb, mask, band=6, iters=4):
    """Refine a coarse instance mask with GrabCut: eroded mask = sure foreground, outside the dilated
    mask = sure background, the band in between is decided by colour models."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * band + 1, 2 * band + 1))
    fg = cv2.erode(mask, k)
    near = cv2.dilate(mask, k)
    gc = np.full(mask.shape, cv2.GC_BGD, np.uint8)
    gc[near > 0] = cv2.GC_PR_BGD
    gc[mask > 0] = cv2.GC_PR_FGD
    gc[fg > 0] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), gc, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    out = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    # keep the component overlapping the original mask most
    n, lab, stats, _ = cv2.connectedComponentsWithStats(out)
    if n > 2:
        best = max(range(1, n), key=lambda i: int(((lab == i) & (mask > 0)).sum()))
        out = np.where(lab == best, 255, 0).astype(np.uint8)
    return out


# ------------------------------------------------------------------ silhouette profiles
def lower_envelope(mask):
    """Row of the lowest mask pixel per column (image v grows downward); NaN where empty."""
    H = mask.shape[0]
    has = mask.any(axis=0)
    low = H - 1 - np.argmax(mask[::-1, :] > 0, axis=0)
    env = low.astype(float) + 0.5
    env[~has] = np.nan
    return env


def upper_envelope(mask):
    has = mask.any(axis=0)
    top = np.argmax(mask > 0, axis=0).astype(float) - 0.5
    top[~has] = np.nan
    return top


def extremes(mask):
    cols = np.where(mask.any(axis=0))[0]
    x0, x1 = int(cols.min()), int(cols.max())
    r0 = np.where(mask[:, x0] > 0)[0]
    r1 = np.where(mask[:, x1] > 0)[0]
    return {"left": (x0 - 0.5, float(np.median(r0))), "right": (x1 + 0.5, float(np.median(r1)))}


def tire_arcs(env, n=2, min_sep_frac=0.12, smooth=3):
    """Find the n lowest bumps of the lower envelope (tire contact regions) and the tire-bottom arc
    around each: walk outwards from the contact while the envelope keeps rising with a non-decreasing
    slope (a circle's bottom arc), stopping where the body underside takes over (slope collapses)
    or the envelope jumps."""
    W = len(env)
    e = env.copy()
    valid = ~np.isnan(e)
    idx = np.where(valid)[0]
    e_s = e.copy()
    e_s[valid] = np.convolve(np.pad(e[valid], smooth, mode="edge"), np.ones(2 * smooth + 1) / (2 * smooth + 1), "valid")
    span = idx.max() - idx.min()
    from scipy.signal import find_peaks
    filled = np.where(valid, e_s, np.nanmin(e_s))
    pk, prop = find_peaks(filled, distance=max(1, int(min_sep_frac * span)), prominence=0.01 * span)
    best = sorted(zip(prop["prominences"], pk), reverse=True)[:n]     # most prominent bumps = tire bottoms
    cands = [(int(c), float(e_s[c])) for _, c in best]
    arcs = []
    for c, vmax in sorted(cands):
        flat = np.where(np.abs(e_s - vmax) <= 1.0)[0]
        flat = flat[np.abs(flat - c) < 0.1 * span]
        lo, hi = int(flat.min()), int(flat.max())     # contact-patch flat
        pts = {}
        for direction, start in ((-1, lo), (1, hi)):
            x, prev_slope, max_slope = start, 0.0, 0.0
            while 0 <= x + direction < W and valid[x + direction]:
                nx = x + direction
                slope = e_s[x] - e_s[nx]             # rise (pixels upward) per column outward
                if abs(e[nx] - e[x]) > 25:           # jump: body edge or occlusion
                    break
                if max_slope > 0.6 and slope < 0.35 * max_slope:   # slope collapsed: body underside
                    break
                if slope < -0.5:                     # envelope going down again
                    break
                max_slope = max(max_slope, slope)
                pts[nx] = e[nx]
                x = nx
        xs = np.array(sorted(pts))
        arcs.append({"contact_u": (lo + hi) / 2.0, "contact_v": float(np.nanmax(e[lo:hi + 1])),
                     "flat": [lo, hi], "u": xs.astype(float), "v": np.array([pts[k] for k in xs])})
    return arcs


def circle_fit(u, v):
    A = np.c_[2 * u, 2 * v, np.ones(len(u))]
    b = u ** 2 + v ** 2
    (cx, cy, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    r = math.sqrt(c + cx ** 2 + cy ** 2)
    return cx, cy, r, float(np.std(np.hypot(u - cx, v - cy) - r))


def top_peak(top):
    """Highest silhouette point: minimum v of the upper envelope; u = median of columns within 0.5 px."""
    vmin = np.nanmin(top)
    cols = np.where(top <= vmin + 0.5)[0]
    return float(np.median(cols)), float(vmin)


def segmented_fit(u, v, k, min_len=6):
    """Optimal k-segment piecewise-linear least squares (independent segments) by dynamic programming.
    Returns breakpoints as indices into u (segment starts)."""
    n = len(u)
    S = np.cumsum(np.r_[0, u]); SS = np.cumsum(np.r_[0, u * u]); T = np.cumsum(np.r_[0, v])
    TT = np.cumsum(np.r_[0, v * v]); ST = np.cumsum(np.r_[0, u * v])

    def sse(i, j):  # segment [i, j)
        m = j - i
        su, suu, sv, svv, suv = S[j] - S[i], SS[j] - SS[i], T[j] - T[i], TT[j] - TT[i], ST[j] - ST[i]
        den = m * suu - su * su
        if den <= 1e-12:
            return svv - sv * sv / m
        b = (m * suv - su * sv) / den
        a = (sv - b * su) / m
        return svv - 2 * a * sv - 2 * b * suv + a * a * m + 2 * a * b * su + b * b * suu

    INF = float("inf")
    D = np.full((k + 1, n + 1), INF)
    P = np.zeros((k + 1, n + 1), int)
    D[0, 0] = 0
    for s in range(1, k + 1):
        for j in range(s * min_len, n + 1):
            best, arg = INF, -1
            for i in range((s - 1) * min_len, j - min_len + 1):
                if D[s - 1, i] < INF:
                    c = D[s - 1, i] + sse(i, j)
                    if c < best:
                        best, arg = c, i
            D[s, j], P[s, j] = best, arg
    starts, j = [], n
    for s in range(k, 0, -1):
        i = P[s, j]
        starts.append(i)
        j = i
    starts = starts[::-1]
    segs = []
    for a, b in zip(starts, starts[1:] + [n]):
        uu, vv = u[a:b], v[a:b]
        slope, icpt = np.polyfit(uu, vv, 1)
        segs.append({"i0": int(a), "i1": int(b), "slope": float(slope), "intercept": float(icpt)})
    return segs, float(D[k, n])


def line_intersection(s1, s2):
    """u where two fitted segment lines v = a + b u intersect."""
    if abs(s1["slope"] - s2["slope"]) < 1e-9:
        return None
    u = (s2["intercept"] - s1["intercept"]) / (s1["slope"] - s2["slope"])
    return u, s1["intercept"] + s1["slope"] * u


# ------------------------------------------------------------------ scans along projected lines
def sample_line(img, p0, p1, n):
    us = np.linspace(p0[0], p1[0], n).astype(np.float32)
    vs = np.linspace(p0[1], p1[1], n).astype(np.float32)
    out = cv2.remap(img.astype(np.float32), us[None, :], vs[None, :], cv2.INTER_LINEAR)
    return us, vs, out[0]


def body_colour(lab, mask, center_uv, radius):
    """Median Lab colour and spread of the mask pixels in a disc (e.g. the door)."""
    H, W = mask.shape
    yy, xx = np.ogrid[:H, :W]
    sel = ((xx - center_uv[0]) ** 2 + (yy - center_uv[1]) ** 2 <= radius ** 2) & (mask > 0)
    px = lab[sel].reshape(-1, 3).astype(float)
    med = np.median(px, axis=0)
    spread = np.median(np.linalg.norm(px - med, axis=1)) + 1e-6
    return med, float(spread)


def first_body_run(lab, p0, p1, body_lab, body_spread, run=3, k=3.0, n=None):
    """Walk from p0 to p1 and return the first point where >= `run` consecutive samples are within
    k x spread (Lab distance) of the body colour (sub-sample: first sample of the run)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = n or max(2, int(L * 2))
    us, vs = np.linspace(p0[0], p1[0], n), np.linspace(p0[1], p1[1], n)
    c = np.stack([sample_line(lab[:, :, i], p0, p1, n)[2] for i in range(3)], axis=1)
    near = np.linalg.norm(c - body_lab, axis=1) <= k * max(body_spread, 4.0)
    for i in range(len(near) - run):
        if near[i:i + run].all():
            return float(us[i]), float(vs[i])
    return None


def mask_exit(mask, p0, p1, n=None):
    """Walk from p0 (inside the mask) towards p1 and return the last inside point (silhouette edge)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = n or max(2, int(L * 4))
    us, vs, m = sample_line(mask, p0, p1, n)
    inside = m >= 128
    if not inside[0]:
        return None
    k = int(np.argmax(~inside)) if (~inside).any() else len(inside) - 1
    return float(us[max(k - 1, 0)]), float(vs[max(k - 1, 0)])


def snap_to_edge(grey, uv, direction, search=12, sigma=1.0):
    """Move a silhouette point along `direction` (unit, image coords) to the strongest intensity
    gradient within +-search px (sub-pixel parabolic peak). Returns (u, v, shift_px)."""
    g = cv2.GaussianBlur(grey.astype(np.float32), (0, 0), sigma)
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    ts = np.arange(-search, search + 0.25, 0.25)
    us = (uv[0] + ts * d[0]).astype(np.float32)
    vs = (uv[1] + ts * d[1]).astype(np.float32)
    prof = cv2.remap(g, us[None, :], vs[None, :], cv2.INTER_LINEAR)[0]
    grad = np.abs(np.gradient(prof, 0.25))
    i = int(np.argmax(grad))
    if 0 < i < len(grad) - 1:
        den = grad[i - 1] - 2 * grad[i] + grad[i + 1]
        off = 0.5 * (grad[i - 1] - grad[i + 1]) / den if den != 0 else 0.0
    else:
        off = 0.0
    t = ts[i] + off * 0.25
    return float(uv[0] + t * d[0]), float(uv[1] + t * d[1]), float(t)


def detect_rim_ellipse(grey, center, r_tire_px, rng=None, iters=600, r_lo=0.55, r_hi=0.95, tol=None, polarity=True):
    """Rim-lip ellipse by RANSAC on Canny edges in an annulus around `center`, keeping only edge pixels
    whose gradient is within 35 deg of radial (spokes give tangential gradients and are rejected).
    Returns dict(center, axes (semi), angle_deg, n_inliers, rms_px) or None."""
    rng = rng or np.random.default_rng(1)
    g = cv2.GaussianBlur(grey, (0, 0), max(0.8, r_tire_px / 80))
    med = float(np.median(g))
    e = cv2.Canny(g, 0.33 * med + 10, 0.66 * med + 30)
    gx = cv2.Sobel(g.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    ys, xs = np.nonzero(e)
    dx, dy = xs - center[0], ys - center[1]
    r = np.hypot(dx, dy)
    sel = (r > r_lo * r_tire_px) & (r < r_hi * r_tire_px)
    xs, ys, dx, dy, r = xs[sel], ys[sel], dx[sel], dy[sel], r[sel]
    if len(xs) < 20:
        return None
    gxx, gyy = gx[ys, xs], gy[ys, xs]
    dot = gxx * dx + gyy * dy
    cosang = np.abs(dot) / (np.hypot(gxx, gyy) * r + 1e-9)
    # radial gradient, and brighter towards the centre (wheel face inside, black tyre outside): rejects spokes
    # (tangential gradients) and the tyre's outline against the body or ground (brighter outside)
    keep = (cosang > math.cos(math.radians(35))) & ((dot < 0) if polarity else True)
    pts = np.c_[xs[keep], ys[keep]].astype(np.float32)
    if len(pts) < 20:
        return None
    tol = tol or max(1.0, r_tire_px / 60)
    best = None
    for _ in range(iters):
        sub = pts[rng.choice(len(pts), 6, replace=False)]
        try:
            (cx, cy), (A, B), ang = cv2.fitEllipse(sub)
        except cv2.error:
            continue
        a, b = A / 2, B / 2
        if not (r_lo * r_tire_px < max(a, b) < r_hi * r_tire_px and min(a, b) > 0.3 * max(a, b)):
            continue
        if math.hypot(cx - center[0], cy - center[1]) > 0.35 * r_tire_px:
            continue
        d = ellipse_distance(pts, (cx, cy), (a, b), ang)
        n = int((np.abs(d) < tol).sum())
        if best is None or n > best[0]:
            best = (n, (cx, cy), (a, b), ang)
    if best is None:
        return None
    n, c, ax, ang = best
    inl = pts[np.abs(ellipse_distance(pts, c, ax, ang)) < tol]
    if len(inl) < 8:
        return None
    (cx, cy), (A, B), ang = cv2.fitEllipse(inl)
    d = ellipse_distance(inl, (cx, cy), (A / 2, B / 2), ang)
    return {"center": [float(cx), float(cy)], "axes": [float(A / 2), float(B / 2)], "angle_deg": float(ang),
            "n_inliers": int(len(inl)), "rms_px": float(np.sqrt(np.mean(d ** 2))), "points": inl}


def ellipse_distance(pts, c, axes, ang_deg):
    """Approximate signed distance (px) of points to an ellipse (OpenCV fitEllipse convention)."""
    t = math.radians(ang_deg)
    x = (pts[:, 0] - c[0]) * math.cos(t) + (pts[:, 1] - c[1]) * math.sin(t)
    y = -(pts[:, 0] - c[0]) * math.sin(t) + (pts[:, 1] - c[1]) * math.cos(t)
    a, b = axes
    q = np.sqrt((x / a) ** 2 + (y / b) ** 2)
    return (q - 1) * np.sqrt(a * b)


def find_wheel(grey, contact_uv, r_range, n_scales=14, rng=None, polarity=True):
    """Locate a wheel's rim-lip ellipse from its tyre contact point: try tyre radii over `r_range` (px),
    guess the centre one radius above the contact, run detect_rim_ellipse, and keep the candidate whose
    inliers cover the largest fraction of its circumference (rms < 2.5 px). Returns the ellipse dict
    with 'coverage' and 'r_tire_guess', or None."""
    best = None
    for r in np.geomspace(r_range[0], r_range[1], n_scales):
        el = detect_rim_ellipse(grey, (contact_uv[0], contact_uv[1] - r), r, rng=rng or np.random.default_rng(7),
                                iters=400, r_lo=0.5, r_hi=0.95, polarity=polarity)
        if el is None or el["rms_px"] > 2.5:
            continue
        circ = math.pi * (3 * sum(el["axes"]) - math.sqrt((3 * el["axes"][0] + el["axes"][1]) * (el["axes"][0] + 3 * el["axes"][1])))
        cov = el["n_inliers"] / max(circ, 1)
        # geometry: the tyre bottom lies about one tyre radius below the rim centre, and the rim-lip radius is
        # ~0.76 of the tyre radius (0.246 / 0.323 m), so contact depth / rim radius should be ~1.3 (1.15-1.55)
        dv = contact_uv[1] - el["center"][1]
        if not (1.15 * max(el["axes"]) < dv < 1.55 * max(el["axes"])) or cov < 0.3:
            continue
        if best is None or el["n_inliers"] > best["n_inliers"]:
            el["coverage"], el["r_tire_guess"] = float(cov), float(r)
            best = el
    return best


def refine_rim_radial(grey, el, n_rays=72, band=(0.80, 1.20), iters=3):
    """Refine a rim-lip ellipse: along rays from the current centre, take the strongest bright->dark
    (wheel face -> tyre) transition within `band` x the current ellipse radius in that direction, then
    refit the ellipse to those points with MAD outlier rejection. Iterates the centre."""
    g = cv2.GaussianBlur(grey.astype(np.float32), (0, 0), 1.0)
    c = np.array(el["center"], float)
    a, b = el["axes"]
    ang = el["angle_deg"]
    pts = None
    for _ in range(iters):
        P = []
        t = math.radians(ang)
        for th in np.linspace(0, 2 * np.pi, n_rays, endpoint=False):
            # ellipse radius along this ray
            dx, dy = math.cos(th), math.sin(th)
            x = dx * math.cos(t) + dy * math.sin(t)
            y = -dx * math.sin(t) + dy * math.cos(t)
            r0 = 1.0 / math.sqrt((x / a) ** 2 + (y / b) ** 2)
            rs = np.arange(band[0] * r0, band[1] * r0, 0.25)
            us = (c[0] + rs * dx).astype(np.float32)
            vs = (c[1] + rs * dy).astype(np.float32)
            prof = cv2.remap(g, us[None, :], vs[None, :], cv2.INTER_LINEAR)[0]
            dprof = -np.gradient(prof, 0.25)          # positive where intensity falls outward
            i = int(np.argmax(dprof))
            if dprof[i] <= 2.0:
                continue
            if 0 < i < len(dprof) - 1:
                den = dprof[i - 1] - 2 * dprof[i] + dprof[i + 1]
                off = 0.5 * (dprof[i - 1] - dprof[i + 1]) / den if den != 0 else 0.0
            else:
                off = 0.0
            r = rs[i] + off * 0.25
            P.append((c[0] + r * dx, c[1] + r * dy, dprof[i]))
        if len(P) < 12:
            return el
        P = np.array(P)
        pts = P[:, :2].astype(np.float32)
        (cx, cy), (A, B), ang2 = cv2.fitEllipse(pts)
        d = ellipse_distance(pts, (cx, cy), (A / 2, B / 2), ang2)
        mad = np.median(np.abs(d - np.median(d))) * 1.4826 + 1e-6
        keep = np.abs(d) < max(3 * mad, 0.5)
        if keep.sum() >= 12:
            pts = pts[keep]
            (cx, cy), (A, B), ang2 = cv2.fitEllipse(pts)
        c, a, b, ang = np.array([cx, cy]), A / 2, B / 2, ang2
    d = ellipse_distance(pts, c, (a, b), ang)
    out = dict(el)
    out.update(center=[float(c[0]), float(c[1])], axes=[float(a), float(b)], angle_deg=float(ang),
               n_inliers=int(len(pts)), rms_px=float(np.sqrt(np.mean(d ** 2))), refined="radial", points=pts)
    return out


def well_to_body_edge(lab, p0, p1, body_lab, run=2, n=None):
    """Walk from p0 (inside the dark wheel well, just above the tyre) to p1 and return the first point
    that is closer (Lab) to the body colour than to the well colour (median of the first samples),
    held for `run` samples; sub-sample position by linear interpolation of the two distances."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = n or max(8, int(L * 2))
    us, vs = np.linspace(p0[0], p1[0], n), np.linspace(p0[1], p1[1], n)
    c = np.stack([sample_line(lab[:, :, i], p0, p1, n)[2] for i in range(3)], axis=1)
    well = np.median(c[:3], axis=0)
    if np.linalg.norm(well - body_lab) < 15:
        return None                                   # no contrast between well and body
    dw = np.linalg.norm(c - well, axis=1)
    db = np.linalg.norm(c - body_lab, axis=1)
    g = dw - db                                       # > 0 once closer to the body
    for i in range(1, n - run):
        if (g[i:i + run] > 0).all():
            t = g[i - 1] / (g[i - 1] - g[i]) if g[i - 1] < 0 else 0.0
            return float(us[i - 1] + t * (us[i] - us[i - 1])), float(vs[i - 1] + t * (vs[i] - vs[i - 1]))
    return None
