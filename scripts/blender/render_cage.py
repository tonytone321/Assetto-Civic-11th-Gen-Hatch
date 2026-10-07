"""Render the reference cage alone: orthographic front, rear, left, right and top, plus front and rear
three-quarter perspective views. Cycles on the CPU at a low sample count.

Run: blender -b blender/reference_cage.blend --python scripts/blender/render_cage.py -- OUT_DIR [SAMPLES]
Framing is computed from the cage's own bounding box; nothing is typed.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 16
os.makedirs(OUT, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"  # white background stays white
world = bpy.data.worlds.new("W") if sc.world is None else sc.world
sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (1, 1, 1, 1)
bg.inputs["Strength"].default_value = 1.0
sun = bpy.data.objects.new("RENDER_sun", bpy.data.lights.new("RENDER_sun", "SUN"))
sun.data.energy = 1.0
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
sc.collection.objects.link(sun)

pts = []
for ob in bpy.data.objects:
    if ob.name.startswith("REF_") and ob.name not in ("REF_ground_plane", "REF_centerline_plane"):
        pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
size = hi - lo
aspect = sc.render.resolution_x / sc.render.resolution_y

cam = bpy.data.objects.new("RENDER_cam", bpy.data.cameras.new("RENDER_cam"))
sc.collection.objects.link(cam)
sc.camera = cam


def look(frm, to):
    d = (to - frm).normalized()
    cam.location = frm
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


dist = 4 * max(size)
# Blender frame: car faces -Y, its left side is +X (docs/COORDINATES.md)
views = {
    "front": (Vector((0, -1, 0)), (size.x, size.z)),
    "rear": (Vector((0, 1, 0)), (size.x, size.z)),
    "left": (Vector((1, 0, 0)), (size.y, size.z)),
    "right": (Vector((-1, 0, 0)), (size.y, size.z)),
    "top": (Vector((0, 0, 1)), (size.y, size.x)),
}
for name, (d, (w, h)) in views.items():
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.12 * max(w, h * aspect)
    look(ctr + d * dist, ctr)
    if name == "top":
        cam.rotation_euler = (0, 0, math.radians(90))  # nose to the left
    sc.render.filepath = os.path.join(OUT, f"cage_ortho_{name}.png")
    bpy.ops.render.render(write_still=True)
for name, d in (("front_3q", Vector((0.8, -1.0, 0.45))), ("rear_3q", Vector((-0.8, 1.0, 0.45)))):
    cam.data.type = "PERSP"
    cam.data.lens = 50
    look(ctr + d.normalized() * 2.2 * max(size), ctr)
    sc.render.filepath = os.path.join(OUT, f"cage_persp_{name}.png")
    bpy.ops.render.render(write_still=True)
print("RENDERS", sorted(os.listdir(OUT)))
