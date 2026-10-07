"""Builds vehicle_data/dimensions.json from cached, opened Honda pages.
Every evidence string is asserted to exist (whitespace-normalised) in the cached page text."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\t", " ")).strip()

SRC = {}
def src(sid, title, url, cache, applic, notes="", publisher="Honda Canada Inc. (hondanews.ca newsroom)", method="static"):
    SRC[sid] = norm(open(os.path.join(ROOT, cache), encoding="utf-8").read())
    db.add_source(d, sid, title=title, url=url, publisher=publisher, cls="A", access_method=method,
                  applicability=applic, notes=notes, cache_file=cache)

def ev(sid, *frags):
    for f in frags:
        assert norm(f) in SRC[sid], (sid, f)
    return " … ".join(norm(f) for f in frags)

d = db.load_or_new("dimensions", "Dimensions")
d["parameters"] = {}
d["sources"] = {}

CA24 = "dim:hondanews-ca-2024-hatch-specs"
CA23 = "dim:hondanews-ca-2023-hatch-specs"
CA22 = "dim:hondanews-ca-2022-hatch-specs"
US24 = "dim:hondanews-us-2024-hatch-specs"
US22 = "dim:hondanews-us-2022-hatch-specs"
IC24 = "dim:hondainfocenter-us-2024-hatch-specs"
IC24S = "dim:hondainfocenter-us-2024-sedan-specs"

src(CA24, "2024 Honda Civic Hatchback Specifications (release, April 4, 2024)",
    "https://hondanews.ca/en-CA/hci-automobiles/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
    "cache/pages/41e62125b9f268de.txt", "2024 Canada Civic Hatchback, columns SPORT and SPORT TOURING (1.5T, MT/CVT)",
    notes="Same table is also distributed by dealers as a PDF (di-uploads-pod2.dealerinspire.com/harmonyhonda/.../2024-Honda-Civic-Hatchback-Specifications.pdf, page 3); not an independent source.")
src(CA23, "2023 Civic Hatchback Specifications (release, April 13, 2023)",
    "https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
    "cache/pages/374416cf6bc6db5d.txt", "2023 Canada Civic Hatchback, columns LX, Sport, Sport-B, Sport Touring")
src(CA22, "2022 Civic Hatchback Specifications (release, October 12, 2021)",
    "https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
    "cache/pages/344bc90bb36560a9.txt", "2022 Canada Civic Hatchback, columns LX, Sport, Sport Touring")
src(US24, "2024 Honda Civic Hatchback Specifications & Features (release, August 9, 2023)",
    "https://hondanews.com/en-US/honda-automobiles/releases/release-5003aaa39c009393f5d06d620f0fc923-2024-honda-civic-hatchback-specifications-features",
    "cache/pages/dd2e2052fcb1a220.txt", "2024 US Civic Hatchback, columns LX, Sport, EX-L, Sport Touring ('<<' = same as left column)",
    publisher="American Honda Motor Co. (hondanews.com)")
src(US22, "2022 Honda Civic Hatchback Specifications & Features",
    "https://hondanews.com/en-US/honda-automobiles/releases/release-cb177600e922c8a5fcfa01b9b80149e2-2022-honda-civic-hatchback-specifications-features",
    "cache/pages/fb1d5790fd3bfda8.txt", "2022 US Civic Hatchback, columns LX, Sport, EX-L, Sport Touring",
    publisher="American Honda Motor Co. (hondanews.com)")
src(IC24, "2024 Civic Hatchback - Civic Hatchback Specifications (Honda Information Center)",
    "https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Civic-Hatchback-Specifications/",
    "cache/pages/b67f7f855816944e.txt", "2024 US Civic Hatchback, columns LX, Sport, EX-L, Sport Touring",
    publisher="American Honda Motor Co. (Honda Information Center)",
    notes="HTML <title> reads '2023 Honda Civic Hatchback' while the page heading reads '2024 Civic Hatchback'. Its Length (184.0 in) equals the Civic Sedan figure on the same site and disagrees with hondanews.com and Honda Canada; treated as a transcription error.")
src(IC24S, "2024 Civic Sedan - Civic Sedan Specifications (Honda Information Center)",
    "https://www.hondainfocenter.com/2024/Civic-Sedan/Feature-Guide/Civic-Sedan-Specifications/",
    "cache/pages/67adc76510e3bc91.txt", "2024 US Civic SEDAN (excluded body; used only to explain the 184.0 in hatchback length anomaly)",
    publisher="American Honda Motor Co. (Honda Information Center)")

CA_ST24 = db.app("2024", "CA", "Sport Touring (table also covers Sport)", "6MT and CVT", notes="Honda Canada 2024 table; trim columns identical for these rows")
CA_ST23 = db.app("2023", "CA", "Sport Touring (all hatch trims identical for this row)", "6MT and CVT",
                 notes="Same body/engine/gearbox as 2024; model-year check: every row also printed in the 2024 Canadian table (length w/o bracket, height, wheelbase, track, ground clearance) is identical, so 2023 values are taken as applicable")
CA_ST22 = db.app("2022", "CA", "Sport Touring (all hatch trims identical for this row)", "6MT and CVT",
                 notes="Launch year of same body; values identical to 2023 and to the rows repeated in 2024")
US_ST24 = db.app("2024", "US", "Sport Touring", "6MT and CVT", notes="US market; Canadian figure is selected where both exist")
US_ST22 = db.app("2022", "US", "Sport Touring", "6MT and CVT", notes="US market, launch year")

def add(key, desc, unit, impact, **kw):
    db.add_candidate(d, key, desc, unit, impact, db.record(**kw))

# ---- length
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(4529, "mm"), cls="A", source_id=CA24, locator="DIMENSIONS table, row 'Length (mm)', SPORT TOURING column",
    evidence=ev(CA24, "DIMENSIONS SPORT SPORT TOURING", "Length (mm) 4529 4529"), as_printed="4529",
    applicability=CA_ST24, confidence="high", prefer=True,
    selection_reason="Canadian 2024 figure; the 2022/2023 Canadian tables identify 4529 mm as the length without the front licence bracket, i.e. the body itself. US 179.0 in (4546.6 mm) equals the with-bracket figure 4547 mm.",
    notes="2024 table does not say whether the bracket is included; 2022/2023 tables print 4547/4529 with/without bracket, so 4529 = without.")
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(4529, "mm"), cls="A", source_id=CA23, locator="DIMENSIONS table, row 'Length (mm) - With licence bracket/without licence bracket', Sport Touring column",
    evidence=ev(CA23, "Length (mm) - With licence bracket/without licence bracket 4547/4529 4547/4529 4547/4529 4547/4529"),
    as_printed="4547/4529 (value after slash = without licence bracket)", applicability=CA_ST23, confidence="high")
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(179.0, "in"), cls="A", source_id=US24, locator="DIMENSIONS / EXTERIOR, row 'Length (in.)' (all trims, '<<')",
    evidence=ev(US24, "Length (in.)", "179.0"), as_printed="179.0", applicability=US_ST24, confidence="medium",
    notes="179.0 in = 4546.6 mm, matching Honda Canada's WITH-licence-bracket length 4547 mm (US cars carry a front plate bracket in most states). Not a disagreement about the body; kept as a candidate for the with-bracket length.")
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(184.0, "in"), cls="A", source_id=IC24, locator="Exterior Measurements, row 'Length', Sport Touring column",
    evidence=ev(IC24, "Exterior Measurements LX Sport EX-L Sport Touring", "Length 184.0 in 184.0 in 184.0 in 184.0 in"),
    as_printed="184.0 in", applicability=US_ST24, confidence="low",
    notes="REJECTED: 184.0 in (4673.6 mm) is the 2024 Civic SEDAN length on the same site (dim:hondainfocenter-us-2024-sedan-specs, 'Length 184.0 in') and contradicts hondanews.com 2024 hatchback (179.0 in) and Honda Canada (4547/4529 mm). Kept as a losing candidate; see CONFLICTS.")
add("dimensions.length_with_licence_bracket", "Overall length including front licence-plate bracket", "m", "medium",
    printed=(4547, "mm"), cls="A", source_id=CA23, locator="DIMENSIONS table, row 'Length (mm) - With licence bracket/without licence bracket'",
    evidence=ev(CA23, "Length (mm) - With licence bracket/without licence bracket 4547/4529 4547/4529 4547/4529 4547/4529"),
    as_printed="4547/4529 (value before slash = with licence bracket)", applicability=CA_ST23, confidence="high", prefer=True,
    selection_reason="Canadian figure; 2024 Canadian table omits the with-bracket value.")
add("dimensions.length_with_licence_bracket", "Overall length including front licence-plate bracket", "m", "medium",
    printed=(4547, "mm"), cls="A", source_id=CA22, locator="DIMENSIONS table, row 'Length (mm) - With licence bracket/without licence bracket'",
    evidence=ev(CA22, "Length (mm) - With licence bracket/without licence bracket 4547/4529 4547/4529 4547/4529"),
    as_printed="4547/4529", applicability=CA_ST22, confidence="high")

# ---- width
add("dimensions.width_body", "Overall width without mirrors", "m", "high",
    printed=(1802, "mm"), cls="A", source_id=CA24, locator="DIMENSIONS table, row 'Width (mm)', SPORT TOURING column",
    evidence=ev(CA24, "Width (mm) 1802 1802"), as_printed="1802", applicability=CA_ST24, confidence="high",
    notes="Taken as body width without mirrors: 2022/2023 Canadian tables give 2081 mm mirrors open and 1900 mm mirrors folded, both larger, and the US 70.9 in (1800.9 mm) agrees.")
add("dimensions.width_body", "Overall width without mirrors", "m", "high",
    printed=(70.9, "in"), cls="A", source_id=US24, locator="DIMENSIONS / EXTERIOR, row 'Width (in.)' (all trims)",
    evidence=ev(US24, "Width (in.)", "70.9"), as_printed="70.9", applicability=US_ST24, confidence="high",
    notes="1800.9 mm; agrees with 1802 mm within the 0.05 in rounding of the printed figure.")
add("dimensions.width_mirrors", "Overall width with mirrors open", "m", "high",
    printed=(2081, "mm"), cls="A", source_id=CA23, locator="DIMENSIONS table, row 'Width (mm) – Mirrors open/Mirrors folded', Sport Touring column",
    evidence=ev(CA23, "Width (mm) – Mirrors open/Mirrors folded 2081/1900 2081/1900 2081/1900 2081/1900"),
    as_printed="2081/1900 (mirrors open)", applicability=CA_ST23, confidence="medium", prefer=True,
    selection_reason="Only manufacturer figure for 2023; the 2024 Canadian table omits it.",
    notes="Not printed for 2024. Mirrors are not listed as changed for 2024 (2024 table repeats all other exterior rows unchanged). Cross-checked by photo in proportions.json (proportions.mirror_width_ratio).")
add("dimensions.width_mirrors", "Overall width with mirrors open", "m", "high",
    printed=(2081, "mm"), cls="A", source_id=CA22, locator="DIMENSIONS table, row 'Width (mm) – Mirrors open/Mirrors folded'",
    evidence=ev(CA22, "Width (mm) – Mirrors open/Mirrors folded 2081/1900 2081/1900 2081/1900"),
    as_printed="2081/1900", applicability=CA_ST22, confidence="medium")
add("dimensions.width_mirrors_folded", "Overall width with mirrors folded", "m", "low",
    printed=(1900, "mm"), cls="A", source_id=CA23, locator="DIMENSIONS table, row 'Width (mm) – Mirrors open/Mirrors folded'",
    evidence=ev(CA23, "Width (mm) – Mirrors open/Mirrors folded 2081/1900 2081/1900 2081/1900 2081/1900"),
    as_printed="2081/1900 (mirrors folded)", applicability=CA_ST23, confidence="medium")

# ---- height
add("dimensions.height", "Overall height (unladen)", "m", "high",
    printed=(1415, "mm"), cls="A", source_id=CA24, locator="DIMENSIONS table, row 'Height (mm)'",
    evidence=ev(CA24, "Height (mm) 1415 1415"), as_printed="1415", applicability=CA_ST24, confidence="high")
add("dimensions.height", "Overall height (unladen)", "m", "high",
    printed=(55.7, "in"), cls="A", source_id=US24, locator="DIMENSIONS / EXTERIOR, row 'Height (in.)' (all trims)",
    evidence=ev(US24, "Height (in.)", "55.7"), as_printed="55.7", applicability=US_ST24, confidence="high",
    notes="1414.8 mm; agrees.")

# ---- wheelbase
add("dimensions.wheelbase", "Wheelbase", "m", "critical",
    printed=(2735, "mm"), cls="A", source_id=CA24, locator="DIMENSIONS table, row 'Wheelbase (mm)'",
    evidence=ev(CA24, "Wheelbase (mm) 2735 2735"), as_printed="2735", applicability=CA_ST24, confidence="high")
add("dimensions.wheelbase", "Wheelbase", "m", "critical",
    printed=(107.7, "in"), cls="A", source_id=US24, locator="DIMENSIONS / EXTERIOR, row 'Wheelbase (in.)' (all trims)",
    evidence=ev(US24, "Wheelbase (in.)", "107.7"), as_printed="107.7", applicability=US_ST24, confidence="high",
    notes="2735.6 mm; agrees.")
add("dimensions.wheelbase", "Wheelbase", "m", "critical",
    printed=(107.7, "in"), cls="A", source_id=IC24, locator="Exterior Measurements, row 'Wheelbase'",
    evidence=ev(IC24, "Wheelbase 107.7 in 107.7 in 107.7 in 107.7 in"), as_printed="107.7 in", applicability=US_ST24, confidence="high")

# ---- track
for key, desc, ca, us, ustxt in (("dimensions.track_front", "Front track (18-in wheels)", 1536, 60.5, "60.5"),
                                 ("dimensions.track_rear", "Rear track (18-in wheels)", 1565, 61.6, "61.6")):
    add(key, desc, "m", "high", printed=(ca, "mm"), cls="A", source_id=CA24,
        locator="DIMENSIONS table, row 'Track – front/rear (mm)', SPORT TOURING column",
        evidence=ev(CA24, "Track – front/rear (mm) 1536/1565 1536/1565"), as_printed="1536/1565",
        applicability=CA_ST24, confidence="high",
        notes="Track depends on wheel: 2022/2023 Canadian LX (16/17-in) prints 1546/1575; Sport and Sport Touring (18-in, 235/40R18) 1536/1565.")
    add(key, desc, "m", "high", printed=(ca, "mm"), cls="A", source_id=CA23,
        locator="DIMENSIONS table, row 'Track (mm) – front/rear', Sport Touring column",
        evidence=ev(CA23, "Track (mm) – front/rear 1546/1575 1536/1565 1536/1565 1536/1565"), as_printed="1536/1565",
        applicability=CA_ST23, confidence="high")
    add(key, desc, "m", "high", printed=(us, "in"), cls="A", source_id=US24,
        locator="DIMENSIONS / EXTERIOR, row 'Track (in.) (front/rear)', 4th column = Sport Touring",
        evidence=ev(US24, "Track (in.) (front/rear) 60.9 / 62.0 60.5 / 61.6 60.9 / 62.0 60.5 / 61.6"),
        as_printed="60.5 / 61.6", applicability=US_ST24, confidence="high",
        notes="Column order LX, Sport, EX-L, Sport Touring; 18-in trims 60.5/61.6 in.")

# ---- Phase 2 Step 2: every other Honda source opened for the six headline dimensions is kept as a candidate
# (re-opened live 2026-10-07 by scripts/phase2/confirm_headline_dims.py; quotes verified against the cached pages)
IC_APP = db.app("2024", "US", "Sport Touring", "6MT and CVT",
                notes="Honda Information Center 2024 hatchback page. Its Length row (184.0 in) is the sedan figure, so every row "
                      "on this page is treated with caution; these rows agree with hondanews.com and Honda Canada.")
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(4529, "mm"), cls="A", source_id=CA22, locator="DIMENSIONS table, row 'Length (mm) - With licence bracket/without licence bracket', Sport Touring column",
    evidence=ev(CA22, "Length (mm) - With licence bracket/without licence bracket 4547/4529 4547/4529 4547/4529"),
    as_printed="4547/4529 (value after slash = without licence bracket)", applicability=CA_ST22, confidence="high")
add("dimensions.length", "Overall length (body, without front licence-plate bracket)", "m", "high",
    printed=(179.0, "in"), cls="A", source_id=US22, locator="Specifications, row 'Length', Sport Touring column",
    evidence=ev(US22, "Length 179.0 in 179.0 in 179.0 in 179.0 in"), as_printed="179.0 in", applicability=US_ST22, confidence="medium",
    notes="4546.6 mm = Honda Canada's with-licence-bracket length (4547 mm), as for the 2024 US figure.")
for sid, app_, txt in ((US22, US_ST22, "Width 70.9 in 70.9 in 70.9 in 70.9 in"), (IC24, IC_APP, "Width 70.9 in 70.9 in 70.9 in 70.9 in")):
    add("dimensions.width_body", "Overall width without mirrors", "m", "high", printed=(70.9, "in"), cls="A", source_id=sid,
        locator="Specifications, row 'Width', Sport Touring column", evidence=ev(sid, txt), as_printed="70.9 in",
        applicability=app_, confidence="high", notes="1800.9 mm; agrees with Honda Canada 1802 mm within print rounding.")
for sid, app_, txt, pr in ((CA23, CA_ST23, "Height (mm) 1415 1415 1415 1415", (1415, "mm")),
                           (CA22, CA_ST22, "Height (mm) 1415 1415 1415", (1415, "mm")),
                           (US22, US_ST22, "Height 55.7 in 55.7 in 55.7 in 55.7 in", (55.7, "in")),
                           (IC24, IC_APP, "Height 55.7 in 55.7 in 55.7 in 55.7 in", (55.7, "in"))):
    add("dimensions.height", "Overall height (unladen)", "m", "high", printed=pr, cls="A", source_id=sid,
        locator="DIMENSIONS / Specifications, row 'Height', Sport Touring column", evidence=ev(sid, txt),
        as_printed=f"{pr[0]} {pr[1]}", applicability=app_, confidence="high")
for sid, app_, txt, pr in ((CA23, CA_ST23, "Wheelbase (mm) 2735 2735 2735 2735", (2735, "mm")),
                           (CA22, CA_ST22, "Wheelbase (mm) 2735 2735 2735", (2735, "mm")),
                           (US22, US_ST22, "Wheelbase 107.7 in 107.7 in 107.7 in 107.7 in", (107.7, "in"))):
    add("dimensions.wheelbase", "Wheelbase", "m", "critical", printed=pr, cls="A", source_id=sid,
        locator="DIMENSIONS / Specifications, row 'Wheelbase', Sport Touring column", evidence=ev(sid, txt),
        as_printed=f"{pr[0]} {pr[1]}", applicability=app_, confidence="high")
for key, desc, ca, us in (("dimensions.track_front", "Front track (18-in wheels)", 1536, 60.5),
                          ("dimensions.track_rear", "Rear track (18-in wheels)", 1565, 61.6)):
    add(key, desc, "m", "high", printed=(ca, "mm"), cls="A", source_id=CA22,
        locator="DIMENSIONS table, row 'Track (mm) – front/rear', Sport Touring column (3rd)",
        evidence=ev(CA22, "Track (mm) – front/rear 1546/1575 1536/1565 1536/1565"), as_printed="1536/1565",
        applicability=CA_ST22, confidence="high")
    for sid, app_ in ((US22, US_ST22), (IC24, IC_APP)):
        add(key, desc, "m", "high", printed=(us, "in"), cls="A", source_id=sid,
            locator="Specifications, row 'Track (front/rear)', 4th column = Sport Touring",
            evidence=ev(sid, "Track (front/rear) 60.9 in / 62.0 in 60.5 in / 61.6 in 60.9 in / 62.0 in 60.5 in / 61.6 in"),
            as_printed="60.5 in / 61.6 in", applicability=app_, confidence="high",
            notes="Column order LX, Sport, EX-L, Sport Touring; 18-in trims 60.5/61.6 in.")

# ---- ground clearance
add("dimensions.ground_clearance", "Minimum ground clearance, no load", "m", "medium",
    printed=(134, "mm"), cls="A", source_id=CA24, locator="DIMENSIONS table, row 'Ground clearance – no-load (mm)'",
    evidence=ev(CA24, "Ground clearance – no-load (mm) 134 134"), as_printed="134", applicability=CA_ST24, confidence="medium",
    notes="Single manufacturer source (US tables do not print ground clearance). Point of measurement not stated; photo rocker height in proportions.json is a different quantity.")
add("dimensions.ground_clearance", "Minimum ground clearance, no load", "m", "medium",
    printed=(134, "mm"), cls="A", source_id=CA22, locator="DIMENSIONS table, row 'Ground clearance (mm) – no-load'",
    evidence=ev(CA22, "Ground clearance (mm) – no-load 134 134 134"), as_printed="134", applicability=CA_ST22, confidence="medium")

# ---- overhangs / angles: unpublished
SEARCH_OH = ["Honda Canada 2022/2023/2024 hatchback spec releases (hondanews.ca): no overhang rows",
             "hondanews.com 2022/2023/2024 hatchback specifications & features: no overhang rows",
             "hondainfocenter.com 2024 hatchback specifications: no overhang rows",
             "WebSearch '2022 Honda Civic Hatchback front overhang rear overhang mm dimensions' (only non-NA spec sites; none print overhangs)",
             "Owner's manual: honda.ca manuals selector did not render a document list headlessly; its API needs a private consumerId header (not worked around)",
             "NHTSA crash-test database (nrd.nhtsa.dot.gov) blocked by egress proxy (502)"]
for key, desc in (("dimensions.approach_angle", "Approach angle"), ("dimensions.departure_angle", "Departure angle")):
    db.add_candidate(d, key, desc, "rad", "low", db.unknown("rad", SEARCH_OH,
        how_to_measure="Car at curb weight on level floor: measure bumper lower-edge height and its horizontal distance ahead of/behind the tyre contact patch; angle = atan(h / x)."))

# ---- interior / cargo (cockpit modelling)
def interior(key, desc, ca_row, ca_vals, idx, us_row, us_val, impact="medium"):
    v = int(ca_vals.split("/")[idx])
    add(key, desc, "m", impact, printed=(v, "mm"), cls="A", source_id=CA24, locator=f"DIMENSIONS table, row '{ca_row}'",
        evidence=ev(CA24, f"{ca_row} {ca_vals} {ca_vals}"), as_printed=ca_vals, applicability=CA_ST24, confidence="high",
        notes="SAE interior dimension (SAE J1100 style); useful for cockpit modelling, not a direct coordinate.")
    if us_val is not None:
        add(key, desc, "m", impact, printed=(float(us_val), "in"), cls="A", source_id=US24, locator=f"INTERIOR, row '{us_row}'",
            evidence=ev(US24, us_row), as_printed=us_val, applicability=US_ST24, confidence="medium",
            notes="Sport Touring column (EX-L/Sport Touring share the moonroof headroom figure).")

interior("dimensions.headroom_front", "Front headroom (with moonroof)", "Headroom – front/rear (mm)", "956/942", 0, "Headroom (in.) (front/rear)", "37.6")
interior("dimensions.headroom_rear", "Rear headroom", "Headroom – front/rear (mm)", "956/942", 1, "Headroom (in.) (front/rear)", "37.1")
interior("dimensions.legroom_front", "Front legroom", "Legroom – front/rear (mm)", "1074/950", 0, "Legroom (in.) (front/rear)", "42.3")
interior("dimensions.legroom_rear", "Rear legroom", "Legroom – front/rear (mm)", "1074/950", 1, "Legroom (in.) (front/rear)", "37.4")
interior("dimensions.shoulder_room_front", "Front shoulder room", "Shoulder room – front/rear (mm)", "1447/1422", 0, "Shoulder Room (in.) (front/rear)", "57.0")
interior("dimensions.shoulder_room_rear", "Rear shoulder room", "Shoulder room – front/rear (mm)", "1447/1422", 1, "Shoulder Room (in.) (front/rear)", "56.0")
interior("dimensions.hip_room_front", "Front hip room", "Hip room – front/rear (mm)", "1380/1243", 0, "Hiproom (in.) (front/rear)", "54.3")
interior("dimensions.hip_room_rear", "Rear hip room", "Hip room – front/rear (mm)", "1380/1243", 1, "Hiproom (in.) (front/rear)", "48.9")
add("dimensions.cargo_volume", "Cargo volume, rear seat up", "m3", "low", printed=(693, "L"), cls="A", source_id=CA24,
    locator="DIMENSIONS table, row 'Cargo volume (L)'", evidence=ev(CA24, "Cargo volume (L) 693 693"), as_printed="693",
    applicability=CA_ST24, confidence="high")
add("dimensions.cargo_volume", "Cargo volume, rear seat up", "m3", "low", printed=(24.5, "ft3"), cls="A", source_id=US24,
    locator="INTERIOR, row 'Cargo Volume (in.) (rear seat up)'", evidence=ev(US24, "Cargo Volume (in.) (rear seat up)5 24.5"),
    as_printed="24.5 (printed unit label 'in.' is a Honda typo for cu ft; footnote 5 cites SAE J1100)", applicability=US_ST24, confidence="medium")
add("dimensions.passenger_volume", "Passenger volume (with moonroof)", "m3", "low", printed=(2735, "L"), cls="A", source_id=CA24,
    locator="DIMENSIONS table, row 'Passenger volume (L)'", evidence=ev(CA24, "Passenger volume (L) 2735 2735"), as_printed="2735",
    applicability=CA_ST24, confidence="high")

p = db.save(d)
print(p)
