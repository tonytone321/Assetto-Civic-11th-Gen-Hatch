#!/usr/bin/env python3
"""Domain 9: build vehicle_data/paint.json (sourced part), vehicle_data/dashboard.json and
references/manifest.json from pages cached under cache/pages/.

Every `evidence` string is checked against the cached page text before it is written
(the script aborts if a quote is not found), so quotes cannot drift from the source.
Scripted photo colour statistics are added separately by scripts/domains/paint_analyze.py.

Usage: python3 scripts/domains/visual_build.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dbutil as db  # noqa: E402

TODAY = db.today()


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def verify(cache_file, evidence):
    """Abort unless every ' … '-separated fragment of `evidence` is in the cached text."""
    path = os.path.join(ROOT, cache_file)
    text = _norm(open(path, encoding="utf-8").read())
    for frag in evidence.split(" … "):
        if _norm(frag) not in text:
            raise SystemExit(f"EVIDENCE NOT FOUND in {cache_file}: {frag!r}")
    return evidence


# ------------------------------------------------------------------ sources
SRC = {
    "hci-2024-specs": dict(
        title="2024 Honda Civic Hatchback Specifications (Honda Canada newsroom, April 4, 2024)",
        url="https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
        publisher="Honda Canada Inc. (hondanews.ca)", cls="A",
        applicability="2024 Civic Hatchback, Canada, Sport and Sport Touring, CVT and 6MT",
        notes="Feature table columns SPORT | SPORT TOURING; column mapping checked in the page HTML table. No colour table on this page.",
        cache_file="cache/pages/22157798d6e48e1c.txt"),
    "hci-2023-specs": dict(
        title="2023 Civic Hatchback Specifications (Honda Canada newsroom)",
        url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
        publisher="Honda Canada Inc. (hondanews.ca)", cls="A",
        applicability="2023 Civic Hatchback, Canada, LX / Sport / Sport Touring",
        notes="EXTERIOR/INTERIOR COLOURS table, columns LX | Sport | Sport Touring.",
        cache_file="cache/pages/374416cf6bc6db5d.txt"),
    "ahm-infocenter-2024-colors": dict(
        title="2024 Civic Hatchback - Colors (Honda Information Center, American Honda)",
        url="https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Colors",
        publisher="American Honda Motor Co. (hondainfocenter.com)", cls="A",
        applicability="2024 Civic Hatchback, USA, LX / Sport / EX-L / Sport Touring",
        notes="Colour/trim matrix; Sonic Gray Pearl row marks Black Leather under Sport Touring (no 'CVT only' note, i.e. both gearboxes). Page <title> reads '2023' but the body heading is '2024 Civic Hatchback'. Swatch image is an MY18 asset (same code NH-877P).",
        cache_file="cache/pages/3a6c7d907fdddd60.txt"),
    "ahm-hondanews-2024-specs": dict(
        title="2024 Honda Civic Hatchback Specifications & Features (hondanews.com)",
        url="https://hondanews.com/en-US/honda-automobiles/releases/2024-honda-civic-hatchback-specifications-features",
        publisher="American Honda Motor Co. (hondanews.com)", cls="A",
        applicability="2024 Civic Hatchback, USA, LX / Sport / EX-L / Sport Touring",
        notes="Columns LX | Sport | EX-L | Sport Touring, checked in the HTML table.",
        cache_file="cache/pages/2b1524caf89378a3.txt"),
    "ahm-presskit-2022": dict(
        title="2022 Honda Civic Hatchback Press Kit (hondanews.com, Sept 2021)",
        url="https://hondanews.com/en-US/releases/release-20c92b0d934f0bc63982bd3eee0149e9-2022-honda-civic-hatchback-press-kit",
        publisher="American Honda Motor Co. (hondanews.com)", cls="A",
        applicability="2022 Civic Hatchback, USA, all trims; launch press kit with 32 press photos",
        notes="Text and photo gallery (preview 928x522 JPEGs on wieck-honda-production S3; higher resolutions not publicly served (403)).",
        cache_file="cache/pages/9964dff4363f93bf.txt"),
    "hybridracing-touchup-nh877pah": dict(
        title="Honda Sonic Gray Pearl Touch Up Paint NH877PAH (Hybrid Racing listing)",
        url="https://www.hybrid-racing.com/products/honda-touch-up-paint-sonic-gray-pearl-nh877pah",
        publisher="Hybrid Racing (aftermarket retailer listing a Genuine Honda touch-up product)", cls="C",
        applicability="Genuine Honda touch-up paint, fitment list includes 2017-2024 Honda Civic",
        notes="Retailer listing; supports the code independently of Honda's spec sheets.",
        cache_file="cache/pages/d1e7ca6de8632e09.txt"),
    "cd-2022-hatch-st-6mt": dict(
        title="Tested: 2022 Honda Civic Hatchback (Car and Driver, by the numbers)",
        url="https://www.caranddriver.com/reviews/a37936938/2022-honda-civic-hatchback-by-the-numbers/",
        publisher="Car and Driver (Hearst)", cls="C",
        applicability="2022 Civic Hatchback Sport Touring 6MT, USA, Sonic Gray paint (test car)",
        notes="Test car photos are on hips.hearstapps.com, whose robots.txt disallows Claude-User; cataloged by link only, not downloaded.",
        cache_file="cache/pages/2df590f6625a05ee.txt"),
    "civicxi-sgp-st-thread": dict(
        title="2022 Civic Hatchback Buying / Leasing Tips, Details, & Photos! (Sport Touring in Sonic Gray Pearl) — CivicXI forum",
        url="https://www.civicxi.com/forum/threads/2022-civic-hatchback-buying-leasing-tips-details-photos-sport-touring-in-sonic-gray-pearl.50129/",
        publisher="civicxi.com forum (owner josh_hp, Chicago IL)", cls="C",
        applicability="2022 Civic Hatchback Sport Touring, USA, Sonic Gray Pearl (owner car; gearbox not stated in the first post text)",
        notes="45 photo attachments on cdn.civicxi.com; the egress proxy resets connections to cdn.civicxi.com, so none were downloaded or analysed.",
        cache_file="cache/pages/eb028c2ffd24c2de.txt"),
    "commons": dict(
        title="Wikimedia Commons, Category:Honda Civic (2021) liftback",
        url="https://commons.wikimedia.org/wiki/Category:Honda_Civic_(2021)_liftback",
        publisher="Wikimedia Commons (individual photographers, licenses per file)", cls="C",
        applicability="Mixed; each manifest item states year/market/trim from its file description",
        notes="Free-licensed photos; per-file license recorded in each item. Downloads in cache/visual/commons/ (git-ignored).",
        cache_file="cache/visual/commons_info.json"),
}

APP_CA24_ST = db.app("2024", "CA", "Sport Touring", "6MT and CVT")
APP_CA23_ST = db.app("2023", "CA", "Sport Touring", "6MT and CVT")
APP_US24_ST = db.app("2024", "US", "Sport Touring", "6MT and CVT")
APP_US22 = db.app("2022", "US", "Sport Touring", "6MT and CVT",
                  notes="2022 launch press kit; the 10.2-inch cluster and 9-inch screen are listed for Sport Touring in the 2024 Canadian table too (no model-year change found for the cluster).")


def add_sources(d, ids):
    for sid in ids:
        s = SRC[sid]
        db.add_source(d, sid, s["title"], s["url"], s["publisher"], s["cls"], accessed=None,
                      access_method="static" if not sid.startswith("civicxi") else "static",
                      applicability=s["applicability"], notes=s["notes"], cache_file=s["cache_file"])


def rec(sid, value=None, printed=None, unit=None, **kw):
    ev = kw.pop("evidence")
    verify(SRC[sid]["cache_file"], ev)
    return db.record(value=value, printed=printed, unit=unit, source_id=sid, evidence=ev, **kw)


# ------------------------------------------------------------------ paint.json
def build_paint():
    p = db.path_for("paint")
    d = db.load(p) if os.path.exists(p) else {"domain": "paint", "title": "Paint", "schema_version": 1,
                                                "sources": {}, "parameters": {}}
    add_sources(d, ["hci-2023-specs", "ahm-infocenter-2024-colors", "ahm-hondanews-2024-specs",
                    "hybridracing-touchup-nh877pah", "cd-2022-hatch-st-6mt", "civicxi-sgp-st-thread"])
    K = "paint.code"
    D = ("Honda paint code of Sonic Grey Pearl", "text", "high")
    db.add_candidate(d, K, *D, rec("hci-2023-specs", value="NH-877P", unit="text", status="confirmed", cls="A",
        locator="EXTERIOR/INTERIOR COLOURS table, Sonic Grey Pearl row",
        evidence="EXTERIOR/INTERIOR COLOURS … Sonic Grey Pearl\tNH-877P", as_printed="NH-877P",
        applicability=APP_CA23_ST, confidence="high", prefer=True,
        selection_reason="Canadian Honda source; same code in the 2024 US tables. No 2024 Canadian colour table was found (the 2024 hondanews.ca spec page lists no colours).",
        notes="Row reads Sonic Grey Pearl / NH-877P / (LX blank) / Black/Combi Fabric (Sport) / Black Leather (Sport Touring). Model-year check: same code in American Honda 2024 tables."))
    db.add_candidate(d, K, *D, rec("ahm-infocenter-2024-colors", value="NH-877P", unit="text", status="confirmed", cls="A",
        locator="Colors table, Sonic Gray Pearl row",
        evidence="Sonic Gray Pearl … [NH-877P]", as_printed="[NH-877P]",
        applicability=APP_US24_ST, confidence="high",
        notes="US spelling 'Gray'. Sport Touring column: Black Leather, no 'CVT only' restriction."))
    db.add_candidate(d, K, *D, rec("ahm-hondanews-2024-specs", value="NH-877P", unit="text", status="confirmed", cls="A",
        locator="Exterior colors table row 'Sonic Gray Pearl (NH-877P)' (cols LX|Sport|EX-L|Sport Touring = -|Black|-|Black)",
        evidence="Sonic Gray Pearl (NH-877P)", as_printed="Sonic Gray Pearl (NH-877P)",
        applicability=APP_US24_ST, confidence="high"))
    db.add_candidate(d, K, *D, rec("hybridracing-touchup-nh877pah", value="NH-877P", unit="text", status="confirmed", cls="C",
        locator="Product title and fitment list",
        evidence="Sonic Gray Pearl Touch-Up Paint (NH877PAH) … 2017-2024 Honda Civic", as_printed="NH877PAH",
        applicability=db.app("2017-2024", "US", "all Civic", "any", body="all", engine="all"),
        confidence="medium", notes="NH877PAH is the touch-up product code (paint code NH-877P + Honda suffix)."))

    K = "paint.name"
    D = ("Paint name (Canadian spelling selected)", "text", "medium")
    db.add_candidate(d, K, *D, rec("hci-2023-specs", value="Sonic Grey Pearl", unit="text", status="confirmed", cls="A",
        locator="EXTERIOR/INTERIOR COLOURS table", evidence="Sonic Grey Pearl\tNH-877P", as_printed="Sonic Grey Pearl",
        applicability=APP_CA23_ST, confidence="high", prefer=True, selection_reason="Canadian name; US name is 'Sonic Gray Pearl'."))
    db.add_candidate(d, K, *D, rec("ahm-hondanews-2024-specs", value="Sonic Gray Pearl", unit="text", status="confirmed", cls="A",
        locator="Exterior colors table", evidence="Sonic Gray Pearl (NH-877P)", as_printed="Sonic Gray Pearl",
        applicability=APP_US24_ST, confidence="high"))

    K = "paint.interior_with_paint"
    db.add_candidate(d, K, "Interior offered with Sonic Grey Pearl on Sport Touring", "text", "low",
        rec("hci-2023-specs", value="Black Leather", unit="text", status="confirmed", cls="A",
            locator="EXTERIOR/INTERIOR COLOURS table, Sonic Grey Pearl row, Sport Touring column",
            evidence="Sonic Grey Pearl\tNH-877P\t \tBlack/Combi Fabric\tBlack Leather", as_printed="Black Leather",
            applicability=APP_CA23_ST, confidence="high"))

    K = "paint.finish_family"
    db.add_candidate(d, K, "Paint finish family (from Honda's name: Pearl = mica/pearlescent effect pigment)", "text", "medium",
        rec("hci-2023-specs", value="pearl (pearlescent effect pigment under clearcoat)", unit="text", status="confirmed", cls="A",
            locator="Colour name", evidence="Sonic Grey Pearl", as_printed="Pearl", applicability=APP_CA23_ST,
            confidence="medium",
            notes="Only the word 'Pearl' is sourced. Number of coats (2-coat vs 3-coat tri-coat), pigment and flake type are not published; see paint.layer_structure."))

    K = "paint.option_cost_us_2022"
    db.add_candidate(d, K, "Sonic Gray paint was an extra-cost option on the C&D 2022 test car (identity cross-check only)", "text", "low",
        rec("cd-2022-hatch-st-6mt", value="Sonic Gray paint, $395 (US 2022)", unit="text", status="confirmed", cls="C",
            locator="Specifications block, Options", evidence="Options: Sonic Gray paint, $395", as_printed="$395",
            applicability=db.app("2022", "US", "Sport Touring", "6MT"), confidence="high",
            notes="Same test car: 'Our Sonic Gray Civic Sport Touring test car'. Photos of it are catalogued in references/manifest.json (not downloadable: robots.txt)."))

    # ---- appearance parameters that photos cannot give reliably: class E with basis, or unknown
    HOW_SPECTRO = ("Measure a clean, polished body panel (door skin) of the real car with a multi-angle "
                   "spectrophotometer (e.g. X-Rite MA-T12 / BYK-mac i: L*a*b* at 15/25/45/75/110 deg aspecular, "
                   "sparkle and graininess) or at minimum photograph the panel beside an X-Rite ColorChecker in open "
                   "shade, RAW, fixed white balance, at several viewing angles.")
    db.add_candidate(d, "paint.layer_structure", "Paint layer structure (e-coat/primer/base/[mid-coat]/clear)", "text", "low",
        db.unknown("text", searches=[
            "hondanews.ca 2022-2024 Civic Hatchback releases (colour names only)",
            "hondainfocenter.com 2022/2023/2024 Civic Hatchback Colors (codes only)",
            "Touch-up listing hybrid-racing NH877PAH (single-stage touch-up bottle; no tri-coat note)",
            "WebSearch: Sonic Gray Pearl NH-877P touch-up paint (retailer pages only)",
            "paintscratch.com NH-877P leads (not opened: retail colour approximations)"],
            how_to_measure="Ask a Honda body shop / paint supplier (PPG, Axalta, BASF) for the NH-877P refinish formula: it states whether a mid-coat is needed. " + HOW_SPECTRO))
    db.add_candidate(d, "paint.pearl_shift", "Pearl flop / colour shift with viewing angle", "text", "medium",
        db.unknown("text", searches=["Honda press photos (no angle-controlled shots)", "owner forum thread (images not downloadable)",
                                     "C&D test car photos (robots.txt disallows download)"],
                   how_to_measure=HOW_SPECTRO))
    db.add_candidate(d, "paint.clearcoat_ior", "Clearcoat refractive index (for a layered BRDF)", "1", "low",
        db.record(value=1.5, unit="1", status="estimated", cls="E", source_id=None, locator="",
                  evidence="", as_printed="", applicability={}, confidence="low", range=[1.45, 1.55],
                  how_to_measure="Not practical to measure on the car; accept the generic value or ask the refinish supplier for the clearcoat chemistry.",
                  notes="Basis: OEM automotive clearcoats are acrylic/urethane polymers with refractive index about 1.45-1.55. Not specific to NH-877P."))
    db.add_candidate(d, "paint.clearcoat_roughness", "Clearcoat roughness (GGX perceptual roughness, new clean car)", "1", "medium",
        db.record(value=0.05, unit="1", status="estimated", cls="E", source_id=None, locator="",
                  evidence="", as_printed="", applicability={}, confidence="low", range=[0.02, 0.12],
                  how_to_measure="Measure 20-degree gloss (GU) on a cleaned panel with a glossmeter (OEM clearcoats are typically 85-95 GU at 20 deg) and map to roughness, or photograph a straight light reflection on the hood and fit the highlight width.",
                  notes="Basis: factory clearcoat on a new car gives sharp, mirror-like reflections (press photos show sharp building reflections on the doors). Engineering judgement, not measured; orange peel is a separate low-frequency normal effect."))
    db.add_candidate(d, "paint.base_roughness", "Base/pearl layer roughness under the clearcoat (GGX perceptual)", "1", "low",
        db.record(value=0.4, unit="1", status="estimated", cls="E", source_id=None, locator="",
                  evidence="", as_printed="", applicability={}, confidence="low", range=[0.25, 0.6],
                  how_to_measure=HOW_SPECTRO,
                  notes="Basis: effect-pigment base coats scatter broadly (soft pearl glow rather than a second sharp highlight). Judgement only."))
    db.add_candidate(d, "paint.flake", "Flake / effect pigment type, size and density", "text", "medium",
        db.unknown("text", searches=["Honda colour names/codes only", "no refinish formula or spectro data found publicly"],
                   how_to_measure="Macro photograph (1:1, ring light, 45 deg) of a clean panel next to a mm scale to see flake size and density; or a sparkle/graininess reading from a BYK-mac i. " + HOW_SPECTRO,
                   notes="'Pearl' implies mica-type (interference) pigment rather than aluminium metallic flake, but the mix is unpublished."))
    db.save(d, p)
    return p


# ------------------------------------------------------------------ dashboard.json
def build_dashboard():
    p = db.path_for("dashboard")
    d = {"domain": "dashboard", "title": "Instrument cluster and displays", "schema_version": 1,
         "sources": {}, "parameters": {}}
    add_sources(d, ["hci-2024-specs", "ahm-hondanews-2024-specs", "ahm-presskit-2022"])

    K, D = "dashboard.cluster_type", ("Instrument cluster type", "text", "high")
    db.add_candidate(d, K, *D, rec("hci-2024-specs", value="10.2-inch colour TFT full digital driver meter display", unit="text",
        status="confirmed", cls="A", locator="COMFORT & CONVENIENCE table (Sport Touring column)",
        evidence='10.2" colour TFT full digital driver meter display', as_printed='10.2" colour TFT full digital driver meter display',
        applicability=APP_CA24_ST, confidence="high", prefer=True,
        selection_reason="Canadian 2024 source for the exact trim.",
        notes='Sport (lower trim) instead has: 7" colour TFT centre meter display with Driver Information Interface.'))
    db.add_candidate(d, K, *D, rec("ahm-hondanews-2024-specs", value="10.2-inch digital instrument cluster", unit="text",
        status="confirmed", cls="A", locator="Features table, row '10.2-Inch Digital Instrument Cluster' (LX|Sport|EX-L|Sport Touring = -|-|-|•)",
        evidence="10.2-Inch Digital Instrument Cluster", as_printed="10.2-Inch Digital Instrument Cluster",
        applicability=APP_US24_ST, confidence="high"))
    db.add_candidate(d, K, *D, rec("ahm-presskit-2022", value="10.2-inch all-digital colour instrument display", unit="text",
        status="confirmed", cls="A", locator="HMI and Technology: Digital Instrumentation",
        evidence="Hatchback Sport Touring grades feature the new all-digital instrument display that debuted on Civic Sedan. Measuring 10.2 inches, the high-definition full-color panel displays a variety of information, all customizable from the steering wheel.",
        as_printed="10.2 inches", applicability=APP_US22, confidence="high"))

    K, D = "dashboard.cluster_diagonal", ("Instrument display diagonal", "m", "medium")
    db.add_candidate(d, K, *D, rec("hci-2024-specs", printed=(10.2, "in"), status="confirmed", cls="A",
        locator="COMFORT & CONVENIENCE table", evidence='10.2" colour TFT full digital driver meter display',
        as_printed='10.2"', applicability=APP_CA24_ST, confidence="high",
        notes="Diagonal of the display panel; active-area width/height and resolution are not published (measure on the car)."))

    K, D = "dashboard.lower_trim_cluster", ("Cluster on lower hatchback trims (what the Sport Touring does NOT have)", "text", "low")
    db.add_candidate(d, K, *D, rec("ahm-presskit-2022", value="7-inch colour digital display (left) with depicted analog tachometer plus a physical (mechanical-needle) speedometer on the right", unit="text",
        status="confirmed", cls="A", locator="HMI and Technology: Digital Instrumentation",
        evidence="LX, Sport and EX-L grades are equipped with a 7-inch color digital display. The right side of the instrumentation is occupied by a physical speedometer.",
        as_printed="7-inch", applicability=db.app("2022", "US", "LX/Sport/EX-L", "6MT and CVT"), confidence="high",
        notes="Visual differentiator: do not model the physical speedometer for Sport Touring."))

    K, D = "dashboard.gauge_styles", ("Selectable gauge layouts of the 10.2-inch display", "text", "high")
    db.add_candidate(d, K, *D, rec("ahm-presskit-2022", value="Round tachometer + round speedometer, or bar graphs at the left/right edges; ACC-only mode hides both gauges but keeps a numerical speed readout", unit="text",
        status="confirmed", cls="A", locator="HMI and Technology: Digital Instrumentation",
        evidence="Information can be displayed with traditional round gauges for the tachometer and speedometer, or with bar graphs flanking the left and right of the screen. A new mode available when using Adaptive Cruise Control eliminates the tachometer and speedometer from the display altogether (but maintains a numerical speed readout) for a more relaxed driving environment.",
        as_printed="", applicability=APP_US22, confidence="high"))

    K, D = "dashboard.layout_zones", ("Zones of the 10.2-inch display", "text", "high")
    db.add_candidate(d, K, *D, rec("ahm-presskit-2022", value="Left customizable area: audio/phone (left steering-wheel controls). Right area: driving info, Honda Sensing settings, navigation (right controls). Centre between gauges: vehicle functions, Honda Sensing status graphic (bird's-eye car icon whose brake/head/turn lights mirror the real car) and numerical speed.", unit="text",
        status="confirmed", cls="A", locator="HMI and Technology: Digital Instrumentation",
        evidence="The left side of the screen is dedicated to audio and telephone information, which the driver can select using the left-side steering wheel controls. The right side is dedicated to driving-related information such as activating or deactivating various Honda Sensing® functions, or navigation system information, which the driver selects using the right-side steering wheel controls. … Between the speedometer and tachometer is an area dedicated to vehicle functions, including Honda Sensing® status and a numerical speed readout. … the brake lights, headlights and turn signals of the Civic icon turn on and off with those functions.",
        as_printed="", applicability=APP_US22, confidence="high"))

    # image-located evidence from the Honda press photo of the cluster (US CVT car)
    IMG30 = ("Press photo 'photos/30' (wieck-honda-production .../cc54663dd9510d2c1538cfea2f8c16cb96c69e99/preview-928x522.jpg), "
             "US 2022 Sport Touring CVT, round-gauge mode")
    img_app = db.app("2022", "US", "Sport Touring", "CVT", notes="US car: mph and deg F; gear letter 'D' shows it is a CVT. Layout applies; units and the gear field differ on the Canadian 6MT car.")
    for key, desc, val, where in [
        ("dashboard.tachometer", "Tachometer presentation (round mode)", "Round tachometer on the left, scale 0-8 x1000 r/min with red band at the top of the scale",
         "left dial, labels 0..8, 'x1000 r/min', red arc near 7-8"),
        ("dashboard.speedometer", "Speedometer presentation (round mode)", "Round speedometer on the right plus large numerical speed at top centre (US car: 0-160 mph scale)",
         "right dial labels 0..160 'mph'; '38 mph' digits above centre"),
        ("dashboard.coolant_temp_gauge", "Coolant temperature gauge", "Segmented arc bar gauge at far left of the display, H (top, red) to C (bottom)",
         "far-left arc, letters H and C, red segment by H"),
        ("dashboard.fuel_gauge", "Fuel gauge", "Segmented arc bar gauge at far right of the display, F (top) to E (bottom, red), fuel-pump icon",
         "far-right arc, letters F and E, pump icon"),
        ("dashboard.odometer_location", "Odometer location", "Bottom right of centre, below the speedometer (shown '000008 miles' on the US car); outside temperature at bottom left under the tachometer; drive-mode text ('NORMAL') bottom centre",
         "bottom row: '69 °F' under tach, 'D' gear field, 'NORMAL', '000008 miles'"),
    ]:
        db.add_candidate(d, key, desc, "text", "medium", db.record(
            value=val, unit="text", status="confirmed", cls="A", source_id="ahm-presskit-2022",
            locator=IMG30, evidence=f"[image] {where}", as_printed="", applicability=img_app, confidence="medium",
            notes="Read from the press image by viewing (layout only, no measurement). The tachometer red-band start rpm is not read from this low-resolution image; engine redline is owned by the engine domain."))

    K = "dashboard.gear_position_indicator_mt"
    db.add_candidate(d, K, "Gear position / shift-up indicator on the 6MT car", "text", "high", db.unknown("text", searches=[
        "Owner's manual: techinfo.honda.com owner's-manual PDFs fail upstream TLS through the egress proxy (502); owners.honda.com redirects to a login; honda.ca now shows the current model; manualslib.com robots.txt disallows ClaudeBot",
        "2022 press kit text (no MT cluster description)", "WebSearch: Civic Hatchback owner's manual 'shift up indicator' (Kia results only)",
        "WebSearch: Honda Canada owner's manual Civic Hatchback 2024", "hondanews.com/hondanews.ca 2024 spec tables (no such row)"],
        how_to_measure="Photograph the real car's cluster while driving the 6MT in each gear (passenger, phone on a mount) and at a steady cruise where Honda's shift indicator would appear; or read the owner's manual 'Instrument Panel > Gauges and Displays' section (printed copy in the glovebox).",
        notes="The press photo of a CVT car shows a gear letter field under the tachometer ('D'); whether the 6MT shows a gear number or only an up/down shift arrow is not established."))
    db.add_candidate(d, "dashboard.units_canada", "Display units on the Canadian car (speed, distance, fuel economy, temperature)", "text", "medium",
        db.unknown("text", searches=["hondanews.ca 2024 spec table (fuel economy published in L/100 km, but that is the spec sheet, not the display)",
                                     "Owner's manual not accessible (see gear_position_indicator_mt)", "No Canadian cluster photo with units legible found"],
                   how_to_measure="Photograph the Canadian car's cluster (speed scale, odometer unit, outside temperature, fuel-economy page).",
                   notes="Expected km/h, km, L/100 km and deg C on a Canadian car, but that expectation is not sourced; the speedometer scale maximum for km/h is unknown."))
    db.add_candidate(d, "dashboard.redzone_and_scale_ca", "Tachometer red-zone start and km/h speedometer scale maximum on the Canadian car", "text", "medium",
        db.unknown("text", searches=["US press photo only (mph, low resolution)"],
                   how_to_measure="Straight-on photo of the cluster in round-gauge mode with ignition on, engine off (all scales visible)."))

    K, D = "dashboard.infotainment_screen", ("Centre touchscreen", "text", "medium")
    db.add_candidate(d, K, *D, rec("hci-2024-specs", value='9-inch colour touchscreen including navigation', unit="text",
        status="confirmed", cls="A", locator="ENTERTAINMENT table (Sport Touring column: 'Including Navigation')",
        evidence='9" colour touchscreen', as_printed='9" colour touchscreen | Including Navigation',
        applicability=APP_CA24_ST, confidence="high", prefer=True, selection_reason="Canadian 2024 exact trim.",
        notes='Sport has a 7" colour touchscreen. Apple CarPlay/Android Auto wired/wireless on Sport Touring.'))
    db.add_candidate(d, K, *D, rec("ahm-hondanews-2024-specs", value="9-inch colour touchscreen", unit="text",
        status="confirmed", cls="A", locator="Features table '9-Inch Color Touchscreen' (Sport Touring only)",
        evidence="9-Inch Color Touchscreen", as_printed="9-Inch Color Touchscreen", applicability=APP_US24_ST, confidence="high"))
    db.add_candidate(d, "dashboard.infotainment_diagonal", "Centre touchscreen diagonal", "m", "low",
        rec("hci-2024-specs", printed=(9, "in"), status="confirmed", cls="A", locator="ENTERTAINMENT table",
            evidence='9" colour touchscreen', as_printed='9"', applicability=APP_CA24_ST, confidence="high"))
    db.add_candidate(d, "dashboard.exterior_temperature_indicator", "Exterior temperature indicator", "bool", "low",
        rec("hci-2024-specs", value=True, unit="bool", status="confirmed", cls="A", locator="COMFORT & CONVENIENCE table",
            evidence="Exterior temperature indicator", as_printed="• | •", applicability=APP_CA24_ST, confidence="high"))
    db.add_candidate(d, "dashboard.maintenance_minder", "Maintenance Minder system (service messages on the display)", "bool", "low",
        rec("hci-2024-specs", value=True, unit="bool", status="confirmed", cls="A", locator="COMFORT & CONVENIENCE table",
            evidence="Maintenance Minder™ system", as_printed="• | •", applicability=APP_CA24_ST, confidence="high"))
    db.add_candidate(d, "dashboard.head_up_display", "Head-up display", "bool", "low", db.record(
        value=False, unit="bool", status="estimated", cls="E", source_id=None, locator="", evidence="", as_printed="",
        applicability={}, confidence="medium", range=[False, False],
        how_to_measure="Look at the dash top of the real car (no HUD combiner/projection window).",
        notes="Basis: absence. Neither the 2024 Honda Canada nor the 2024 American Honda feature tables nor the 2022 press kit (searched for 'head-up', 'HUD') list a head-up display for the hatchback. Absence from a table is not a statement, hence class E."))

    # Indicator lamps: the owner's manual is the required source and was not obtainable
    d["indicators"] = {
        "status": "not populated",
        "reason": ("The owner's manual (primary source for every warning/indicator lamp) could not be opened: "
                   "techinfo.honda.com owner's-manual URLs fail with an upstream TLS error through the egress proxy (502), "
                   "owners.honda.com requires a login, honda.ca now hosts the current model, manualslib.com disallows "
                   "ClaudeBot in robots.txt. No lamp is listed from memory."),
        "seen_in_press_photo": [
            {"name": "unidentified green lamps at the upper left of the display", "colour": "green",
             "where": "press photo 30, left edge above the temperature gauge (two green icons; likely headlight/auto-high-beam, not legible at 928x522)",
             "status": "unknown meaning"},
            {"name": "eco/drive icon next to odometer", "colour": "green", "where": "press photo 30, left of '000008 miles'",
             "status": "unknown meaning"}],
        "how_to_obtain": ("Owner's manual printed copy (glovebox) section 'Instrument Panel > Indicators', or photograph the "
                          "cluster bulb check at ignition-on (all lamps lit for a few seconds) on the real car."),
        "table": [],
    }
    db.save(d, p)
    return p


# ------------------------------------------------------------------ references/manifest.json
PK = "https://wieck-honda-production.s3.amazonaws.com/photos/{h}/preview-928x522.jpg"
PKPAGE = "https://hondanews.com/en-US/releases/release-20c92b0d934f0bc63982bd3eee0149e9/photos/{i}"
PRESS_LIC = "Honda media/press image (editorial use); catalogued by link, preview copy in git-ignored cache only"
TRIM_ST_EV = "machined split 5-spoke 18-inch wheels with black inserts and round LED fog lamps (Sport Touring identifiers per the press kit and the 2024 Honda Canada table)"

PRESS = [  # (index, hash, view, year_trim_shown, trim_evidence, gearbox, colour, diffs, usefulness, notes)
    (0, "69fbdc4d2951c9de262725784ad389eda02091d9", "exterior/rear-3q-left (rolling)", "2022 US Civic Hatchback, trim unknown", "caption: 'with Accessory Wheels' (accessory wheels, so wheels are not stock)", "n/a", "Boost Blue Pearl (by appearance)", "accessory wheels; colour", "low", "motion blur background"),
    (3, "85da3f5a1bd12b45d8f483eff5544867b28c661e", "exterior/rear-3q-right", "2022 US Civic Hatchback, trim unknown", "caption 'with Accessory Wheels'", "n/a", "Boost Blue Pearl (by appearance)", "accessory wheels; US plate recess", "medium", "rear bumper, exhaust finishers, spoiler, taillights"),
    (5, "c2fd5f88a3c6a7282ed69dc273051a5673e024de", "exterior/front-3q-right", "2022 US Civic Hatchback, trim unknown", "caption 'with Accessory Wheels'", "n/a", "Boost Blue Pearl (by appearance)", "accessory wheels", "medium", "grille, headlights, front bumper"),
    (6, "f7039164019c65d2f8ceca182b48d315b3e0a654", "exterior/side-right (near-profile, rolling)", "2022 US Civic Hatchback, trim unknown", "caption 'with Accessory Wheels'", "n/a", "Boost Blue Pearl (by appearance)", "accessory wheels; slight 3/4 angle", "medium", "side glass and beltline; normal lens"),
    (10, "3cc1b5be5579fa0f71acb469088d2fc11afb4e31", "exterior/rear-detail (taillight, spoiler, badge)", "2022 US Civic Hatchback", "Civic script badge; trim not determinable", "n/a", "blue", "wide-angle close-up", "medium", "taillight and integrated spoiler detail"),
    (12, "d9ddb87e9ec1193024d6f5a3347158ca8603d86b", "exterior/front-3q-left", "2022 US Civic Hatchback", "dark wheels; trim not determinable", "n/a", "Platinum White Pearl (by appearance)", "", "medium", "studio-like lighting"),
    (14, "b06a2daf4b73df8e382df2141a9e0d96d5e54cd8", "exterior/roof (high 3/4 top-down, rear-left)", "2022 US Civic Hatchback", "machined-face wheels visible (consistent with Sport Touring)", "n/a", "Crystal Black Pearl (by appearance)", "", "high", "only press view showing roof, moonroof and hatch top"),
    (16, "c928c567621b4f88aa6028f4055c239422fdf477", "exterior/rear-3q-left (rolling)", "2022 US Civic Hatchback", "machined-face 18-inch wheels (consistent with Sport Touring)", "n/a", "dark grey (Meteorite Gray Metallic?) - unconfirmed", "", "medium", "used by paint_analyze.py as a grey-paint comparison image"),
    (17, "cd3db434396a7767c7ca2e2ca85bb9ce056f2205", "exterior/front-detail (grille, headlight, fog lamp, bumper)", "2022 US Civic Hatchback Sport Touring", TRIM_ST_EV, "n/a", "light grey (Sonic Gray Pearl or Lunar Silver; unconfirmed)", "coloured night lighting", "high", "front fascia detail; used by paint_analyze.py"),
    (18, "8e7b3cbca24c99dcc87857f936e9f9ae660ec7cf", "exterior/rear-3q-left (sunlit street)", "2022 US Civic Hatchback", "trim not determinable at this size", "n/a", "light bluish grey (unconfirmed)", "", "medium", "used by paint_analyze.py"),
    (20, "e12e8e3340bee4cd9717637daa0e5b84ee88839e", "exterior/front-wheel-detail (headlight, fog lamp, wheel, brake behind spokes)", "2022 US Civic Hatchback Sport Touring", TRIM_ST_EV, "n/a", "light grey (unconfirmed)", "wide-angle close-up, coloured lighting", "high", "best press view of the Sport Touring wheel face and front fog lamp; front caliper partly visible"),
    (21, "309d16e6395fa858eddf749511190043815b1701", "interior/cargo-area (load in place)", "2022 US Civic Hatchback", "trim not determinable", "n/a", "red", "boxes obscure the floor", "low", ""),
    (22, "6acc1b5ee44a26204e9e352f57887facc9dd3287", "interior/dash (wide, from rear seat)", "2022 US Civic Hatchback, Sport Touring (9-inch screen)", "9-inch touchscreen (Sport Touring only)", "not determinable at this size", "black interior", "", "medium", "whole dash layout"),
    (23, "a31c5c49798487824a63695474834f2a26bac54c", "interior/front-seats", "2022 US Civic Hatchback", "perforated leather-like seats (Sport Touring has leather-trimmed seating)", "n/a", "black", "", "medium", "seat shape and perforation"),
    (24, "c04c7ed80b91062e34ed957647cd871a0e8f0afa", "interior/cargo-area (seats up, cover)", "2022 US Civic Hatchback", "trim not determinable", "n/a", "red exterior", "", "high", "cargo floor, side trims, tonneau"),
    (25, "26e1e7b175bc168a450f40c4ee71ac1e6899a2e6", "exterior/mirror + interior A-pillar", "2022 US Civic Hatchback", "", "n/a", "red", "", "low", "mirror housing and tweeter"),
    (26, "9c7b3c7b81d576a6088065dd7360be142eebc9f9", "interior/infotainment + steering wheel + climate", "2022 US Civic Hatchback Sport Touring", "9-inch touchscreen (Sport Touring only)", "not visible", "black", "", "high", "screen bezel, honeycomb vent mesh, climate knobs"),
    (27, "1113da2150b8e401d83e6c8d564f270ab093fccb", "interior/centre-stack + console", "2022 US Civic Hatchback", "", "CVT (console with CVT selector layout)", "black", "CVT console differs from 6MT (cupholders beside the selector)", "medium", "centre stack only; console not representative of the 6MT"),
    (28, "75aa090b3c3745a9b027357b6c634b221b6768f6", "interior/cargo-area (rear seats folded)", "2022 US Civic Hatchback", "", "n/a", "red exterior", "", "high", "60/40 folded floor"),
    (29, "ffdeaffb4938d108b6a0f4a29fd9dab82cc39ce5", "interior/driver-area (dash, cluster, wheel, shifter, pedals, door card, seats)", "2022 US Civic Hatchback Sport Touring 6MT", "10.2-inch digital cluster + 9-inch screen + leather seats (Sport Touring); manual confirmed by gear lever and three pedals", "6MT (three pedals and gear lever visible)", "black leather", "US car; low light", "high", "best single cabin reference for the target: shows clutch/brake/throttle pedals, shift knob, door card, driver seat"),
    (30, "cc54663dd9510d2c1538cfea2f8c16cb96c69e99", "interior/cluster (round-gauge mode)", "2022 US Civic Hatchback Sport Touring (10.2-inch display)", "10.2-inch full digital cluster", "CVT ('D' shown in gear field)", "n/a", "US units (mph, deg F, miles); CVT gear field", "high", "layout reference for the cluster; units and gear field differ on the Canadian 6MT"),
    (31, "b4f08329a30b8ea3f7f52724a2c43601da75b69c", "interior/shifter + console (6MT)", "2022 US Civic Hatchback, manual", "manual gear lever with drive-mode and parking-brake buttons to its left", "6MT (gear lever)", "black", "trim not provable from this crop", "high", "6MT console layout matches the press-kit text"),
]

COMMONS = [  # file title, view, year_trim, trim_evidence, colour, lens, usefulness, notes
    ("File:2022 Honda Civic Sport Touring, Front Right, 11-07-2021.jpg", "exterior/front-3q-right", "2022 Civic Hatchback Sport Touring, Canada (Sault Ste. Marie, ON, dealer lot)", "file description 'Sport Touring'; round fog lamp in the bumper; dark machined wheels", "Platinum White Pearl (by appearance)", "normal (EXIF focal 12.1 mm on a 1/1.7-inch compact, ~56 mm equiv.)", "high", "Canadian-market car; dealer plate"),
    ("File:2022 Honda Civic Sport Touring, Rear Left, 11-07-2021.jpg", "exterior/rear-3q-left", "2022 Civic Hatchback Sport Touring, Canada (Sault Ste. Marie, ON)", "file description 'Sport Touring'; window sticker", "Platinum White Pearl (by appearance)", "normal (EXIF 10.8 mm on 1/1.7-inch compact, ~50 mm equiv.)", "high", "rear fascia, exhaust finishers, spoiler, Canadian car"),
    ("File:2022 Honda Civic Sport Touring liftback, rear 6.18.22.jpg", "exterior/rear-3q-left", "2022 Civic Hatchback Sport Touring, USA (Queens, NY)", "file description 'Sport Touring'", "Platinum White Pearl (by appearance)", "normal-long (EXIF 36.8 mm on 1-inch sensor, ~100 mm equiv.)", "high", "low distortion rear 3/4"),
    ("File:22 Honda Civic Hatchback Sport Touring.jpg", "exterior/front-3q-left + wheel", "2022 Civic Hatchback Sport Touring, USA (Gilbert AZ dealer lot)", "file description; machined split 5-spoke wheel with black inserts; fog lamp", "silver (Lunar Silver Metallic by appearance, not Sonic Gray)", "wide-angle (tablet camera, EXIF 26 mm equiv.)", "medium", "good wheel-face detail; perspective distortion"),
    ("File:2022 Honda Civic Hatchback EX-L in Platinum White Pearl, front right.jpg", "exterior/front-3q-right", "2022 Civic Hatchback EX-L CVT, USA", "file description 'EX-L ... CVT' (lower trim)", "Platinum White Pearl", "long (70 mm on full frame)", "medium", "lower trim (17-inch wheels, no fog lamps); body panels shared; good low-distortion geometry"),
    ("File:2022 Honda Civic Hatchback EX-L in Platinum White Pearl, rear right.jpg", "exterior/rear-3q-right", "2022 Civic Hatchback EX-L CVT, USA", "file description (lower trim)", "Platinum White Pearl", "long (67 mm on full frame)", "medium", "body geometry; wheels/trim differ"),
    ("File:L15C in Honda Civic (11th-gen).jpeg", "engine-bay (top, cover removed area)", "11th-gen Civic, 1.5 L; body and market not stated", "file description 'L15C engine in Honda Civic'", "n/a", "wide (iPhone main camera, 26 mm equiv.)", "low", "L15C is the Japanese-market code; may not be a North-American car. Use only for general layout."),
]

OTHER = [
    dict(id="cd-2022-st-6mt-309", url="https://hips.hearstapps.com/hmg-prod/images/2022-honda-civic-hatchback-sport-touring-309-1634066512.jpg",
         page_url=SRC["cd-2022-hatch-st-6mt"]["url"], owner="Car and Driver (Hearst)", license_note="Copyright Hearst; robots.txt disallows download; link only",
         view="exterior (lead photo; view not inspected)", lens_character="not inspected (not downloaded)", year_trim_shown="2022 US Civic Hatchback Sport Touring 6MT (C&D test car)",
         trim_evidence="article text: 'Our Sonic Gray Civic Sport Touring test car' … 'The six-speed manual'", gearbox_shown="6MT (per article)",
         color_shown="Sonic Gray Pearl (per article: 'Options: Sonic Gray paint, $395')", differences_from_target="US 2022", usefulness="high",
         notes="The only confirmed Sonic Gray Pearl Sport Touring 6MT photos found; four more on the same page (…-763, -329, -804, -821). Viewable in a browser by the user."),
    dict(id="civicxi-sgp-st-thread", url=SRC["civicxi-sgp-st-thread"]["url"], page_url=SRC["civicxi-sgp-st-thread"]["url"],
         owner="josh_hp (CivicXI forum)", license_note="Owner photos, all rights reserved; link only", view="mixed exterior/interior (45 attachments)",
         lens_character="phone (not inspected)", year_trim_shown="2022 US Civic Hatchback Sport Touring", trim_evidence="thread title 'Sport Touring in Sonic Gray Pearl'",
         gearbox_shown="not stated in the opening post", color_shown="Sonic Gray Pearl (per title)", differences_from_target="US 2022; gearbox unknown",
         usefulness="medium", notes="cdn.civicxi.com is blocked by the egress proxy (connection reset); images not viewed."),
]


def build_manifest():
    p = os.path.join(ROOT, "references", "manifest.json")
    m = {"domain": "references", "title": "Visual reference manifest", "schema_version": 1, "updated": TODAY,
         "sources": {}, "parameters": {},
         "notes": ("Third-party images are catalogued by link. Copies (if any) live under cache/visual/ (git-ignored) "
                   "and are never committed. Trim/colour judgements from viewing an image are stated as such; "
                   "measurements come only from scripts."),
         "items": []}
    add_sources(m, ["ahm-presskit-2022", "cd-2022-hatch-st-6mt", "civicxi-sgp-st-thread", "commons"])
    for (i, h, view, yts, tev, gb, col, diff, use, notes) in PRESS:
        m["items"].append(dict(
            id=f"ahm-press22-{i:02d}", url=PK.format(h=h), page_url=PKPAGE.format(i=i), source_id="ahm-presskit-2022",
            owner="American Honda Motor Co. (hondanews.com)", license_note=PRESS_LIC, view=view,
            lens_character=("wide-angle (close-up with strong perspective)" if "detail" in view or "wide" in view else "normal/long (press photography; judged by low perspective convergence)"),
            year_trim_shown=yts, trim_evidence=tev, gearbox_shown=gb, color_shown=col,
            differences_from_target="US 2022 press car" + (f"; {diff}" if diff else ""), usefulness=use,
            resolution="928x522 preview (higher resolutions return 403 / need a press login)", notes=notes,
            cache_path=f"cache/visual/presskit22/{i:02d}_{h[:12]}.jpg"))
    info_p = os.path.join(ROOT, "cache", "visual", "commons_info.json")
    info = json.load(open(info_p)) if os.path.exists(info_p) else {}
    for (t, view, yts, tev, col, lens, use, notes) in COMMONS:
        v = info.get(t, {})
        m["items"].append(dict(
            id="commons-" + re.sub(r"[^a-z0-9]+", "-", t[5:].lower()).strip("-")[:60], url=v.get("url"), page_url=v.get("page"),
            source_id="commons", owner=re.sub("<[^>]+>", "", v.get("artist") or "") or None,
            license_note=v.get("license"), view=view, lens_character=lens, year_trim_shown=yts, trim_evidence=tev,
            gearbox_shown="n/a (exterior)" if "exterior" in view else "n/a", color_shown=col,
            differences_from_target="see year_trim_shown", usefulness=use,
            resolution=f"{v.get('w')}x{v.get('h')}", exif={"make": v.get("make"), "model": v.get("model"), "focal": v.get("focal"),
                                                         "focal_35mm": v.get("focal35"), "date": v.get("date")},
            notes=notes, cache_path="cache/visual/commons/" + t[5:].replace(" ", "_").replace("'", "")))
    for o in OTHER:
        o = dict(o); o["source_id"] = o["id"] if o["id"] in SRC else "cd-2022-hatch-st-6mt"
        m["items"].append(o)
    m["excluded"] = [
        {"url": PK.format(h="2a402a44a3675fd2a2e77ed5cba2e5ad2cea736e"), "reason": "caption '2022 Honda Civic Hatchback - Japan Market Model' (non-North-American)"},
        {"url": "https://commons.wikimedia.org/wiki/File:Honda_Civic_Hatchback_EX_%2721_(1).jpg", "reason": "Japanese-specification car (file description); colour looks like a grey-blue but name/code not stated"},
        {"url": "https://commons.wikimedia.org/wiki/Category:Honda_Civic_(2021)_liftback", "reason": "Type R, Si, e:HEV/hybrid, Chinese-market and 2025+ facelift files in the category were not used"},
    ]
    db.save(m, p)
    return p


if __name__ == "__main__":
    for f in (build_paint, build_dashboard, build_manifest):
        print("wrote", f())
