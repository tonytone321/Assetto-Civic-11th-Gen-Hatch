#!/usr/bin/env python3
"""Coordinator cross-domain additions made during integration (re-runnable).

Adds leads one thread found that belong in another domain's file, with the same
evidence rules. Every quote is checked against the cached page before saving."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dbutil as db  # noqa: E402
from validate_db import norm  # noqa: E402

ROOT = db.ROOT


def cached(path, *frags):
    hay = norm(open(os.path.join(ROOT, path), encoding="utf-8").read())
    for f in frags:
        if norm(f) not in hay:
            sys.exit(f"quote not in {path}: {f!r}")
    return " … ".join(frags)


t = db.load("tires")
CD = "perf:cd-2022-civic-hatch-st-6mt"
cd_src = db.load("validation_targets")["sources"][CD]
t["sources"][CD] = cd_src
ev = cached(cd_src["cache_file"], "Our Sonic Gray Civic Sport Touring test car",
            "hunky 235/40R-18 Continental ContiProContact all-season tires")
db.add_candidate(t, "tires.make_model", "Factory tire make and model", "text", "high", db.record(
    value="Continental ContiProContact", unit="text", status="confirmed", cls="C", source_id=CD,
    locator="article body, paragraph 3; spec box 'Tires: Continental ContiProContact'", evidence=ev,
    as_printed="Continental ContiProContact", confidence="medium",
    applicability=db.app("2022", "US", "Sport Touring", "6MT"),
    how_to_measure="Read the sidewall of the car's original tires (brand, line, OE marking, DOT date).",
    notes="Fitted to Car and Driver's 2022 US Sport Touring 6MT test car. Honda may source more than one OE tire "
          "(the tire thread's unverified lead was Goodyear Eagle Sport All-Season); confirm on the target car."))

RS = "tires:tirediscounters-contiprocontact-235-40r18"
rs_path = "cache/pages/d5faa74c61813f3e.txt"
db.add_source(t, RS, "235/40R18 Continental ContiProContact 91W BSW SL (product page)",
              "https://tirediscounters.com/products/235-40r18-continental-contiprocontact-91w-bsw-sl-2354018-235-40-18",
              "Tire Discounters (retailer)", "C", access_method="static",
              applicability="Continental ContiProContact 235/40R18 91W (replacement-market listing, not OE-specific)",
              notes="Retailer spec table; Continental's own product page returned 404.", cache_file=rs_path)
app = db.app("n/a", "US", "tire: ContiProContact 235/40R18 91W", "n/a", notes="tire spec, not vehicle-specific")
db.add_candidate(t, "tires.overall_diameter", "Tire overall diameter (unloaded, published)", "m", "high", db.record(
    printed=(25.4, "in"), status="confirmed", cls="C", source_id=RS, locator="spec table 'Overall Diameter'",
    evidence=cached(rs_path, "Overall Diameter", "| 25.4 |"), as_printed="25.4", applicability=app,
    confidence="low", how_to_measure="Tape the circumference of the inflated, unloaded tire and divide by pi.",
    notes="Retailer figure for the tire model on Car and Driver's test car; OE fitment on the target car unconfirmed."))
db.add_candidate(t, "tires.revs_per_mile", "Tire revolutions per mile (published)", "count", "high", db.record(
    value=818, unit="count", status="confirmed", cls="C", source_id=RS, locator="spec table 'Revolutions Per Mile'",
    evidence=cached(rs_path, "Revolutions Per Mile | 818"), as_printed="818", applicability=app,
    confidence="low", how_to_measure="Roll the car 10 wheel turns on level ground at rated pressure and measure the distance.",
    notes="Per mile. Used by the coordinator derivation tires.rolling_circumference_from_revs as a cross-check."))
db.save(t)
print("tires.json updated")

# The engine thread found no rpm-resolved stock 6MT curve; make the gap a first-class unknown so it is
# ranked in docs/UNCERTAINTIES.md (engine_curve.csv has no rows).
e = db.load("engine")
db.add_candidate(e, "engine.torque_curve_stock_6mt", "Stock torque/power vs rpm curve for the 1.5T 6MT "
                 "(crank or wheel, with boost onset, plateau and taper)", "N*m", "critical", db.unknown(
    "N*m",
    searches=["hondanews.ca / hondainfocenter.com / hondanews.com spec and powertrain pages (rated points only)",
              "Hondata 2022 EX sedan CVT stock dyno via The Drive (CVT, peak only)",
              "PRL Motorsports 2022 Touring sedan CVT baselines (CVT, speed x-axis)",
              "TSP 2022 non-Si CVT stock dyno (CVT, peak only)",
              "hondata.com (robots.txt disallows; not fetched)",
              "civicxi.com / reddit / forum dyno threads (no stock 6MT hatch rpm curve found)"],
    how_to_measure="Stock car, chassis dyno (state make: Dynojet/Mustang/Dynapack), SAE J1349 correction, 4th gear "
                   "(or 3rd), 3 pulls from 1500 rpm to fuel cut, with a simultaneous OBD log of rpm, MAP and "
                   "throttle. Export the rpm-resolved CSV, not just the chart.",
    notes="Rated anchor points (180 hp @ 6000, 177 lb-ft @ 1700-4500, class A) are in engine.json; the shape "
          "between them, boost onset below 1700 rpm and the taper above 4500 rpm are unsourced."))
db.save(e)
print("engine.json updated")

# audio.exhaust_layout quoted two part pages under one source id, and one fragment
# ("FINISHER" line) was not on the cached page. Re-quote from the cached source page only,
# keep the diagram reading as an explicit [image] description, and add the left-muffler
# page as its own source and candidate.
au = db.load(os.path.join(ROOT, "audio", "reference_database.json"))
lay = au["parameters"]["audio.exhaust_layout"]["candidates"][0]
lay["evidence"] = cached("cache/pages/cc897d0f556a8710.txt",
                         "18307-T47-A51 MUFFLER, R- EX is Ref No. 9 in the diagram below") + \
    " … [image] diagram T404B0200: ref 9 drawn as centre pipe with a cylindrical in-line silencer, " \
    "Y-junction and a rear box; ref 8 a second rear box; refs 10/11 tip finishers"
lay["notes"] = (lay.get("notes", "") + " Coordinator: evidence re-quoted from this source's cached page only; "
                "the left-muffler fact is a separate candidate citing hpn-18305-T47-A51; the 18310-T47-A52 "
                "finisher line was not found on the cached page and was dropped from the quote.").strip()
HL = "hpn-18305-T47-A51"
db.add_source(au, HL, "18305-T47-A51 Genuine Honda MUFFLER, L- EX (part page)",
              "https://www.hondapartsnow.com/genuine/honda~muffler~l~ex~18305-t47-a51.html", "HondaPartsNow", "A",
              access_method="static", applicability="2022-2024 Civic 5-door Sport Touring 6MT, CVT (fitment list)",
              cache_file="cache/pages/5310f0c70dcb3019.txt")
db.add_candidate(au, "audio.exhaust_rear_muffler_left", "Left rear muffler part and diagram position", "text", "medium",
    db.record(value="18305-T47-A51 MUFFLER, L- EX, diagram ref 8", unit="text", status="confirmed", cls="A",
              source_id=HL, locator="part page 'Ref No.' line and Vehicle Fitment table",
              evidence=cached("cache/pages/5310f0c70dcb3019.txt", "18305-T47-A51 MUFFLER, L- EX is", "Ref No. 8",
                              "2024 Honda Civic | 5 Door 1.5T Sport Touring | 6MT, CVT"),
              as_printed="18305-T47-A51 MUFFLER, L- EX … Ref No. 8",
              applicability=db.app("2022-2024", "US", "Sport Touring", "6MT, CVT"), confidence="high",
              how_to_measure="Underside photo of the rear exhaust.",
              notes="US parts catalog (HondaPartsNow, Honda OEM retailer). Canadian part numbers not checked."))
db.save(au, os.path.join(ROOT, "audio", "reference_database.json"))
print("audio/reference_database.json updated")
