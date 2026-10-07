# Coordinates

One mapping module, `scripts/blender/coords.py`, is used by every Phase 2 script (cage builder, cage check,
tests, photo comparison). Tests: `tests/test_coords.py` (`python3 -m pytest tests/`).

## Blender used

| | |
|---|---|
| Version | **Blender 5.2.2 LTS** (build date 2026-09-15), the newest LTS listed on blender.org/download/lts on 2026-10-07 (5.2 LTS and 4.5 LTS maintained) |
| Route | **Official Linux build** `blender-5.2.2-linux-x64.tar.xz` from `download.blender.org/release/Blender5.2/`; SHA-256 `84098912789dc450e95697c4184fb8a90acbe5111c2ba4aede3fecb57806a168`, matching Blender's published `blender-5.2.2.sha256`. The PyPI `bpy` fallback was not needed. |
| Install | `scripts/blender/install_blender.sh` (extracts to `/opt/blender/blender-5.2.2-linux-x64/`; bundled Python 3.13.13) |
| Mode | Headless (`blender -b`), Cycles on the CPU at low sample counts |

## Project frame (unchanged from Phase 1)

- Origin: on the ground, on the vehicle centreline, directly below the **front axle**.
- **+X** to the car's right, **+Y** forward, **+Z** up. Metres.
- The rear axle is at Y = −wheelbase = −2.735 m. Wheel names FL/FR/RL/RR use the car's own left and right: FL is at X = −track_front/2.

## Blender frame

- Metres, unit scale 1.0, Z up.
- The car faces **Blender −Y**, so Blender's Front view (looking along +Y) shows the nose.
- **blender (x, y, z) = project (−X, −Y, Z)**: a 180° rotation about Z (determinant +1, so nothing is mirrored).
- Consequences: the car's **left side is at Blender +x**; the front axle is at Blender y = 0 and the rear axle at y = +2.735; the nose is at Blender y = −(front overhang).

| Point | Project (X, Y, Z) | Blender (x, y, z) |
|---|---|---|
| FL wheel centre | (−track_f/2, 0, z_w) | (+track_f/2, 0, z_w) |
| FR wheel centre | (+track_f/2, 0, z_w) | (−track_f/2, 0, z_w) |
| RL wheel centre | (−track_r/2, −wheelbase, z_w) | (+track_r/2, +wheelbase, z_w) |
| RR wheel centre | (+track_r/2, −wheelbase, z_w) | (−track_r/2, +wheelbase, z_w) |
| Nose (body box front) | (0, +overhang_f, ·) | (0, −overhang_f, ·) |

Functions: `project_to_blender`, `blender_to_project`, `wheel_center_project`, `body_extents_project`.

## Assetto Corsa frame — only partly confirmed

Status of each point (sources in `docs/PLATFORM_CONSTRAINTS.md` §10). No official Kunos document was available: `user_supplied/ac_sdk/` was not supplied.

| Point | Status |
|---|---|
| AC car space is +Y up, +Z forward ("all dummies must have Z-axis pointing forward and Y-up") | community-reported |
| Ground at Y = 0 (wheels touching 0) | community-reported |
| A community Blender exporter maps kn5 (x, y, z) = blender (x, z, −y) | community-reported (code) |
| **Sign of AC +X (car's left or right)** | **unconfirmed** |
| **AC longitudinal origin** (front axle? CG? `GRAPHICS_OFFSET`?) | **unconfirmed** |

Provisional mapping: `x_ac = s·X, y_ac = Z, z_ac = Y − y0`, where `s = ±1` and `y0` are unknown. If the community exporter mapping holds, then with our Blender frame `x_ac = x_blender = −X`, i.e. `s = −1` (AC +X = the car's left). That is an inference, not a confirmed fact. `coords.project_to_ac()` raises an error unless `x_sign` and `y0` are passed explicitly, so nothing can silently use the unconfirmed mapping.

**Questions for you:**
1. In ksEditor or the Content Manager showroom, open any stock Kunos car and read the X coordinate of `WHEEL_LF`. Is it positive or negative?
2. Where is the AC model origin along the car: the front axle, the CG, or something set by `car.ini [BASIC] GRAPHICS_OFFSET`? The `sdk/dev/car_pipeline*.pdf` on your PC should say.
