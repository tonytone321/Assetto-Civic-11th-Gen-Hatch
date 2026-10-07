#!/usr/bin/env python3
"""Regenerate the whole database from the domain builders, in dependency order, then run the
integration pipeline. Used to prove that the committed files are reproducible.

Usage:
  python3 scripts/rebuild_all.py            # run builders over the existing files
  python3 scripts/rebuild_all.py --clean    # delete every builder output first (strong test)
  python3 scripts/rebuild_all.py --no-reports

Inputs that are not in git: cache/ (pages, PDFs, photos, vPIC JSON) holds the opened sources the
builders quote from. Builders never fetch when a cached copy exists. user_measurements.json is never
deleted (it holds the user's own data).
"""
import argparse
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (script, outputs it creates or rewrites). Order matters: later builders read or extend earlier outputs.
BUILDERS = [
    ("scripts/domains/identity_build.py", ["vehicle_data/identity.json"]),
    ("scripts/domains/dimensions_build.py", ["vehicle_data/dimensions.json"]),
    ("scripts/domains/photo_measure_side.py", ["vehicle_data/proportions.json"]),
    ("scripts/domains/mass_build.py", ["vehicle_data/mass_inertia.json"]),
    ("scripts/domains/engine_db.py", ["vehicle_data/engine.json", "vehicle_data/turbo.json", "engine_curves/*.json"]),
    ("scripts/domains/transmission_build.py", ["vehicle_data/transmission.json", "vehicle_data/drivetrain.json"]),
    ("scripts/domains/drivetrain_build.py", []),  # extends drivetrain.json
    ("scripts/domains/steering_build.py", ["vehicle_data/steering.json"]),
    ("scripts/domains/suspension_build.py", ["vehicle_data/suspension.json", "vehicle_data/alignment.json"]),
    ("scripts/domains/wheels_tires_brakes_aero_build.py", ["vehicle_data/wheels.json", "vehicle_data/tires.json",
                                                           "vehicle_data/brakes.json", "vehicle_data/aero.json"]),
    ("scripts/resolve.py", []),  # hardpoints read resolved wheelbase, tracks and tire size
    ("scripts/domains/hardpoints_estimate.py", ["vehicle_data/hardpoints.json"]),
    ("scripts/domains/perf_targets.py", ["vehicle_data/validation_targets.json"]),
    ("scripts/domains/visual_build.py", ["references/manifest.json", "vehicle_data/paint.json",
                                         "vehicle_data/dashboard.json"]),
    ("scripts/domains/paint_analyze.py", []),  # extends paint.json
    ("scripts/domains/audio_build.py", ["audio/reference_database.json"]),
    ("scripts/domains/platform_build.py", ["vehicle_data/platform.json"]),
    ("scripts/domains/coordinator_additions.py", []),  # extends tires, engine, audio
    ("scripts/make_user_template.py", []),  # keeps user values
]
PIPELINE = ["scripts/resolve.py", "scripts/derive.py", "scripts/resolve.py"]
GENERATED = ["vehicle_data/_resolved.json", "vehicle_data/derived.json", "vehicle_data/gear_speed_table.csv",
             "vehicle_data/engine_curve.csv"]


def run(script, extra=()):
    t = time.time()
    p = subprocess.run([sys.executable, os.path.join(ROOT, script), *extra], cwd=ROOT,
                       capture_output=True, text=True)
    status = "ok" if p.returncode == 0 else f"FAILED (exit {p.returncode})"
    print(f"[{status}] {script} ({time.time()-t:.1f}s)")
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-4000:], sep="\n")
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--no-reports", action="store_true")
    a = ap.parse_args()
    if a.clean:
        for _, outs in BUILDERS:
            for pat in outs:
                for f in glob.glob(os.path.join(ROOT, pat)):
                    os.remove(f)
        for f in GENERATED:
            if os.path.exists(os.path.join(ROOT, f)):
                os.remove(os.path.join(ROOT, f))
        print("deleted builder outputs and generated files")
    failed = [s for s, _ in BUILDERS if run(s) != 0]
    if failed:
        print("builders failed:", failed)
        return 1
    for s in PIPELINE:
        if run(s) != 0:
            return 1
    rc = run("scripts/validate_db.py", ["--json", "cache/validate.json"])
    if not a.no_reports:
        run("scripts/make_report.py")
    return rc


if __name__ == "__main__":
    sys.exit(main())
