# Data format and file ownership

This is the contract every research thread follows. The spec (`docs/SPEC.md`) wins on any conflict.

## Target vehicle

2024 Honda Civic Hatchback **Sport Touring**, 1.5 L turbo, **6-speed manual**, FWD, **Canadian market**, Sonic Grey Pearl.
Exclusions (unless evidence of a shared part is recorded): Civic Sedan, Si, Type R, lower hatchback trims, 2.0 L, CVT, 2025+ facelift, 10th generation, non-North-American markets. 2022–2023 hatchbacks with the same body/engine/gearbox count only when the record says so and a model-year-change check was made.

## Domain files

`vehicle_data/<topic>.json`:

```json
{
  "domain": "transmission",
  "title": "Transmission",
  "schema_version": 1,
  "updated": "2026-10-03",
  "sources": { "<source_id>": { "title", "url", "publisher", "class", "accessed", "access_method", "applicability", "notes", "cache_file" } },
  "parameters": {
    "transmission.gear_1": {
      "description": "1st gear ratio", "unit": "1", "impact": "high",
      "candidates": [ <record>, <record>, ... ]
    }
  }
}
```

Other top-level tables (lists of lamps, link catalogs, etc.) may be added next to `parameters`.

### Record (one candidate value)

| field | meaning |
|---|---|
| `value` | SI number, list, string or bool; `null` when unknown |
| `unit` | SI unit (`m`, `kg`, `W`, `N*m`, `rpm`, `m3`, `Pa`, `rad`, `s`, `N/m`, `1`, `text`, `bool`, …) |
| `printed` | `{"value", "unit"}` as printed in the source. When present, `value` **must** be `units.to_si(printed)` — build records with `dbutil.record(printed=(180, "hp"), …)` so conversion is done by code |
| `status` | `confirmed` \| `estimated` \| `unknown` |
| `class` | `A` manufacturer/government · `B` direct measurement · `C` reputable third party · `D` derived by script · `E` engineering estimate · `F` fallback assumption (`null` only for `unknown`) |
| `source_id` | key into `sources` (required for A–C) |
| `locator` | page number, section heading, table row, timestamp |
| `evidence` | **verbatim** text from the opened page/PDF stating the value (or where it sits in an image). Copy it from the cached text; never paraphrase. Several non-adjacent fragments are joined with ` … ` |
| `as_printed` | the figure exactly as printed, e.g. `"2,735 mm"` |
| `applicability` | what the **source** describes: `{year, market, trim, body, gearbox, engine, notes}` |
| `confidence` | `high` \| `medium` \| `low` \| `none` |
| `range` | `[lo, hi]` in SI — required for classes D, E, F and any `estimated` |
| `how_to_measure` | required for `estimated` and `unknown` |
| `notes` | anything else: model-year check, why this source applies, caveats |
| `searches` | for `unknown`: list of sources opened and queries tried |
| `prefer` + `selection_reason` | set on the candidate you select when credible same-class candidates disagree (the conflict is listed in `docs/CONFLICTS.md`) |

Build records with `scripts/dbutil.py` (`record`, `unknown`, `add_candidate`, `add_source`) and check a file with
`python3 scripts/dbutil.py check vehicle_data/<file>.json`.

### Precedence (resolver)

1. Verified user measurement (`vehicle_data/user_measurements.json`, class B, `source_id` starting `user:`)
2. Class A
3. Class B (other cars) and C
4. D, then E, then F

Within a class: exact applicability (2024 · CA · Sport Touring · 6MT) beats shared/other-year/US; then `prefer`; then confidence. Losing candidates are kept. Same-class disagreement beyond tolerance is a conflict and is listed in `docs/CONFLICTS.md`.

### Derived and estimated numbers

* Every computed number comes from code. Register it in `scripts/derivations/<domain>.py` (`DERIVATIONS`, `TABLES`; interface in `scripts/derivations/__init__.py`). `scripts/derive.py` evaluates them from resolved inputs into `vehicle_data/derived.json` and generated tables; `scripts/validate_db.py` recomputes them.
* Hand-entered class E/F records are allowed only for judgments that are not arithmetic (e.g. "shift time 0.25 s, range 0.20–0.35 s, basis: …"), always with a range, basis and `how_to_measure`.
* Photo measurements and dyno digitizing are scripts in `scripts/domains/`, with the image URL, pixel coordinates and error recorded in the output JSON.

### Coordinates and units

SI throughout. Vehicle frame: origin on the ground at the centerline below the **front axle**; +X right, +Y forward, +Z up, meters. The rear axle is at Y = −wheelbase.

## Evidence rules

* Open the page and find the value; a search snippet or recollection is only a lead.
* Use `scripts/fetch_page.py URL [--render] [--grep REGEX]` (it honors `robots.txt` and caches text under `cache/pages/`, git-ignored) or `scripts/pdf_text.py URL --grep REGEX` (prints page numbers). Put the printed cache path in the source's `cache_file` so quotes can be re-checked by script.
* The `WebFetch` tool paraphrases through a model: use it to find things, never as the text of `evidence`.
* Do not work around logins, paywalls, bot walls or 403 blocks. Record the block in the research log.
* Third-party photos/video/audio are cataloged by link; downloaded copies go only under `cache/` (git-ignored). Nothing from games or other mods.
* ~5 distinct searches plus the obvious primary sources without a value → record `unknown` with `searches` and `how_to_measure`, and move on.

## File ownership (one thread per row; write only your own files)

| # | Domain | Files |
|---|---|---|
| 1 | Identity | `vehicle_data/identity.json`, `docs/research_log/01_identity.md` |
| 2 | Dimensions | `vehicle_data/dimensions.json`, `vehicle_data/proportions.json`, `scripts/domains/photo_measure*.py`, `scripts/derivations/dimensions.py`, `docs/research_log/02_dimensions.md` |
| 3 | Mass & inertia | `vehicle_data/mass_inertia.json`, `scripts/derivations/mass_inertia.py`, `docs/research_log/03_mass_inertia.md` |
| 4 | Engine & turbo | `vehicle_data/engine.json`, `vehicle_data/turbo.json`, `engine_curves/*`, `scripts/domains/engine_*.py`, `scripts/derivations/engine.py` (builds `vehicle_data/engine_curve.csv`), `docs/research_log/04_engine.md` |
| 5 | Drivetrain | `vehicle_data/transmission.json`, `vehicle_data/drivetrain.json`, `scripts/derivations/drivetrain.py` (builds `vehicle_data/gear_speed_table.csv`), `docs/research_log/05_drivetrain.md` |
| 6 | Steering & suspension | `vehicle_data/steering.json`, `vehicle_data/suspension.json`, `vehicle_data/alignment.json`, `vehicle_data/hardpoints.json`, `scripts/domains/hardpoints*.py`, `scripts/derivations/suspension.py`, `scripts/derivations/steering.py`, `docs/research_log/06_steering_suspension.md` |
| 7 | Wheels, tires, brakes, aero | `vehicle_data/wheels.json`, `vehicle_data/tires.json`, `vehicle_data/brakes.json`, `vehicle_data/aero.json`, `scripts/derivations/wheels_tires.py`, `scripts/derivations/brakes_aero.py`, `docs/research_log/07_wheels_tires_brakes_aero.md` |
| 8 | Performance targets | `vehicle_data/validation_targets.json`, `docs/research_log/08_performance.md` |
| 9 | Visual references | `references/manifest.json`, `references/COVERAGE.md`, `vehicle_data/paint.json`, `vehicle_data/dashboard.json`, `scripts/domains/paint_*.py`, `docs/research_log/09_visual.md` |
| 10 | Audio | `audio/reference_database.json`, `audio/OBSERVATIONS.md`, `scripts/domains/audio_*.py`, `docs/research_log/10_audio.md` |
| 11 | Platform | `docs/PLATFORM_CONSTRAINTS.md`, `vehicle_data/platform.json`, `docs/research_log/11_platform.md` |
| — | Coordinator | `scripts/{resolve,derive,validate_db,make_report,dbutil,units,fetch_page,pdf_text}.py`, `vehicle_data/user_measurements.json`, `vehicle_data/_resolved.json`, `vehicle_data/derived.json`, all generated reports |

## Canonical keys used across domains

Derivations in other domains read these exact keys, so use them (add more as needed with the same prefix):

* `dimensions.length`, `dimensions.width_body`, `dimensions.width_mirrors`, `dimensions.height`, `dimensions.wheelbase`, `dimensions.track_front`, `dimensions.track_rear`, `dimensions.ground_clearance`, `dimensions.overhang_front`, `dimensions.overhang_rear`
* `mass.curb_mass`, `mass.gvwr`, `mass.gawr_front`, `mass.gawr_rear`, `mass.fuel_capacity` (m3), `mass.fuel_density` (kg/m3), `mass.front_fraction`
* `engine.displacement` (m3), `engine.bore`, `engine.stroke`, `engine.compression_ratio`, `engine.power_max` (W), `engine.power_max_rpm`, `engine.torque_max` (N*m), `engine.torque_max_rpm_low`, `engine.torque_max_rpm_high`, `engine.idle_rpm`, `engine.redline_rpm`, `engine.limiter_rpm`
* `transmission.gear_1` … `transmission.gear_6`, `transmission.gear_reverse`, `transmission.final_drive`
* `tires.size` (text), `tires.section_width`, `tires.aspect_ratio`, `tires.rim_diameter`, `tires.overall_diameter`, `tires.rolling_circumference`, `tires.loaded_radius`, `tires.mass`
* `wheels.diameter`, `wheels.width`, `wheels.offset`, `wheels.mass`
* `steering.ratio_overall`, `steering.turns_lock_to_lock`, `steering.turning_circle_diameter` (curb-to-curb unless stated), `steering.wheel_diameter`, `steering.max_angle_inner`, `steering.max_angle_outer`
* `brakes.front_rotor_diameter`, `brakes.rear_rotor_diameter`, …
* `aero.cd`, `aero.frontal_area`
* `perf.*` in `validation_targets.json`
