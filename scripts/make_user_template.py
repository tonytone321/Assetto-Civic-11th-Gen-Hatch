#!/usr/bin/env python3
"""Write vehicle_data/user_measurements.json: a fill-in template whose entries use the same
parameter keys as the research files. The resolver gives any entry with a non-null value top
precedence, so nothing else needs editing. Re-running keeps values already filled in."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dbutil as db  # noqa: E402

OUT = os.path.join(db.DATA, "user_measurements.json")
STATIC = [
    # key, description, SI unit, how to measure (precision)
    ("mass.curb_mass", "Curb mass, full tank, no driver", "kg", "Four-pad corner scales or certified axle scale; full tank; ±2 kg."),
    ("mass.corner_fl", "Corner weight front left", "kg", "Corner scales on level pads, full tank, no driver; ±1 kg."),
    ("mass.corner_fr", "Corner weight front right", "kg", "As above."),
    ("mass.corner_rl", "Corner weight rear left", "kg", "As above."),
    ("mass.corner_rr", "Corner weight rear right", "kg", "As above."),
    ("mass.front_fraction", "Front axle fraction of curb mass", "1", "(FL+FR)/total from corner weights."),
    ("mass.gvwr", "GVWR from door-jamb label", "kg", "Photograph the B-pillar certification label (kg and lb printed)."),
    ("mass.gawr_front", "Front GAWR from door-jamb label", "kg", "Same label."),
    ("mass.gawr_rear", "Rear GAWR from door-jamb label", "kg", "Same label."),
    ("mass.cg_height", "CG height", "m", "Axle-lift method: weigh rear axle level and with front raised ≥250 mm (wheels locked, suspension blocked); ±15 mm."),
    ("dimensions.length", "Overall length", "m", "Plumb bob to floor at bumper extremes, tape between marks; ±3 mm."),
    ("dimensions.width_body", "Body width without mirrors", "m", "Plumb bobs at widest body points; ±3 mm."),
    ("dimensions.width_mirrors", "Width across open mirrors", "m", "Plumb bobs at mirror tips; ±3 mm."),
    ("dimensions.height", "Overall height (unladen)", "m", "Straight edge on roof, tape to floor; ±3 mm."),
    ("dimensions.wheelbase", "Wheelbase (left and right average)", "m", "Plumb from hub centres, both sides; ±2 mm."),
    ("dimensions.track_front", "Front track", "m", "Tire centreline to centreline at contact patch; ±3 mm."),
    ("dimensions.track_rear", "Rear track", "m", "As above."),
    ("dimensions.ground_clearance", "Minimum ground clearance", "m", "Lowest point under car to floor; ±2 mm."),
    ("dimensions.overhang_front", "Front overhang (axle to bumper)", "m", "Plumb marks; ±3 mm."),
    ("dimensions.overhang_rear", "Rear overhang (axle to bumper)", "m", "Plumb marks; ±3 mm."),
    ("proportions.arch_top_z_front", "Fender arch top height above ground, front", "m", "Floor to arch lip directly above hub, full tank; ±2 mm."),
    ("proportions.arch_top_z_rear", "Fender arch top height above ground, rear", "m", "As above."),
    ("proportions.wheel_center_z_front", "Front hub centre height", "m", "Floor to hub centre; ±2 mm."),
    ("proportions.wheel_center_z_rear", "Rear hub centre height", "m", "As above."),
    ("proportions.sill_z_mid_wheelbase", "Sill height at mid-wheelbase", "m", "Floor to sill underside; ±2 mm."),
    ("proportions.windshield_base_y", "Windshield base Y (from front axle, +forward)", "m", "Plumb from cowl glass edge at centreline; ±5 mm."),
    ("proportions.windshield_base_z", "Windshield base height", "m", "Floor to cowl glass edge; ±5 mm."),
    ("proportions.roof_peak_z", "Roof peak height", "m", "Straight edge; ±3 mm."),
    ("proportions.mirror_y", "Mirror glass centre Y", "m", "Plumb to floor, measure to front-axle line; ±5 mm."),
    ("proportions.mirror_z", "Mirror glass centre height", "m", "Floor to mirror centre; ±5 mm."),
    ("steering.wheel_diameter", "Steering wheel outer diameter", "m", "Caliper or tape across rim; ±2 mm."),
    ("steering.max_angle_inner", "Max road-wheel angle, inner wheel", "rad", "Turn plates at full lock; ±0.5 deg (enter radians)."),
    ("steering.max_angle_outer", "Max road-wheel angle, outer wheel", "rad", "As above."),
    ("suspension.spring_free_length_front", "Front spring free length", "m", "Removed spring, caliper; ±1 mm."),
    ("suspension.spring_free_length_rear", "Rear spring free length", "m", "As above."),
    ("suspension.spring_wire_diameter_front", "Front spring wire diameter", "m", "Caliper; ±0.05 mm."),
    ("suspension.spring_wire_diameter_rear", "Rear spring wire diameter", "m", "Caliper; ±0.05 mm."),
    ("suspension.spring_active_coils_front", "Front spring active coils", "count", "Count coils minus closed ends; ±0.25."),
    ("suspension.spring_active_coils_rear", "Rear spring active coils", "count", "As above."),
    ("suspension.spring_mean_coil_diameter_front", "Front spring mean coil diameter", "m", "OD minus wire diameter; ±0.5 mm."),
    ("suspension.spring_mean_coil_diameter_rear", "Rear spring mean coil diameter", "m", "As above."),
    ("suspension.spring_rate_front", "Front spring rate (bench)", "N/m", "Spring tester or loaded-length at two loads; ±3 %."),
    ("suspension.spring_rate_rear", "Rear spring rate (bench)", "N/m", "As above."),
    ("suspension.arb_front_diameter", "Front anti-roll bar OD", "m", "Caliper at straight section; ±0.1 mm."),
    ("suspension.arb_rear_diameter", "Rear anti-roll bar OD", "m", "Caliper; ±0.1 mm."),
    ("suspension.arb_front_lever_arm", "Front bar lever arm (bushing axis to link eye)", "m", "Tape/caliper; ±2 mm."),
    ("suspension.arb_rear_lever_arm", "Rear bar lever arm", "m", "As above."),
    ("suspension.arb_front_active_length", "Front bar length between bushings", "m", "Tape; ±2 mm."),
    ("suspension.arb_rear_active_length", "Rear bar length between bushings", "m", "Tape; ±2 mm."),
    ("suspension.travel_bump_front", "Front bump travel from ride height to bump-stop contact", "m", "Spring removed or jack under knuckle; ±2 mm."),
    ("suspension.travel_bump_rear", "Rear bump travel", "m", "As above."),
    ("suspension.travel_rebound_front", "Front rebound travel (droop)", "m", "Lift body until wheel hangs; ±2 mm."),
    ("suspension.travel_rebound_rear", "Rear rebound travel", "m", "As above."),
    ("wheels.mass", "Bare wheel mass (Sport Touring 18x8)", "kg", "Bathroom/hanging scale, tire removed; ±0.1 kg."),
    ("wheels.offset", "Wheel offset (stamped on wheel)", "m", "Read stamp 'ET'; exact."),
    ("wheels.center_bore", "Wheel centre bore", "m", "Caliper; ±0.1 mm."),
    ("tires.mass", "Tire mass", "kg", "Scale, tire off wheel; ±0.1 kg (or wheel+tire minus wheel)."),
    ("tires.make_model", "Original tire brand/model/OE marking", "text", "Read sidewall; include DOT date code."),
    ("tires.rolling_circumference", "Rolling circumference at rated pressure, loaded", "m", "Mark tire, roll 10 turns in a straight line, measure; ±5 mm per turn."),
    ("tires.loaded_radius", "Loaded radius (hub centre to ground)", "m", "Floor to hub centre at curb weight and placard pressure; ±1 mm."),
    ("brakes.front_caliper_piston_diameter", "Front caliper piston diameter", "m", "Caliper on piston face with pads out; ±0.1 mm."),
    ("brakes.rear_caliper_piston_diameter", "Rear caliper piston diameter", "m", "As above."),
    ("engine.idle_rpm", "Warm idle rpm", "rpm", "OBD-II logger, warm engine, accessories off; ±10 rpm."),
    ("engine.limiter_rpm", "Fuel-cut / limiter rpm (neutral and in gear)", "rpm", "OBD-II logger at 20+ Hz while touching the limiter briefly; ±25 rpm."),
    ("drivetrain.obs_rpm_at_100kmh_6th", "Engine rpm at GPS 100 km/h in 6th", "rpm", "Level road, steady speed, GPS speed, OBD rpm; ±10 rpm."),
    ("drivetrain.obs_rpm_at_70mph_6th", "Engine rpm at GPS 70 mph (112.7 km/h) in 6th", "rpm", "As above."),
]


def entry(desc, unit, how):
    rec = db.record(value=None, unit=unit, status="unknown", cls="B", source_id="user:measurement",
                    locator="", evidence="", as_printed="", applicability=db.app("2024", "CA", "Sport Touring", "6MT",
                                                                               notes="the user's own car"),
                    confidence="none", how_to_measure=how,
                    notes="FILL IN: set value (SI unit shown), status 'confirmed', locator (date/place), evidence "
                          "(what you did and the raw reading), as_printed (raw reading with its unit), confidence.")
    return {"description": desc, "unit": unit, "impact": "high", "candidates": [rec]}


def main():
    old = db.load(OUT) if os.path.exists(OUT) else {"parameters": {}}
    d = {"domain": "user_measurements", "title": "User measurements of the real car (top precedence)",
         "schema_version": 1, "sources": {},
         "_instructions": [
             "Fill only what you measured. A candidate whose value is not null wins over every other record for that key.",
             "Units are SI (m, kg, N/m, rad, rpm). Put the raw reading in as_printed, e.g. '1,384 kg' or '26.5 mm'.",
             "Hard points: value = [x, y, z] in metres in the vehicle frame (origin on the ground at the centreline "
             "below the front axle; +X right, +Y forward, +Z up). Left side (x < 0) unless stated.",
             "Files (dyno sheets, datalogs, recordings, photos): put them in user_supplied/ and list them under 'attachments'.",
             "After editing run: python3 scripts/resolve.py && python3 scripts/derive.py && python3 scripts/resolve.py && "
             "python3 scripts/validate_db.py && python3 scripts/make_report.py"],
         "parameters": {},
         "attachments": old.get("attachments") or [
             {"kind": "dyno", "path": "user_supplied/", "notes": "stock dyno sheet: dyno make/type, correction (SAE/STD), gear, fuel, ambient", "provided": False},
             {"kind": "datalog", "path": "user_supplied/", "notes": "OBD/FlashPro/KTuner stock log: rpm, MAP/boost, throttle, ign. timing, fuel trims, gear, speed; WOT pulls in 3rd and 4th plus throttle lifts", "provided": False},
             {"kind": "recording", "path": "user_supplied/", "notes": "exhaust audio (WAV, ≥48 kHz, no clipping), mic position stated; idle, rev sweeps, WOT pulls, lift-offs at 3000/4500/6000 rpm, upshifts; synced OBD log if possible", "provided": False},
             {"kind": "photos", "path": "user_supplied/", "notes": "straight-on long-lens side/front/rear at axle height; door-jamb label; tire sidewall; cluster in each display mode", "provided": False}]}
    keys = list(STATIC)
    hp = db.load("hardpoints")
    for k, p in sorted(hp.get("parameters", {}).items()):
        keys.append((k, p.get("description", k), "m",
                     "Car on lift at ride height (or with corner weights restored): plumb/laser to the joint or bushing "
                     "centre, measure X, Y, Z from the reference origin; ±3 mm."))
    al = db.load("alignment")
    for k, p in sorted(al.get("parameters", {}).items()):
        keys.append((k, p.get("description", k), p.get("unit", "rad"),
                     "Alignment rack printout (before and after values), at curb weight; enter radians."))
    seen = set()
    for k, desc, unit, how in keys:
        if k in seen:
            continue
        seen.add(k)
        prev = old.get("parameters", {}).get(k)
        if prev and any(c.get("value") is not None for c in prev.get("candidates", [])):
            d["parameters"][k] = prev  # keep the user's data
        else:
            d["parameters"][k] = entry(desc, unit, how)
    db.save(d, OUT)
    print(f"wrote {os.path.relpath(OUT, db.ROOT)} with {len(d['parameters'])} fill-in entries")


if __name__ == "__main__":
    main()
