"""Coordinate-mapping tests (Phase 2, Step 5).

Pure-Python tests check the mapping itself against the database values. The cage tests open
blender/reference_cage.blend in headless Blender (path from $BLENDER, else the Phase 2 install
location) and check that the four wheel centres and the body extents sit where the mapping says.
Run: python3 -m pytest tests/
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "blender"))
import coords  # noqa: E402

RES = json.load(open(os.path.join(ROOT, "vehicle_data", "_resolved.json"), encoding="utf-8"))["parameters"]
V = {k: RES[k]["value"] for k in ("dimensions.length", "dimensions.width_body", "dimensions.height",
                                  "dimensions.wheelbase", "dimensions.track_front", "dimensions.track_rear",
                                  "dimensions.overhang_front", "tires.loaded_radius")}
L, W, H, WB, TF, TR, OHF, RZ = (V[k] for k in V)
F32 = 2e-6  # Blender stores coordinates as float32


def close(a, b, tol=1e-12):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


# ---------------------------------------------------------------- mapping
def test_mapping_is_spec_rotation():
    assert coords.project_to_blender((1.0, 2.0, 3.0)) == (-1.0, -2.0, 3.0)


def test_mapping_round_trip():
    for p in [(0.3, -1.7, 0.9), (-0.768, 0.0, 0.3), (1e-3, -2.735, 1.415)]:
        assert close(coords.blender_to_project(coords.project_to_blender(p)), p)


def test_mapping_is_a_proper_rotation():
    ex, ey, ez = (coords.project_to_blender(e) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    det = (ex[0] * (ey[1] * ez[2] - ey[2] * ez[1]) - ex[1] * (ey[0] * ez[2] - ey[2] * ez[0])
           + ex[2] * (ey[0] * ez[1] - ey[1] * ez[0]))
    assert det == 1  # no mirroring: a left-hand part stays left-hand


def test_car_faces_blender_minus_y_and_left_is_plus_x():
    assert coords.project_to_blender((0, 1, 0))[1] == -1   # forward -> Blender -Y (Front view shows the nose)
    assert coords.project_to_blender((-1, 0, 0))[0] == 1   # car's left -> Blender +X
    assert coords.project_to_blender((0, 0, 1))[2] == 1    # up stays up


def test_wheel_centres_land_where_mapping_says():
    exp_blender = {"FL": (TF / 2, 0.0, RZ), "FR": (-TF / 2, 0.0, RZ), "RL": (TR / 2, WB, RZ), "RR": (-TR / 2, WB, RZ)}
    for w, eb in exp_blender.items():
        p = coords.wheel_center_project(w, WB, TF, TR, RZ)
        assert close(coords.project_to_blender(p), eb), w


def test_body_extents_land_where_mapping_says():
    e = coords.body_extents_project(L, W, H, OHF)
    front = coords.project_to_blender((0, e["y"][1], 0))
    rear = coords.project_to_blender((0, e["y"][0], 0))
    assert abs(front[1] - (-OHF)) < 1e-12 and abs(rear[1] - (L - OHF)) < 1e-12
    assert abs((e["y"][1] - e["y"][0]) - L) < 1e-12
    assert abs((e["x"][1] - e["x"][0]) - W) < 1e-12 and e["z"] == (0.0, H)


def test_ac_mapping_refuses_unconfirmed_axes():
    with pytest.raises(ValueError):
        coords.project_to_ac((0, 0, 0))


# ---------------------------------------------------------------- cage in the saved .blend
def blender_bin():
    for c in (os.environ.get("BLENDER"), shutil.which("blender"),
              "/opt/blender/blender-5.2.2-linux-x64/blender"):
        if c and os.path.exists(c):
            return c
    return None


@pytest.fixture(scope="module")
def cage(tmp_path_factory):
    b = blender_bin()
    blend = os.path.join(ROOT, "blender", "reference_cage.blend")
    if not b or not os.path.exists(blend):
        pytest.skip("Blender or blender/reference_cage.blend not available")
    out = str(tmp_path_factory.mktemp("cage") / "dump.json")
    subprocess.run([b, "-b", blend, "--python", os.path.join(ROOT, "scripts", "blender", "dump_cage.py"), "--", out],
                   check=True, capture_output=True)
    return json.load(open(out))


def test_cage_wheel_centres(cage):
    for w in coords.WHEELS:
        loc = cage[f"REF_wheel_center_{w}"]["location"]
        expect = coords.project_to_blender(coords.wheel_center_project(w, WB, TF, TR, RZ))
        assert close(loc, expect, F32), (w, loc, expect)


def test_cage_body_extents(cage):
    pts = cage["REF_body_box"]["points"]
    xs, ys, zs = zip(*pts)
    e = coords.body_extents_project(L, W, H, OHF)
    corners = [coords.project_to_blender((x, y, z)) for x in e["x"] for y in e["y"] for z in e["z"]]
    bx, by, bz = zip(*corners)
    for got, exp in ((xs, bx), (ys, by), (zs, bz)):
        assert abs(min(got) - min(exp)) <= F32 and abs(max(got) - max(exp)) <= F32
    # the nose is at Blender -Y, the left side at Blender +X
    assert abs(min(ys) - (-OHF)) <= F32 and abs(max(xs) - W / 2) <= F32
