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
