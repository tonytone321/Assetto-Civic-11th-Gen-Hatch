# Step 1 — Phase 1 reproducibility

Method: fresh `git clone` of `claude/zen-gates-3y0ani` into a temporary directory, the git-ignored
source cache (`cache/`, the opened pages the builders quote from) linked in, then
`python3 scripts/rebuild_all.py --clean` (deletes every builder output and generated file, runs all
17 builders in dependency order plus `make_user_template.py`, then resolve → derive → resolve →
validate → report), then `git status` / `scripts/diff_data.py`.

## First run (clone of 8d40407): builders all ran; output not identical

No builder failed and **no `value` field, range or selected record changed**. Differences, classified by
`scripts/diff_data.py`:

| Difference | Files | Cause | Version kept |
|---|---|---|---|
| `updated` / source `accessed` dates (2026-10-03 → run date) | 20 files | `dbutil.save()` and `add_source()` stamped today's date; `visual_build.py` passed `today()` | committed dates (2026-10-03, the day the pages were opened) |
| Duplicate `unknown` record for `engine.torque_curve_stock_6mt` | engine.json | `add_candidate()` appended a second unknown when `coordinator_additions.py` ran twice | rebuilt (single record) |
| Evidence quote for `drivetrain.differential_type`: `Other Name Differential Case` vs `Other Name : Differential Case` | drivetrain.json | committed JSON had been corrected after the builder last ran; the cached page reads `Other Name` / `:` / `Differential Case` | committed (matches the page) |
| `basis` text of hardpoint inputs (same numbers) | hardpoints.json | `hardpoints_estimate.py` read `_resolved.json` when present, else typed fallback numbers | committed (resolved values); typed fallbacks removed |

These are metadata and record-bookkeeping differences, not value differences, so per the Phase 2 rules
the builders were fixed rather than the data hand-edited.

## Fixes (commits 250ba02, bc2e040)

- `dbutil.save()`: `updated` is kept from disk when nothing else changed, otherwise the newest source
  `accessed` date, else an explicit `as_of`; never the run date for a file with dated sources.
- `dbutil.add_source()`: `accessed` defaults to the cached page's `FETCHED:` date (or file date).
- `dbutil.add_candidate()`: a new unknown replaces an older unknown; an unsourced D/E/F estimate
  replaces the builder's earlier record of the same class and locator (re-runs no longer stack copies,
  found when `paint_analyze.py` was re-run).
- `hardpoints_estimate.py`: reads wheelbase, tracks and tire size from `_resolved.json` only and stops if
  they are missing; `rebuild_all.py` runs `resolve.py` before it. Same numbers as before.
- `transmission_build.py`: quote corrected to the page text. `suspension_build.py`: `alignment.json`
  gets `as_of` (it has no dated sources). `visual_build.py`: no run-date access stamps.

## Final result (fresh clone of bc2e040)

- `rebuild_all.py --clean`: 24/24 steps ok, `git status` clean (empty diff).
- `rebuild_all.py` again without `--clean`: 24/24 ok, empty diff (builders are idempotent).
- `validate_db.py`: 0 errors, 1 warning (gear-speed cross-check not run: no observation yet);
  320/320 cached evidence quotes re-found.

Limit: the builders quote from `cache/`, which is git-ignored by design (third-party pages are not
redistributed). A clone on another machine without that cache cannot re-verify quotes; `photo_measure_side.py`
would re-download its image and `identity_vin_decode.py` would re-query vPIC.
