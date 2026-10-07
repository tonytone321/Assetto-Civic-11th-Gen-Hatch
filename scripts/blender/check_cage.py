"""Check that the saved reference cage reproduces the database's headline dimensions.

Run: blender -b blender/reference_cage.blend --python scripts/blender/check_cage.py
Writes docs/phase2/cage_check.json and exits non-zero on any failure.

Geometry is measured from the stored mesh/curve coordinates (Blender stores them as 32-bit floats,
so "exact" means equal within float32 storage precision, TOL below). The double-precision custom
properties written by the builder must equal the database values bit-for-bit.
"""
import json
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import coords  # noqa: E402

TOL = 2e-6  # m: float32 storage of coordinates up to ~5 m (spacing ~4.8e-7 m); not a modelling tolerance
RES = json.load(open(os.path.join(ROOT, "vehicle_data", "_resolved.json"), encoding="utf-8"))["parameters"]


def db(k):
    return RES[k]["value"]


def project_points(obj):
    mw = obj.matrix_world
    if obj.type == "MESH":
        pts = [mw @ v.co for v in obj.data.vertices]
    elif obj.type == "CURVE":
        pts = [mw @ p.co.xyz for s in obj.data.splines for p in s.points]
    else:
        pts = [mw.translation]
    return [coords.blender_to_project(tuple(p)) for p in pts]


def extent(pts, i):
    vals = [p[i] for p in pts]
    return min(vals), max(vals)


def main():
    o = bpy.data.objects
    checks = []

    def chk(name, measured, key, note):
        expect = db(key)
        diff = measured - expect
        checks.append({"check": name, "key": key, "database": expect, "cage": measured, "diff_m": diff,
                       "pass": abs(diff) <= TOL, "note": note})

    box = project_points(o["REF_body_box"])
    (x0, x1), (y0, y1), (z0, z1) = extent(box, 0), extent(box, 1), extent(box, 2)
    chk("length (body box Y extent)", y1 - y0, "dimensions.length", "REF_body_box")
    chk("width (body box X extent)", x1 - x0, "dimensions.width_body", "REF_body_box")
    chk("height (body box Z extent)", z1 - z0, "dimensions.height", "REF_body_box")
    chk("box front face Y = front overhang", y1, "dimensions.overhang_front", "photo-derived placement")
    yf = extent(project_points(o["REF_contact_line_front"]), 1)[0]
    yr = extent(project_points(o["REF_contact_line_rear"]), 1)[0]
    chk("wheelbase (contact lines)", yf - yr, "dimensions.wheelbase", "REF_contact_line_front/rear")
    wf = project_points(o["REF_wheel_center_FL"])[0], project_points(o["REF_wheel_center_FR"])[0]
    wr = project_points(o["REF_wheel_center_RL"])[0], project_points(o["REF_wheel_center_RR"])[0]
    chk("front track (wheel centres FR - FL)", wf[1][0] - wf[0][0], "dimensions.track_front", "REF_wheel_center_FL/FR")
    chk("rear track (wheel centres RR - RL)", wr[1][0] - wr[0][0], "dimensions.track_rear", "REF_wheel_center_RL/RR")
    chk("wheelbase (wheel centres FL - RL)", wf[0][1] - wr[0][1], "dimensions.wheelbase", "REF_wheel_center_FL/RL")
    cf = extent(project_points(o["REF_contact_line_front"]), 0)
    cr = extent(project_points(o["REF_contact_line_rear"]), 0)
    chk("front track (contact line)", cf[1] - cf[0], "dimensions.track_front", "REF_contact_line_front")
    chk("rear track (contact line)", cr[1] - cr[0], "dimensions.track_rear", "REF_contact_line_rear")
    if "REF_mirror_width_L" in o:
        ml, mr = project_points(o["REF_mirror_width_L"])[0][0], project_points(o["REF_mirror_width_R"])[0][0]
        chk("width over mirrors", mr - ml, "dimensions.width_mirrors", "REF_mirror_width_L/R")

    props = []
    for ob in o:
        for k in ob.keys():
            if k.startswith("db:"):
                key = k[3:]
                ok = float(ob[k]) == float(db(key))
                props.append({"object": ob.name, "key": key, "pass": ok})
    out = {"tolerance_m": TOL, "tolerance_basis": "float32 coordinate storage in Blender",
           "blender": bpy.app.version_string, "checks": checks,
           "custom_property_checks": {"n": len(props), "failed": [p for p in props if not p["pass"]]},
           "pass": all(c["pass"] for c in checks) and all(p["pass"] for p in props)}
    p = os.path.join(ROOT, "docs", "phase2", "cage_check.json")
    json.dump(out, open(p, "w"), indent=1)
    for c in checks:
        print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['check']}: cage {c['cage']:.7f} vs db {c['database']:.7f} "
              f"(diff {c['diff_m']*1e6:+.3f} um)")
    print(f"custom properties: {len(props)} checked, {len(out['custom_property_checks']['failed'])} failed")
    print("CAGE_CHECK", "PASS" if out["pass"] else "FAIL")
    sys.exit(0 if out["pass"] else 1)


main()
