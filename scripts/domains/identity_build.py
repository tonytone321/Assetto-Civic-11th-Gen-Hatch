#!/usr/bin/env python3
"""Build vehicle_data/identity.json (Domain 1: Identity) from cached, opened sources.

Every evidence string is checked by verify_evidence() against the cached page text
(whitespace-normalised) so quotes cannot drift from the source. vPIC decodes come from
identity_vin_decode.py (raw JSON cached under cache/vpic/).
Run: python3 scripts/domains/identity_build.py
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)
import dbutil as db  # noqa: E402
from identity_vin_decode import decode, url as vpic_url  # noqa: E402

ACC = "2026-10-03"
C = {  # cache files (git-ignored) of the opened pages
    "id:hci-2024-specs": "cache/pages/41e62125b9f268de.txt",
    "id:hci-2023-specs": "cache/pages/374416cf6bc6db5d.txt",
    "id:hci-2022-specs": "cache/pages/344bc90bb36560a9.txt",
    "id:hci-2025-specs-page": "cache/pages/e230b13acdcf3696.txt",
    "id:hci-2022-arrival": "cache/pages/a2b12d6f912e06a3.txt",
    "id:hci-2022-debut": "cache/pages/011b73eb9216ebcd.txt",
    "id:hci-2025-refresh": "cache/pages/7807c4fe44812d43.txt",
    "id:ahm-infocenter-2024-colors": "cache/pages/87f27b45d7784846.txt",
    "id:cuv-hatch-list": "cache/pages/14f629ca5159267d.txt",
}


def norm(s):
    return re.sub(r"\s+", " ", s.replace(" | ", " ")).strip()


_texts = {}


def verify_evidence(sid, ev):
    if sid not in C:
        return
    p = os.path.join(ROOT, C[sid])
    if not os.path.exists(p):
        raise SystemExit(f"cache missing for {sid}: {p}")
    t = _texts.setdefault(sid, norm(open(p, encoding="utf-8").read()))
    for frag in ev.split(" … "):
        if norm(frag) not in t:
            raise SystemExit(f"EVIDENCE NOT FOUND in {sid}: {frag!r}")


def ev(sid, *frags):
    e = " … ".join(frags)
    verify_evidence(sid, e)
    return e


CA24ST6 = db.app("2024", "CA", "Sport, Sport Touring (table columns)", "6MT and CVT",
                 notes="Honda Canada 2024 Civic Hatchback specification table (Sport, Sport Touring columns)")


def build():
    d = {"domain": "identity", "title": "Identity", "schema_version": 1, "updated": ACC,
         "sources": {}, "parameters": {}}
    S = lambda sid, **kw: db.add_source(d, sid, accessed=ACC, cache_file=C.get(sid), **kw)
    S("id:hci-2024-specs", title="2024 Honda Civic Hatchback Specifications (release, April 4, 2024)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
      publisher="Honda Canada Inc. (hondanews.ca newsroom)", cls="A", access_method="rendered",
      applicability="2024 Civic Hatchback, Canada; columns SPORT and SPORT TOURING",
      notes="Primary source for the target. No colour table on this page. Label typo 'Steering ratio – (curb-to-curb) (m) 11.4:1'.")
    S("id:hci-2023-specs", title="2023 Civic Hatchback Specifications (release, April 13, 2023)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="2023 Civic Hatchback, Canada; LX, Sport, Sport-B, Sport Touring; includes EXTERIOR/INTERIOR COLOURS table with paint codes")
    S("id:hci-2022-specs", title="2022 Civic Hatchback Specifications (release, October 12, 2021)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="2022 Civic Hatchback, Canada; LX, Sport, Sport Touring")
    S("id:hci-2025-specs-page", title="'2025 Civic Hatchback Specifications' (release, May 21, 2024)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-16f7afa1eda16f08561d54be9a0095b8-2025-civic-hatchback-specifications",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="NOT USABLE: page body contains Ridgeline (3.5 L V6, i-VTM4) specifications under a Civic Hatchback title",
      notes="Honda Canada content error; recorded so nobody uses it. No 2025 Civic Hatchback spec table was available from Honda Canada.")
    S("id:hci-2022-arrival", title="All-New 2022 Civic Hatchback to arrive at Honda Dealerships ... Available Manual Transmission (Sep 20, 2021)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f5ca16bc4a91ff33c2da538124f5afe69c43bfa0-all-new-2022-civic-hatchback-to-arrive-at-honda-dealerships-with-euro-inspired-design-enhanced-sporty-driving-character-and-an-available-manual-transmission",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="2022 Civic Hatchback, Canada launch: trims, engines, MSRP")
    S("id:hci-2022-debut", title="2022 Honda Civic Hatchback Makes Global Debut ... (June 23, 2021)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f62a8a2e1d52802dd04a2618822ad44329120a90-2022-honda-civic-hatchback-makes-global-debut-during-honda-civic-tour-remix-virtual-performance",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="2022 Civic Hatchback, North America (pre-production); plant, powertrain, key specs",
      notes="Pre-launch figures (e.g. length 4549 mm, wheel insert colour 'Shark Gray') differ from later production spec tables; prefer the spec tables for those.")
    S("id:hci-2025-refresh", title="New 2025 Honda Civic Gains Powerful Hybrid Trims, Sportier Styling and Improved Tech (May 21, 2024)",
      url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-13b596316ac6e66d601e6e282b0059a9-new-2025-honda-civic-gains-powerful-hybrid-trims-sportier-styling-and-improved-tech",
      publisher="Honda Canada Inc.", cls="A", access_method="rendered",
      applicability="2025 Civic (refresh), Canada; used only to define exclusions")
    S("id:ahm-infocenter-2024-colors", title="2024 Civic Hatchback – Feature Guide – Colors (Honda Information Center)",
      url="https://www.hondainfocenter.com/2024/civic-hatchback/feature-guide/colors/",
      publisher="American Honda Motor Co., Inc. (page footer: 'All information contained herein applies to U.S. vehicles only.')",
      cls="A", access_method="rendered",
      applicability="2024 Civic Hatchback, USA; LX, Sport, EX-L, Sport Touring",
      notes="Trim availability is shown by check-circle icons; parsed from the cached HTML (cache/pages/87f27b45d7784846.html). Sonic Gray Pearl row: Black Cloth checked under Sport; Black Leather checked under Sport Touring with no 'CVT only' note.")
    S("id:vpic", title="NHTSA vPIC DecodeVinValuesExtended API", url="https://vpic.nhtsa.dot.gov/api/",
      publisher="NHTSA (data from manufacturer's 49 CFR 565 VIN-decoding submission)", cls="A",
      access_method="api", applicability="US VIN patterns; Canadian-market VINs decode through the same patterns",
      notes="Raw JSON cached in cache/vpic/. CAUTION: vPIC returns Trim 'Sport Touring' for 19XFL1H8 and 19XFL1G8 patterns, but Canadian listings show the same patterns on Canadian 'Sport' cars (Canada's Sport is 1.5T; US Sport is 2.0 L), so vPIC trim is NOT reliable for Canadian VINs.")
    S("id:cuv-hatch-list", title="Honda Certified Used Vehicles – used Civic Hatchback listings",
      url="https://cuv.honda.ca/used/Honda-Civic_Hatchback.html", publisher="Honda Canada dealer network (cuv.honda.ca)",
      cls="C", access_method="rendered", applicability="Canadian used-vehicle listings (dealer-entered data)",
      notes="Dealer-entered trim/colour text; weak. Used only for VIN patterns of Canadian cars.")

    def A(key, desc, unit, impact, rec):
        db.add_candidate(d, key, desc, unit, impact, rec)

    s24 = "id:hci-2024-specs"
    A("identity.model_year", "Model year", "text", "critical", db.record(
        printed=("2024", "text"), source_id=s24, locator="Title",
        evidence=ev(s24, "2024 Honda Civic Hatchback Specifications"), as_printed="2024",
        applicability=CA24ST6, confidence="high"))
    A("identity.trim", "Trim", "text", "critical", db.record(
        printed=("Sport Touring", "text"), source_id=s24, locator="Table column headings",
        evidence=ev(s24, "SPORT TOURING", "6-speed manual transmission (MT)"), as_printed="SPORT TOURING",
        applicability=CA24ST6, confidence="high",
        notes="Canadian 2024 Civic Hatchback line-up on this page is SPORT and SPORT TOURING only (both 1.5T)."))
    A("identity.body", "Body style", "text", "critical", db.record(
        printed=("5-door hatchback", "text"), source_id="id:vpic", locator="DecodeVinValuesExtended 19XFL1G82RE400164: BodyClass, Doors, NCSABodyType",
        evidence="BodyClass: Hatchback/Liftback/Notchback; Doors: 5; NCSABodyType: 5-door/4-door hatchback",
        as_printed="Hatchback/Liftback/Notchback, 5 doors", applicability=db.app("2024", "US/CA VIN pattern", "Sport Touring (vPIC)", "6MT"),
        confidence="high", notes="Honda Canada calls the body 'Civic Hatchback' (page title)."))
    A("identity.market", "Market", "text", "high", db.record(
        printed=("Canada", "text"), source_id=s24, locator="Publisher / footer",
        evidence=ev(s24, "HONDA CANADA AUTOMOBILES NEWSROOM", "©2026 Honda Canada Inc"),
        as_printed="Honda Canada", applicability=CA24ST6, confidence="high",
        notes="Target is the Canadian-market car; US data recorded separately in us_ca_differences."))

    # plant: Honda Canada press release + vPIC
    sdeb = "id:hci-2022-debut"
    A("identity.assembly_plant", "Assembly plant", "text", "medium", db.record(
        printed=("Honda Manufacturing of Indiana, Greensburg, Indiana, USA", "text"), source_id=sdeb,
        locator="Para. 5 and 'A New Chapter in Civic North American Manufacturing'",
        evidence=ev(sdeb, "Starting with the 2022 model year, the Civic Hatchback will be manufactured in the U.S. for the first time at the company’s Greensburg, Indiana auto plant."),
        as_printed="Greensburg, Indiana auto plant", applicability=db.app("2022", "North America", "all hatchback", "all"),
        confidence="high", notes="Statement covers 2022 MY onward; 2024 confirmed by vPIC candidate (plant decoded from VIN)."))
    vd, vp = decode("19XFL1G82RE400164")
    A("identity.assembly_plant", "Assembly plant", "text", "medium", db.record(
        printed=(f"{vd['PlantCity']}, {vd['PlantState']}, {vd['PlantCountry']}", "text"), source_id="id:vpic",
        locator=f"{vpic_url('19XFL1G82RE400164')} (cache {vp}) PlantCity/PlantState/PlantCountry",
        evidence=f"PlantCity: {vd['PlantCity']}; PlantState: {vd['PlantState']}; PlantCountry: {vd['PlantCountry']}",
        as_printed=vd["PlantCity"], applicability=db.app("2024", "CA (serial 4xxxxx; see notes)", "Sport Touring (vPIC)", "6MT"),
        confidence="high", notes="VIN check digit valid ('" + vd["ErrorText"] + "'). Also decoded identically for the pattern 19XFL1G8*RE and for Canadian 2024 CVT VINs 19XFL1H87RE400675 / 19XFL1H84RE400858 (cuv.honda.ca)."))

    A("identity.model_code", "Honda model/chassis code (VIN positions 4-6)", "text", "medium", db.record(
        printed=("FL1", "text"), status="estimated", cls="E", source_id="id:vpic",
        locator="VehicleDescriptor 19XFL1G8*RE",
        evidence=f"VehicleDescriptor: {vd['VehicleDescriptor']}", as_printed="19XFL1G8*RE",
        applicability=db.app("2024", "US/CA VIN pattern", "Sport Touring (vPIC)", "6MT"), confidence="medium",
        range=["FL1", "FL1"],
        how_to_measure="Read the VIN and the model code on the door-jamb / firewall ID plate of the real car; Honda parts catalogs for the VIN list the frame code.",
        notes="Interpretation, not a quoted value: Honda VIN positions 4-6 ('FL1') are the line/body/engine code; FL1 = 5-door hatch 1.5T (2.0 L hatches decode as FL2, e.g. 19XFL2G52NE400414 on cuv.honda.ca). Position 7 'G' = 6MT and 'H' = CVT per vPIC TransmissionStyle on G vs H patterns. Honda's own documents calling the North American car 'FL1' were not opened."))

    A("identity.engine_code", "Engine code", "text", "high", db.record(
        printed=(vd["EngineModel"], "text"), source_id="id:vpic", locator=f"{vpic_url('19XFL1G82RE400164')} EngineModel",
        evidence=f"EngineModel: {vd['EngineModel']}; DisplacementL: {vd['DisplacementL']}; EngineHP: {vd['EngineHP']}; Turbo: {vd['Turbo']}",
        as_printed=vd["EngineModel"], applicability=db.app("2024", "US/CA VIN pattern", "Sport Touring (vPIC)", "6MT"),
        confidence="medium", notes="Single source (manufacturer VIN submission via NHTSA). Same code decoded for MY2022 and MY2023 FL1G8 patterns. Second independent source not found within budget; beware the Si (different L15 variant, 200 hp) and JDM documents that use other designations."))
    A("identity.transmission_code", "Gearbox (manual transmission) code", "text", "medium", db.unknown(
        "text", searches=["WebSearch: 11th gen Civic hatchback 1.5T 6-speed manual transmission code L15B7 'transmission code'",
                          "WebSearch: 2024 Civic hatchback Sport Touring MT 'transmission assembly' 20011 part number (hondapartsnow lead 20011-65M-G51 is for 2.0 L Sport per snippet; not opened)",
                          "Honda Canada 2022/2023/2024 spec pages (no code printed)", "vPIC decode (gives only 'Manual/Standard', 6 speeds)"],
        how_to_measure="Read the transmission ID number stamped on the gearbox case (Honda prints the type code at the start of the transmission number), or ask a Honda parts counter for the MT assembly part number/type for the VIN.",
        notes="Techinfo/service information is paywalled and was not used."))
    A("identity.transmission_type", "Transmission type", "text", "critical", db.record(
        printed=("6-speed manual", "text"), source_id=s24, locator="DRIVETRAIN table",
        evidence=ev(s24, "6-speed manual transmission (MT)	 	Available"), as_printed="6-speed manual transmission (MT) — SPORT: blank, SPORT TOURING: Available",
        applicability=CA24ST6, confidence="high"))
    A("identity.drivetrain", "Driven wheels", "text", "critical", db.record(
        printed=("FWD", "text"), source_id="id:hci-2022-specs", locator="DRIVETRAIN table",
        evidence=ev("id:hci-2022-specs", "Front-wheel drive"), as_printed="Front-wheel drive (all trims)",
        applicability=db.app("2022", "CA", "LX, Sport, Sport Touring", "6MT and CVT"), confidence="high",
        notes="2024 Canadian table does not repeat the line; vPIC 2024 FL1G8 pattern DriveType '4x2' confirms; no AWD Civic hatch exists in this generation."))
    A("identity.engine_description", "Engine description (Honda Canada)", "text", "high", db.record(
        printed=("1.5-litre, 16-valve, Direct Injection, DOHC, VTEC turbocharged 4-cylinder", "text"), source_id=s24, locator="ENGINE table",
        evidence=ev(s24, "1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder"),
        as_printed="1.5-litre, 16-valve, Direct Injection, DOHC, VTEC® turbocharged 4-cylinder", applicability=CA24ST6, confidence="high"))

    # sold in Canada 2024 ST 6MT
    A("identity.sold_in_canada_2024_st_6mt", "2024 Civic Hatchback Sport Touring 1.5T 6MT offered in Canada", "bool", "critical", db.record(
        printed=(True, "bool"), source_id=s24, locator="DRIVETRAIN table; FUEL ECONOMY table; DIMENSIONS table",
        evidence=ev(s24, "6-speed manual transmission (MT)	 	Available", "Manual transmission (City/Hwy/Combined)	 	8.5/6.3/7.5", "Curb weight – MT/CVT (kg)", "1382/1412"),
        as_printed="Available (Sport Touring column only)", applicability=CA24ST6, confidence="high",
        notes="Offered per Honda Canada. In 2024 Canada the 6MT is listed only for Sport Touring (Sport column blank; Sport MT curb weight 'NA'). A Canadian-serial VIN (19XFL1G82RE400164) decodes in vPIC as 2024 Civic hatch 6MT 1.5T, but its listing (carpages.ca, Cambridge ON) returned HTTP 403 and was seen only as a search snippet."))

    # paint
    s23 = "id:hci-2023-specs"
    A("identity.paint_name", "Exterior colour name (Canada spelling)", "text", "high", db.record(
        printed=("Sonic Grey Pearl", "text"), source_id=s23, locator="EXTERIOR/INTERIOR COLOURS table",
        evidence=ev(s23, "Sonic Grey Pearl	NH-877P	 	Black/Combi Fabric	Black Leather"),
        as_printed="Sonic Grey Pearl", applicability=db.app("2023", "CA", "LX, Sport, Sport Touring", "all"),
        confidence="high", notes="US spelling is 'Sonic Gray Pearl' (hondainfocenter 2024)."))
    A("identity.paint_code", "Paint code", "text", "high", db.record(
        printed=("NH-877P", "text"), source_id=s23, locator="EXTERIOR/INTERIOR COLOURS table",
        evidence=ev(s23, "Sonic Grey Pearl	NH-877P"), as_printed="NH-877P",
        applicability=db.app("2023", "CA", "Sport Touring", "all"), confidence="high"))
    A("identity.paint_code", "Paint code", "text", "high", db.record(
        printed=("NH-877P", "text"), source_id="id:ahm-infocenter-2024-colors", locator="Colors table, Sonic Gray Pearl row",
        evidence=ev("id:ahm-infocenter-2024-colors", "Sonic Gray Pearl69", "[NH-877P]"), as_printed="[NH-877P]",
        applicability=db.app("2024", "US", "Sport, Sport Touring", "all"), confidence="high",
        notes="Second, independent (US, 2024) source agrees with Honda Canada 2023."))
    A("identity.sonic_grey_offered_2024_ca_st", "Sonic Grey Pearl offered on 2024 Canadian Civic Hatchback Sport Touring", "bool", "high", db.record(
        printed=(True, "bool"), status="estimated", cls="E", source_id=None, locator="inference from id:hci-2023-specs + id:ahm-infocenter-2024-colors",
        evidence="", as_printed="", range=[True, True],
        applicability=db.app("2023 CA / 2024 US", "CA+US", "Sport Touring", "all"), confidence="medium",
        how_to_measure="Check the real car's colour label (driver door jamb / VIN label) for NH877P, or a Honda Canada 2024 brochure / Build & Price archive.",
        notes="Not directly confirmed for 2024 Canada: Honda Canada's 2024 spec page has no colour table, honda.ca now shows the current model, web.archive.org is blocked and the sm360 2024 ST MT catalog page was blocked by the egress proxy. Evidence: Honda Canada 2023 lists Sonic Grey Pearl NH-877P with Black Leather on Sport Touring; American Honda 2024 lists Sonic Gray Pearl NH-877P with Black Leather on Sport Touring with no 'CVT only' restriction. No 2024 MY change to the colour list was found. The user's own car (if it is this colour) settles it."))
    A("identity.sonic_grey_offered_2023_ca_st", "Sonic Grey Pearl offered on 2023 Canadian Civic Hatchback Sport Touring", "bool", "medium", db.record(
        printed=(True, "bool"), source_id=s23, locator="EXTERIOR/INTERIOR COLOURS table",
        evidence=ev(s23, "EXTERIOR/INTERIOR COLOURS	 	LX	Sport	Sport Touring", "Sonic Grey Pearl	NH-877P	 	Black/Combi Fabric	Black Leather"),
        as_printed="Sport Touring: Black Leather", applicability=db.app("2023", "CA", "Sport Touring", "all"), confidence="high"))
    A("identity.interior_color", "Interior colour", "text", "medium", db.record(
        printed=("Black", "text"), source_id=s23, locator="EXTERIOR/INTERIOR COLOURS table, Sonic Grey Pearl row, Sport Touring column",
        evidence=ev(s23, "Sonic Grey Pearl	NH-877P	 	Black/Combi Fabric	Black Leather"), as_printed="Black Leather",
        applicability=db.app("2023", "CA", "Sport Touring", "all"), confidence="high",
        notes="US 2024 also offers only Black Leather with Sonic Gray Pearl on Sport Touring (Gray Leather is CVT-only and not with Sonic Gray)."))
    A("identity.seat_material", "Seat material", "text", "medium", db.record(
        printed=("Leather-trimmed seating surfaces", "text"), source_id=s24, locator="SEATING & TRIM table",
        evidence=ev(s24, "Leather-trimmed seating surfaces	 	•"), as_printed="Leather-trimmed seating surfaces (SPORT TOURING only)",
        applicability=CA24ST6, confidence="high"))
    A("identity.seating", "Seating capacity / adjustment", "text", "low", db.record(
        printed=("5 seats; driver 8-way power, passenger 4-way power; heated front and rear seats; 60/40 rear", "text"),
        source_id=s24, locator="SEATING & TRIM table",
        evidence=ev(s24, "Seating capacity	5	5", "Driver’s seat with 8-way power adjustment	 	•", "Front passenger’s seat with 4-way power adjustment	 	•", "Heated rear seats	 	•", "60/40 split fold-down rear seatback	•	•"),
        as_printed="5", applicability=CA24ST6, confidence="high"))
    A("identity.cluster_type", "Instrument cluster", "text", "high", db.record(
        printed=("10.2-inch colour TFT full digital driver meter display", "text"), source_id=s24, locator="COMFORT & CONVENIENCE table",
        evidence=ev(s24, "10.2\" colour TFT full digital driver meter display"), as_printed="10.2\" colour TFT full digital driver meter display (SPORT TOURING)",
        applicability=CA24ST6, confidence="high"))
    A("identity.options_ca_2024_st", "Factory options on 2024 Canadian Sport Touring", "text", "medium", db.record(
        printed=("Transmission (6MT or CVT) and colour only; no packages listed", "text"), status="estimated", cls="E",
        source_id=None, locator="inference from id:hci-2024-specs", evidence="", as_printed="", range=["n/a", "n/a"],
        applicability=CA24ST6, confidence="medium",
        how_to_measure="Check the real car's window sticker / Honda Canada order guide.",
        notes="Honda Canada's 2024 table lists every Sport Touring feature as standard ('•') except items marked 'CVT only'; the only 'Available' entry is the 6MT. Dealer accessories are not covered."))
    d["model_year_check"] = ("2022, 2023 and 2024 Honda Canada spec tables compared row by row (see my_2022_2024_changes). "
                             "Engine, ratings, bore/stroke, compression, track, wheelbase, tires, stabilizer bars, curb weight MT, "
                             "fuel economy MT, 10.2\" cluster and equipment of the Sport Touring are unchanged 2022→2024 in Canada.")
    return d


def tables(d):
    s24, s23, s22 = "id:hci-2024-specs", "id:hci-2023-specs", "id:hci-2022-specs"
    a24 = "2024 CA Civic Hatchback, Sport vs Sport Touring"

    def row(item, st, lower, sid, frags, app=a24, notes=""):
        return {"item": item, "sport_touring": st, "lower_trims": lower, "source_id": sid,
                "locator": "spec table", "evidence": ev(sid, *frags), "applicability": app, "notes": notes}

    d["trim_distinguishers"] = [
        row("Wheels", "18\" aluminum-alloy, machined with black inserts", "Sport: 18\" black alloys", s24,
            ["18\" aluminum-alloy wheels (black)", "18\" aluminum-alloy wheels (machined with black inserts)"],
            notes="2021 debut release said 'Shark Gray inserts' (pre-production); production tables say black inserts."),
        row("Fog lights", "LED fog lights", "Sport: none", s24, ["LED fog lights	 	•"]),
        row("Parking sensors", "Body-coloured front and rear parking sensors (visible in bumpers)", "Sport: none", s24, ["Body-coloured front and rear parking sensors", ]),
        row("Wipers", "Rain-sensing windshield wipers", "Sport: speed-sensing intermittent", s24, ["Rain-sensing windshield wipers	 	•", "Speed-sensing, variable intermittent windshield wipers	•	 "]),
        row("Instrument cluster", "10.2\" full digital TFT meter", "Sport: 7\" TFT centre meter with analogue speedometer", s24,
            ["7\" colour TFT centre meter display with Driver Information Interface", "10.2\" colour TFT full digital driver meter display"]),
        row("Infotainment", "9\" touchscreen with navigation, wireless CarPlay/Android Auto", "Sport: 7\" touchscreen, wired", s24,
            ["9\" colour touchscreen	 	Including Navigation2,5", "7\" colour touchscreen	•	 ", "Apple CarPlay®2,3 / Android Auto™2,3	Wired	Wired/Wireless"]),
        row("Audio", "BOSE 12 speakers incl. subwoofer", "Sport: 8 speakers", s24,
            ["BOSE® Premium Sound System with 12 speakers including subwoofer	 	•", "AM/FM audio system with 8 speakers	•	 "]),
        row("Seats", "Leather-trimmed; 8-way power driver; 4-way power passenger; heated rear", "Sport: black combi (synthetic leather/fabric), manual seats", s24,
            ["Black combi seats (synthetic leather/fabric)	•	 ", "Leather-trimmed seating surfaces	 	•", "Driver’s seat with 8-way power adjustment	 	•"]),
        row("Mirror", "Auto-dimming rearview mirror; HomeLink", "Sport: no", s24, ["Auto-dimming rearview mirror", "HomeLink® remote system6"]),
        row("Wireless charging / USB", "Wireless charging; 4 USB", "Sport: 3 USB", s24, ["Wireless charging", "USB device connector3	3	4"]),
        row("Exterior shared with Sport (not distinguishing)", "Dual exhaust finisher, moonroof, mirror LED turn signals, LED headlights, front splash guards", "same on Sport", s24,
            ["Duel exhaust finishe	•	•", "Mirror-integrated LED turn signal indicators	•	•", "One-touch power moonroof with tilt feature	•	•"]),
        row("LX (2022–2023 only) vs Sport Touring", "ST: dual exhaust finisher, moonroof, mirror turn signals, aluminium pedals, 18\" wheels", "LX: 16\" wheels, none of these", s23,
            ["16\" aluminum-alloy wheels 	•", "Duel exhaust finisher	 	•	•	•", "Aluminum-trimmed sport pedals	 	•	•	•"],
            app="2023 CA Civic Hatchback LX/Sport/Sport-B/Sport Touring"),
    ]
    d["manual_vs_cvt_cabin"] = [
        {"item": "Gear selector", "manual": "6-speed manual shifter (three pedals implied)", "cvt": "CVT selector",
         "source_id": s24, "locator": "DRIVETRAIN", "evidence": ev(s24, "6-speed manual transmission (MT)	 	Available"),
         "applicability": a24, "notes": "Shifter knob/boot appearance: see references/ (domain 9); not stated by Honda Canada."},
        {"item": "Paddle shifters", "manual": "absent", "cvt": "present", "source_id": s24, "locator": "DRIVETRAIN",
         "evidence": ev(s24, "Steering wheel-mounted paddle shifters", "CVT only"), "applicability": a24, "notes": ""},
        {"item": "Drive mode switch (Normal/Econ/Sport)", "manual": "not listed (CVT only)", "cvt": "present", "source_id": s24, "locator": "DRIVETRAIN",
         "evidence": ev(s24, "Three-mode drive system (Normal, Econ, Sport)    	•	CVT only"), "applicability": a24,
         "notes": "2022 table lists an 'ECON mode button' on all trims incl. MT; whether the 2024 MT car has an ECON button is unconfirmed."},
        {"item": "Parking brake", "manual": "Electronic Parking Brake with automatic brake hold (no hand lever)", "cvt": "same", "source_id": s24, "locator": "CHASSIS",
         "evidence": ev(s24, "Electronic Parking Brake (EPB) with automatic brake hold"), "applicability": a24, "notes": "Listed without a CVT-only qualifier."},
        {"item": "Idle-stop", "manual": "listed '•' for Sport Touring without qualifier", "cvt": "listed", "source_id": s24, "locator": "ENGINE",
         "evidence": ev(s24, "Idle-stop"), "applicability": a24,
         "notes": "Conflicting hint: 2021 debut release says idle-stop is 'CVT only' (sentence about the 2.0 L LX). Whether the 6MT 1.5T car has idle-stop is UNCONFIRMED; check the owner's manual or the real car."},
        {"item": "Adaptive Cruise Control", "manual": "ACC without Low-Speed Follow", "cvt": "ACC with Low-Speed Follow", "source_id": s24, "locator": "DRIVER ASSIST TECHNOLOGY",
         "evidence": ev(s24, "Adaptive Cruise Control (ACC)2 with Low-Speed Follow (HS*)	 	CVT only"), "applicability": a24,
         "notes": "2022 table: 'Adaptive Cruise Control (ACC)2  with Low-Speed Follow (HS*) *LSF on CVT only'."},
        {"item": "Traffic Jam Assist / Low-speed braking control", "manual": "absent", "cvt": "present", "source_id": s24, "locator": "DRIVER ASSIST TECHNOLOGY",
         "evidence": ev(s24, "Low-speed braking control	 	CVT only", "Traffic Jam Assist2	•	CVT only"), "applicability": a24, "notes": ""},
        {"item": "Remote engine starter", "manual": "absent", "cvt": "present", "source_id": s24, "locator": "COMFORT & CONVENIENCE",
         "evidence": ev(s24, "Remote engine starter", "CVT only"), "applicability": a24, "notes": ""},
        {"item": "Pedals", "manual": "Aluminum-trimmed sport pedals (clutch, brake, throttle)", "cvt": "aluminium-trimmed (2 pedals)", "source_id": s24, "locator": "COMFORT & CONVENIENCE",
         "evidence": ev(s24, "Aluminum-trimmed sport pedals"), "applicability": a24, "notes": ""},
        {"item": "Rev-match control", "manual": "UNKNOWN (not listed for Civic Hatchback; do not assume the Si's rev-matching)", "cvt": "n/a",
         "source_id": None, "locator": "", "evidence": "", "applicability": a24,
         "notes": "Not mentioned in any Honda Canada 2022–2024 hatchback table or release opened. Verify on the real car (blip on downshift with clutch in)."},
        {"item": "Flywheel", "manual": "dual-mass flywheel (lead for drivetrain domain)", "cvt": "n/a", "source_id": "id:hci-2022-debut", "locator": "Sporty and Fun Powertrains",
         "evidence": ev("id:hci-2022-debut", "A new dual-mass flywheel helps reduce noise and vibration transmitted through the drivetrain."),
         "applicability": "2022 North America hatchback 6MT", "notes": ""},
    ]
    d["us_ca_differences"] = [
        {"item": "Trim line-up 2024", "canada": "Sport (1.5T, CVT only), Sport Touring (1.5T, CVT or 6MT)",
         "us": "LX, Sport, EX-L, Sport Touring", "source_ids": [s24, "id:ahm-infocenter-2024-colors"], "locator": "table headings",
         "evidence": ev(s24, "SPORT TOURING") + " | " + ev("id:ahm-infocenter-2024-colors", "LX", "Sport", "EX-L", "Sport Touring"),
         "notes": "US Sport is 2.0 L (US 1.5T trims: EX-L, Sport Touring) per Honda US; Canadian Sport is 1.5T. US engine split from US page not opened (automobiles.honda.com 403)."},
        {"item": "Manual availability 2024", "canada": "Sport Touring only", "us": "Sport and Sport Touring (US Sport = 2.0 L)", "source_ids": [s24],
         "locator": "DRIVETRAIN", "evidence": ev(s24, "6-speed manual transmission (MT)	 	Available"),
         "notes": "US side from the 2021 debut release ('6-speed manual transmission is available in all grades') and US colour table MT rows; not a 2024 US spec sheet."},
        {"item": "Paint name spelling", "canada": "Sonic Grey Pearl", "us": "Sonic Gray Pearl", "source_ids": [s23, "id:ahm-infocenter-2024-colors"],
         "locator": "colour tables", "evidence": ev(s23, "Sonic Grey Pearl") + " | " + ev("id:ahm-infocenter-2024-colors", "Sonic Gray Pearl69"), "notes": "Same code NH-877P."},
        {"item": "Units/cluster", "canada": "metric (L/100 km, km/h primary)", "us": "imperial", "source_ids": [s24], "locator": "FUEL ECONOMY",
         "evidence": ev(s24, "FUEL ECONOMY9 (L/100 KM)"), "notes": "Cluster unit details: domain 9."},
        {"item": "Sport Touring MT feature gaps (Canada)", "canada": "ACC LSF, Traffic Jam Assist, Low-speed braking control, remote starter: CVT only", "us": "not checked (US spec page blocked)",
         "source_ids": [s24], "locator": "DRIVER ASSIST TECHNOLOGY", "evidence": ev(s24, "Low-speed braking control	 	CVT only"), "notes": ""},
        {"item": "Model/VIN serial block", "canada": "Canadian cars observed with serial 4xxxxx (e.g. 19XFL1H87RE400675)", "us": "US cars observed with serial 0xxxxx (search snippets only)",
         "source_ids": ["id:cuv-hatch-list"], "locator": "listing VINs", "evidence": ev("id:cuv-hatch-list", "VIN: 19XFL1H87RE400675"), "notes": "Observation, not a Honda statement."},
    ]
    d["my_2022_2024_changes"] = [
        {"change": "Canadian hatch line-up: 2022 LX/Sport/Sport Touring; 2023 adds Sport-B, Sport becomes CVT-only; 2024 LX dropped (Sport and Sport Touring only)",
         "affects_target": False, "source_ids": [s22, s23, s24],
         "evidence": ev(s22, "ENGINE	LX	Sport	Sport Touring") + " | " + ev(s23, "ENGINE	LX	Sport	Sport-B	Sport Touring") + " | " + ev(s24, "SPORT TOURING"), "notes": ""},
        {"change": "Sport Touring MT data unchanged 2022→2024: 180 hp @ 6000, 177 lb-ft @ 1700-4500, 1498 cc, 73 x 89.5, 10.3:1, 235/40R18 91W, stabilizers 26.5/17.5, track 1536/1565, wheelbase 2735, curb weight MT 1382 kg, MT fuel 8.5/6.3/7.5",
         "affects_target": False, "source_ids": [s22, s24],
         "evidence": ev(s22, "Curb weight (kg) MT/CVT	1322/1333	1361/1391	1382/1412") + " | " + ev(s24, "1382/1412", "8.5/6.3/7.5", "26.5/17.5"),
         "notes": "So 2022–2023 Sport Touring MT data are usable for the 2024 target where the record says so."},
        {"change": "Width presentation: 2022/2023 'Mirrors open/Mirrors folded 2081/1900'; 2024 lists 'Width (mm) 1802'", "affects_target": False,
         "source_ids": [s22, s24], "evidence": ev(s22, "2081/1900") + " | " + ev(s24, "Width (mm)      	1802	1802"),
         "notes": "Different measurement definitions, not a body change; dimensions domain resolves."},
        {"change": "Length presentation: 2022/2023 '4547/4529' (with/without licence bracket); 2024 '4529'", "affects_target": False,
         "source_ids": [s23, s24], "evidence": ev(s23, "4547/4529") + " | " + ev(s24, "4529"), "notes": ""},
        {"change": "2024 table adds 'Steering wheel turns, lock-to-lock 2.2' and 'Steering ratio 11.4:1' (not in 2022/2023 tables)", "affects_target": False,
         "source_ids": [s24], "evidence": ev(s24, "Steering wheel turns, lock-to-lock", "11.4:1"), "notes": "New disclosure, not evidence of a change."},
        {"change": "TPMS type decodes 'Indirect' for MY2022/2023 FL1G8 patterns and 'Direct' for MY2024 (vPIC only)", "affects_target": "unconfirmed",
         "source_ids": ["id:vpic"], "evidence": "19XFL1G8*NE TPMS: Indirect; 19XFL1G8*PE TPMS: Indirect; 19XFL1G8*RE TPMS: Direct",
         "notes": "Low confidence; may be a database entry difference. Check the 2024 owner's manual (TPMS vs Deflation Warning System) or the real car's valve stems."},
        {"change": "Colour list 2024 (US): Boost Blue, Smokey Mauve, Crystal Black, Lunar Silver, Meteorite Gray, Rallye Red, Sonic Gray, Platinum White; Canada 2023: Boost Blue, Crystal Black, Meteoroid Grey, Platinum White, Rallye Red, Sonic Grey",
         "affects_target": False, "source_ids": [s23, "id:ahm-infocenter-2024-colors"],
         "evidence": ev(s23, "Meteoroid Grey Metallic	NH-904M") + " | " + ev("id:ahm-infocenter-2024-colors", "Lunar Silver Metallic"), "notes": "Canada 2024 colour list not found."},
    ]
    d["facelift_2025_exclusions"] = [
        {"change": "New more aggressive front fascia and grille on every 2025 Civic", "source_id": "id:hci-2025-refresh",
         "evidence": ev("id:hci-2025-refresh", "The exterior styling of every 2025 Honda Civic is enhanced with a new more aggressive front fascia and grille")},
        {"change": "Hybrid replaces the 1.5T in Canada; non-hybrid Sport/LX use the 2.0 L", "source_id": "id:hci-2025-refresh",
         "evidence": ev("id:hci-2025-refresh", "The Civic LX and Sport trims continue to be powered by the responsive and efficient 2.0-liter 4-cylinder engine", "The resulting performance is even quicker than the outgoing 1.5L turbo-powered Civic.")},
        {"change": "New wheels (machine-finished design exclusive to Sport Touring Hybrid) and three new colours", "source_id": "id:hci-2025-refresh",
         "evidence": ev("id:hci-2025-refresh", "A new machine-finished wheel design is exclusive to the top-of-the-line Sport Touring Hybrid.", "Three new colors including Solar Silver Metallic, Urban Grey Pearl and Blue Lagoon Pearl")},
        {"change": "Front USB-C ports, Google built-in (ST Hybrid) — 2025 cabin details to exclude", "source_id": "id:hci-2025-refresh",
         "evidence": ev("id:hci-2025-refresh", "All Civic models now come standard with front USB-C ports.")},
    ]
    d["vin_decodes"] = []
    for v, origin in [("19XFL1G82RE400164", "search snippet of carpages.ca Cambridge ON listing (page 403, not opened); Canadian serial block"),
                      ("19XFL1G8*RE", "pattern"), ("19XFL1G8*PE", "pattern"), ("19XFL1G8*NE", "pattern"),
                      ("19XFL1H87RE400675", "cuv.honda.ca 2024 Civic Hatchback 'Sport Touring Rare', Winnipeg, CVT"),
                      ("19XFL1H84RE400858", "cuv.honda.ca 2024 Civic Hatchback 'Sport', Toronto, CVT (vPIC says Sport Touring: trim decode unreliable for CA)"),
                      ("19XFL1G86NE401019", "cuv.honda.ca 2022 Civic Hatchback 'Sport', Truro NS, Man. (vPIC says Sport Touring)")]:
        dec, p = decode(v)
        d["vin_decodes"].append({"vin": v, "origin": origin, "api_url": vpic_url(v), "cache_file": p, "decode": dec})


if __name__ == "__main__":
    d = build()
    tables(d)
    print(db.save(d))
