#!/usr/bin/env python3
"""Builder for vehicle_data/mass_inertia.json (domain 3). Kept in scratchpad; the JSON is the product.
Every SI value is produced by dbutil.record(printed=...) from the figure as printed."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db

d = {"domain": "mass_inertia", "title": "Mass and inertia", "schema_version": 1,
     "updated": db.today(), "sources": {}, "parameters": {}}

R = db.record
APP_CA_ST_MT = db.app("2024", "CA", "Sport Touring", "6MT")
APP_US_ST_MT = db.app("2024", "US", "Sport Touring", "6MT")

# ------------------------------------------------------------------ sources
db.add_source(d, "mass:hondanews-ca-2024-hatch-specs",
              title="2024 Honda Civic Hatchback Specifications (release, April 4, 2024)",
              url="https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
              publisher="Honda Canada Inc. (Honda Canada News)", cls="A", access_method="rendered",
              applicability="2024 Civic Hatchback, Canada, Sport and Sport Touring columns (1.5T; CVT, MT on Sport Touring)",
              cache_file="cache/pages/22157798d6e48e1c.txt")
db.add_source(d, "mass:hondainfocenter-us-2024-hatch-specs",
              title="2024 Civic Hatchback - Specifications (Honda Information Center feature guide)",
              url="https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Civic-Hatchback-Specifications/",
              publisher="American Honda Motor Co., Inc.", cls="A", access_method="static",
              applicability="2024 Civic Hatchback, US market, LX / Sport / EX-L / Sport Touring columns; page footer: 'All information contained herein applies to U.S. veh[icles]'",
              notes="Column order in the HTML table is LX, Sport, EX-L, Sport Touring (data-model-identifier 1..4); the 6MT weight-distribution row has values only in columns 2 (Sport) and 4 (Sport Touring), verified in cached HTML cache/pages/b67f7f855816944e.html.",
              cache_file="cache/pages/b67f7f855816944e.txt")

# ------------------------------------------------------------------ curb mass
K = "mass.curb_mass"
desc = "Curb mass (manufacturer curb weight), 2024 Sport Touring hatchback 6MT"
db.add_candidate(d, K, desc, "kg", "critical", R(
    printed=(1382, "kg"), status="confirmed", cls="A", source_id="mass:hondanews-ca-2024-hatch-specs",
    locator="DIMENSIONS table, row 'Curb weight – MT/CVT (kg)', SPORT TOURING column",
    evidence="Curb weight – MT/CVT (kg) NA/1391 1382/1412",
    as_printed="1382 (MT, Sport Touring)", applicability=APP_CA_ST_MT, confidence="high",
    notes="Canadian figure for exactly the target trim and gearbox. Columns are SPORT then SPORT TOURING; "
          "Sport is CVT-only in Canada for 2024 (NA for MT). The resolver selects the Canadian record."))
db.add_candidate(d, K, desc, "kg", "critical", R(
    printed=(3036, "lb"), status="confirmed", cls="A", source_id="mass:hondainfocenter-us-2024-hatch-specs",
    locator="Exterior Measurements table, row 'Curb Weight (6MT/CVT)', Sport Touring column",
    evidence="Curb Weight (6MT/CVT) NA / 2877 lbs 2932 lbs / 2956 lbs NA / 3053 lbs 3036 lbs / 3102 lbs",
    as_printed="3036 lbs (6MT, Sport Touring)", applicability=APP_US_ST_MT, confidence="high",
    notes="US figure for the same trim/gearbox; 3036 lb = 1377.1 kg, about 5 kg below the Canadian 1382 kg. "
          "The difference is small (0.4 %) and may come from Canadian-market equipment or rounding/definition "
          "differences; both are kept, the Canadian value is the target-market value."))

# ------------------------------------------------------------------ front fraction
K = "mass.front_fraction"
desc = "Static front-axle share of curb mass"
db.add_candidate(d, K, desc, "1", "critical", R(
    printed=(59, "%"), status="confirmed", cls="A", source_id="mass:hondainfocenter-us-2024-hatch-specs",
    locator="Exterior Measurements table, row 'Weight Distribution (front/rear, 6MT)', Sport Touring column (4th)",
    evidence="Weight Distribution (front/rear, 6MT) 60% / 40% 59% / 41%",
    as_printed="59% / 41%", applicability=APP_US_ST_MT, confidence="high",
    notes="Published to whole percent, so the true value lies in about 0.585-0.595. The two printed values sit in "
          "the Sport (60/40) and Sport Touring (59/41) columns; LX and EX-L cells are empty (no 6MT), checked in raw HTML. "
          "US-market figure; no Canadian distribution figure found (Honda Canada spec release lists none). "
          "Same trim/gearbox/body/engine, so mechanically applicable to the Canadian car (CA curb mass differs by ~5 kg)."))

# ------------------------------------------------------------------ fuel capacity
K = "mass.fuel_capacity"
desc = "Fuel tank capacity"
db.add_candidate(d, K, desc, "m3", "medium", R(
    printed=(46, "L"), status="confirmed", cls="A", source_id="mass:hondanews-ca-2024-hatch-specs",
    locator="DIMENSIONS table, row 'Fuel tank capacity (L)'",
    evidence="Fuel tank capacity (L) 46 46",
    as_printed="46", applicability=db.app("2024", "CA", "Sport, Sport Touring", "CVT and 6MT"), confidence="high",
    notes="Same value in both Canadian trim columns."))
db.add_candidate(d, K, desc, "m3", "medium", R(
    printed=(12.39, "US gal"), status="confirmed", cls="A", source_id="mass:hondainfocenter-us-2024-hatch-specs",
    locator="EPA Mileage Ratings / Fuel table, row 'Fuel Tank Capacity'",
    evidence="Fuel Tank Capacity 12.39 gal 12.39 gal 12.39 gal 12.39 gal",
    as_printed="12.39 gal", applicability=db.app("2024", "US", "LX, Sport, EX-L, Sport Touring", "CVT and 6MT"),
    confidence="high",
    notes="12.39 US gal = 46.9 L; Canada prints 46 L. Same tank, different rounding/unit convention (not a conflict "
          "beyond rounding: 46 L as printed vs 46.9 L)."))

# ================================================================== additional sources
db.add_source(d, "mass:hondanews-us-2024-hatch-specs",
              title="2024 Honda Civic Hatchback Specifications & Features (release, August 9, 2023)",
              url="https://hondanews.com/en-US/honda-automobiles/releases/release-5003aaa39c009393f5d06d620f0fc923-2024-honda-civic-hatchback-specifications-features",
              publisher="American Honda Motor Co., Inc. (Honda Auto News)", cls="A", access_method="rendered",
              applicability="2024 Civic Hatchback, US, columns LX / Sport / EX-L / Sport Touring",
              cache_file="cache/pages/dd2e2052fcb1a220.txt")
db.add_source(d, "mass:hondanews-us-2022-hatch-specs",
              title="2022 Honda Civic Hatchback Specifications & Features",
              url="https://hondanews.com/en-US/honda-automobiles/releases/release-cb177600e922c8a5fcfa01b9b80149e2-2022-honda-civic-hatchback-specifications-features",
              publisher="American Honda Motor Co., Inc. (Honda Auto News)", cls="A", access_method="rendered",
              applicability="2022 Civic Hatchback, US, columns LX / Sport / EX-L / Sport Touring",
              cache_file="cache/pages/fb1d5790fd3bfda8.txt")
db.add_source(d, "mass:hondanews-ca-2023-hatch-specs",
              title="2023 Civic Hatchback Specifications (April 13, 2023)",
              url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
              publisher="Honda Canada Inc.", cls="A", access_method="rendered",
              applicability="2023 Civic Hatchback, Canada, LX / Sport / Sport-B / Sport Touring",
              cache_file="cache/pages/374416cf6bc6db5d.txt")
db.add_source(d, "mass:hondanews-ca-2022-hatch-specs",
              title="2022 Civic Hatchback Specifications (October 12, 2021)",
              url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
              publisher="Honda Canada Inc.", cls="A", access_method="rendered",
              applicability="2022 Civic Hatchback, Canada, LX / Sport / Sport Touring",
              cache_file="cache/pages/344bc90bb36560a9.txt")
db.add_source(d, "mass:nhtsa-safercar-data",
              title="NHTSA Safercar_data.csv (NCAP 5-Star ratings flat file) and READ ME",
              url="https://static.nhtsa.gov/nhtsa/downloads/Safercar/Safercar_data.csv",
              publisher="US DOT NHTSA", cls="A", access_method="static (curl, CSV)",
              applicability="Row MAKE=HONDA, MODEL=CIVIC HATCHBACK, MODEL_YR=2024, BODY_STYLE=5 HB, DRIVE_TRAIN=FWD (identical rows for 2023; 2022 row has the same SSF). "
                            "Crash-test VINs in that row are 2HGFE2F2xNH... (2022 Civic Sedan); the same SSF 1.48 is listed for Civic Sedan, Si and Type R rows, "
                            "so the SSF was measured on one representative Civic (not identified as a hatchback).",
              notes="Field definitions from https://static.nhtsa.gov/nhtsa/downloads/Safercar/Safercar_data_READ_ME_file.txt "
                    "(MIN_GROSS_WEIGHT 'Vehicle Minimum Gross Weight (lbs)', MAX_GROSS_WEIGHT 'Vehicle Maximum Gross Weight (lbs)', "
                    "STATIC_STABI_FACTOR 'Static Stability Factor', ROLLOVER_POSSIBILITY 'Vehicle Rollover Possibility'). "
                    "Cross-checked with api.nhtsa.gov/SafetyRatings/VehicleId/19595: RolloverPossibility 0.095, dynamicTipResult 'No Tip'. "
                    "Evidence quotes are 'FIELD = value' pairs from the CSV row.",
              cache_file="cache/safercar_data.csv")
db.add_source(d, "mass:fr-2003-rollover-final-rule",
              title="Consumer Information; New Car Assessment Program; Rollover Resistance (final rule), 68 FR 59250, Oct 14 2003, Appendix II",
              url="https://www.govinfo.gov/content/pkg/FR-2003-10-14/pdf/03-25360.pdf",
              publisher="US DOT NHTSA (Federal Register)", cls="A", access_method="pdf_text.py",
              applicability="Rollover risk model used for NCAP rollover ratings (all vehicles)",
              cache_file="cache/pdf/46c251cc3d4c6e86.pdf")
db.add_source(d, "mass:heydinger1999-via-psu-notes",
              title="Notes_07_04 'Vehicle Inertial Measurements', p.5 'Inertial Properties of American Vehicles' (table from Heydinger et al., SAE 1999-01-1336, 'Measured Vehicle Inertial Parameters - NHTSA's Data Through November 1998')",
              url="https://www.me.psu.edu/sommer/me481/notes_07_04.pdf",
              publisher="Penn State ME481 course notes (H.J. Sommer), citing NHTSA/SAE data", cls="C", access_method="pdf_text.py",
              applicability="Class-average sprung mass, wheelbase, track, CG and Jxx/Jyy/Jzz of measured US vehicles (Passenger Small / Passenger Large)",
              notes="Secondary reproduction of NHTSA VIPD class averages; the SAE paper itself is paywalled (saemobilus) and was not opened. Values are class means, not individual-vehicle scatter.",
              cache_file="cache/pdf/8a8c996d5cf5417c.pdf")
db.add_source(d, "mass:ecfr-49cfr571.3",
              title="49 CFR 571.3 Definitions (Federal Motor Vehicle Safety Standards)",
              url="https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/subpart-A/section-571.3",
              publisher="US Government (eCFR)", cls="A", access_method="static (eCFR renderer API)",
              applicability="US regulatory definition of curb weight",
              cache_file="cache/pages/eecfe26001f3e59f.txt")
db.add_source(d, "mass:wikipedia-gasoline",
              title="Gasoline - Physical properties - Density",
              url="https://en.wikipedia.org/wiki/Gasoline",
              publisher="Wikipedia", cls="C", access_method="static",
              applicability="Gasoline in general (specific gravity range; European trading reference density)",
              notes="Wikipedia cites its sources [21][22]; used only for a generic fuel-density range.",
              cache_file="cache/pages/6c076f78f9fa784b.txt")

# ------------------------------------------------------------------ more curb-mass candidates (second sources, model-year check)
K = "mass.curb_mass"; desc = "Curb mass (manufacturer curb weight), 2024 Sport Touring hatchback 6MT"
db.add_candidate(d, K, desc, "kg", "critical", R(
    printed=(3036, "lb"), status="confirmed", cls="A", source_id="mass:hondanews-us-2024-hatch-specs",
    locator="WEIGHT section, row 'Curb Weight (lbs.) (6MT)', 4th column (Sport Touring)",
    evidence="Curb Weight (lbs.) (6MT) - 2,932 - 3,036",
    as_printed="3,036", applicability=APP_US_ST_MT, confidence="high",
    notes="Independent Honda press document agreeing with hondainfocenter (3036 lb)."))
db.add_candidate(d, K, desc, "kg", "critical", R(
    printed=(1382, "kg"), status="confirmed", cls="A", source_id="mass:hondanews-ca-2023-hatch-specs",
    locator="DIMENSIONS table, row 'Curb weight (kg) MT/CVT', Sport Touring column",
    evidence="Curb weight (kg) MT/CVT 1322/1333 1391 1391 1382/1412",
    as_printed="1382 (MT)", applicability=db.app("2023", "CA", "Sport Touring", "6MT"), confidence="high",
    notes="Model-year check: identical to 2024 (1382 kg)."))
db.add_candidate(d, K, desc, "kg", "critical", R(
    printed=(1382, "kg"), status="confirmed", cls="A", source_id="mass:hondanews-ca-2022-hatch-specs",
    locator="DIMENSIONS table, row 'Curb weight (kg) MT/CVT', Sport Touring column",
    evidence="Curb weight (kg) MT/CVT 1322/1333 1361/1391 1382/1412",
    as_printed="1382 (MT)", applicability=db.app("2022", "CA", "Sport Touring", "6MT"), confidence="high",
    notes="Model-year check: identical to 2023 and 2024 (1382 kg)."))

# ------------------------------------------------------------------ front fraction, more candidates
K = "mass.front_fraction"; desc = "Static front-axle share of curb mass"
db.add_candidate(d, K, desc, "1", "critical", R(
    printed=(59, "%"), status="confirmed", cls="A", source_id="mass:hondanews-us-2024-hatch-specs",
    locator="WEIGHT section, row 'Weight Distribution (%) (front/rear) (6MT)', 4th column (Sport Touring)",
    evidence="Weight Distribution (%) (front/rear) (6MT) - 60 / 40 - 59 / 41",
    as_printed="59 / 41", applicability=APP_US_ST_MT, confidence="high",
    notes="Second Honda document, same 59/41 to whole percent."))
db.add_candidate(d, K, desc, "1", "critical", R(
    printed=(59.1, "%"), status="confirmed", cls="A", source_id="mass:hondanews-us-2022-hatch-specs",
    locator="EXTERIOR MEASUREMENTS, row 'Weight Distribution (front/rear, 6MT)', Sport Touring column",
    evidence="Weight Distribution (front/rear, 6MT) NA 59.7% / 40.3% NA 59.1% / 40.9%",
    as_printed="59.1% / 40.9%", applicability=db.app("2022", "US", "Sport Touring", "6MT"), confidence="high",
    prefer=True,
    selection_reason="Same value as the 2024 figure (59 %) printed to one more decimal; curb weight is unchanged "
                      "2022-2024 (US 3036 lb, CA 1382 kg), so the 2022 decimal figure is the most precise applicable value.",
    notes="Also on hondainfocenter.com 2022 specs (cache/pages/ff52eae8cd7d0fc1.txt, column 4 = Sport Touring checked in HTML)."))

# ------------------------------------------------------------------ fuel capacity, second US candidate
K = "mass.fuel_capacity"; desc = "Fuel tank capacity"
db.add_candidate(d, K, desc, "m3", "medium", R(
    printed=(12.4, "US gal"), status="confirmed", cls="A", source_id="mass:hondanews-us-2024-hatch-specs",
    locator="row 'Fuel Tank Capacity (U.S. gal.)'",
    evidence="Fuel Tank Capacity (U.S. gal.) 12.4",
    as_printed="12.4", applicability=db.app("2024", "US", "all hatchback trims", "CVT and 6MT"), confidence="high",
    notes="Rounded version of 12.39 gal."))

# ------------------------------------------------------------------ fuel density
db.add_candidate(d, "mass.fuel_density", "Gasoline density (for fuel mass)", "kg/m3", "low", R(
    value=755.0, unit="kg/m3", status="estimated", cls="C", source_id="mass:wikipedia-gasoline",
    locator="Physical properties > Density",
    evidence="The specific gravity of gasoline ranges from 0.71 to 0.77 … Finished marketable gasoline is traded (in Europe) with a standard reference of 0.755 kilograms per liter",
    as_printed="0.755 kilograms per liter (range 0.71 to 0.77)", applicability={"notes": "generic gasoline, not Canadian regular specifically"},
    confidence="medium", range=[710.0, 770.0],
    how_to_measure="Hydrometer on a sample of the fuel actually used (Canadian regular, summer/winter blend), at 15 C.",
    notes="Value 755 kg/m3 = 0.755 kg/L as printed (unit change only); range from specific gravity 0.71-0.77. Canadian winter blends are at the light end."))

# ------------------------------------------------------------------ fuel level implied by curb mass
db.add_candidate(d, "mass.fuel_level_assumed", "Fuel fill fraction included in the published curb mass", "1", "medium", R(
    value=1.0, unit="1", status="estimated", cls="E", source_id="mass:ecfr-49cfr571.3",
    locator="§571.3(b) Definitions, 'Curb weight'",
    evidence="Curb weight means the weight of a motor vehicle with standard equipment; maximum capacity of engine fuel, oil, and coolant",
    as_printed="maximum capacity of engine fuel", applicability={"market": "US", "notes": "US federal definition"},
    confidence="medium", range=[0.9, 1.0],
    how_to_measure="Weigh the car on four corner scales with a full tank (filled to first click) and again near empty; the difference over 46 L fuel mass confirms the convention.",
    notes="Honda does not state its curb-weight definition on the spec pages opened; applying the US FMVSS definition (full tank) "
          "is an inference, hence class E. No Canadian definition found on the Honda Canada spec release."))

# ------------------------------------------------------------------ NHTSA SSF, rollover, gross weight
SAFE = db.app("2024", "US", "CIVIC HATCHBACK row (all trims)", "all", engine="all")
SAFE["notes"] = "NHTSA lists one SSF for the whole 2022-2024 Civic family; test vehicle not identified (crash-test VINs in row are 2022 Civic Sedans)."
db.add_candidate(d, "mass.ssf_nhtsa", "NHTSA measured Static Stability Factor, T/(2h)", "1", "high", R(
    printed=(1.48, "1"), status="confirmed", cls="A", source_id="mass:nhtsa-safercar-data",
    locator="Safercar_data.csv, row HONDA / CIVIC HATCHBACK / 2024 / 5 HB / FWD, field STATIC_STABI_FACTOR",
    evidence="STATIC_STABI_FACTOR = 1.48", as_printed="1.48", applicability=SAFE, confidence="medium",
    notes="Government measurement, but probably on a Civic Sedan (same platform; hatch differs in rear body, ST trim has 18 in wheels). "
          "Printed to 0.01, i.e. 1.475-1.485. Used by derivation mass.cg_height."))
db.add_candidate(d, "mass.rollover_possibility_nhtsa", "NHTSA predicted rollover possibility (single-vehicle crash)", "1", "low", R(
    printed=(0.095, "1"), status="confirmed", cls="A", source_id="mass:nhtsa-safercar-data",
    locator="Safercar_data.csv, row HONDA / CIVIC HATCHBACK / 2024, fields ROLLOVER_POSSIBILITY and TIP",
    evidence="ROLLOVER_POSSIBILITY = 0.095 … TIP = No Tip", as_printed="0.095", applicability=SAFE, confidence="high",
    notes="Also returned by api.nhtsa.gov/SafetyRatings/VehicleId/19595 ('RolloverPossibility': 0.095, 'dynamicTipResult': 'No Tip'). "
          "Used only to cross-check the SSF through the 2003 NHTSA risk model (derivation mass.check_rollover_risk_from_ssf)."))
GW = db.app("2024", "US", "CIVIC HATCHBACK row (lineup min/max across trims)", "all", engine="all")
db.add_candidate(d, "mass.gvwr_lineup_min", "Lowest GVWR across the 2024 Civic Hatchback lineup (NHTSA)", "kg", "medium", R(
    printed=(3946, "lb"), status="confirmed", cls="A", source_id="mass:nhtsa-safercar-data",
    locator="Safercar_data.csv, row HONDA / CIVIC HATCHBACK / 2024, field MIN_GROSS_WEIGHT",
    evidence="MIN_GROSS_WEIGHT = 3946", as_printed="3946 (lbs per READ ME)", applicability=GW, confidence="high",
    notes="Lineup includes 2.0 L LX/Sport and 1.5T EX-L/Sport Touring, CVT and MT; which trim has which GVWR is not stated. Same values for 2023."))
db.add_candidate(d, "mass.gvwr_lineup_max", "Highest GVWR across the 2024 Civic Hatchback lineup (NHTSA)", "kg", "medium", R(
    printed=(4056, "lb"), status="confirmed", cls="A", source_id="mass:nhtsa-safercar-data",
    locator="Safercar_data.csv, row HONDA / CIVIC HATCHBACK / 2024, field MAX_GROSS_WEIGHT",
    evidence="MAX_GROSS_WEIGHT = 4056", as_printed="4056 (lbs per READ ME)", applicability=GW, confidence="high",
    notes="The Sport Touring 6MT GVWR lies within [3946, 4056] lb = [1789.9, 1839.8] kg; the exact value is on the door-jamb label."))

db.add_candidate(d, "mass.gvwr", "Gross vehicle weight rating, Sport Touring 6MT", "kg", "medium", db.unknown(
    "kg", searches=["hondanews.ca 2022/2023/2024 hatchback spec releases (no GVWR row)",
                    "hondanews.com 2022/2023/2024 hatchback spec releases (no GVWR row)",
                    "hondainfocenter.com 2022/2024 spec tables (no GVWR row)",
                    "owners.honda.com manuals (redirects to login portal mygarage.honda.com, empty)",
                    "web search: civic hatchback 2022 GVWR GAWR door jamb label sport touring kg (no label photo found)",
                    "web search: 2024 Honda Civic Hatchback owner's manual PDF specifications (no manual PDF found)",
                    "NHTSA Safercar_data.csv: only lineup min/max 3946/4056 lb (see mass.gvwr_lineup_min/max)"],
    how_to_measure="Photograph the certification label on the driver's door B-pillar (GVWR, GAWR FRT, GAWR RR in kg and lb).",
    notes="Bounded to 1789.9-1839.8 kg by NHTSA lineup min/max (mass.gvwr_lineup_min/max)."))
for k, dsc in (("mass.gawr_front", "Gross axle weight rating, front"), ("mass.gawr_rear", "Gross axle weight rating, rear")):
    db.add_candidate(d, k, dsc, "kg", "low", db.unknown(
        "kg", searches=["Honda CA/US spec releases 2022-2024 (not listed)", "NHTSA Safercar_data.csv (no axle ratings)",
                        "web search for door-jamb label photos (none found)", "owner's manual not obtainable (owners.honda.com login portal)"],
        how_to_measure="Read from the door-jamb certification label (GAWR FRT / GAWR RR)."))

db.add_candidate(d, "mass.corner_weights", "Static corner masses FL/FR/RL/RR", "kg", "high", db.unknown(
    "kg", searches=["Honda spec releases give only axle split (59.1/40.9)", "no instrumented test with corner weights found in time budget"],
    how_to_measure="Four-pad corner scales, full tank, no driver, tyres at placard pressure, level floor; record each corner ±1 kg.",
    notes="Left/right split unknown; a lateral CG offset of a few mm is expected (driver-side steering column, battery position) but is unpublished."))
db.add_candidate(d, "mass.unsprung_mass_front", "Unsprung mass per front corner", "kg", "high", db.unknown(
    "kg", searches=["no published part masses for knuckle/hub/brake/strut found; parts-catalog shipping weights are not part masses"],
    how_to_measure="Weigh wheel+tyre, rotor, caliper, knuckle/hub during a brake or strut job; add half of strut, driveshaft and control arm masses."))
db.add_candidate(d, "mass.unsprung_mass_rear", "Unsprung mass per rear corner", "kg", "high", db.unknown(
    "kg", searches=["no published rear multi-link component masses found"],
    how_to_measure="Weigh wheel+tyre, rotor, caliper, hub/knuckle; add half of link, damper and spring masses."))

# ------------------------------------------------------------------ lateral CG (judgment)
db.add_candidate(d, "mass.cg_x", "Lateral CG position (vehicle X, +right)", "m", "low", R(
    value=0.0, unit="m", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability={"notes": "this car (judgment)"}, confidence="low", range=[-0.015, 0.015],
    how_to_measure="Corner scales: x_cg = (T/2)*((FR+RR)-(FL+RL))/m using front/rear tracks per axle.",
    notes="Taken as the centreline: the body is symmetric and no lateral split is published. Range allows for driver-side "
          "column/pedal box and the battery; a measured left/right split replaces it."))

if __name__ == "__main__":
    p = db.save(d)
    print("saved", p)
