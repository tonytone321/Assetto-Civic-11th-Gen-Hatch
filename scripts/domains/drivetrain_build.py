import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import dbutil as db
D=db.load("drivetrain")
# fix shift mechanism value (no unsourced 'cable-operated')
D["parameters"]["drivetrain.shift_mechanism"]["candidates"][0]["value"]="6MT revised for improved shift rigidity and shorter shift throws"
db.add_source(D,"dt:civicxi-clutch-thread","1.5T - Has the clutch system of the 11th generation Civic weakened? (CivicXI forum, post #2 by cwtechshiz, Dec 9, 2024)",
 "https://www.civicxi.com/forum/threads/has-the-clutch-system-of-the-11th-generation-civic-weakened.53431/","CivicXI forum (owner post)","C",
 applicability="11th-gen Civic 1.5T 6MT hatch (owner's car, clutch/flywheel replacement)",cache_file="cache/pages/b3c87c11a636fa75.txt",
 notes="Single owner teardown report: weak source, corroborating only.")
db.add_source(D,"dt:tractionlife-2022-st-mt-review","2022 Honda Civic Sport Touring Hatchback Review (Manual)","https://tractionlife.com/2022-honda-civic-hatchback-sport-touring-manual-review/",
 "Traction Life","C",applicability="2022 Civic Hatchback Sport Touring 6MT",cache_file="cache/pages/0e3fb114824cb550.txt")
F=db.app("2022-2024 (owner car, year not stated)","US/CA (not stated)","hatch (1.5T)","6MT")
db.add_candidate(D,"drivetrain.clutch_type","Clutch type","text","medium",db.record(value="single dry plate, rigid (unsprung) hub disc; torsional damping in the dual-mass flywheel",unit="text",
  cls="C",source_id="dt:civicxi-clutch-thread",locator="post #2",evidence="Also blown away the oem clutch disc has no springs on it at all. All of the dampening for the oem system comes from the dual mass flywheel",
  as_printed="oem clutch disc has no springs",applicability=F,confidence="low",
  notes="'single dry plate' is the conventional FWD manual layout, not stated by the source. Rigid disc is consistent with a DMF (dt flywheel_type, class A)."))
db.add_candidate(D,"drivetrain.clutch_actuation","Clutch actuation","text","low",db.record(value="hydraulic (master cylinder, line with in-line damper)",unit="text",cls="C",
  source_id="dt:civicxi-clutch-thread",locator="original post and post #2",
  evidence="even when I adjusted the stroke of the clutch master cylinder to the longest … I even deleted on the stupid in-line clutch damper and replaced the rubber oem clutch line",
  as_printed="clutch master cylinder … in-line clutch damper … oem clutch line",applicability=F,confidence="medium",notes="Owner posts; parts catalog clutch-hydraulics diagram not opened (lead)."))
CL=["hondapartsnow 2024 Civic flywheel/differential listings (no clutch dimensions)","hondapartsnow clutch-disc/pressure-plate category URLs (404)",
    "WebSearch: 11th gen Civic 1.5T 6MT clutch kit OEM disc diameter (Exedy/ACT/Clutch Masters)","prlmotorsports Exedy 2022+ Civic 1.5T kit page (404)",
    "civicxi clutch thread (no diameter)"]
db.add_candidate(D,"drivetrain.clutch_disc_outer_diameter","Clutch disc outer diameter","m","medium",db.unknown("m",CL,
  "Measure the removed OEM disc (22200-series part) with calipers during a clutch job, or read an OEM/aftermarket kit spec sheet that names the OEM size.",
  notes="Lead only (search snippet, not opened): an Exedy Stage 2 kit for the 11th-gen 1.5T is described with a 230 mm disc and 24T spline; that is the aftermarket disc, not verified OEM."))
db.add_candidate(D,"drivetrain.clutch_disc_inner_diameter","Clutch friction-facing inner diameter","m","low",db.unknown("m",CL,"Measure the removed OEM disc facing inner diameter with calipers."))
db.add_candidate(D,"drivetrain.clutch_torque_capacity","Clutch static torque capacity (or clamp load)","N*m","medium",db.unknown("N*m",CL,
  "Not measurable without a test rig; derive from pressure-plate clamp load (published by aftermarket makers for the OEM unit), facing diameters and friction coefficient (~0.27-0.32 organic).",
  notes="An owner post says the OEM pressure plate is 'approximately 500kg, I believe' — hearsay, not recorded as a value. Stock car does not slip at 177 lb-ft (240 N*m), so capacity > 240 N*m."))
db.add_candidate(D,"drivetrain.flywheel_inertia","Flywheel + clutch assembly inertia (engine side)","kg*m2","high",db.unknown("kg*m2",
  ["hondapartsnow flywheel listing (only a shipping weight)","Honda press releases (type only)","civicxi forum clutch threads"],
  "Remove the DMF and clutch cover; bifilar/trifilar pendulum or measure mass and outer/inner radii of each disc; or estimate from free-revving rpm decay logged at clutch-in with known engine friction.",
  notes="DMF primary and secondary inertias differ; for a sim a lumped value is used. Shipping weight 34.6 lb (incl. box) is an upper bound on mass."))
db.add_candidate(D,"drivetrain.driveline_inertia","Driveline rotating inertia downstream of clutch (gearbox, diff, halfshafts), referred to wheels","kg*m2","medium",db.unknown("kg*m2",
  ["no published data for this gearbox","Honda press materials","parts listings"],
  "Coast-down / free-roll test with the car on a lift (wheel spin-down in neutral vs in gear), or CAD of the gearset; small relative to wheel+tyre inertia."))
db.add_candidate(D,"drivetrain.rev_hang_qualitative","Rev hang on throttle lift / clutch-in (qualitative)","text","high",db.record(value="present (reviewer-reported); not quantified",unit="text",cls="C",
  source_id="dt:tractionlife-2022-st-mt-review",locator="driving impressions paragraph",
  evidence="There’s also some rev hang, so you’ll need to be patient before dumping the clutch on your next gear.",as_printed="some rev hang",
  applicability=db.app("2022","US","Sport Touring","6MT"),confidence="medium",notes="Qualitative only; duration and rpm amount unknown (see drivetrain.rev_hang_duration)."))
db.add_candidate(D,"drivetrain.rev_hang_duration","Rev hang: time for rpm to fall after clutch-in at high rpm, and rpm held","s","high",db.unknown("s",
  ["tractionlife review (qualitative only)","WebSearch: 2022 Civic hatchback Sport Touring manual rpm/rev hang review","civicxi forum threads (lead)"],
  "OBD-II log (>=10 Hz rpm, throttle, clutch switch if available) of 3000->idle and 6000->idle drops with clutch in after a full-throttle pull; and rpm trace during 1-2 and 2-3 upshifts. Report time to drop 1000 rpm and any plateau.",
  notes="Do not model a specific hang until logged."))
db.add_candidate(D,"drivetrain.shift_time","Gear-change time (clutch open to closed) for a brisk human shift","s","medium",db.record(value=0.30,unit="s",status="estimated",cls="E",
  locator="engineering judgment",evidence="",as_printed="",range=[0.2,0.5],applicability=db.app("generic","-","-","6MT",notes="judgment"),confidence="low",
  how_to_measure="Datalog clutch switch / rpm during brisk shifts; or time from video with on-screen tach.",
  notes="Basis: typical brisk manual shifts in road tests take ~0.2-0.5 s; reviewer-reported rev hang argues against shorter values. Not a measurement of this car."))
db.add_candidate(D,"drivetrain.rev_match","Automatic rev-matching on downshifts","bool","medium",db.unknown("bool",
  ["2022/2023/2024 US hondanews spec tables (no rev-match row)","2024 Honda Canada spec table (no rev-match row)","2022 Honda Canada launch release (not mentioned)"],
  "Check owner's manual for 'Rev Match Control' or test: downshift with clutch in and watch for an automatic blip.",
  notes="Absence from all Honda spec tables suggests not fitted (unlike Si/Type R), but absence is not recorded as evidence."))
db.add_candidate(D,"drivetrain.shift_indicator","Upshift/gear indicator in cluster (MT)","bool","low",db.unknown("bool",
  ["Honda US/CA spec tables (no shift-indicator row)"],"Owner's manual cluster section, or photo of the cluster while driving the MT.",
  notes="Lead for domain 9 (dashboard.json)."))
for k,unit,s in (("drivetrain.obs_rpm_at_100kmh_6th","rpm",100),("drivetrain.obs_rpm_at_70mph_6th","rpm",70)):
    db.add_candidate(D,k,f"Observed engine rpm at {s} {'km/h' if s==100 else 'mph'} in 6th (real-world cross-check)",unit,"high",db.unknown(unit,
      ["WebSearch: 2022 Civic hatchback Sport Touring manual 6th gear rpm at 70 mph / 100 km/h review","tractionlife review (no cruise rpm)","autotrader.ca editorial (blocked host)"],
      "Cruise at GPS-verified speed in 6th on level road, photograph the tach or log OBD rpm.",
      notes="Compare with drivetrain.pred_rpm_at_* derivations. None found in an opened source."))
print(db.save(D))
