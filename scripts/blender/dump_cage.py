"""Dump world-space geometry of every REF_ object in the open .blend to JSON (Blender frame).

Run: blender -b blender/reference_cage.blend --python scripts/blender/dump_cage.py -- OUT.json
"""
import json
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]
data = {}
for ob in bpy.data.objects:
    if not ob.name.startswith("REF_"):
        continue
    mw = ob.matrix_world
    if ob.type == "MESH":
        pts = [list(mw @ v.co) for v in ob.data.vertices]
    elif ob.type == "CURVE":
        pts = [list(mw @ p.co.xyz) for s in ob.data.splines for p in s.points]
    else:
        pts = []
    data[ob.name] = {"type": ob.type, "location": list(mw.translation), "points": pts,
                     "collection": ob.users_collection[0].name if ob.users_collection else None}
json.dump(data, open(out, "w"))
print("DUMPED", len(data))
