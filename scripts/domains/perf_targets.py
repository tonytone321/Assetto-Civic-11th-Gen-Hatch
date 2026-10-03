#!/usr/bin/env python3
"""Domain 8 - performance targets.

Stage 1 builds the class C candidate records for vehicle_data/validation_targets.json
from cached, opened test pages (every evidence string is checked against the cached
page text before it is written). Stage 2 computes the "targets" table across tests:
per metric min, max, n and test ids. With n == 1 the target is that single test and
is flagged as such; nothing is widened silently.

Usage: python3 scripts/domains/perf_targets.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import dbutil as db  # noqa: E402
import units  # noqa: E402

ROOT = db.ROOT
SCRIPT = "scripts/domains/perf_targets.py"

CD_SID = "perf:cd-2022-civic-hatch-st-6mt"
CD_CACHE = "cache/pages/2df590f6625a05ee.txt"
CD_METHOD_SID = "perf:cd-how-we-test"
CD_METHOD_CACHE = "cache/pages/8c550355c08b8a10.txt"
CD_URL = "https://www.caranddriver.com/reviews/a37936938/2022-honda-civic-hatchback-by-the-numbers/"

CD_APP = db.app("2022", "US", "Sport Touring", "6MT",
                notes="Car and Driver test car: 2022 Civic Sport Touring Hatchback, 6-speed manual, "
                      "Sonic Gray paint, Continental ContiProContact 235/40R-18 91W M+S, "
                      "C/D-measured curb weight 3024 lb. Same body/engine/gearbox as the 2024 "
                      "target; model-year powertrain/chassis changes 2022->2024 to be confirmed by "
                      "the identity thread (none known to this thread).")

LOC = "Specifications box, 'C/D TEST RESULTS'"


def _norm(s):
    # page text splits inline markup onto separate lines ("Top Speed (\nC/D\n est)")
    return re.sub(r"\(\s+", "(", re.sub(r"\s+", " ", s)).strip()


def verify(cache_rel, evidence):
    with open(os.path.join(ROOT, cache_rel), encoding="utf-8") as f:
        txt = _norm(f.read())
    for frag in evidence.split(" … "):
        if _norm(frag) not in txt:
            raise SystemExit(f"evidence not found in {cache_rel}: {frag!r}")
    return evidence


def cd(printed, evidence, as_printed, locator=LOC, notes="", status="confirmed", conf="high", **kw):
    return db.record(printed=printed, status=status, cls="C", source_id=CD_SID, locator=locator,
                     evidence=verify(CD_CACHE, evidence), as_printed=as_printed,
                     applicability=CD_APP, confidence=conf, notes=notes, **kw)


ROLLOUT_NOTE = ("C/D standing-start times omit a 1-ft rollout; this test printed the rollout as "
                "0.4 s (see perf.cd_rollout_1ft). Add it back for a timer-from-standstill comparison.")


def build():
    d = db.load_or_new("validation_targets", "Performance validation targets")
    d["parameters"] = {}
    d["sources"] = {}
    db.add_source(d, CD_SID, "Tested: 2022 Honda Civic Hatchback Brings Stick-Shift Fun (Rich Ceppos, "
                  "published Oct 12, 2021)", CD_URL, "Car and Driver (Hearst Autos)", "C",
                  applicability="2022 Civic Sport Touring Hatchback, 6MT, US, Continental ContiProContact "
                                "235/40R-18 91W M+S, curb weight 3024 lb as tested",
                  notes="Instrumented test (VBOX). Same numbers repeated on caranddriver.com/honda/civic-2022 "
                        "(cache/pages/e2b19c8e54228dee.txt). Weather: corrected to 60 F at sea level per C/D "
                        "method; actual test-day weather not printed. Front/rear % not printed.",
                  cache_file=CD_CACHE)
    db.add_source(d, CD_METHOD_SID, "Car and Driver's Comprehensive Car Testing Explained",
                  "https://www.caranddriver.com/features/a32018270/how-we-test-cars/",
                  "Car and Driver (Hearst Autos)", "C",
                  applicability="Test methodology (current page, read 2026; rollout convention dates from 2019, "
                                "before the 2021 test)", cache_file=CD_METHOD_CACHE)

    add = lambda k, desc, unit, imp, rec: db.add_candidate(d, k, desc, unit, imp, rec)  # noqa: E731

    add("perf.accel_0_60mph", "0-60 mph, standing start (C/D convention: 1-ft rollout omitted)", "s", "high",
        cd((7.3, "s"), "60 mph: 7.3 sec", "7.3 sec", notes=ROLLOUT_NOTE))
    add("perf.cd_rollout_1ft", "1-ft rollout time omitted from C/D standing-start results", "s", "medium",
        cd((0.4, "s"), "Results above omit 1-ft rollout of 0.4 sec.", "0.4 sec"))
    add("perf.accel_0_100mph", "0-100 mph (rollout omitted)", "s", "medium",
        cd((19.0, "s"), "100 mph: 19.0 sec", "19.0 sec", notes=ROLLOUT_NOTE))
    add("perf.accel_0_120mph", "0-120 mph (rollout omitted)", "s", "low",
        cd((30.9, "s"), "120 mph: 30.9 sec", "30.9 sec", notes=ROLLOUT_NOTE))
    add("perf.quarter_mile_time", "Standing quarter mile, elapsed time (rollout omitted)", "s", "high",
        cd((15.5, "s"), "1/4-Mile: 15.5 sec @ 91 mph", "15.5 sec", notes=ROLLOUT_NOTE))
    add("perf.quarter_mile_trap", "Standing quarter mile, trap speed", "m/s", "high",
        cd((91, "mph"), "1/4-Mile: 15.5 sec @ 91 mph", "91 mph"))
    add("perf.accel_5_60mph", "Rolling start 5-60 mph", "s", "high",
        cd((8.3, "s"), "Rolling Start, 5–60 mph: 8.3 sec", "8.3 sec",
           notes="Rolling start: creep at 5 mph then full throttle (C/D method). Larger 5-60 vs 0-60 gap "
                 "indicates lag; here 5-60 is 1.0 s slower than the rollout-omitted 0-60."))
    add("perf.pass_30_50mph_top", "30-50 mph in top gear (6th), no downshift", "s", "high",
        cd((12.1, "s"), "Top Gear, 30–50 mph: 12.1 sec", "12.1 sec",
           notes="Manual car: top gear = 6th, throttle only, no downshift (C/D method). Very sensitive to "
                 "6th-gear ratio and low-rpm boost: 30 mph in 6th is roughly 1000-1300 rpm."))
    add("perf.pass_50_70mph_top", "50-70 mph in top gear (6th), no downshift", "s", "high",
        cd((9.4, "s"), "Top Gear, 50–70 mph: 9.4 sec", "9.4 sec", notes="Manual car, 6th gear, no downshift."))
    add("perf.top_speed", "Top speed", "m/s", "medium",
        cd((130, "mph"), "Top Speed (C/D est): 130 mph", "130 mph", status="estimated", conf="low",
           range=[units.to_si(130, "mph")[0], units.to_si(130, "mph")[0]],
           how_to_measure="Not measured by C/D (their estimate). Governed or drag-limited is not stated "
                          "for this car; C/D's 2022 Civic Touring sedan CVT was 'gov ltd' at 126 mph "
                          "(different car, not used). Measure only on a closed course or read Honda's "
                          "speed-limiter spec if one is ever published.",
           notes="Car and Driver estimate, not a measurement; whether a governor applies to the 6MT "
                 "hatch is unknown. Range is the single printed estimate (n=1), not a tolerance."))
    add("perf.braking_70_0mph", "Braking 70-0 mph", "m", "high",
        cd((173, "ft"), "Braking, 70–0 mph: 173 ft", "173 ft",
           notes="C/D reports the second-best of six stops, corrected to exactly 70.0 mph (method page)."))
    add("perf.skidpad_g", "Steady-state lateral grip on skidpad (C/D: usually 300-ft circle)", "m/s2", "high",
        cd((0.90, "g0"), "We recorded an impressive 0.90 g of cornering grip on our skidpad, which would "
                         "easily have been higher had the stability control not intervened.", "0.90 g",
           locator="Article body, paragraph beginning 'Stick shift or no'", conf="medium",
           notes="Diameter not printed in this article; C/D method page: 'we usually use a "
                 "300-foot-diameter circle'. Stability control intervened, so this is an ESC-limited "
                 "lower bound of tire/chassis grip. Not in the spec box."))
    add("perf.test_weight", "Test weight as measured by the tester (lead for mass thread)", "kg", "high",
        cd((3024, "lb"), "Curb Weight: 3024 lb", "3024 lb", locator="Specifications box, DIMENSIONS",
           notes="C/D weighs each test car on Intercomp scales after topping off fuel (method page: "
                 "'First, the vehicle is carefully topped off with fuel and weighed'). So: full tank, no "
                 "driver. Front/rear distribution not printed."))

    searches_common = [
        "caranddriver.com honda/civic-2022, -2023, -2024 pages (only the 2022 ST 6MT hatch test exists)",
        "MotorTrend 2022 Civic Sport Touring Hatchback First Test (opened; car was a CVT - excluded)",
        "Edmunds hatchback review 2022/2023/2024 (HTTP 403, not worked around)",
        "MotorWeek 2022 Civic Hatchback first impressions (opened; no figures)",
        "WebSearch: 'Civic Hatchback Sport Touring manual 0-100 km/h mesuré essai guideautoweb / Motor Illustrated / edmunds'",
        "WebSearch: 'MotorTrend 2022 Civic Hatchback Sport Touring manual first test'",
        "autos.yahoo.com C/D syndication (robots.txt disallows ClaudeBot; not fetched)",
        "Consumer Reports road test (paywalled; not bypassed)",
    ]
    for k, desc, unit, imp, htm in [
        ("perf.accel_0_100kmh", "0-100 km/h (instrumented)", "s", "high",
         "GPS logger (VBOX/Dragy-class, >=10 Hz) on level dry ground, two directions, record "
         "temperature/pressure; report with and without 1-ft rollout."),
        ("perf.honda_claim_0_100kmh", "Honda (manufacturer) 0-100 km/h claim", "s", "low",
         "No Honda Canada/US claim found; Honda NA typically publishes none."),
        ("perf.braking_100_0kmh", "Braking 100-0 km/h", "m", "medium",
         "GPS logger, tape switch on brake pedal, several stops, correct to exact 100.0 km/h."),
        ("perf.braking_60_0mph", "Braking 60-0 mph (6MT hatch)", "m", "medium",
         "As above from 60 mph. (MotorTrend's 117 ft is a CVT car - excluded.)"),
        ("perf.accel_0_30mph", "0-30 mph", "s", "low",
         "GPS logger; C/D did not print 0-30 in this test."),
    ]:
        add(k, desc, unit, imp, db.unknown(unit, searches_common, htm,
                                           notes="No instrumented 6MT Sport Touring hatch figure found."))

    d["tests"] = [{
        "id": "cd-2021-10", "source_id": CD_SID, "publication": "Car and Driver",
        "title": "Tested: 2022 Honda Civic Hatchback Brings Stick-Shift Fun", "url": CD_URL,
        "date": "2021-10-12", "author": "Rich Ceppos",
        "car": "2022 Honda Civic Sport Touring Hatchback, 6-speed manual, US, Sonic Gray (option $395)",
        "tires": "Continental ContiProContact 235/40R-18 91W M+S",
        "test_weight_lb_as_printed": "3024 lb (curb, full fuel, C/D scales)",
        "front_rear_pct": None,
        "weather_correction": "corrected to 60 F at sea level (C/D method page); test-day weather not printed",
        "rollout": "1-ft rollout omitted from standing-start times; printed as 0.4 s",
        "surface": "not stated", "applicability_rank": "primary (trim, body, engine, gearbox match; 2022 MY, US)",
    }]
    d["excluded_tests"] = [{
        "publication": "MotorTrend",
        "url": "https://www.motortrend.com/reviews/2022-honda-civic-sport-touring-hatchback-first-test-review",
        "date": "2021-11-24", "cache_file": "cache/pages/f7e5fe67a115d807.txt",
        "reason": "Test car was a CVT ('This hatchback was an automatic model'); spec excludes CVT results. "
                  "Figures (0-60 7.7 s, 1/4 15.9 s @ 89.8 mph, 60-0 117 ft, figure-eight 26.8 s @ 0.65 g) "
                  "kept here only as context, not as targets.",
    }]
    return d


# ------------------------------------------------------------- stage 2: targets

def targets(d):
    tests = {t["source_id"]: t["id"] for t in d.get("tests", [])}
    out = {}
    for k, p in d["parameters"].items():
        vals = [(c["value"], tests.get(c["source_id"], c["source_id"]), c["status"])
                for c in p["candidates"]
                if c["status"] != "unknown" and c["class"] == "C" and isinstance(c["value"], (int, float))]
        if not vals:
            out[k] = {"unit": p["unit"], "n": 0, "min": None, "max": None, "tests": [],
                      "note": "no instrumented 6MT Sport Touring hatch result found"}
            continue
        v = [x[0] for x in vals]
        out[k] = {"unit": p["unit"], "n": len(v), "min": min(v), "max": max(v),
                  "tests": [x[1] for x in vals],
                  "note": ("n=1: single test; this is not a cross-test range and has not been widened"
                           if len(v) == 1 else "range across tests")
                  + ("; includes a tester estimate, not a measurement"
                     if any(x[2] == "estimated" for x in vals) else "")}
    # rollout-inclusive standing-start times (timer from first motion), computed, not typed
    roll = out.get("perf.cd_rollout_1ft")
    if roll and roll["n"]:
        for k in ("perf.accel_0_60mph", "perf.accel_0_100mph", "perf.quarter_mile_time"):
            t = out.get(k)
            if t and t["n"] and t["tests"] == roll["tests"]:
                out[k + "_incl_rollout"] = {
                    "unit": "s", "n": t["n"], "min": t["min"] + roll["min"], "max": t["max"] + roll["max"],
                    "tests": t["tests"], "derivation": f"{k} + perf.cd_rollout_1ft (same test)",
                    "note": "C/D time with its printed 1-ft rollout added back: compare with an in-game timer "
                            "started at first wheel motion"}
    return out


def main():
    d = build()
    d["targets"] = targets(d)
    d["targets_script"] = SCRIPT
    d["targets_policy"] = ("Per metric: min/max/n across instrumented tests of 2022-2024 Civic Hatchback "
                           "Sport Touring 6MT; CVT, sedan, Si, Type R and 2.0 L results excluded. n=1 is "
                           "flagged, never widened by hand.")
    p = db.save(d)
    errs = db.check_domain(d)
    print(p, "OK" if not errs else errs)
    for k, t in d["targets"].items():
        print(f"{k:38s} n={t['n']} min={t['min']} max={t['max']} {t['unit']}")


if __name__ == "__main__":
    main()
