#!/usr/bin/env python3
"""Physical cross-checks between resolved values. Each check returns
{name, status: pass|fail|not_run, detail}. Used by validate_db.py and make_report.py.
A check whose inputs are unresolved is 'not_run' (reported, not silently passed)."""
import math


def _v(res, key):
    r = res.get(key)
    return None if r is None else r.get("value")


def _need(res, *keys):
    miss = [k for k in keys if not isinstance(_v(res, k), (int, float)) or isinstance(_v(res, k), bool)]
    return miss


def check_length_sum(res):
    k = ("dimensions.length", "dimensions.wheelbase", "dimensions.overhang_front", "dimensions.overhang_rear")
    m = _need(res, *k)
    if m:
        return "not_run", f"missing {m}"
    L, wb, of, orr = (_v(res, x) for x in k)
    d = L - (wb + of + orr)
    return ("pass" if abs(d) <= 0.010 else "fail"), f"length - (wheelbase+overhangs) = {d*1000:.1f} mm (tol 10 mm)"


def check_axle_masses(res):
    """Axle masses (curb x distribution) must sum to curb mass and fit inside the ratings.
    Uses the trim GVWR/GAWRs when known; otherwise the NHTSA lineup minimum GVWR as a bound."""
    m = _need(res, "mass.curb_mass")
    if m:
        return "not_run", f"missing {m}"
    curb = _v(res, "mass.curb_mass")
    msgs, ok = [], True
    fa, ra = _v(res, "mass.front_axle_mass"), _v(res, "mass.rear_axle_mass")
    if isinstance(fa, (int, float)) and isinstance(ra, (int, float)):
        d = fa + ra - curb
        ok &= abs(d) <= 1.0
        msgs.append(f"front {fa:.0f} + rear {ra:.0f} = {fa+ra:.0f} kg vs curb {curb:.0f} kg (diff {d:+.1f})")
    else:
        msgs.append("axle masses unresolved")
    gvwr = _v(res, "mass.gvwr")
    label = "GVWR"
    if not isinstance(gvwr, (int, float)):
        gvwr, label = _v(res, "mass.gvwr_lineup_min"), "lineup-minimum GVWR (trim GVWR unknown)"
    if isinstance(gvwr, (int, float)):
        ok &= curb < gvwr
        msgs.append(f"curb {curb:.0f} kg < {label} {gvwr:.0f} kg: {curb < gvwr} (payload margin {gvwr-curb:.0f} kg)")
    gf, gr = _v(res, "mass.gawr_front"), _v(res, "mass.gawr_rear")
    if isinstance(gf, (int, float)) and isinstance(gr, (int, float)) and isinstance(fa, (int, float)):
        ok &= fa <= gf and ra <= gr
        msgs.append(f"axle loads within GAWR F {gf:.0f} / R {gr:.0f} kg: {fa <= gf and ra <= gr}")
    else:
        msgs.append("GAWR unknown: per-axle rating check not run")
    return ("pass" if ok else "fail"), "; ".join(msgs)


def check_track_width(res):
    m = _need(res, "dimensions.track_front", "dimensions.track_rear", "dimensions.width_body", "tires.section_width")
    if m:
        return "not_run", f"missing {m}"
    W, sw = _v(res, "dimensions.width_body"), _v(res, "tires.section_width")
    out = []
    ok = True
    for ax in ("front", "rear"):
        t = _v(res, f"dimensions.track_{ax}")
        outer = t + sw
        margin = W - outer
        out.append(f"{ax}: track+section width {outer*1000:.0f} mm vs body width {W*1000:.0f} mm "
                   f"(margin {margin*1000:.0f} mm)")
        if not (0.0 <= margin <= 0.20):
            ok = False
    return ("pass" if ok else "fail"), "; ".join(out) + " (expected 0–200 mm)"


def check_steering(res):
    m = _need(res, "steering.ratio_overall", "steering.turns_lock_to_lock", "steering.turning_circle_diameter",
               "dimensions.wheelbase", "dimensions.track_front")
    if m:
        return "not_run", f"missing {m}"
    ratio, turns = _v(res, "steering.ratio_overall"), _v(res, "steering.turns_lock_to_lock")
    D, wb, tf = (_v(res, k) for k in ("steering.turning_circle_diameter", "dimensions.wheelbase",
                                       "dimensions.track_front"))
    hand_angle = turns * 360.0 / 2.0
    road_from_ratio = hand_angle / ratio  # mean road-wheel angle at lock, deg
    R = D / 2.0  # outer front wheel path radius (curb-to-curb approx.)
    outer = math.degrees(math.asin(min(1.0, wb / R)))
    inner = math.degrees(math.atan(wb / (math.sqrt(max(R * R - wb * wb, 1e-9)) - tf)))
    mean = (outer + inner) / 2.0
    dev = (road_from_ratio - mean) / mean
    st = "pass" if abs(dev) <= 0.20 else "fail"
    return st, (f"ratio x lock gives mean road-wheel angle {road_from_ratio:.1f} deg; turning circle "
                f"(outer-wheel radius {R:.2f} m, wheelbase, track) implies outer {outer:.1f} / inner {inner:.1f} "
                f"deg (mean {mean:.1f}); deviation {dev*100:+.0f}% (tol ±20%: variable ratio and turning-circle "
                f"definition make this approximate)")


def check_gear_speed(res, derived_tables=None):
    """Compare predicted engine rpm at an observed road speed in a gear with the observation.
    Observation parameters: drivetrain.obs_* records whose value is rpm and whose record notes
    the speed/gear; the drivetrain derivations register drivetrain.pred_* counterparts."""
    pairs = []
    for k in res:
        if k.startswith("drivetrain.obs_rpm"):
            p = k.replace("obs_", "pred_", 1)
            if p in res:
                pairs.append((k, p))
    if not pairs:
        return "not_run", "no drivetrain.obs_rpm_* observation with a matching drivetrain.pred_rpm_* derivation"
    out, ok, ran = [], True, False
    for o, p in pairs:
        ov, pv = _v(res, o), _v(res, p)
        if not isinstance(ov, (int, float)) or not isinstance(pv, (int, float)):
            out.append(f"{o}: not computable")
            continue
        ran = True
        dev = (pv - ov) / ov
        out.append(f"{o}: observed {ov:.0f} rpm, predicted {pv:.0f} rpm ({dev*100:+.1f}%)")
        if abs(dev) > 0.04:
            ok = False
    if not ran:
        return "not_run", "; ".join(out)
    return ("pass" if ok else "fail"), "; ".join(out) + " (tol ±4%: tach resolution, rounding, tire growth)"


def check_tire_diameter(res):
    """Maker-published overall diameter vs nominal from the size string (derived)."""
    r = res.get("tires.overall_diameter")
    n = res.get("tires.overall_diameter_nominal")
    if not r or not n or r.get("value") is None or n.get("value") is None:
        return "not_run", "need tires.overall_diameter and tires.overall_diameter_nominal"
    dev = (r["value"] - n["value"]) / n["value"]
    return ("pass" if abs(dev) <= 0.02 else "fail"), (f"selected {r['value']*1000:.1f} mm vs nominal "
                                                     f"{n['value']*1000:.1f} mm ({dev*100:+.2f}%, tol ±2%)")


def check_rolling_circumference(res):
    a, b = res.get("tires.rolling_circumference"), res.get("tires.rolling_circumference_from_revs")
    if not a or not b or a.get("value") is None or b.get("value") is None:
        return "not_run", "need tires.rolling_circumference and tires.rolling_circumference_from_revs"
    dev = (a["value"] - b["value"]) / b["value"]
    return ("pass" if abs(dev) <= 0.015 else "fail"), (f"selected {a['value']:.4f} m vs published revs/mile "
                                                      f"{b['value']:.4f} m ({dev*100:+.2f}%, tol ±1.5%)")


CHECKS = [
    ("Overall length = wheelbase + overhangs", check_length_sum),
    ("Axle masses vs curb mass and ratings", check_axle_masses),
    ("Track + tire width vs overall width", check_track_width),
    ("Steering ratio x lock vs turning circle", check_steering),
    ("Gear speed vs real observation", check_gear_speed),
    ("Tire diameter: published vs nominal", check_tire_diameter),
    ("Rolling circumference: size-based vs published revs/mile", check_rolling_circumference),
]


def run(res):
    out = []
    for name, fn in CHECKS:
        try:
            st, detail = fn(res)
        except Exception as e:
            st, detail = "fail", f"check error {type(e).__name__}: {e}"
        out.append({"name": name, "status": st, "detail": detail})
    return out
