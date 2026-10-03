#!/usr/bin/env python3
"""Domain 4 builder: writes vehicle_data/engine.json, vehicle_data/turbo.json and the
engine_curves/*.json stock-dyno run files from sources opened in this session.
Every class A-C evidence fragment is checked (whitespace-normalized) against the cached
page text before saving, so a quote that is not on the page aborts the build.
Run: python3 scripts/domains/engine_db.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import dbutil as db  # noqa: E402

ROOT = db.ROOT
ACC = "2026-10-03"

SRC = {
 "eng:hondanews-ca-2024-hatch-specs": dict(
    title="2024 Honda Civic Hatchback Specifications (Honda Canada newsroom, April 4, 2024)",
    url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
    publisher="Honda Canada Inc.", cls="A", access_method="rendered",
    applicability="2024 Civic Hatchback Sport and Sport Touring, Canada; 6MT available on Sport Touring",
    cache_file="cache/pages/41e62125b9f268de.txt"),
 "eng:hondanews-ca-2023-hatch-specs": dict(
    title="2023 Civic Hatchback Specifications (Honda Canada newsroom)",
    url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
    publisher="Honda Canada Inc.", cls="A", access_method="rendered",
    applicability="2023 Civic Hatchback LX/Sport/Sport-B/Sport Touring, Canada", cache_file="cache/pages/374416cf6bc6db5d.txt"),
 "eng:hondanews-ca-2022-hatch-specs": dict(
    title="2022 Civic Hatchback Specifications (Honda Canada newsroom)",
    url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
    publisher="Honda Canada Inc.", cls="A", access_method="rendered",
    applicability="2022 Civic Hatchback LX/Sport/Sport Touring, Canada", cache_file="cache/pages/344bc90bb36560a9.txt"),
 "eng:hic-us-2024-hatch-specs": dict(
    title="2024 Civic Hatchback Specifications - Honda Info Center",
    url="https://www.hondainfocenter.com/2024/civic-hatchback/feature-guide/civic-hatchback-specifications/",
    publisher="American Honda Motor Co., Inc.", cls="A", access_method="static",
    applicability="2024 Civic Hatchback LX/Sport/EX-L/Sport Touring, USA (Engineering table; Sport Touring column)",
    notes="Page footer: 'All information contained herein applies to U.S. vehicles only.' Engineering table columns LX | Sport | EX-L | Sport Touring; parsed with BeautifulSoup from the cached HTML.",
    cache_file="cache/pages/b2916d402fafb825.txt"),
 "eng:hic-us-2022-hatch-specs": dict(
    title="2022 Civic Hatchback Specifications - Honda Info Center",
    url="https://www.hondainfocenter.com/2022/civic-hatchback/feature-guide/civic-hatchback-specifications/",
    publisher="American Honda Motor Co., Inc.", cls="A", access_method="static",
    applicability="2022 Civic Hatchback, USA", cache_file="cache/pages/304f563463881e56.txt"),
 "eng:hic-us-2024-turbo-feature": dict(
    title="Turbocharged 1.5-liter Engine (EX-L and Sport Touring) - 2024 Civic Hatchback feature guide",
    url="https://www.hondainfocenter.com/2024/civic-hatchback/feature-guide/engine-chassis-features/turbocharged-1-5-liter-engine/",
    publisher="American Honda Motor Co., Inc.", cls="A", access_method="static",
    applicability="2024 Civic Hatchback EX-L and Sport Touring, USA", cache_file="cache/pages/9b044a27ab7f7a52.txt"),
 "eng:hondanews-us-15t-engine-2024": dict(
    title="Honda 1.5-Liter Turbo Engine (hondanews.com technical release, May 16, 2024)",
    url="https://hondanews.com/en-US/releases/release-40b876fa88ce36bf41449f6e441f9b95-honda-15-liter-turbo-engine",
    publisher="American Honda Motor Co., Inc. (Honda News)", cls="A", access_method="static",
    applicability="All US 1.5T applications; specific section and applications table for Civic Hatchback 2022-2024 EX-L, Sport Touring (L15B7 w/VTEC)",
    cache_file="cache/pages/799735a051baae71.txt"),
 "eng:thedrive-hondata-2022-ex": dict(
    title="2022 Honda Civic Gains an Impressive 34 HP From a Simple ECU Tune (The Drive, reporting Hondata dyno)",
    url="https://www.thedrive.com/news/41686/2022-honda-civic-gains-an-impressive-34-hp-from-a-simple-ecu-tune",
    publisher="The Drive (data: Hondata)", cls="C", access_method="static",
    applicability="2022 Civic Sedan EX (US EX sedan is CVT-only), stock, Hondata dyno; dyno type/correction/gear not stated in the article",
    notes="Hondata's own page (hondata.com) is disallowed to ClaudeBot by robots.txt and was not fetched.",
    cache_file="cache/pages/15bf21fbac0943ac.txt"),
 "eng:prl-civicxi-intake-baseline-2021": dict(
    title="PRL Motorsports 1.5T Civic Stage 1 Intake Development, post #3 (civicxi.com)",
    url="https://www.civicxi.com/forum/threads/prl-motorsports-1-5t-civic-stage-1-intake-development.49861/post-811911",
    publisher="PRL Motorsports (sponsor post on CivicXI forum)", cls="C", access_method="static",
    applicability="2022 Civic Touring sedan 1.5T CVT, stock; DynoJet 224X, 4th (CVT mode) gear 70-90 mph, 95 F, 1000 ft",
    cache_file="cache/pages/060fc065a7a61b16.txt"),
 "eng:prl-frontpipe-2021": dict(
    title="11th Gen Civic 1.5T Front Pipe Upgrade Dyno Testing (PRL Motorsports blog, Nov 17, 2021)",
    url="https://prlmotorsports.com/blogs/news/11th-gen-civic-1-5t-front-pipe-upgrade-dyno-testing",
    publisher="PRL Motorsports", cls="C", access_method="static",
    applicability="PRL's 11th-gen 1.5T development car (a 2022 Civic Touring sedan CVT per PRL's CivicXI thread), stock baseline; 59 F, 1160 ft",
    cache_file="cache/pages/39835d22ed7eaa96.txt"),
 "eng:tsp-stage1-non-si": dict(
    title="TSP Stage 1 Tune for 2022+ Honda Civic 1.5T Non-Si (Two Step Performance product page)",
    url="https://www.twostepperformance.com/products/tsp-stage-1-tune-for-2022-honda-civic-1-5t-non-si",
    publisher="Two Step Performance", cls="C", access_method="static",
    applicability="Unmodified 2022 non-Si Civic 1.5T CVT (body not stated), factory calibration",
    cache_file="cache/pages/004eb1d37a3e1be8.txt"),
}

def norm(s):
    return " ".join(s.split())

_cache = {}
def verify(sid, evidence):
    cf = SRC[sid]["cache_file"]
    if cf not in _cache:
        _cache[cf] = norm(open(os.path.join(ROOT, cf), encoding="utf-8").read())
    for frag in evidence.split(" … "):
        if norm(frag) not in _cache[cf]:
            raise SystemExit(f"EVIDENCE NOT FOUND in {cf} ({sid}): {frag!r}")

CA24 = db.app("2024", "CA", "Sport, Sport Touring", "6MT or CVT (engine ratings not split by gearbox)")
CA23 = db.app("2023", "CA", "Sport, Sport-B, Sport Touring", "6MT or CVT (not split)")
CA22 = db.app("2022", "CA", "Sport, Sport Touring", "6MT or CVT (not split)")
US24 = db.app("2024", "US", "EX-L, Sport Touring", "6MT or CVT (not split)")
US22 = db.app("2022", "US", "EX-L, Sport Touring", "6MT or CVT (not split)")
US15 = db.app("2022-2024", "US", "Civic Hatchback EX-L, Sport Touring", "not split",
              notes="Honda 1.5T technical release; Civic Sedan EX/Touring share the same code and ratings per the same table")
MYNOTE = "Model-year check: Honda Canada 2022, 2023 and 2024 hatchback spec sheets list identical engine figures."


def rec(sid, **kw):
    if kw.get("cls", "A") in ("A", "B", "C"):
        verify(sid, kw["evidence"])
    return db.record(source_id=sid, **kw)


def build():
    e = db.load_or_new("engine", "Engine")
    e["sources"], e["parameters"] = {}, {}
    t = db.load_or_new("turbo", "Turbocharger and boost")
    t["sources"], t["parameters"] = {}, {}
    for sid, s in SRC.items():
        s = dict(s); cls = s.pop("cls")
        db.add_source(e, sid, cls=cls, accessed=ACC, **s)
    for sid in ("eng:hondanews-us-15t-engine-2024", "eng:hic-us-2024-hatch-specs",
                "eng:hic-us-2022-hatch-specs", "eng:hic-us-2024-turbo-feature"):
        s = dict(SRC[sid]); cls = s.pop("cls")
        db.add_source(t, sid, cls=cls, accessed=ACC, **s)
    A = lambda k, d, u, imp, r: db.add_candidate(e, k, d, u, imp, r)
    T = lambda k, d, u, imp, r: db.add_candidate(t, k, d, u, imp, r)

    # ---------------- identity of the engine
    A("engine.code", "Honda engine code", "text", "medium", rec(
        "eng:hondanews-us-15t-engine-2024", value="L15B7 (w/VTEC)", unit="text", cls="A",
        locator="Section '11th-Generation Civic (2022-present)' and 'Honda 1.5-Liter Turbo Applications' table",
        evidence="From 2022 to 2024, the 11th generation Civic Sedan EX and Touring grades, as well as the Civic Hatchback EX-L and Sport Touring, were also powered by the 1.5-liter Turbo (L15B7 with VTEC®). … Civic Hatchback 2022-2024 EX-L, Sport Touring L15B7 (w/VTEC®) 180 @ 6000 rpm 177 @ 1700-4500 rpm",
        as_printed="L15B7 (w/VTEC®)", applicability=US15, confidence="high",
        notes="US release; Canadian sheets give no code but identical ratings/bore/stroke/CR. NOT the Si's L15CA (200 hp, 11-blade turbine, 17.8 psi)."))
    A("engine.description", "Engine description as printed by Honda Canada", "text", "low", rec(
        "eng:hondanews-ca-2024-hatch-specs", value="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC turbocharged 4-cylinder",
        unit="text", cls="A", locator="ENGINE table, first row",
        evidence="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder",
        as_printed="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder",
        applicability=CA24, confidence="high", notes=MYNOTE))
    A("engine.valvetrain", "Valvetrain", "text", "medium", rec(
        "eng:hondanews-us-15t-engine-2024", value="DOHC 16-valve, chain-driven; dual VTC (intake and exhaust cam phasing); VTEC on exhaust cam (lift/timing/duration)",
        unit="text", cls="A", locator="'DOHC Cylinder Head and Valvetrain' and '11th-Generation Civic' sections",
        evidence="A low-friction, silent chain drives the dual overhead cams … Variable Timing Control™ (VTC™) varies the phase of both the intake and exhaust camshafts independently … The most significant was the addition of VTEC® to the exhaust cam, improving exhaust efficiency and optimizing valve overlap.",
        as_printed="DOHC; dual VTC; VTEC® on exhaust cam", applicability=US15, confidence="high"))
    A("engine.valvetrain", "Valvetrain", "text", "medium", rec(
        "eng:hic-us-2024-hatch-specs", value="16-Valve DOHC VTEC", unit="text", cls="A",
        locator="Engineering table, Valve Train row, Sport Touring column",
        evidence="Valve Train 16-Valve DOHC i-VTEC® 16-Valve DOHC i-VTEC® 16-Valve DOHC VTEC® 16-Valve DOHC VTEC®",
        as_printed="16-Valve DOHC VTEC®", applicability=US24, confidence="high"))
    A("engine.injection", "Fuel injection type", "text", "low", rec(
        "eng:hic-us-2024-hatch-specs", value="Direct", unit="text", cls="A",
        locator="Engineering table, Fuel Injection row, Sport Touring column",
        evidence="Fuel Injection Multi-Point Multi-Point Direct Direct", as_printed="Direct",
        applicability=US24, confidence="high"))
    A("engine.injection", "Fuel injection type", "text", "low", rec(
        "eng:hondanews-ca-2024-hatch-specs", value="Direct", unit="text", cls="A", locator="ENGINE table, first row",
        evidence="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder", as_printed="Direct Injection",
        applicability=CA24, confidence="high"))
    A("engine.fuel_recommended", "Recommended fuel", "text", "medium", rec(
        "eng:hondanews-ca-2024-hatch-specs", value="Regular", unit="text", cls="A", locator="ENGINE table, Recommended fuel row",
        evidence="Recommended fuel Regular Regular", as_printed="Regular", applicability=CA24, confidence="high",
        notes="Ratings are on regular (US: 87 AKI). The 10th-gen Sport hatch (L15BA) needed premium; this one does not."))
    A("engine.fuel_recommended", "Recommended fuel", "text", "medium", rec(
        "eng:hic-us-2024-hatch-specs", value="Regular Unleaded", unit="text", cls="A", locator="Required Fuel row",
        evidence="Required Fuel Regular Unleaded Regular Unleaded Regular Unleaded Regular Unleaded",
        as_printed="Regular Unleaded", applicability=US24, confidence="high"))
    A("engine.rating_standard", "Power/torque rating standard", "text", "medium", rec(
        "eng:hondanews-ca-2024-hatch-specs", value="SAE net, SAE J1349 (Rev. 08/04)", unit="text", cls="A", locator="Footnote 1",
        evidence="Horsepower and torque calculations reflect SAE net, Rev. 08/04, SAE J1349 procedures.",
        as_printed="SAE net, Rev. 08/04, SAE J1349", applicability=CA24, confidence="high"))
    A("engine.throttle", "Throttle actuation", "text", "low", rec(
        "eng:hondanews-ca-2023-hatch-specs", value="Drive-by-wire (electronic throttle)", unit="text", cls="A",
        locator="ENGINE table, Drive-by-Wire Throttle System row",
        evidence="Drive-by-Wire Throttle System™ • • • •", as_printed="Drive-by-Wire Throttle System™",
        applicability=CA23, confidence="high", notes="Row not repeated on the 2024 sheet; no hardware change is indicated."))
    A("engine.idle_stop", "Idle-stop fitted", "bool", "low", rec(
        "eng:hondanews-ca-2024-hatch-specs", value=True, unit="bool", cls="A", locator="ENGINE table, Idle-stop row",
        evidence="Idle-stop • •", as_printed="•", applicability=CA24, confidence="medium",
        notes="Listed for both Sport and Sport Touring columns; the sheet does not say whether it applies to the 6MT."))

    # ---------------- geometry
    for sid, app_, ev, ap in (
        ("eng:hondanews-ca-2024-hatch-specs", CA24, "Displacement (cc) 1498 1498", "1498"),
        ("eng:hic-us-2024-hatch-specs", US24, "Displacement 1996 cc 1996 cc 1498 cc 1498 cc", "1498 cc")):
        A("engine.displacement", "Swept volume", "m3", "high", rec(
            sid, printed=(1498, "cc"), cls="A", locator="Displacement row (Sport Touring column)", evidence=ev,
            as_printed=ap, applicability=app_, confidence="high", notes=MYNOTE))
    for sid, app_, ev, ap in (
        ("eng:hondanews-ca-2024-hatch-specs", CA24, "Bore and stroke (mm) 73 x 89.5 73 x 89.5", "73 x 89.5"),
        ("eng:hic-us-2024-hatch-specs", US24, "Bore and Stroke 86.0 mm / 85.9 mm 86.0 mm / 85.9 mm 73.0 mm / 89.5 mm 73.0 mm / 89.5 mm", "73.0 mm / 89.5 mm")):
        A("engine.bore", "Cylinder bore", "m", "medium", rec(sid, printed=(73.0, "mm"), cls="A", locator="Bore and stroke row",
          evidence=ev, as_printed=ap, applicability=app_, confidence="high"))
        A("engine.stroke", "Piston stroke", "m", "medium", rec(sid, printed=(89.5, "mm"), cls="A", locator="Bore and stroke row",
          evidence=ev, as_printed=ap, applicability=app_, confidence="high"))
    for sid, app_, ev, ap in (
        ("eng:hondanews-ca-2024-hatch-specs", CA24, "Compression ratio 10.3:1 10.3:1", "10.3:1"),
        ("eng:hic-us-2024-hatch-specs", US24, "Compression Ratio 10.8 : 1 10.8 : 1 10.3 : 1 10.3 : 1", "10.3 : 1")):
        A("engine.compression_ratio", "Geometric compression ratio", "1", "low", rec(sid, printed=(10.3, "ratio"), cls="A",
          locator="Compression ratio row", evidence=ev, as_printed=ap, applicability=app_, confidence="high"))
    A("engine.cylinders", "Number of cylinders (inline)", "count", "medium", rec(
        "eng:hondanews-ca-2024-hatch-specs", printed=(4, "count"), cls="A", locator="ENGINE table, first row",
        evidence="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder", as_printed="4-cylinder",
        applicability=CA24, confidence="high"))

    # ---------------- ratings
    pw = [("eng:hondanews-ca-2024-hatch-specs", CA24, "Horsepower @ rpm1 180 @ 6000 180 @ 6000", "180 @ 6000"),
          ("eng:hondanews-ca-2023-hatch-specs", CA23, "Horsepower @ rpm1 158 @ 6500 180 @ 6000 180 @ 6000 180 @ 6000", "180 @ 6000"),
          ("eng:hondanews-ca-2022-hatch-specs", CA22, "Horsepower @ rpm1 158 @ 6500 180 @ 6000 180 @ 6000", "180 @ 6000"),
          ("eng:hic-us-2024-hatch-specs", US24, "Horsepower (SAE net) * 158 @ 6500 rpm 158 @ 6500 rpm 180 @ 6000 rpm 180 @ 6000 rpm", "180 @ 6000 rpm"),
          ("eng:hondanews-us-15t-engine-2024", US15, "Civic Hatchback 2022-2024 EX-L, Sport Touring L15B7 (w/VTEC®) 180 @ 6000 rpm 177 @ 1700-4500 rpm", "180 @ 6000 rpm")]
    for sid, app_, ev, ap in pw:
        A("engine.power_max", "Rated peak power (SAE J1349 net, crank)", "W", "critical", rec(
            sid, printed=(180, "hp"), cls="A", locator="Horsepower row (Sport Touring column) / applications table",
            evidence=ev, as_printed=ap, applicability=app_, confidence="high",
            notes="SAE net hp (745.7 W). Ratings are not split by gearbox in any 2022-2024 source (the 10th-gen L15BA did split them: 6MT 180 @ 5500 / 177 @ 1900-5000)."))
        A("engine.power_max_rpm", "Engine speed at rated peak power", "rpm", "high", rec(
            sid, printed=(6000, "rpm"), cls="A", locator="Horsepower row", evidence=ev, as_printed=ap,
            applicability=app_, confidence="high"))
    tq = [("eng:hondanews-ca-2024-hatch-specs", CA24, "Torque (lb.-ft. @ rpm)1 177 @ 1700-4500 177 @ 1700-4500", "177 @ 1700-4500"),
          ("eng:hondanews-ca-2023-hatch-specs", CA23, "Torque (lb.-ft. @ rpm)1 138 @ 4200 177 @ 1700-4500 177 @ 1700-4500 177 @ 1700-4500", "177 @ 1700-4500"),
          ("eng:hondanews-ca-2022-hatch-specs", CA22, "Torque (lb.-ft. @ rpm)1 138 @ 4200 177 @ 1700-4500 177 @ 1700-4500", "177 @ 1700-4500"),
          ("eng:hic-us-2024-hatch-specs", US24, "Torque (SAE net) * 138 lb-ft @ 4200 rpm 138 lb-ft @ 4200 rpm 177 lb-ft @ 1700-4500 rpm 177 lb-ft @ 1700-4500 rpm", "177 lb-ft @ 1700-4500 rpm"),
          ("eng:hondanews-us-15t-engine-2024", US15, "the engine's peak output of 180 hp (SAE net @ 6,000 rpm) and 177 lb.-ft. of torque (SAE net @ 1,700-4,500 rpm) are possible at 16.5 psi of boost on regular unleaded fuel", "177 lb.-ft. (SAE net @ 1,700-4,500 rpm)")]
    for sid, app_, ev, ap in tq:
        A("engine.torque_max", "Rated peak torque (SAE J1349 net, crank)", "N*m", "critical", rec(
            sid, printed=(177, "lb-ft"), cls="A", locator="Torque row (Sport Touring column) / 11th-gen section",
            evidence=ev, as_printed=ap, applicability=app_, confidence="high"))
        A("engine.torque_max_rpm_low", "Start of rated peak-torque plateau", "rpm", "high", rec(
            sid, printed=(1700, "rpm"), cls="A", locator="Torque row", evidence=ev, as_printed=ap, applicability=app_, confidence="high"))
        A("engine.torque_max_rpm_high", "End of rated peak-torque plateau", "rpm", "high", rec(
            sid, printed=(4500, "rpm"), cls="A", locator="Torque row", evidence=ev, as_printed=ap, applicability=app_, confidence="high"))

    # ---------------- speeds
    for sid, app_, ev in (("eng:hic-us-2024-hatch-specs", US24, "Redline 6800 rpm 6800 rpm 6600 rpm 6600 rpm"),
                          ("eng:hic-us-2022-hatch-specs", US22, "Redline | 6800 rpm | 6800 rpm | 6600 rpm | 6600 rpm".replace(" | ", " "))):
        A("engine.redline_rpm", "Redline (tachometer red zone start, as published)", "rpm", "high", rec(
            sid, printed=(6600, "rpm"), cls="A", locator="Engineering table, Redline row, Sport Touring column",
            evidence=ev, as_printed="6600 rpm", applicability=app_, confidence="high",
            notes="US source; the Honda Canada spec sheets do not list a redline. No US/Canada engine difference is indicated (identical ratings, bore/stroke, CR). The Si (L15CA) release also cites a 6600 rpm redline."))
    A("engine.limiter_rpm", "Fuel-cut (rev limiter) engine speed, stock calibration", "rpm", "high", db.unknown(
        "rpm", searches=["Honda Canada/US spec sheets (no limiter figure)", "hondanews.com 1.5T technical release (redline only)",
                         "WebSearch: Car and Driver 2022 Civic hatch manual test (Redline/Fuel Cutoff) - syndicated copy on autos.yahoo.com is robots-disallowed",
                         "civicxi.com threads (rev hang, dyno) - no stock 6MT limiter figure found",
                         "PRL blog 2026 gives a stock 6500 rpm limit for a 10th-gen Si only (different engine/calibration; not used)"],
        how_to_measure="In neutral or 2nd gear, record OBD-II rpm (10 Hz+) or the tach on video while holding WOT into the limiter; note the cut rpm, the re-enable rpm and the cut pattern (fuel/spark).",
        notes="Lead only: limiter expected slightly above the 6600 rpm redline; do not use as data."))
    A("engine.idle_rpm", "Warm idle speed", "rpm", "medium", db.record(
        value=750, unit="rpm", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
        applicability={}, confidence="low", range=[650, 850],
        how_to_measure="Warm engine (fan cycled), A/C off, neutral: read rpm via OBD-II; repeat with A/C on.",
        notes="Engineering estimate: typical warm idle of modern Honda L-series DI engines; no published figure found for this car (service manual on techinfo.honda.com is paywalled; owner's manual gives none)."))
    A("engine.fuel_cut_behavior", "Overrun (deceleration) fuel cut behaviour", "text", "high", db.unknown(
        "text", searches=["Honda spec sheets and 1.5T release (not described)", "civicxi rev-hang threads (rev hang discussed, no logged DFCO thresholds)"],
        how_to_measure="OBD-II log of rpm, throttle, short-term fuel trim / injector pulse (KTuner/Hondata datalog ideal) during lift-offs at 2000-6000 rpm in gear and during clutch-in revs; DFCO is visible as fuel trim/injection going to zero.",
        notes="Matters for overrun burble modelling (audio domain): burble with a cat-back needs combustion on overrun, i.e. before DFCO engages or after it re-enables."))
    A("engine.limiter_behavior", "Rev-limiter behaviour (hard/soft cut, pattern)", "text", "medium", db.unknown(
        "text", searches=["as engine.limiter_rpm"], how_to_measure="As engine.limiter_rpm; record audio + OBD at the limiter in neutral and in 2nd."))
    A("engine.rev_hang_engine_side", "Engine-side causes of rev hang between shifts", "text", "medium", db.unknown(
        "text", searches=["Honda spec/feature pages (not described)", "civicxi.com build/rev-hang threads"],
        how_to_measure="Datalog rpm, pedal and commanded throttle during clutch-in upshifts (drivetrain thread owns rev-hang numbers).",
        notes="Lead only (forum): civicxi 'Chilly's 2023 Civic FL1 Sport Touring 6MT Build' (cache/pages/d759f192e18e2393.txt) says 'Still running a stock tune, but I reduced the rev hang.' with KTuner, suggesting a calibration (throttle/ignition decay) cause, not hardware."))
    A("engine.inertia", "Rotating inertia of engine (crank, damper, rods/pistons equivalent, cam drive) excluding flywheel", "kg*m2", "high", db.record(
        value=0.05, unit="kg*m2", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
        applicability={}, confidence="low", range=[0.035, 0.08],
        how_to_measure="Free-rev test: log rpm at 50-100 Hz with clutch disengaged after a blip; dw/dt with known friction torque gives engine+flywheel inertia; subtract the flywheel (weigh/measure or swing-test it when the clutch is serviced).",
        notes="Engineering estimate. Basis: 1.5 L inline-4 with forged micropolished crank, crack-split rods and light pistons (Honda 1.5T release); crank+damper inertia for small I4s is commonly a few hundredths kg*m2. Flywheel (dual-mass vs single-mass) is owned by the drivetrain thread; none was found in public sources here."))
    A("engine.driveline_loss_assumed", "Assumed fraction of crank power lost between crank and chassis-dyno roller (FWD manual)", "1", "high", db.record(
        value=0.13, unit="1", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
        applicability={}, confidence="low", range=[0.10, 0.18],
        how_to_measure="Back-to-back engine dyno and chassis dyno of the same engine (not practical); or coastdown-corrected chassis dyno with known tire losses.",
        notes="Rule-of-thumb range for transverse FWD manual on an inertia chassis dyno; used only to convert wheel to crank in engine_curve.csv. No stock 6MT hatch dyno was found to cross-check it against the 180 hp rating."))

    # ---------------- turbo
    T15 = US15
    T("turbo.make_model", "Turbocharger make/model", "text", "medium", rec(
        "eng:hondanews-us-15t-engine-2024", value="Mitsubishi Heavy Industries (MHI) TD03 family, small-diameter, single-scroll; 11-blade reshaped turbine with diagonal exhaust entry on 2022-2024 Civic",
        unit="text", cls="A", locator="'Turbo System' and '11th-Generation Civic' sections",
        evidence="For maximum responsiveness, a small-diameter MHI TD03 turbo is used. The single-scroll housing design helps the turbo build boost even at relatively small throttle openings and low engine speeds. … In the latest Civic the engine also uses a reshaped 11-blade turbine impeller design in the turbocharger … Exhaust channeled to the turbo now enters the turbine wheel diagonally, rather than from the side as before.",
        as_printed="small-diameter MHI TD03 turbo", applicability=T15, confidence="medium",
        notes="The 'Turbo System' section describes all 1.5T versions; the 11th-gen section adds the 11-blade turbine. Exact TD03 sub-model/trim not published."))
    T("turbo.wastegate", "Wastegate type and control", "text", "high", rec(
        "eng:hondanews-us-15t-engine-2024", value="Internal wastegate, electrically actuated (ECU-controlled)", unit="text", cls="A",
        locator="Opening summary and 'Turbo System' section",
        evidence="a low-inertia mono-scroll turbo system that uses an electric wastegate to control boost pressure … The electrically actuated wastegate enables precise control of boost pressure.",
        as_printed="electric wastegate", applicability=T15, confidence="high",
        notes="'Internal' inferred from the integrated exhaust manifold/turbo layout; not stated."))
    T("turbo.exhaust_manifold", "Exhaust manifold layout", "text", "low", rec(
        "eng:hondanews-us-15t-engine-2024", value="Cast into cylinder head, 4-into-2 (cyl 1+4, 2+3)", unit="text", cls="A",
        locator="'DOHC Cylinder Head' and '11th-Generation Civic' sections",
        evidence="with the exhaust manifold cast directly into the cylinder head … The new Civic engine also uses a \"4 into 2\" exhaust manifold design, similar to the one used on Accord",
        as_printed="4 into 2", applicability=T15, confidence="high"))
    T("turbo.intercooler", "Intercooler layout", "text", "medium", rec(
        "eng:hondanews-us-15t-engine-2024", value="Air-to-air, front-mounted low in the front of the car, resin composite inlet pipes", unit="text", cls="A",
        locator="'Turbo System' section",
        evidence="Cooling the intake charge is a large low-restriction intercooler, in all cases positioned low in the front of the car where it receives essentially unobstructed airflow when the vehicle is in motion. … Lightweight resin composite inlet pipes carry air to and from the intercooler",
        as_printed="large low-restriction intercooler … positioned low in the front", applicability=T15, confidence="high"))
    for sid, app_, ev, ap in (
        ("eng:hic-us-2024-hatch-specs", US24, "Boost Pressure 16.5 psi 16.5 psi", "16.5 psi"),
        ("eng:hondanews-us-15t-engine-2024", T15, "are possible at 16.5 psi of boost on regular unleaded fuel", "16.5 psi")):
        T("turbo.boost_peak", "Peak boost pressure (gauge)", "Pa", "high", rec(
            sid, printed=(16.5, "psi"), cls="A", locator="Engineering table Boost Pressure row / 11th-gen section",
            evidence=ev, as_printed=ap, applicability=app_, confidence="high",
            notes="Gauge pressure as printed by Honda (psi of boost). Rpm at which it is reached and how it tapers are not published."))
    T("turbo.response", "Transient response (manufacturer description)", "text", "medium", rec(
        "eng:hic-us-2024-turbo-feature", value="Negligible turbo lag; quick throttle response (small-diameter turbine)", unit="text", cls="A",
        locator="Feature text",
        evidence="Thanks to careful tuning and use of a relatively small-diameter turbine wheel, the Honda version of the forced-induction engine exhibits negligible turbo lag—a phenomenon that bedevils many of its turbocharged competitors—so response to the throttle is quick.",
        as_printed="negligible turbo lag", applicability=US24, confidence="medium",
        notes="Marketing description; consistent with the rated torque plateau starting at 1700 rpm. No measured spool time found."))
    T("turbo.boost_onset_rpm", "Engine speed at which full-load boost is reached (WOT, steady)", "rpm", "high", db.record(
        value=1700, unit="rpm", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
        applicability={}, confidence="low", range=[1500, 2200],
        how_to_measure="WOT pull in 3rd/4th from 1200 rpm with OBD-II MAP (or Hondata/KTuner log) at 10 Hz+: record MAP vs rpm.",
        notes="Inference: the rated 177 lb-ft plateau begins at 1700 rpm (class A), which on a turbo engine requires near-target boost there. Not a measurement; no public stock 11th-gen boost log was found (Hondata/KTuner logs not public/accessible)."))
    T("turbo.boost_taper", "Boost vs rpm above the torque plateau", "text", "high", db.unknown(
        "text", searches=["Honda 1.5T release (peak only)", "PRL/TSP/Hondata dyno pages (no boost traces for stock)", "civicxi searches for stock datalogs"],
        how_to_measure="Same WOT log as boost_onset_rpm to the limiter; torque falls from 177 lb-ft at 4500 to ~158 lb-ft at 6000 (computed from rating), so boost is expected to taper, but only a log shows it."))
    T("turbo.torque_management", "Torque limiting by gear / torque management (6MT)", "text", "medium", db.unknown(
        "text", searches=["Honda spec/feature pages (none)", "civicxi tuning threads (tuners mention raised boost limits, no stock per-gear tables)",
                          "Hondata product page blocked by robots.txt"],
        how_to_measure="WOT logs in 1st, 2nd and 3rd from the same rpm: compare MAP and calculated load; a lower 1st/2nd plateau indicates per-gear torque limits."))

    db.save(e); db.save(t)
    return e, t


# ---------------- stock dyno run files (no curve points could be digitized; see log)
RUNS = [
  dict(run_id="hondata_2022_civic_sedan_ex_cvt_stock", source_id="eng:thedrive-hondata-2022-ex",
       vehicle="2022 Honda Civic Sedan EX (US), 1.5T L15B7, CVT", stock=True, dyno_type=None, correction=None,
       gear=None, fuel=None, ambient=None,
       peak={"wheel_power": {"printed": [162.46, "hp"]}, "wheel_torque": {"printed": [163.63, "lb-ft"]}},
       evidence="When Hondata put the untuned car on the dyno, it showed 162.46 hp and 163.63 pound-feet at the axle",
       equivalence="Same engine code and rating as the target (Honda 1.5T release), but sedan + CVT: wheel figures include CVT losses and CVT/torque-management behaviour; not equivalent for a curve.",
       chart_url=None, points=[], use_for_curve=False),
  dict(run_id="prl_2022_civic_touring_cvt_stock_intake_baseline", source_id="eng:prl-civicxi-intake-baseline-2021",
       vehicle="2022 Honda Civic Touring sedan, 1.5T, CVT", stock=True, dyno_type="DynoJet 224X (chassis, inertia)",
       correction=None, gear="4th (CVT), 70-90 mph", fuel=None, ambient="95 F, 1000 ft",
       peak={"wheel_power": {"printed": [168.6, "hp"]}},
       evidence="For the set of dyno runs with the completely stock car, we saw an average power across all runs of 165.4 HP and an average peak power of 168.6 HP.",
       equivalence="CVT sedan; x-axis was road speed (no tach signal), so no rpm curve exists.",
       chart_url=None, points=[], use_for_curve=False),
  dict(run_id="prl_2022_civic_cvt_stock_frontpipe_baseline", source_id="eng:prl-frontpipe-2021",
       vehicle="PRL 11th-gen 1.5T development car (2022 Civic Touring sedan, CVT)", stock=True, dyno_type=None,
       correction=None, gear=None, fuel=None, ambient="59 F, 1160 ft",
       peak={"wheel_power": {"printed": [171, "hp"]}},
       evidence="With the car completely stock, we saw a maximum horsepower of 171WHP.",
       equivalence="CVT sedan; same engine code; peak only.", chart_url=None, points=[], use_for_curve=False),
  dict(run_id="tsp_2022_civic_non_si_cvt_stock", source_id="eng:tsp-stage1-non-si",
       vehicle="Unmodified 2022 non-Si Civic 1.5T, CVT (body not stated)", stock=True, dyno_type=None,
       correction=None, gear=None, fuel=None, ambient=None,
       peak={"wheel_power": {"printed": [154, "hp"]}, "wheel_torque": {"printed": [163, "lb-ft"]}},
       evidence="154whp / 163tq - Factory Calibration (Dyno testing was completed on an unmodified 2022 Non-Si Civic 1.5T with a CVT.)",
       equivalence="CVT; peak only; chart image on the page not digitized (CVT rpm axis not representative of a 6MT pull).",
       chart_url=None, points=[], use_for_curve=False),
]


def write_runs():
    import units
    d = os.path.join(ROOT, "engine_curves")
    os.makedirs(d, exist_ok=True)
    for r in RUNS:
        verify(r["source_id"], r["evidence"].replace("(Dyno", "| (Dyno") if False else r["evidence"])
        r = dict(r)
        for k, v in r["peak"].items():
            si, u = units.to_si(*v["printed"])
            v["value"], v["unit"] = si, u
        r["source_url"] = SRC[r["source_id"]]["url"]
        r["cache_file"] = SRC[r["source_id"]]["cache_file"]
        r["digitizing"] = None
        r["notes"] = ("Stock run of the same engine code/rating but NOT the target body/gearbox. "
                      "Peak figures only; no rpm-resolved points were available, so this run contributes no rows to engine_curve.csv.")
        with open(os.path.join(d, r["run_id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False); f.write("\n")


if __name__ == "__main__":
    build()
    write_runs()
    print("ok")
