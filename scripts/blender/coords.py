"""Coordinate mapping used by every Phase 2 script (see docs/COORDINATES.md).

Project frame (unchanged from Phase 1): origin on the ground at the vehicle centreline directly
below the front axle; +X to the car's right, +Y forward, +Z up; metres.

Blender frame: metres, unit scale 1.0, Z up, car facing Blender -Y so that Blender's Front view
(looking along +Y) shows the front of the car:
    blender (x, y, z) = project (-X, -Y, Z)
The mapping is a 180-degree rotation about Z (determinant +1, handedness preserved).

Assetto Corsa frame: only partly documented. Community sources (not the official SDK documents,
which were not supplied) say AC car space is +Y up and +Z forward with the ground at Y = 0. The sign
of AC +X (car's left or right) and the AC longitudinal origin are UNCONFIRMED, so `project_to_ac`
refuses to run unless both are passed explicitly.

This module is plain Python (no bpy) so tests and the photo-comparison code can import it.
"""

PROJECT_FRAME = "origin ground/centreline/below front axle; +X right, +Y forward, +Z up; m"
BLENDER_FRAME = "Z up, car faces -Y; blender (x, y, z) = project (-X, -Y, Z); m, scale 1.0"


def project_to_blender(p):
    """Project (X, Y, Z) -> Blender (x, y, z). Accepts any 3-sequence; returns a tuple."""
    X, Y, Z = p
    return (-X, -Y, Z)


def blender_to_project(b):
    """Blender (x, y, z) -> project (X, Y, Z). Exact inverse of project_to_blender."""
    x, y, z = b
    return (-x, -y, z)


def project_dir_to_blender(v):
    """Directions transform the same way as points (the map is linear: no translation)."""
    return project_to_blender(v)


def project_to_ac(p, x_sign=None, y0=None):
    """Project (X, Y, Z) -> AC car space (x_ac, y_ac, z_ac) = (x_sign * X, Z, Y - y0).

    Community-reported only: AC +Y up, +Z forward, ground at Y = 0.
    x_sign: +1 if AC +X is the car's right, -1 if it is the car's left. UNCONFIRMED: pass it only
            after checking WHEEL_LF's X in ksEditor / the CM showroom (see docs/COORDINATES.md).
    y0:     project Y of the AC model origin along the car. UNCONFIRMED.
    """
    if x_sign not in (1, -1) or y0 is None:
        raise ValueError("AC mapping is unconfirmed: pass x_sign (+1/-1) and y0 explicitly once verified "
                         "(see docs/COORDINATES.md, open questions)")
    X, Y, Z = p
    return (x_sign * X, Z, Y - y0)


# Wheel naming in the project frame (car's own left/right, independent of any software).
WHEELS = {
    "FL": {"side": -1, "axle": "front"},  # car's left  = project -X = Blender +x
    "FR": {"side": +1, "axle": "front"},  # car's right = project +X = Blender -x
    "RL": {"side": -1, "axle": "rear"},
    "RR": {"side": +1, "axle": "rear"},
}


def wheel_center_project(wheel, wheelbase, track_front, track_rear, z):
    """Project-frame wheel centre for 'FL', 'FR', 'RL' or 'RR' at height z."""
    w = WHEELS[wheel]
    track = track_front if w["axle"] == "front" else track_rear
    y = 0.0 if w["axle"] == "front" else -wheelbase
    return (w["side"] * track / 2.0, y, z)


def body_extents_project(length, width, height, overhang_front):
    """Project-frame axis-aligned body box: front face at Y = +overhang_front, rear face at
    Y = overhang_front - length, sides at X = +/- width/2, from Z = 0 to Z = height."""
    return {"x": (-width / 2.0, width / 2.0), "y": (overhang_front - length, overhang_front), "z": (0.0, height)}
