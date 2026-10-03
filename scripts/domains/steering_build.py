#!/usr/bin/env python3
"""Builds vehicle_data/steering.json (domain 6). Records are built with dbutil so unit
conversion is done by code. Evidence strings are whitespace-normalised verbatim copies
from the cached page text (cache_file in each source)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.chdir(ROOT)
import dbutil as db  # noqa: E402

d = {"domain": "steering", "title": "Steering", "schema_version": 1, "updated": db.today(),
     "sources": {}, "parameters": {}}

# ------------------------------------------------------------------ sources
db.add_source(d, "steer:hondanews-ca-2024-hatch-specs",
              title="2024 Honda Civic Hatchback Specifications (release, April 4, 2024)",
              url="https://hondanews.ca/en-CA/releases/release-1128768177ab00a73471b1938c152ddf-2024-honda-civic-hatchback-specifications",
              publisher="Honda Canada Inc. (Honda Canada News)", cls="A", access_method="rendered",
              applicability="2024 Civic Hatchback, Canada, SPORT and SPORT TOURING columns (1.5T; Sport Touring 6MT or CVT)",
              notes="Steering rows are in the DIMENSIONS table, not per gearbox.",
              cache_file="cache/pages/22157798d6e48e1c.txt")
db.add_source(d, "steer:hondanews-ca-2022-hatch-specs",
              title="2022 Civic Hatchback Specifications (release, October 12, 2021)",
              url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-9d4b663caef09e412c833d744c4365f9-2022-civic-hatchback-specifications",
              publisher="Honda Canada Inc. (Honda Canada News)", cls="A", access_method="static",
              applicability="2022 Civic Hatchback, Canada, LX / Sport / Sport Touring columns",
              cache_file="cache/pages/344bc90bb36560a9.txt")
db.add_source(d, "steer:hondanews-ca-2023-hatch-specs",
              title="2023 Civic Hatchback Specifications (release, April 13, 2023)",
              url="https://hondanews.ca/en-CA/hci-automobiles/releases/release-f61ab7d13cb83fb181b8bc22df100303-2023-civic-hatchback-specifications",
              publisher="Honda Canada Inc. (Honda Canada News)", cls="A", access_method="static",
              applicability="2023 Civic Hatchback, Canada, LX / Sport / Sport-B / Sport Touring columns",
              cache_file="cache/pages/374416cf6bc6db5d.txt")
db.add_source(d, "steer:hondanews-us-2024-hatch-specs",
              title="2024 Honda Civic Hatchback Specifications & Features",
              url="https://hondanews.com/en-US/honda-automobiles/releases/2024-honda-civic-hatchback-specifications-features",
              publisher="American Honda Motor Co., Inc. (Honda News)", cls="A", access_method="static",
              applicability="2024 Civic Hatchback, US market, columns LX / Sport / EX-L / Sport Touring (HTML table column order verified in cache .html)",
              cache_file="cache/pages/2b1524caf89378a3.txt")
db.add_source(d, "steer:hondainfocenter-us-2024-hatch-specs",
              title="2024 Civic Hatchback - Specifications (Honda Information Center feature guide)",
              url="https://www.hondainfocenter.com/2024/Civic-Hatchback/Feature-Guide/Civic-Hatchback-Specifications/",
              publisher="American Honda Motor Co., Inc.", cls="A", access_method="static",
              applicability="2024 Civic Hatchback, US market, LX / Sport / EX-L / Sport Touring columns",
              notes="Same publisher as hondanews.com US, so not an independent source; used as a consistency check.",
              cache_file="cache/pages/b67f7f855816944e.txt")
db.add_source(d, "steer:hondanews-us-2022-hatch-specs",
              title="2022 Honda Civic Hatchback Specifications & Features",
              url="https://hondanews.com/en-US/honda-automobiles/releases/release-cb177600e922c8a5fcfa01b9b80149e2-2022-honda-civic-hatchback-specifications-features",
              publisher="American Honda Motor Co., Inc. (Honda News)", cls="A", access_method="static",
              applicability="2022 Civic Hatchback, US market, LX / Sport / EX-L / Sport Touring columns",
              notes="Model-year check: steering rows identical to the 2024 US table.",
              cache_file="cache/pages/fb1d5790fd3bfda8.txt")
db.add_source(d, "steer:hondanews-us-2022-hatch-debut",
              title="2022 Honda Civic Hatchback Makes Global Debut During Honda Civic Remix Virtual Performance",
              url="https://hondanews.com/en-US/releases/release-53541be6030b25a47a2899aba12f09d7-2022-honda-civic-hatchback-makes-global-debut-during-honda-civic-remix-virtual-performance",
              publisher="American Honda Motor Co., Inc. (Honda News)", cls="A", access_method="static",
              applicability="2022 Civic Hatchback, US market, all trims (narrative press release)",
              cache_file="cache/pages/6b8fd454f6a040ce.txt")

A24CA = db.app("2024", "CA", "Sport Touring", "6MT or CVT (row not split by gearbox)")
A24US = db.app("2024", "US", "Sport Touring", "6MT or CVT (row not split by gearbox)")
A22US = db.app("2022", "US", "Sport Touring", "6MT or CVT (row not split by gearbox)",
               notes="Model-year check: same value printed in the 2024 US table.")
A22CA = db.app("2022", "CA", "Sport Touring", "6MT or CVT (row not split by gearbox)",
               notes="Model-year check: same value printed in the 2023 and 2024 Canadian tables.")

# ------------------------------------------------------------------ steering type
K = "steering.type"
DESC = "Steering system type"
db.add_candidate(d, K, DESC, "text", "medium", db.record(
    value="Variable-ratio electric power-assisted rack-and-pinion (EPS)", unit="text",
    status="confirmed", cls="A", source_id="steer:hondanews-ca-2024-hatch-specs",
    locator="CHASSIS table, row 'Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS)', SPORT TOURING column",
    evidence="Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS) • •",
    as_printed="Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS)",
    applicability=A24CA, confidence="high",
    notes="Honda does not say in public material whether the EPS is column-, pinion- or dual-pinion-assisted; see steering.assist_layout."))
db.add_candidate(d, K, DESC, "text", "medium", db.record(
    value="Variable-ratio electric power-assisted rack-and-pinion (EPS)", unit="text",
    status="confirmed", cls="A", source_id="steer:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS)', all four columns",
    evidence="Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS) • • • •",
    as_printed="Variable Ratio Electric Power-Assisted Rack-and-Pinion Steering (EPS)",
    applicability=A24US, confidence="high"))

# ------------------------------------------------------------------ overall ratio
K = "steering.ratio_overall"
DESC = "Steering ratio as published by Honda (handwheel angle / road-wheel angle); Honda publishes one figure for a variable-ratio rack"
NOTE_RATIO = ("Honda prints a single 'steering ratio' for a variable-ratio rack and does not say whether it is the "
              "on-centre or the overall (lock-to-lock average) ratio. Treated as the overall ratio because "
              "turns x 360 / (2 x ratio) gives a mean lock angle consistent with the published turning circle "
              "(cross-check registered in scripts/derivations/steering.py). Sport/Sport Touring (18-in wheels) "
              "print 11.41:1 and 2.21 turns; LX/EX-L (16/17-in) print 11.27:1 and 2.29 turns.")
db.add_candidate(d, K, DESC, "1", "high", db.record(
    printed=(11.4, "ratio"), status="confirmed", cls="A", source_id="steer:hondanews-ca-2024-hatch-specs",
    locator="DIMENSIONS table, row 'Steering ratio – (curb-to-curb) (m)', SPORT TOURING column",
    evidence="Steering ratio – (curb-to-curb) (m) 11.4:1 11.4:1",
    as_printed="11.4:1", applicability=A24CA, confidence="high",
    notes=NOTE_RATIO + " The Canadian row label carries a copy-paste unit '(curb-to-curb) (m)'; the value is a ratio. "
          "Canadian figure is rounded to one decimal; agrees with the US 11.41:1."))
db.add_candidate(d, K, DESC, "1", "high", db.record(
    printed=(11.41, "ratio"), status="confirmed", cls="A", source_id="steer:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Steering Ratio', 4th column (Sport Touring)",
    evidence="Steering Ratio 11.27:1 11.41:1 11.27:1 11.41:1",
    as_printed="11.41:1", applicability=A24US, confidence="high", notes=NOTE_RATIO))
db.add_candidate(d, K, DESC, "1", "high", db.record(
    printed=(11.41, "ratio"), status="confirmed", cls="A", source_id="steer:hondainfocenter-us-2024-hatch-specs",
    locator="Body/Suspension/Chassis table, row 'Steering Ratio', Sport Touring column",
    evidence="Steering Ratio 11.27 : 1 11.41 : 1 11.27 : 1 11.41 : 1",
    as_printed="11.41 : 1", applicability=A24US, confidence="high",
    notes="Same publisher as hondanews.com (American Honda); consistency check only."))
db.add_candidate(d, K, DESC, "1", "high", db.record(
    printed=(11.41, "ratio"), status="confirmed", cls="A", source_id="steer:hondanews-us-2022-hatch-specs",
    locator="CHASSIS table, row 'Steering Ratio', Sport Touring column",
    evidence="Steering Ratio | 11.27 : 1 | 11.41 : 1 | 11.27 : 1 | 11.41 : 1".replace(" |", ""),
    as_printed="11.41 : 1", applicability=A22US, confidence="high",
    notes="Model-year check 2022 vs 2024: unchanged."))

# ------------------------------------------------------------------ turns lock to lock
K = "steering.turns_lock_to_lock"
DESC = "Steering wheel turns, lock to lock"
db.add_candidate(d, K, DESC, "turns", "high", db.record(
    printed=(2.2, "turns"), status="confirmed", cls="A", source_id="steer:hondanews-ca-2024-hatch-specs",
    locator="DIMENSIONS table, row 'Steering wheel turns, lock-to-lock', SPORT TOURING column",
    evidence="Steering wheel turns, lock-to-lock 2.2 2.2", as_printed="2.2",
    applicability=A24CA, confidence="high",
    notes="Canadian figure rounded to one decimal; agrees with US 2.21."))
db.add_candidate(d, K, DESC, "turns", "high", db.record(
    printed=(2.21, "turns"), status="confirmed", cls="A", source_id="steer:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Steering Wheel Turns, Lock-to-Lock', 4th column (Sport Touring)",
    evidence="Steering Wheel Turns, Lock-to-Lock 2.29 2.21 2.29 2.21", as_printed="2.21",
    applicability=A24US, confidence="high"))
db.add_candidate(d, K, DESC, "turns", "high", db.record(
    printed=(2.21, "turns"), status="confirmed", cls="A", source_id="steer:hondanews-us-2022-hatch-specs",
    locator="CHASSIS table, row 'Steering Wheel Turns, Lock-to-Lock', Sport Touring column",
    evidence="Steering Wheel Turns, Lock-to-Lock 2.29 2.21 2.29 2.21", as_printed="2.21",
    applicability=A22US, confidence="high", notes="Model-year check 2022 vs 2024: unchanged."))

# ------------------------------------------------------------------ turning circle
K = "steering.turning_circle_diameter"
DESC = "Turning circle diameter, curb-to-curb (path of the outer front tyre)"
db.add_candidate(d, K, DESC, "m", "medium", db.record(
    printed=(11.6, "m"), status="confirmed", cls="A", source_id="steer:hondanews-ca-2024-hatch-specs",
    locator="DIMENSIONS table, row 'Turning radius – (curb-to-curb) (m)', SPORT TOURING column",
    evidence="Turning radius – (curb-to-curb) (m) 11.6 11.6", as_printed="11.6 m",
    applicability=A24CA, confidence="high",
    notes=("Printed label says 'Turning radius' but the figure is the curb-to-curb DIAMETER: it equals the US "
           "'Turning Diameter, Curb-to-Curb' 38.1 ft (11.61 m) for the same trim, and a radius of 11.6 m would need a "
           "mean road-wheel lock of only ~14 deg, inconsistent with 2.2 turns at 11.4:1 (~35 deg). Lower trims print "
           "11 m (= US 36.1 ft) in the same row. Sport/Sport Touring (18-in wheel) turning circle is larger than "
           "LX/EX-L because lock is reduced (2.21 vs 2.29 turns).")))
db.add_candidate(d, K, DESC, "m", "medium", db.record(
    printed=(38.1, "ft"), status="confirmed", cls="A", source_id="steer:hondanews-us-2024-hatch-specs",
    locator="CHASSIS table, row 'Turning Diameter, Curb-to-Curb (ft.)', 4th column (Sport Touring)",
    evidence="Turning Diameter, Curb-to-Curb (ft.) 36.1 38.1 36.1 38.1", as_printed="38.1 ft",
    applicability=A24US, confidence="high"))
db.add_candidate(d, K, DESC, "m", "medium", db.record(
    printed=(38.1, "ft"), status="confirmed", cls="A", source_id="steer:hondainfocenter-us-2024-hatch-specs",
    locator="Body/Suspension/Chassis table, row 'Turning Diameter, Curb-to-Curb', Sport Touring column",
    evidence="Turning Diameter, Curb-to-Curb 36.1 ft 38.1 ft 36.1 ft 38.1 ft", as_printed="38.1 ft",
    applicability=A24US, confidence="high", notes="Same publisher as hondanews.com; consistency check."))
db.add_candidate(d, K, DESC, "m", "medium", db.record(
    printed=(11.6, "m"), status="confirmed", cls="A", source_id="steer:hondanews-ca-2022-hatch-specs",
    locator="DIMENSIONS table, row 'Turning radius (m) (curb-to-curb)', Sport Touring column",
    evidence="Turning radius (m) (curb-to-curb) 11 11.6 11.6", as_printed="11.6",
    applicability=A22CA, confidence="high",
    notes="Model-year check 2022 vs 2024 (Canada): unchanged. Label says radius; value is the diameter (see 2024 record)."))

db.save(d, os.path.join(ROOT, "vehicle_data", "steering.json"))
print("saved steering.json")
