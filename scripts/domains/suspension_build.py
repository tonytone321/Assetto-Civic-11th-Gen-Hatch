#!/usr/bin/env python3
"""Builds vehicle_data/suspension.json and vehicle_data/alignment.json (domain 6) and adds
the unknown steering records to steering.json."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.chdir(ROOT)
import dbutil as db  # noqa: E402

V = os.path.join(ROOT, "vehicle_data")
A24CA = db.app("2024", "CA", "Sport Touring", "6MT or CVT (row not split by gearbox)")
A24US = db.app("2024", "US", "Sport Touring", "6MT or CVT (row not split by gearbox)")
A22US = db.app("2022", "US", "Sport Touring", "6MT or CVT (row not split by gearbox)",
               notes="Model-year check: same value in the 2024 US table.")
A22CA = db.app("2022", "CA", "Sport Touring", "6MT or CVT", notes="Model-year check: same value in 2023 and 2024 Canadian tables.")
TARGET = db.app("2024", "CA", "Sport Touring", "6MT", notes="estimate made for the target car")

d = {"domain": "suspension", "title": "Suspension", "schema_version": 1, "updated": db.today(),
     "sources": {}, "parameters": {}}
S = d["sources"]


def src(sid, **kw):
    db.add_source(d, sid, **kw)


src("susp:hondanews-ca-2024-hatch-specs",
    title="2024 Honda Civic Hatchback Specifications (release, April 4, 2024)",
    url="https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
    publisher="Honda Canada Inc. (Honda Canada News)", cls="A", access_method="rendered",
    applicability="2024 Civic Hatchback, Canada, SPORT and SPORT TOURING columns", cache_file="cache/pages/22157798d6e48e1c.txt")
src("susp:hondanews-ca-2022-hatch-specs",
    title="2022 Civic Hatchback Specifications (release, October 12, 2021)",
    url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
    publisher="Honda Canada Inc. (Honda Canada News)", cls="A",
    applicability="2022 Civic Hatchback, Canada, LX / Sport / Sport Touring", cache_file="cache/pages/344bc90bb36560a9.txt")
src("susp:hondanews-us-2024-hatch-specs",
    title="2024 Honda Civic Hatchback Specifications & Features",
    url="https://hondanews.com/en-US/honda-automobiles/releases/2024-honda-civic-hatchback-specifications-features",
    publisher="American Honda Motor Co., Inc. (Honda News)", cls="A",
    applicability="2024 Civic Hatchback, US, LX / Sport / EX-L / Sport Touring; stabilizer cell spans all trims ('<<' = same as left)",
    cache_file="cache/pages/2b1524caf89378a3.txt")
src("susp:hondainfocenter-us-2024-hatch-specs",
    title="2024 Civic Hatchback - Specifications (Honda Information Center feature guide)",
    url="https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Civic-Hatchback-Specifications/",
    publisher="American Honda Motor Co., Inc.", cls="A",
    applicability="2024 Civic Hatchback, US, LX / Sport / EX-L / Sport Touring",
    notes="Prints rear bar 17.0 mm for LX/Sport/EX-L and 17.5 mm for Sport Touring, while hondanews.com 2024 prints 17.5 for all trims. Both agree on 17.5 mm for Sport Touring.",
    cache_file="cache/pages/b67f7f855816944e.txt")
src("susp:hondanews-us-2022-hatch-debut",
    title="2022 Honda Civic Hatchback Makes Global Debut During Honda Civic Remix Virtual Performance",
    url="https://hondanews.com/en-US/releases/release-53541be6030b25a47a2899aba12f09d7-2022-honda-civic-hatchback-makes-global-debut-during-honda-civic-remix-virtual-performance",
    publisher="American Honda Motor Co., Inc. (Honda News)", cls="A",
    applicability="2022 Civic Hatchback, US, all trims (narrative)", cache_file="cache/pages/6b8fd454f6a040ce.txt")
src("susp:hondapartsnow-2024-civic-control-arm",
    title="OEM 2024 Honda Civic Control Arm (parts catalogue listing with submodel fitment)",
    url="https://www.hondapartsnow.com/oem-2024-honda-civic-control_arm.html",
    publisher="HondaPartsNow (Honda dealer parts retailer)", cls="C",
    applicability="2024 Civic, all bodies; each part lists fitting submodels incl. '5 Door 1.5T Sport Touring | 6MT, CVT'",
    notes="Dealer catalogue derived from Honda EPC; class C because it is a retailer page, not Honda's own catalogue. Diagram images were not analysed.",
    cache_file="cache/pages/e9f731ff6b9e9d47.txt")
src("susp:hondapartsnow-2024-civic-trailing-arm",
    title="OEM 2024 Honda Civic Trailing Arm (parts catalogue listing with submodel fitment)",
    url="https://www.hondapartsnow.com/oem-2024-honda-civic-trailing_arm.html",
    publisher="HondaPartsNow (Honda dealer parts retailer)", cls="C",
    applicability="2024 Civic, all bodies", cache_file="cache/pages/b8b52890c32a91d3.txt")
# leads (not used as values for the target; recorded so the estimates' basis is traceable)
src("susp:spoon-fl1-progressive-spring",
    title="[New item] CIVIC FL1 PROGRESSIVE SPRING (Spoon Sports blog, 2022-08-16)",
    url="https://www.spoonsports.jp/blog/?p=4237", publisher="Spoon Sports (Tokyo)", cls="C",
    applicability="Japanese-market Civic hatchback FL1 (1.5T). NOT North American: lead only (identity rule).",
    notes="States the stock ('normal') rates F 2.7 / R 2.8 kgf/mm. Market differs from target; no evidence the NA Sport Touring springs share part numbers.",
    cache_file="cache/pages/bbd81e64ddfb48f3.txt")
src("susp:civicxi-si-spring-rates-2023",
    title="2023 Civic Si Spring Rates, Motion Ratio, Ride Frequencies, Autocross (CivicXI forum, user eromani, 2023-08-09)",
    url="https://www.civicxi.com/forum/threads/2023-civic-si-spring-rates-motion-ratio-ride-frequencies-autocross.52362/",
    publisher="CivicXI forum", cls="C",
    applicability="2023 Civic Si sedan 6MT (excluded variant): lead only.",
    notes="Owner's table: front spring 27.0 N/mm, rear 55.9 N/mm, motion ratio (wheel/spring) front 1.029, rear 1.333, unsprung 55/45 kg estimated. Source of the spring rates not stated; motion ratios 'measuring calculating'.",
    cache_file="cache/pages/b0264e7152552462.txt")

# ------------------------------------------------------------------ architecture
d["architecture"] = {
    "notes": "Members and functions for the target car. 'status' is confirmed only where a cited page names the item for the 1.5T Sport Touring hatch; function assignments that rest on the usual Honda layout are marked inferred.",
    "front": [
        {"item": "Suspension type", "description": "MacPherson strut (independent)", "status": "confirmed",
         "source_ids": ["susp:hondanews-ca-2024-hatch-specs", "susp:hondanews-us-2024-hatch-specs"],
         "evidence": "Independent strut front suspension • • | MacPherson Strut Front Suspension • • • •"},
        {"item": "Strut top", "description": "Damper mount bearing; low-friction ball joints; spring and damper alignment optimised for low friction; larger compliance bushing", "status": "confirmed",
         "source_ids": ["susp:hondanews-us-2022-hatch-debut"],
         "evidence": "the front MacPherson struts feature new low-friction ball joints and front damper mount bearings to improve steering feel and self-centering. The spring and damper alignment has been optimized to minimize operational friction, and a new larger compliance bushing with an improved bushing axis minimizes harshness."},
        {"item": "Front lower arm (L/R)", "description": "One lower control arm per side ('LOWER ARM COMP, FR', 51350-T20-A10 / 51360-T20-A10), listed for 5 Door 1.5T Sport Touring 6MT/CVT; carries the lower ball joint; two inner bushings (A-arm/L-arm) inferred", "status": "confirmed (part); shape inferred",
         "source_ids": ["susp:hondapartsnow-2024-civic-control-arm"]},
        {"item": "Front subframe", "description": "Aluminium front subframe with truss and rib structure", "status": "confirmed",
         "source_ids": ["susp:hondanews-us-2022-hatch-debut"],
         "evidence": "The all-new aluminum front subframe, with an efficient truss and rib structure, provides rigidity and stability."},
        {"item": "Spring", "description": "Coil spring concentric with the strut damper (MacPherson)", "status": "inferred (MacPherson by definition; 'spring and damper alignment' in press text)"},
        {"item": "Anti-roll bar", "description": "Tubular bar 26.5 mm OD x 4.5 mm wall, drop links to the struts (link mounting point inferred)", "status": "confirmed (bar); link location inferred",
         "source_ids": ["susp:hondanews-us-2024-hatch-specs", "susp:hondainfocenter-us-2024-hatch-specs"]},
        {"item": "Steering", "description": "Variable-ratio EPS rack-and-pinion; rack position (ahead of/behind axle) not confirmed", "status": "confirmed (type); layout unknown"},
    ],
    "rear": [
        {"item": "Suspension type", "description": "Multi-link (independent)", "status": "confirmed",
         "source_ids": ["susp:hondanews-ca-2024-hatch-specs", "susp:hondanews-us-2024-hatch-specs"],
         "evidence": "Independent multi-link rear suspension • •"},
        {"item": "Upper arm (L/R)", "description": "'UPPER ARM COMP, RR' 52510-T20-A00, listed for 5 Door 1.5T Sport Touring; camber control", "status": "confirmed (part); function inferred",
         "source_ids": ["susp:hondapartsnow-2024-civic-control-arm"]},
        {"item": "Lower arm A (L/R)", "description": "'Lower Arm A Complete' 52370-TGH-A00 (other name 'Front Lower Arm, Lateral Link'), listed for 5 Door 1.5T Sport Touring; front lateral link, acts as toe-control link (aftermarket 'rear toe links' replace this member - inferred)", "status": "confirmed (part); toe function inferred",
         "source_ids": ["susp:hondapartsnow-2024-civic-control-arm"]},
        {"item": "Lower arm B (L/R)", "description": "'ARM COMP, RR- B L / R' 52355-T20-A00 / 52350-T20-A00, listed for 5 Door 1.5T Sport Touring; main rear lower arm; press text says the rear lower arms got new bushings", "status": "confirmed (part); spring seat on this arm inferred, not confirmed",
         "source_ids": ["susp:hondapartsnow-2024-civic-control-arm", "susp:hondanews-us-2022-hatch-debut"],
         "evidence": "New rear lower control arm bushings promote better straight-line stability and turn in, while reducing noise and vibration inside the cabin."},
        {"item": "Trailing arm / knuckle (L/R)", "description": "'TRAILING ARM COMP, L/R' 52365-T20-A10 / 52360-T20-A10, listed for 1.5T EX-L/Sport Touring hatch and 1.5T Touring sedan (2.0 L cars use -A00; Si/Type R use T22); longitudinal location, carries the hub", "status": "confirmed (part); function inferred",
         "source_ids": ["susp:hondapartsnow-2024-civic-trailing-arm"]},
        {"item": "Rear spring and damper", "description": "Separate spring and damper believed (spring on lower arm B, damper to knuckle/trailing arm) as in the previous Civic multi-link; NOT confirmed for this car", "status": "unknown",
         "how_to_measure": "Underside photo of the rear corner (wheel off) or the Honda parts diagram 'RR. SHOCK ABSORBER / RR. LOWER ARM' image for the FL hatch."},
        {"item": "Rear anti-roll bar", "description": "Solid bar 17.5 mm; link location unknown", "status": "confirmed (bar)",
         "source_ids": ["susp:hondanews-ca-2024-hatch-specs"]},
    ],
}

# ------------------------------------------------------------------ anti-roll bars
K, DSC = "suspension.arb_front_diameter", "Front anti-roll bar outside diameter"
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(26.5, "mm"), cls="A", source_id="susp:hondanews-ca-2024-hatch-specs",
    locator="CHASSIS table, row 'Front and rear stabilizer bars (mm)', SPORT TOURING column",
    evidence="Front and rear stabilizer bars (mm) 26.5/17.5 26.5/17.5", as_printed="26.5/17.5",
    applicability=A24CA, confidence="high", notes="Canadian table gives diameters only (no tubular/solid)."))
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(26.5, "mm"), cls="A", source_id="susp:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Stabilizer Bar (mm) (front/rear)' (cell spans all trims)",
    evidence="Stabilizer Bar (mm) (front/rear) 26.5 x 4.5 (tubular) 17.5 (solid) << << <<",
    as_printed="26.5 x 4.5 (tubular)", applicability=A24US, confidence="high"))
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(26.5, "mm"), cls="A", source_id="susp:hondainfocenter-us-2024-hatch-specs",
    locator="Body/Suspension/Chassis table, row 'Stabilizer Bar (front/rear)', Sport Touring column",
    evidence="26.5 mm x 4.5 mm (tubular) / 17.5 mm (solid)", as_printed="26.5 mm x 4.5 mm (tubular)",
    applicability=A24US, confidence="high"))

K, DSC = "suspension.arb_front_wall_thickness", "Front anti-roll bar wall thickness (tubular bar)"
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(4.5, "mm"), cls="A", source_id="susp:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Stabilizer Bar (mm) (front/rear)'",
    evidence="Stabilizer Bar (mm) (front/rear) 26.5 x 4.5 (tubular) 17.5 (solid) << << <<",
    as_printed="26.5 x 4.5 (tubular)", applicability=A24US, confidence="high",
    notes="Not printed by Honda Canada; the bar diameter matches, so the US wall thickness is taken for the Canadian car."))
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(4.5, "mm"), cls="A", source_id="susp:hondainfocenter-us-2024-hatch-specs",
    locator="Body/Suspension/Chassis table, row 'Stabilizer Bar (front/rear)', Sport Touring column",
    evidence="26.5 mm x 4.5 mm (tubular) / 17.5 mm (solid)", as_printed="4.5 mm", applicability=A24US, confidence="high"))

K, DSC = "suspension.arb_rear_diameter", "Rear anti-roll bar diameter (solid)"
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(17.5, "mm"), cls="A", source_id="susp:hondanews-ca-2024-hatch-specs",
    locator="CHASSIS table, row 'Front and rear stabilizer bars (mm)', SPORT TOURING column",
    evidence="Front and rear stabilizer bars (mm) 26.5/17.5 26.5/17.5", as_printed="26.5/17.5",
    applicability=A24CA, confidence="high"))
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(17.5, "mm"), cls="A", source_id="susp:hondainfocenter-us-2024-hatch-specs",
    locator="Body/Suspension/Chassis table, row 'Stabilizer Bar (front/rear)', Sport Touring column (4th)",
    evidence="26.5 mm x 4.5 mm (tubular) / 17.5 mm (solid) Steering Wheel Turns", as_printed="17.5 mm (solid)",
    applicability=A24US, confidence="high",
    notes="This page prints 17.0 mm for LX/Sport/EX-L; hondanews.com 2024 prints 17.5 for all trims. For Sport Touring all sources agree."))
db.add_candidate(d, K, DSC, "m", "high", db.record(
    printed=(17.5, "mm"), cls="A", source_id="susp:hondanews-ca-2022-hatch-specs",
    locator="CHASSIS table, row 'Front and rear stabilizer bars', Sport Touring column",
    evidence="Front and rear stabilizer bars 26.5/17.5 26.5/17.5 26.5/17.5", as_printed="26.5/17.5",
    applicability=A22CA, confidence="high", notes="Model-year check 2022 vs 2024: unchanged."))

for k, desc, val in (("suspension.arb_front_construction", "Front anti-roll bar construction", "tubular"),
                     ("suspension.arb_rear_construction", "Rear anti-roll bar construction", "solid")):
    db.add_candidate(d, k, desc, "text", "medium", db.record(
        value=val, unit="text", cls="A", source_id="susp:hondanews-us-2024-hatch-specs",
        locator="CHASSIS table, row 'Stabilizer Bar (mm) (front/rear)'",
        evidence="Stabilizer Bar (mm) (front/rear) 26.5 x 4.5 (tubular) 17.5 (solid)", as_printed=val,
        applicability=A24US, confidence="high"))

# ------------------------------------------------------------------ type rows
for k, desc, val, ev, sid, loc, ap in (
    ("suspension.front_type", "Front suspension type", "MacPherson strut", "MacPherson Strut Front Suspension • • • •",
     "susp:hondanews-us-2024-hatch-specs", "CHASSIS table", A24US),
    ("suspension.rear_type", "Rear suspension type", "Multi-link (independent)", "Independent multi-link rear suspension • •",
     "susp:hondanews-ca-2024-hatch-specs", "CHASSIS table, SPORT TOURING column", A24CA)):
    db.add_candidate(d, k, desc, "text", "medium", db.record(
        value=val, unit="text", cls="A", source_id=sid, locator=loc, evidence=ev, as_printed=val,
        applicability=ap, confidence="high"))

# ------------------------------------------------------------------ springs (estimates)
SPR_SEARCH = ["Honda Canada / hondanews.com / hondainfocenter 2022-2024 hatch spec tables (no spring rates)",
              "WebSearch: '2022 Civic hatchback 1.5T OEM stock spring rate front rear kg/mm'",
              "WebSearch: 'FL1 Civic hatchback stock spring rates front rear Sport Touring EX-L'",
              "Eibach Pro-Kit listing onefastshop.com (progressive, no stock rate)",
              "Spoon Sports FL1 progressive spring blog (JDM stock rate F2.7/R2.8 kgf/mm)",
              "CivicXI 2023 Si spring-rate thread (Si: F27.0/R55.9 N/mm)"]
db.add_candidate(d, "suspension.spring_rate_front", "Front coil spring rate (at the spring)", "N/m", "high", db.record(
    value=26.5e3, unit="N/m", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[22.0e3, 32.0e3],
    how_to_measure="Remove a front spring and load-test it (or measure wire diameter d, mean coil diameter D and active coils n: k = G d^4 / (8 D^3 n), G = 79.3 GPa). Precision +/-3 %.",
    notes="Basis: two leads, neither for the target. Spoon Sports gives the JDM FL1 1.5T hatch 'normal rate' F 2.7 kgf/mm (26.5 N/mm); a CivicXI owner gives 27.0 N/mm for a 2023 Si sedan. The two agree, but the NA Sport Touring spring part number is not verified to match either.",
    searches=SPR_SEARCH))
db.add_candidate(d, "suspension.spring_rate_rear", "Rear coil spring rate (at the spring)", "N/m", "high", db.record(
    value=27.5e3, unit="N/m", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[24.0e3, 60.0e3],
    how_to_measure="Load-test a rear spring off the car, or measure d, D, n as for the front. Precision +/-3 %.",
    notes="Basis: Spoon Sports JDM FL1 'normal rate' R 2.8 kgf/mm (27.5 N/mm) vs CivicXI 2023 Si owner 55.9 N/mm (5.7 kgf/mm). The leads disagree by 2x (Si may simply be stiffer, or one figure is wrong); the range spans both. Value uses the hatch-body lead. Not averaged.",
    searches=SPR_SEARCH))

# motion ratios: convention spring travel / wheel travel; wheel rate = k_spring * MR^2
db.add_candidate(d, "suspension.motion_ratio_front", "Front spring motion ratio (spring travel / wheel travel); wheel rate = k * MR^2", "1", "high", db.record(
    value=0.97, unit="1", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[0.90, 1.00],
    how_to_measure="Jack one front wheel through +/-30 mm about ride height (spring removed or with a dial gauge on the strut) and record strut compression vs wheel-centre travel.",
    notes="Basis: MacPherson struts are near 1:1 (strut nearly vertical, lower mount close to the wheel centre). Lead: CivicXI 2023 Si owner measured wheel/spring 1.029 (= spring/wheel 0.972). The Si shares the front lower arm part family but not verified as identical."))
db.add_candidate(d, "suspension.motion_ratio_rear", "Rear spring motion ratio (spring travel / wheel travel); wheel rate = k * MR^2", "1", "high", db.record(
    value=0.75, unit="1", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[0.62, 0.85],
    how_to_measure="Measure spring-seat travel vs wheel-centre travel with the wheel jacked through +/-30 mm (or measure spring-seat and ball-joint distances from the lower arm B inner pivot).",
    notes="Basis: spring believed seated part-way along lower arm B (inboard of the wheel). Lead: CivicXI 2023 Si owner gives wheel/spring 1.333 (= 0.75). Rear lower arm B on the Si is a different part number (T22) from the 1.5T hatch (T20)."))
db.add_candidate(d, "suspension.motion_ratio_damper_front", "Front damper motion ratio (damper travel / wheel travel)", "1", "medium", db.record(
    value=0.97, unit="1", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[0.90, 1.00],
    how_to_measure="Same test as the front spring motion ratio (damper is concentric with the spring).",
    notes="Concentric coil-over strut: damper and spring ratios are equal."))
db.add_candidate(d, "suspension.motion_ratio_damper_rear", "Rear damper motion ratio (damper travel / wheel travel)", "1", "medium", db.record(
    value=0.85, unit="1", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[0.70, 1.00],
    how_to_measure="Measure damper length change vs wheel-centre travel (+/-30 mm) with the wheel jacked.",
    notes="Basis: separate rear damper believed mounted near the knuckle, so closer to 1 than the spring; layout not confirmed."))

# unsprung mass per corner
db.add_candidate(d, "suspension.unsprung_mass_corner_front", "Unsprung mass per front corner (wheel, tyre, brake, knuckle, hub + share of links/strut/driveshaft)", "kg", "high", db.record(
    value=50.0, unit="kg", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[40.0, 60.0],
    how_to_measure="Weigh wheel+tyre, rotor, caliper, knuckle/hub separately on a scale; add half of strut, lower arm, driveshaft and anti-roll link masses.",
    notes="Basis: 18x8 alloy + 235/40R18 (~20-24 kg combined), 282 mm vented rotor and caliper (~10 kg), knuckle/hub/bearing (~8-10 kg), plus half-masses of strut, arm and driveshaft. CivicXI Si owner estimated 55 kg. Wheels/tyres thread may later supply measured wheel and tyre masses."))
db.add_candidate(d, "suspension.unsprung_mass_corner_rear", "Unsprung mass per rear corner", "kg", "high", db.record(
    value=40.0, unit="kg", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
    applicability=TARGET, confidence="low", range=[32.0, 50.0],
    how_to_measure="Weigh wheel+tyre, rotor, caliper, trailing arm/knuckle and hub; add half of the four links, spring and damper.",
    notes="Basis: same wheel/tyre as front, 259 mm solid rotor, no driveshaft. CivicXI Si owner estimated 45 kg."))

# ARB lever geometry (needed for roll stiffness; unpublished)
for k, desc, v, rg, note in (
    ("suspension.arb_front_active_length", "Front anti-roll bar effective torsion length (between bushings)", 0.85, [0.70, 1.00],
     "Basis: body width 1.802 m, front track 1.536 m; a strut-car front bar typically spans most of the subframe width."),
    ("suspension.arb_front_lever_arm", "Front anti-roll bar lever arm length (bar axis to link)", 0.20, [0.15, 0.27],
     "Basis: typical strut-link bar arm; unmeasured."),
    ("suspension.arb_front_motion_ratio", "Front anti-roll bar link motion ratio (link travel / wheel travel)", 0.95, [0.85, 1.00],
     "Basis: link to the strut body near the wheel (inferred)."),
    ("suspension.arb_rear_active_length", "Rear anti-roll bar effective torsion length", 0.95, [0.80, 1.10],
     "Basis: rear track 1.565 m; bar mounted to the rear subframe."),
    ("suspension.arb_rear_lever_arm", "Rear anti-roll bar lever arm length", 0.18, [0.12, 0.25], "Basis: typical; unmeasured."),
    ("suspension.arb_rear_motion_ratio", "Rear anti-roll bar link motion ratio (link travel / wheel travel)", 0.75, [0.55, 0.95],
     "Basis: link believed to a lower arm or knuckle; layout not confirmed.")):
    db.add_candidate(d, k, desc, "1" if "ratio" in k else "m", "medium", db.record(
        value=v, unit="1" if "ratio" in k else "m", status="estimated", cls="E", source_id=None, locator="", evidence="",
        as_printed="", applicability=TARGET, confidence="low", range=rg,
        how_to_measure="Measure on the car (wheels on ramps or lift): bushing-to-bushing distance, arm length from bar axis to link eye, and link travel vs wheel travel.",
        notes=note))

# unknowns
UNK = [
    ("suspension.spring_free_length_front", "Front spring free length", "m", "low"),
    ("suspension.spring_free_length_rear", "Rear spring free length", "m", "low"),
    ("suspension.spring_wire_diameter_front", "Front spring wire diameter", "m", "low"),
    ("suspension.spring_wire_diameter_rear", "Rear spring wire diameter", "m", "low"),
    ("suspension.travel_bump_front", "Front wheel travel, ride height to bump-stop contact", "m", "high"),
    ("suspension.travel_rebound_front", "Front wheel travel, ride height to full droop", "m", "medium"),
    ("suspension.travel_bump_rear", "Rear wheel travel, ride height to bump-stop contact", "m", "high"),
    ("suspension.travel_rebound_rear", "Rear wheel travel, ride height to full droop", "m", "medium"),
    ("suspension.bump_stop_length_front", "Front bump stop free length / gap at ride height", "m", "medium"),
    ("suspension.bump_stop_length_rear", "Rear bump stop free length / gap at ride height", "m", "medium"),
    ("suspension.damper_curve_front", "Front damper force-velocity curve (bump and rebound)", "N", "high"),
    ("suspension.damper_curve_rear", "Rear damper force-velocity curve (bump and rebound)", "N", "high"),
    ("suspension.roll_center_height_front", "Front roll-centre height at ride height", "m", "high"),
    ("suspension.roll_center_height_rear", "Rear roll-centre height at ride height", "m", "high"),
]
HTM = {
    "spring": "Remove the spring and measure with calipers / tape; or read off the Honda parts label.",
    "travel": "With the spring removed (or using a lift and a dial gauge), move the wheel from ride height to bump-stop contact and to full droop; record wheel-centre travel. Or measure exposed damper shaft and bump-stop gap at ride height.",
    "bump_stop": "Remove the dust boot and measure the bump stop and the shaft gap at ride height.",
    "damper": "Dyno a stock damper (shock dyno, 0.025-1.0 m/s), or borrow published dyno sheets for Honda part numbers of the FL hatch struts/dampers.",
    "roll_center": "Requires hard points (front: lower-arm and strut geometry; rear: link geometry); measure pickup points and compute.",
}
for k, desc, u, imp in UNK:
    h = next(v for kk, v in HTM.items() if kk in k)
    db.add_candidate(d, k, desc, u, imp, db.unknown(
        u, searches=["Honda Canada/US spec tables 2022-2024 (not published)", "hondanews.com 2022 hatch debut press release (narrative only)",
                     "WebSearch: OEM spring rates FL1 hatch (no NA data)", "hondapartsnow parts listings (no dimensions beyond shipping size)",
                     "techinfo.honda.com service manual is paywalled (not accessed)"],
        how_to_measure=h, applicability=TARGET))

db.save(d, os.path.join(V, "suspension.json"))

# ================================================================== alignment
a = {"domain": "alignment", "title": "Alignment", "schema_version": 1, "updated": db.today(),
     "sources": {}, "parameters": {}}
ASEARCH = ["Honda Canada / hondanews.com / hondainfocenter 2022-2024 hatch spec tables (no alignment data)",
           "WebSearch: '2022 2023 Honda Civic hatchback factory alignment specifications camber caster toe service manual' (only 10th-gen CivicX thread found)",
           "WebSearch: 'civicxi forum alignment specs 11th gen front camber caster toe rear camber factory spec' (no 11th-gen spec chart)",
           "WebSearch: '2022 Honda Civic alignment printout specs ... 11th gen hatchback' (SPC spec book is a paid product; not accessed)",
           "techinfo.honda.com service manual (paywalled; not accessed); kbb.com alignment page (cost info only)"]
for k, desc, u, imp in (
    ("alignment.front_camber", "Front camber, nominal and tolerance", "rad", "high"),
    ("alignment.front_caster", "Front caster, nominal and tolerance", "rad", "high"),
    ("alignment.front_toe_total", "Front total toe, nominal and tolerance", "rad", "high"),
    ("alignment.rear_camber", "Rear camber, nominal and tolerance", "rad", "high"),
    ("alignment.rear_toe_total", "Rear total toe, nominal and tolerance", "rad", "high"),
    ("alignment.thrust_angle", "Thrust angle limit", "rad", "low"),
    ("alignment.kingpin_inclination", "Kingpin (steering-axis) inclination", "rad", "medium"),
    ("alignment.scrub_radius", "Scrub radius at ground", "m", "medium"),
):
    a["parameters"][k] = {"description": desc, "unit": u, "impact": imp, "candidates": [db.unknown(
        u, searches=ASEARCH,
        how_to_measure=("Get a four-wheel alignment printout (before/after) from a Honda dealer or an alignment shop: the printout "
                        "shows Honda's spec window (min/nominal/max) for 2022-2024 Civic Hatchback and the car's actual values. "
                        "KPI and scrub need a caster/KPI sweep on the alignment rig." if "kingpin" in k or "scrub" in k else
                        "Get a four-wheel alignment printout (before/after) from a Honda dealer or an alignment shop: it shows Honda's spec window (min/nominal/max) and the car's actual values."),
        applicability=TARGET,
        notes="Lead (not recorded as a value): the 10th-generation Civic spec quoted on civicx.com was front camber -0.8..+0.2 deg, caster 4.8..5.8 deg, rear camber -2.0..-0.5 deg, rear toe-in 0.04..0.16 deg (10th gen is excluded; 11th gen not verified).")]}
a["as_of"] = "2026-10-03"  # date the alignment searches were made (no dated sources: every record is unknown)
db.save(a, os.path.join(V, "alignment.json"))

# ================================================================== steering unknowns
s = db.load(os.path.join(V, "steering.json"))
STS = ["Honda Canada / hondanews.com / hondainfocenter 2022-2024 hatch spec tables",
       "hondanews.com 2022 hatch debut press release (only 'electronic power steering has been re-tuned')",
       "techinfo.honda.com (paywalled; not accessed)"]
db.add_candidate(s, "steering.ratio_center", "On-centre steering ratio of the variable-ratio rack", "1", "medium", db.unknown(
    "1", searches=STS, how_to_measure="With front wheels on turn plates, read road-wheel angle at handwheel +/-30 deg and +/-90 deg (or log steering-angle sensor via OBD and wheel angle); ratio = handwheel delta / road-wheel delta.",
    applicability=TARGET, notes="Honda publishes one ratio (11.41:1 US, 11.4:1 CA) for a variable-ratio rack; the on-centre value is expected to be slower (higher) than that."))
db.add_candidate(s, "steering.ratio_lock", "Near-lock steering ratio of the variable-ratio rack", "1", "medium", db.unknown(
    "1", searches=STS, how_to_measure="Turn plates: road-wheel angle per handwheel degree over the last 90 deg before lock.", applicability=TARGET))
db.add_candidate(s, "steering.wheel_diameter", "Steering wheel outside diameter", "m", "medium", db.unknown(
    "m", searches=STS + ["Owner's manual not opened for this item (no dimension expected)", "No dimensioned straight-on cabin photo identified; not photo-scaled"],
    how_to_measure="Tape across the rim at 3 and 9 o'clock (outside edges) and rim grip thickness with calipers; +/-2 mm.", applicability=TARGET))
db.add_candidate(s, "steering.assist_layout", "EPS assist motor layout (column, pinion, dual-pinion or rack-concentric)", "text", "low", db.unknown(
    "text", searches=STS, how_to_measure="Underside/engine-bay photo of the steering rack (a second pinion housing with motor = dual-pinion).",
    applicability=TARGET, notes="Earlier Civics used dual-pinion EPS; not confirmed for this car."))
db.save(s, os.path.join(V, "steering.json"))
print("saved suspension.json, alignment.json, steering.json")
