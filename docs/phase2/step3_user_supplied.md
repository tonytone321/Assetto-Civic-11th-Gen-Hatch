# Step 3 — what was supplied

Checked 2026-10-07 on branch `claude/zen-gates-3y0ani` after `git fetch` (no other branch exists on the remote).

| Expected item | Present? |
|---|---|
| `user_supplied/measurements.txt` (fender-lip and wheel-centre heights, tire pressures, fuel level, rpm at 100 km/h in 6th, photo distance/height) | **missing** |
| `user_supplied/photos/side_left`, `side_right`, `front`, `rear` (+ optional `front_3q`, `rear_3q`) | **missing** |
| `user_supplied/photos/door_jamb` (GVWR, GAWRs, build date, tire size/pressures, paint code) | **missing** |
| `user_supplied/photos/tire_sidewall` (tire make/model) | **missing** |
| `user_supplied/ac_sdk/` (official AC pipeline documents) | **missing** |

The only file is `user_supplied/README.md`, which I wrote in Phase 1.

Consequences:

- Nothing was transcribed into `vehicle_data/user_measurements.json`; every entry is still an empty template row.
- The gear-speed cross-check still cannot run (no rpm-at-100 km/h figure).
- `docs/PLATFORM_CONSTRAINTS.md` is unchanged: axis conventions and node naming stay community-reported, and the side of `WHEEL_LF` stays unconfirmed.
- Step 7 falls back to third-party references from `references/manifest.json`, used for numbers only (images stay in the git-ignored cache). None is a straight-on long-lens photo of the target car with known camera distance and height, so camera positions must be fitted from the images alone. No straight-on front or rear view exists, so width, mirror position and anything seen only from the front or rear cannot be checked against a photo.
