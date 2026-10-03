#!/usr/bin/env python3
"""Generate vehicle_data/hardpoints.json (domain 6): suspension and steering pickup points
in vehicle coordinates (origin on the ground at the centreline below the front axle,
+X right, +Y forward, +Z up, metres). LEFT side only (X < 0); the right side is the
mirror image X -> -X (assumed symmetric).

No dimensioned drawing of this car's suspension is publicly available (Honda service
information is paywalled; parts-catalogue diagrams are undimensioned), so:
  * confirmed : none.
  * estimated : generated HERE from stated constraints. Published inputs (wheelbase, track,
                tyre size) are class A; every other offset is an engineering packaging
                assumption for a compact FWD car with MacPherson front / 4-link rear
                (class E), given with a range. Points that depend on several assumptions
                (strut top from KPI + caster) are Monte-Carlo propagated; the reported range
                is the min/max over the samples.
  * unknown   : points with no usable constraint.
Every estimated point is a placeholder for Phase 2 geometry, to be replaced by measured
points (vehicle_data/user_measurements.json). Never hand-edit the JSON: change the
constraints below and re-run.

Usage: python3 scripts/domains/hardpoints_estimate.py
"""
import json
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db  # noqa: E402

N_SAMPLES = 4000
SEED = 20261003


# ----------------------------------------------------------------- published inputs
def resolved(key, fallback, fallback_src):
    """Take the resolved value if the coordinator has resolved it, else the cited fallback."""
    p = os.path.join(ROOT, "vehicle_data", "_resolved.json")
    try:
        r = json.load(open(p, encoding="utf-8"))["parameters"][key]
        if r.get("value") is not None:
            return r["value"], f"{key} from vehicle_data/_resolved.json (source {r.get('source_id')})"
    except (OSError, KeyError, ValueError):
        pass
    return fallback, f"{key} fallback {fallback} m ({fallback_src})"


WB, WB_SRC = resolved("dimensions.wheelbase", 2.735, "hondanews.ca 2024 Civic Hatchback Specifications, 'Wheelbase (mm) 2735'")
TF, TF_SRC = resolved("dimensions.track_front", 1.536, "hondanews.ca 2024, 'Track – front/rear (mm) 1536/1565'")
TR, TR_SRC = resolved("dimensions.track_rear", 1.565, "hondanews.ca 2024, 'Track – front/rear (mm) 1536/1565'")
# tyre 235/40R18 (hondanews.ca 2024 'All-season tires P235/40 R18 91W'); radii computed, not typed
R_FREE = (18 * 0.0254) / 2 + 0.235 * 0.40
TYRE_DEFL = (0.008, 0.022)          # static deflection assumption (class E)

INPUTS = {
    "wheelbase": {"value": WB, "basis": WB_SRC},
    "track_front": {"value": TF, "basis": TF_SRC},
    "track_rear": {"value": TR, "basis": TR_SRC},
    "tyre_free_radius": {"value": R_FREE, "basis": "computed from 235/40R18: 18 in rim/2 + 0.235 m x 0.40 (hondanews.ca 2024 tyre size)"},
    "tyre_static_deflection": {"range": list(TYRE_DEFL), "basis": "class E assumption for a 40-series tyre at curb load"},
}

# ----------------------------------------------------------------- constraints (class E)
# Each entry: name -> (kind, args). Offsets: 'inb' = distance inboard of the wheel-centre
# plane (+ = towards centreline); 'dy' = longitudinal offset from the axle line (+ forward);
# 'z' = absolute height above ground, or 'dz' = offset from wheel-centre height.
# (lo, hi) uniform ranges; nominal = midpoint.
FRONT = {
    "lower_ball_joint": dict(inb=(0.085, 0.125), dy=(-0.020, 0.020), z=(0.120, 0.170),
                             basis="MacPherson lower ball joint packaged inside an 18-in wheel barrel, below the hub"),
    "lca_front_inner": dict(inb=(0.360, 0.470), dy=(-0.020, 0.060), z=(0.170, 0.240),
                            basis="front lower-arm front bushing on the subframe, roughly in line with the axle"),
    "lca_rear_inner": dict(inb=(0.340, 0.460), dy=(-0.400, -0.260), z=(0.180, 0.260),
                           basis="front lower-arm rear (compliance) bushing behind the axle; press kit: 'larger compliance bushing'"),
    "tie_rod_outer": dict(inb=(0.100, 0.160), dy=(-0.170, -0.100), dz=(-0.050, 0.050),
                          basis="steering arm behind the axle (rear-steer rack, usual for transverse-engine FWD); not confirmed"),
    "tie_rod_inner": dict(x_abs=(0.300, 0.420), dy=(-0.200, -0.100), dz=(-0.030, 0.080),
                          basis="rack ball joint ~0.30-0.42 m from centreline at rack height"),
}
STRUT = dict(kpi_deg=(11.0, 15.0), caster_deg=(3.5, 6.5), top_z=(0.900, 1.020),
             basis="strut top from lower ball joint along the steering axis: KPI 11-15 deg, caster 3.5-6.5 deg (typical road-car MacPherson; Honda alignment spec not accessible), top mount 0.90-1.02 m above ground")
REAR = {
    "trailing_arm_front": dict(inb=(0.150, 0.270), dy=(0.400, 0.600), z=(0.260, 0.350),
                               basis="trailing-arm front bushing to body ahead of the rear axle"),
    "upper_arm_outer": dict(inb=(0.090, 0.160), dy=(-0.050, 0.050), dz=(0.130, 0.230), basis="upper arm to knuckle above the hub"),
    "upper_arm_inner": dict(inb=(0.350, 0.480), dy=(-0.060, 0.060), dz=(0.120, 0.220), basis="upper arm to rear subframe"),
    "lower_arm_a_outer": dict(inb=(0.070, 0.140), dy=(0.040, 0.160), dz=(-0.110, -0.050), basis="front lower lateral link (toe control) at knuckle, ahead of the axle"),
    "lower_arm_a_inner": dict(inb=(0.450, 0.600), dy=(0.060, 0.180), dz=(-0.090, -0.030), basis="front lower lateral link to subframe"),
    "lower_arm_b_outer": dict(inb=(0.060, 0.110), dy=(-0.120, 0.020), dz=(-0.170, -0.090), basis="rear lower arm B to knuckle, below the hub"),
    "lower_arm_b_inner": dict(inb=(0.480, 0.620), dy=(-0.140, 0.000), dz=(-0.120, -0.040), basis="rear lower arm B to subframe"),
    "damper_lower": dict(inb=(0.080, 0.140), dy=(-0.120, -0.020), dz=(-0.130, -0.060), basis="separate rear damper to knuckle/arm B (layout not confirmed)"),
    "damper_upper": dict(inb=(0.180, 0.300), dy=(-0.160, -0.040), dz=(0.420, 0.580), basis="damper top in the rear wheelhouse (layout not confirmed)"),
}
REAR_SPRING = dict(mr=(0.62, 0.85), height=(0.200, 0.300),
                   basis="spring believed seated on lower arm B at the motion-ratio fraction of the arm's lateral span (suspension.motion_ratio_rear range 0.62-0.85); upper seat 0.20-0.30 m above (layout not confirmed)")

UNKNOWN = {
    "front.arb_link_upper": "front anti-roll-bar link on the strut",
    "front.arb_link_lower": "front anti-roll-bar link on the bar arm",
    "front.arb_bushing": "front anti-roll-bar body/subframe bushing",
    "front.subframe_mounts": "front subframe-to-body mounts",
    "rear.arb_link_upper": "rear anti-roll-bar link at arm/knuckle",
    "rear.arb_bushing": "rear anti-roll-bar bushing",
    "rear.subframe_mounts": "rear subframe-to-body mounts",
    "steering.rack_mounts": "steering rack mounting bushes",
}


# ----------------------------------------------------------------- generation
def u(rng, r):
    return rng.uniform(r[0], r[1])


def sample_point(rng, c, half_track, y_axle, wcz):
    if "x_abs" in c:
        x = -u(rng, c["x_abs"])
    else:
        x = -(half_track - u(rng, c["inb"]))
    y = y_axle + u(rng, c["dy"])
    z = u(rng, c["z"]) if "z" in c else wcz + u(rng, c["dz"])
    return (x, y, z)


def nominal(c, half_track, y_axle, wcz):
    mid = lambda r: 0.5 * (r[0] + r[1])  # noqa: E731
    x = -mid(c["x_abs"]) if "x_abs" in c else -(half_track - mid(c["inb"]))
    z = mid(c["z"]) if "z" in c else wcz + mid(c["dz"])
    return (x, y_axle + mid(c["dy"]), z)


def strut_top(lbj, kpi, caster, top_z):
    h = top_z - lbj[2]
    return (lbj[0] + h * math.tan(math.radians(kpi)), lbj[1] - h * math.tan(math.radians(caster)), top_z)


def rear_spring(arm_in, arm_out, wc_x, mr, height):
    # point on arm B whose lateral distance from the inner pivot is mr x (inner pivot -> wheel plane)
    frac = mr * (wc_x - arm_in[0]) / (arm_out[0] - arm_in[0])
    p = tuple(arm_in[i] + frac * (arm_out[i] - arm_in[i]) for i in range(3))
    return p, (p[0], p[1], p[2] + height)


def run():
    rng = random.Random(SEED)
    wcz_mid = R_FREE - 0.5 * sum(TYRE_DEFL)
    samples = {}

    def add(name, pt):
        samples.setdefault(name, []).append(pt)

    for _ in range(N_SAMPLES):
        wcz = R_FREE - u(rng, TYRE_DEFL)
        add("front.wheel_center", (-TF / 2, 0.0, wcz))
        add("rear.wheel_center", (-TR / 2, -WB, wcz))
        fp = {n: sample_point(rng, c, TF / 2, 0.0, wcz) for n, c in FRONT.items()}
        for n, p in fp.items():
            add("front." + n, p)
        add("front.strut_top", strut_top(fp["lower_ball_joint"], u(rng, STRUT["kpi_deg"]), u(rng, STRUT["caster_deg"]), u(rng, STRUT["top_z"])))
        rp = {n: sample_point(rng, c, TR / 2, -WB, wcz) for n, c in REAR.items()}
        for n, p in rp.items():
            add("rear." + n, p)
        lo, hi = rear_spring(rp["lower_arm_b_inner"], rp["lower_arm_b_outer"], -TR / 2, u(rng, REAR_SPRING["mr"]), u(rng, REAR_SPRING["height"]))
        add("rear.spring_lower_seat", lo)
        add("rear.spring_upper_seat", hi)

    # nominal points (mid-range constraints)
    nom = {"front.wheel_center": (-TF / 2, 0.0, wcz_mid), "rear.wheel_center": (-TR / 2, -WB, wcz_mid)}
    fn = {n: nominal(c, TF / 2, 0.0, wcz_mid) for n, c in FRONT.items()}
    nom.update({"front." + n: p for n, p in fn.items()})
    mid = lambda r: 0.5 * (r[0] + r[1])  # noqa: E731
    nom["front.strut_top"] = strut_top(fn["lower_ball_joint"], mid(STRUT["kpi_deg"]), mid(STRUT["caster_deg"]), mid(STRUT["top_z"]))
    rn = {n: nominal(c, TR / 2, -WB, wcz_mid) for n, c in REAR.items()}
    nom.update({"rear." + n: p for n, p in rn.items()})
    lo, hi = rear_spring(rn["lower_arm_b_inner"], rn["lower_arm_b_outer"], -TR / 2, mid(REAR_SPRING["mr"]), mid(REAR_SPRING["height"]))
    nom["rear.spring_lower_seat"], nom["rear.spring_upper_seat"] = lo, hi

    basis = {"front.wheel_center": "X = -track_front/2, Y = 0, Z = tyre free radius - static deflection (published inputs + deflection assumption)",
             "rear.wheel_center": "X = -track_rear/2, Y = -wheelbase, Z as front",
             "front.strut_top": STRUT["basis"], "rear.spring_lower_seat": REAR_SPRING["basis"], "rear.spring_upper_seat": REAR_SPRING["basis"]}
    basis.update({"front." + n: c["basis"] for n, c in FRONT.items()})
    basis.update({"rear." + n: c["basis"] for n, c in REAR.items()})

    out = {"domain": "hardpoints", "title": "Suspension hard points (left side, vehicle coordinates)", "schema_version": 1,
           "updated": db.today(),
           "generator": {"script": "scripts/domains/hardpoints_estimate.py", "samples": N_SAMPLES, "seed": SEED,
                         "method": "uniform Monte-Carlo over the stated constraint ranges; value = point from mid-range constraints; range = per-coordinate min/max over samples",
                         "frame": "origin on ground at centreline below front axle; +X right, +Y forward, +Z up; metres; LEFT side (right = mirror X -> -X)"},
           "inputs": INPUTS,
           "constraints": {"front": FRONT, "strut": STRUT, "rear": REAR, "rear_spring": REAR_SPRING},
           "sources": {}, "parameters": {}}
    for name in sorted(samples):
        pts = samples[name]
        lo_v = [round(min(p[i] for p in pts), 4) for i in range(3)]
        hi_v = [round(max(p[i] for p in pts), 4) for i in range(3)]
        v = [round(c, 4) for c in nom[name]]
        wc = name.endswith("wheel_center")
        rec = db.record(value=v, unit="m", status="estimated", cls="D" if wc else "E", source_id=None, locator="",
                        evidence="", as_printed="", applicability=db.app("2024", "CA", "Sport Touring", "6MT", notes="estimate for the target car"),
                        confidence="medium" if wc else "low", range=[lo_v, hi_v],
                        how_to_measure=("Wheel centre: measure track at hub faces and hub height above ground at curb load." if wc else
                                        "Car on a lift at curb ride height (or ride height recorded): plumb-bob/laser to the floor grid for X,Y and height gauge for Z at the bushing/ball-joint centre; +/-3 mm. Photogrammetry of the underside with a scale bar is an alternative."),
                        notes="Basis: " + basis[name] + ". Value/range are [x, y, z] (range = [[x_lo, y_lo, z_lo], [x_hi, y_hi, z_hi]]).",
                        derivation={"script": "scripts/domains/hardpoints_estimate.py", "function": "run",
                                    "inputs": ["dimensions.wheelbase", "dimensions.track_front", "dimensions.track_rear", "tyre 235/40R18"]})
        out["parameters"]["hardpoints." + name] = {"description": f"{name.replace('.', ' ').replace('_', ' ')} (left side)", "unit": "m",
                                                   "impact": "high" if wc else "medium", "candidates": [rec]}
    for name, desc in UNKNOWN.items():
        out["parameters"]["hardpoints." + name] = {"description": desc + " (left side)", "unit": "m", "impact": "low", "candidates": [db.unknown(
            "m", searches=["Honda Canada/US spec tables and press releases (no geometry)", "hondapartsnow.com parts listings (undimensioned)",
                           "hondapartsconnection.com diagrams (Cloudflare challenge, not worked around)", "techinfo.honda.com (paywalled)"],
            how_to_measure="Measure on a lift as for the other hard points (+/-5 mm adequate).")]}

    counts = {"confirmed": 0, "estimated": 0, "unknown": 0}
    for p in out["parameters"].values():
        counts[p["candidates"][0]["status"]] += 1
    out["summary"] = dict(counts, total=sum(counts.values()),
                          note="Counts are per left-side point (right side mirrors). No hard point is confirmed: no dimensioned public source exists.")
    path = os.path.join(ROOT, "vehicle_data", "hardpoints.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(path, out["summary"])


if __name__ == "__main__":
    run()
