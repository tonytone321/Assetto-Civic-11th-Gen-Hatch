"""Build the Phase 2 dimensional reference cage in Blender from vehicle_data/_resolved.json.

Run (headless):
  blender -b --factory-startup --python scripts/blender/build_reference_cage.py -- [--out blender/reference_cage.blend]

No dimension is typed here: every size and position comes from _resolved.json (traced through
derived.json to tell photo-derived values from other derived ones). Display sizes of markers,
line thickness and plane margins are cosmetic and are not vehicle dimensions.

Collections (each object goes to the collection of the WEAKEST data that positions or sizes it):
  REF_measured   user's own measurements (vehicle_data/user_measurements.json)
  REF_published  manufacturer / government / reputable third party (classes A, C)
  REF_photo      derived from photo measurements (proportions.* and values derived from them)
  REF_estimated  engineering estimates and other derived values (classes D, E, F)
  REF_frame      the ground and centreline planes (definitions of the frame, no vehicle data)
Strength order for "weakest": measured > published > photo > estimated.

Writes blender/reference_cage.blend and blender/_build/cage_manifest.json (objects, values, classes,
missing items), which check_cage.py, the tests and the photo comparison read.
"""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import coords  # noqa: E402

RES = json.load(open(os.path.join(ROOT, "vehicle_data", "_resolved.json"), encoding="utf-8"))["parameters"]
DER = json.load(open(os.path.join(ROOT, "vehicle_data", "derived.json"), encoding="utf-8"))["parameters"]

# cosmetic display sizes (not vehicle data)
LINE = 0.010        # curve bevel radius / wireframe thickness, m
MARK = 0.018        # marker sphere radius, m
HP_MARK = 0.012     # hard-point marker radius, m
PLANE_MARGIN = 0.3  # ground/centreline plane margin around the car, m

STRENGTH = {"measured": 0, "published": 1, "photo": 2, "estimated": 3}
COLL = {"measured": "REF_measured", "published": "REF_published", "photo": "REF_photo", "estimated": "REF_estimated"}
COLORS = {"REF_measured": (0.10, 0.65, 0.20, 1), "REF_published": (0.10, 0.35, 0.90, 1),
          "REF_photo": (0.95, 0.50, 0.05, 1), "REF_estimated": (0.60, 0.20, 0.75, 1), "REF_frame": (0.6, 0.6, 0.6, 1)}

MISSING = []    # (item, reason)
OBJECTS = {}    # name -> manifest entry


# ------------------------------------------------------------------ data access
def rec(key):
    r = RES.get(key)
    return r if r and r.get("value") is not None else None


def val(key):
    r = rec(key)
    return None if r is None else r["value"]


def _photo_derived(key, seen=None):
    if key.startswith("proportions."):
        return True
    seen = seen or set()
    if key in seen:
        return False
    seen.add(key)
    d = DER.get(key)
    if not d:
        return False
    ins = (d["candidates"][0].get("derivation") or {}).get("inputs", {})
    return any(_photo_derived(k, seen) for k in ins.values())


def data_class(key):
    """'measured' | 'published' | 'photo' | 'estimated' for one resolved key."""
    r = RES[key]
    if str(r.get("class")).startswith("B(user)"):
        return "measured"
    if r.get("class") in ("A", "C", "B"):
        return "published"
    if _photo_derived(key):
        return "photo"
    return "estimated"


def weakest(keys):
    return max((data_class(k) for k in keys), key=lambda c: STRENGTH[c])


def need(item, keys):
    miss = [k for k in keys if rec(k) is None]
    if miss:
        MISSING.append((item, f"unresolved: {', '.join(miss)}"))
        return False
    return True


# ------------------------------------------------------------------ scene helpers
def material(name, rgba):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.6
    if bsdf is not None and name != "MAT_REF_frame":  # class colours read clearly in renders
        for k in ("Emission Color", "Emission"):
            if k in bsdf.inputs:
                bsdf.inputs[k].default_value = rgba
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.8
    if name == "MAT_REF_frame" and bsdf is not None and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = 0.04  # frame planes nearly see-through so they do not hide the cage
    m.diffuse_color = rgba
    return m


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link(obj, coll_name, keys, note=""):
    collection(coll_name).objects.link(obj)
    mat = material("MAT_" + coll_name, COLORS[coll_name])
    if hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    obj["ref_collection"] = coll_name
    obj["ref_keys"] = ",".join(keys)
    obj["ref_note"] = note
    for k in keys:  # exact database values as double-precision custom properties
        v = val(k)
        if isinstance(v, (int, float)):
            obj["db:" + k] = float(v)
    OBJECTS[obj.name] = {"collection": coll_name, "keys": keys, "note": note,
                         "classes": {k: RES[k].get("class") for k in keys}}
    return obj


def mesh_obj(name, verts, edges=(), faces=()):
    me = bpy.data.meshes.new(name)
    me.from_pydata([coords.project_to_blender(v) for v in verts], list(edges), list(faces))
    me.update()
    return bpy.data.objects.new(name, me)


def wire(obj, thickness=LINE):
    m = obj.modifiers.new("wire", "WIREFRAME")
    m.thickness = thickness
    m.use_replace = True
    return obj


def box(name, x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return mesh_obj(name, v, faces=f)


def rect_plane(name, pts):
    return mesh_obj(name, pts, faces=[(0, 1, 2, 3)])


def sphere(name, p, r):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=r)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = coords.project_to_blender(p)
    return o


def polyline(name, pts, radius=LINE):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*coords.project_to_blender(p), 1.0)
    return bpy.data.objects.new(name, cu)


def tire_outline(name, center, diameter, width, segments=48):
    """Two sidewall circles plus 8 tread lines (axis along project X), as one bevelled curve object."""
    cx, cy, cz = center
    r = diameter / 2
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = LINE
    cu.bevel_resolution = 2
    for s in (-0.5, 0.5):
        sp = cu.splines.new("POLY")
        sp.points.add(segments - 1)
        for i in range(segments):
            a = 2 * math.pi * i / segments
            sp.points[i].co = (*coords.project_to_blender((cx + s * width, cy + r * math.cos(a), cz + r * math.sin(a))), 1.0)
        sp.use_cyclic_u = True
    for i in range(8):
        a = 2 * math.pi * i / 8
        sp = cu.splines.new("POLY")
        sp.points.add(1)
        for j, s in enumerate((-0.5, 0.5)):
            sp.points[j].co = (*coords.project_to_blender((cx + s * width, cy + r * math.cos(a), cz + r * math.sin(a))), 1.0)
    return bpy.data.objects.new(name, cu)


# ------------------------------------------------------------------ build
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = "METERS"
    for c in ("REF_frame", "REF_published", "REF_measured", "REF_photo", "REF_estimated"):
        collection(c)

    core = ["dimensions.length", "dimensions.width_body", "dimensions.height", "dimensions.wheelbase",
            "dimensions.track_front", "dimensions.track_rear"]
    if not need("core dimensions", core):
        raise SystemExit("core dimensions unresolved")
    L, W, H, WB, TF, TR = (val(k) for k in core)
    OHF = val("dimensions.overhang_front")

    # frame: ground and centreline planes (cosmetic extents around the published wheelbase/length)
    ymin, ymax = -WB - L / 2 - PLANE_MARGIN, L / 2 + PLANE_MARGIN
    g = rect_plane("REF_ground_plane", [(-W / 2 - 1, ymin, 0), (W / 2 + 1, ymin, 0), (W / 2 + 1, ymax, 0), (-W / 2 - 1, ymax, 0)])
    link(g, "REF_frame", [], "z = 0 (project origin height); extents cosmetic")
    c = rect_plane("REF_centerline_plane", [(0, ymin, 0), (0, ymax, 0), (0, ymax, H + PLANE_MARGIN), (0, ymin, H + PLANE_MARGIN)])
    link(c, "REF_frame", [], "x = 0 vehicle centreline plane; extents cosmetic")

    # body bounding box
    if OHF is not None:
        ext = coords.body_extents_project(L, W, H, OHF)
        b = wire(box("REF_body_box", *ext["x"], *ext["y"], *ext["z"]))
        keys = core[:3] + ["dimensions.overhang_front"]
        cls = weakest(keys)
        link(b, COLL[cls], keys, "length/width/height published; fore-aft position from dimensions.overhang_front "
             f"({data_class('dimensions.overhang_front')}: published total overhang x photo-measured front fraction), "
             "so the box's Y placement is photo-derived")
        OBJECTS["REF_body_box"]["extents_project"] = ext
    else:
        MISSING.append(("body box fore-aft position", "dimensions.overhang_front unresolved"))

    # published ground-contact (axle) lines: X from tracks, Y from wheelbase, Z = 0
    for name, y, tr in (("REF_contact_line_front", 0.0, TF), ("REF_contact_line_rear", -WB, TR)):
        o = polyline(name, [(-tr / 2, y, 0.0), (tr / 2, y, 0.0)])
        link(o, "REF_published", ["dimensions.wheelbase", "dimensions.track_front" if y == 0 else "dimensions.track_rear"],
             "axle position projected on the ground, between tire contact centres (track definition)")

    # wheel centre height: user measurement if given, else loaded tire radius
    zf_key = "proportions.wheel_center_z_front" if data_class_if("proportions.wheel_center_z_front") == "measured" else "tires.loaded_radius"
    zr_key = "proportions.wheel_center_z_rear" if data_class_if("proportions.wheel_center_z_rear") == "measured" else "tires.loaded_radius"
    if need("wheel centres", [zf_key, zr_key]):
        for axle, y, tr, zk in (("front", 0.0, TF, zf_key), ("rear", -WB, TR, zr_key)):
            z = val(zk)
            keys = ["dimensions.wheelbase", f"dimensions.track_{axle}", zk]
            o = polyline(f"REF_axle_line_{axle}", [(-tr / 2, y, z), (tr / 2, y, z)])
            link(o, COLL[weakest(keys)], keys, f"axle line at wheel-centre height from {zk}")
        for wname in coords.WHEELS:
            axle = coords.WHEELS[wname]["axle"]
            zk = zf_key if axle == "front" else zr_key
            p = coords.wheel_center_project(wname, WB, TF, TR, val(zk))
            o = sphere(f"REF_wheel_center_{wname}", p, MARK)
            keys = ["dimensions.wheelbase", f"dimensions.track_{axle}", zk]
            link(o, COLL[weakest(keys)], keys, f"X = ±track/2, Y = 0 or -wheelbase (published), Z from {zk}")
            OBJECTS[o.name]["center_project"] = list(p)
            # tire outline
            tk = ["tires.overall_diameter", "tires.section_width"]
            if need(f"tire outline {wname}", tk):
                t = tire_outline(f"REF_tire_{wname}", p, val(tk[0]), val(tk[1]))
                keys2 = keys + tk
                link(t, COLL[weakest(keys2)], keys2, "unloaded outline (overall diameter, section width) at the "
                     "loaded-radius centre: it dips below z = 0 by the static deflection")

    # width over mirrors: two planes at x = ±width_mirrors/2 spanning the wheelbase and height (all published)
    if need("width over mirrors", ["dimensions.width_mirrors"]):
        WM = val("dimensions.width_mirrors")
        for side, s in (("L", -1), ("R", 1)):
            x = s * WM / 2
            o = wire(rect_plane(f"REF_mirror_width_{side}", [(x, -WB, 0), (x, 0, 0), (x, 0, H), (x, -WB, H)]))
            link(o, "REF_published", ["dimensions.width_mirrors", "dimensions.wheelbase", "dimensions.height"],
                 "plane at x = ±width over open mirrors / 2; mirror Y and Z are unknown, the plane only shows the width")
    MISSING.append(("mirror position (Y, Z)", "proportions.mirror_y / proportions.mirror_z unknown"))

    # suspension hard points (left side as estimated; right side mirrored X -> -X)
    for k in sorted(RES):
        if not k.startswith("hardpoints."):
            continue
        r = rec(k)
        if r is None or not isinstance(r["value"], list) or len(r["value"]) != 3:
            MISSING.append((k, "unknown in database"))
            continue
        X, Y, Z = r["value"]
        for side, x in (("L", X), ("R", -X)):
            o = sphere(f"REF_hp_{k[len('hardpoints.'):].replace('.', '_')}_{side}", (x, Y, Z), HP_MARK)
            link(o, COLL[weakest([k])], [k], "left side from database" if side == "L" else "mirror of the left side (X -> -X)")

    guides(L, W, H, WB)

    # save manifest
    out = {"generator": "scripts/blender/build_reference_cage.py", "blender": bpy.app.version_string,
           "frames": {"project": coords.PROJECT_FRAME, "blender": coords.BLENDER_FRAME},
           "objects": OBJECTS, "missing": [{"item": i, "reason": r} for i, r in MISSING],
           "values": {k: RES[k]["value"] for o in OBJECTS.values() for k in o["keys"]}}
    return out


def data_class_if(key):
    return data_class(key) if key in RES and RES[key].get("value") is not None else None


def guides(L, W, H, WB):
    """Profile guides from the side-view photo measurements (proportions.*), drawn in the plane each
    point is assumed to lie on: centreline (x = 0) or body side (x = ±width/2)."""
    def add(name, pts, keys, plane):
        o = polyline(name, pts)
        link(o, COLL[weakest(keys)], keys, f"assumed plane: {plane}")

    def mark(name, p, keys, plane):
        o = sphere(name, p, MARK)
        link(o, COLL[weakest(keys)], keys, f"assumed plane: {plane}")

    wsb = ["proportions.windshield_base_y", "proportions.windshield_base_z"]
    hdr = ["proportions.windshield_header_y", "proportions.windshield_angle"]
    if need("windshield line", wsb + hdr):
        y0, z0 = val(wsb[0]), val(wsb[1])
        y1 = val(hdr[0])
        z1 = z0 + (y0 - y1) * math.tan(val(hdr[1]))  # straight glass at the measured angle up to the header Y
        add("REF_guide_windshield", [(0, y0, z0), (0, y1, z1)], wsb + hdr, "centreline (straight line at the measured angle)")
        mark("REF_guide_windshield_base", (0, y0, z0), wsb, "centreline")
        if need("roofline", ["proportions.roof_peak_y", "proportions.roof_peak_z"]):
            rk = ["proportions.roof_peak_y", "proportions.roof_peak_z"]
            add("REF_guide_roofline", [(0, y1, z1), (0, val(rk[0]), val(rk[1]))], wsb + hdr + rk,
                "centreline (windshield header to roof peak; the roof aft of the peak is not measured)")
            mark("REF_guide_roof_peak", (0, val(rk[0]), val(rk[1])), rk, "centreline")
    hk = ["proportions.hood_z_at_front_axle"]
    if need("hood line", hk + wsb):
        add("REF_guide_hood", [(0, 0.0, val(hk[0])), (0, val(wsb[0]), val(wsb[1]))], hk + wsb,
            "centreline (hood at the front axle to the windshield base)")
    MISSING.append(("hood leading edge", "not measured in Phase 1 (no proportions key)"))
    MISSING.append(("hatch line", "proportions.hatch_angle and hatch_glass_top_y exist but the hatch-top height was not measured, "
                                  "so the line cannot be placed"))
    MISSING.append(("beltline", "not measured in Phase 1 (no proportions key)"))
    for end, yk, zk in (("front", "dimensions.front_bumper_y", "proportions.front_bumper_extreme_z"),
                        ("rear", "dimensions.rear_bumper_y", "proportions.rear_bumper_extreme_z")):
        if need(f"{end} bumper extent", [yk, zk]):
            y = val(yk)
            add(f"REF_guide_{end}_bumper_extent", [(0, y, 0.0), (0, y, val("dimensions.height"))], [yk, "dimensions.height"],
                "centreline (vertical line through the extreme bumper Y)")
            mark(f"REF_guide_{end}_bumper_extreme_point", (0, y, val(zk)), [yk, zk], "centreline")
    for axle, y, zk in (("front", 0.0, "proportions.arch_top_z_front"), ("rear", -WB, "proportions.arch_top_z_rear")):
        if need(f"{axle} arch tops", [zk]):
            for side, s in (("L", -1), ("R", 1)):
                mark(f"REF_guide_arch_top_{axle}_{side}", (s * W / 2, y, val(zk)), [zk, "dimensions.width_body", "dimensions.wheelbase"],
                     "body side (x = ±width/2); arch top above the axle; arch shape not measured")
    MISSING.append(("wheel-arch curves", "only the arch-top heights were measured; arch radius/shape not measured"))
    if need("sill", ["proportions.sill_z_mid_wheelbase"]):
        for side, s in (("L", -1), ("R", 1)):
            mark(f"REF_guide_sill_mid_{side}", (s * W / 2, -WB / 2, val("proportions.sill_z_mid_wheelbase")),
                 ["proportions.sill_z_mid_wheelbase", "dimensions.width_body", "dimensions.wheelbase"], "body side")
    for axle, y, zk in (("front", 0.0, "proportions.wheel_center_z_front"), ("rear", -WB, "proportions.wheel_center_z_rear")):
        if need(f"photo wheel centre {axle}", [zk]) and data_class(zk) == "photo":
            mark(f"REF_photo_wheel_center_{axle}", (-val(f"dimensions.track_{axle}") / 2, y, val(zk)),
                 [zk, f"dimensions.track_{axle}", "dimensions.wheelbase"], "body side (left), photo wheel-centre height")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.join(ROOT, "blender", "reference_cage.blend")
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    man = build()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "blender", "_build"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    mp = os.path.join(ROOT, "blender", "_build", "cage_manifest.json")
    json.dump(man, open(mp, "w"), indent=1, default=float)
    print(f"CAGE saved {out}: {len(man['objects'])} objects, {len(man['missing'])} missing items; manifest {mp}")


main()
