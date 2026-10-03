#!/usr/bin/env python3
"""Build audio/reference_database.json (Domain 10, audio).

Everything here was read from opened pages cached under cache/pages/ (git-ignored).
No audio or video was downloaded or analyzed: YouTube playback is behind a bot wall
in this sandbox and downloading from streaming sites is contrary to their terms.
Clip entries therefore describe only what the TEXT (title, description, comments)
states; sound content is recorded as not analyzed.

Run: python3 scripts/domains/audio_build.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import dbutil as db  # noqa: E402

OUT = os.path.join(db.ROOT, "audio", "reference_database.json")
ACC = "2026-10-03"

d = {"domain": "audio", "title": "Audio reference database", "schema_version": 1,
     "updated": ACC, "sources": {}, "parameters": {}, "clips": [], "products": [],
     "reference_clip": {}}

NOT_ANALYZED = ("NOT ANALYZED. The audio was not listened to or processed: YouTube playback "
                "is gated by a 'Sign in to confirm you're not a bot' wall in this sandbox, and "
                "downloading/ripping streaming media is contrary to the site's terms. Pop count, "
                "spacing, duration, tone, level and delay after throttle close are unknown.")

# ------------------------------------------------------------------ sources
S = {}


def src(sid, title, url, publisher, cls, cache, method="static", appl="", notes=""):
    db.add_source(d, sid, title=title, url=url, publisher=publisher, cls=cls, accessed=ACC,
                  access_method=method, applicability=appl, notes=notes, cache_file=cache)
    S[sid] = True
    return sid


src("hpn-2024-civic-exhaust-pipe",
    "Genuine 2024 Honda Civic Exhaust Pipe (catalog listing with submodel fitment)",
    "https://www.hondapartsnow.com/oem-2024-honda-civic-exhaust_pipe.html",
    "HondaPartsNow (Genuine Parts Now Inc., US Honda parts retailer; Honda EPC data)", "A",
    "cache/pages/220275fc0acb9df8.txt",
    appl="2024 Honda Civic, US catalog, all trims, fitment listed per submodel",
    notes="Class A as a reproduction of Honda's parts catalog (part numbers/fitment), US market. "
          "Canadian EPC not checked (no open Canadian catalog found).")
src("hpn-2024-civic-muffler",
    "Genuine 2024 Honda Civic Muffler (catalog listing with submodel fitment)",
    "https://www.hondapartsnow.com/oem-2024-honda-civic-muffler.html",
    "HondaPartsNow", "A", "cache/pages/27d21fe7b393c3a0.txt",
    appl="2024 Honda Civic, US catalog")
src("hpn-18307-T47-A51", "18307-T47-A51 Genuine Honda MUFFLER, R- EX (part page + diagram T404B0200)",
    "https://www.hondapartsnow.com/genuine/honda~muffler~r~ex~18307-t47-a51.html",
    "HondaPartsNow", "A", "cache/pages/cc897d0f556a8710.txt",
    appl="2022-2024 Honda Civic (part page title); 2024 fitment 5 Door 1.5T Sport Touring 6MT, CVT",
    notes="Diagram image (cache/audio_refs/hpn_exhaust_diagram_large.png, Honda illustration "
          "T404B0200) downloaded to the git-ignored cache for reading only.")
src("hpn-18305-T47-A51", "18305-T47-A51 Genuine Honda MUFFLER, L- EX (part page)",
    "https://www.hondapartsnow.com/genuine/honda~muffler~l~ex~18305-t47-a51.html",
    "HondaPartsNow", "A", "cache/pages/5310f0c70dcb3019.txt",
    appl="2022-2024 Honda Civic; 2024 fitment 5 Door 1.5T Sport Touring 6MT, CVT")
src("hpn-18150-64A-L00", "18150-64A-L00 Genuine Honda CONVERTER ASSY (part page)",
    "https://www.hondapartsnow.com/genuine/honda~converter~assy~18150-64a-l00.html",
    "HondaPartsNow", "A", "cache/pages/8684f83f0c79a7de.txt", appl="2022-2026 Honda Civic")

# ------------------------------------------------------------------ stock exhaust layout
APP_ST_US = db.app("2024", "US", "Sport Touring (5 Door 1.5T)", "6MT, CVT",
                   notes="US parts catalog; same part numbers listed for 6MT and CVT")
APP_15T_ALL = db.app("2024", "US", "all 1.5T (sedan EX/Touring, Si, hatch EX-L, Sport Touring)",
                     "6MT, CVT", body="sedan and hatchback")


def P(key, desc, unit, impact, rec):
    db.add_candidate(d, key, desc, unit, impact, rec)


P("audio.exhaust_rear_muffler_count", "Number of rear mufflers on the stock exhaust", "1", "medium",
  db.record(value=2, unit="1", status="confirmed", cls="A", source_id="hpn-2024-civic-muffler",
            locator="listing rows 18305-T47-A51 and 18307-T47-A51",
            evidence="2024 Honda Civic MUFFLER, L- EX Part Number: 18305-T47-A51 … Position : Driver Side "
                     "… Fits the following 2024 Honda Civic Submodels: 5 Door 1.5T Sport Touring | 6MT, CVT "
                     "… 2024 Honda Civic MUFFLER, R- EX … 18307-T47-A51 … Position : Passenger Side … "
                     "5 Door 1.5T Sport Touring | 6MT, CVT",
            as_printed="MUFFLER, L- EX 18305-T47-A51; MUFFLER, R- EX 18307-T47-A51",
            applicability=APP_ST_US, confidence="high",
            notes="Separate left (driver side) and right (passenger side) rear mufflers. The 1.5T "
                  "hatch EX-L (CVT) uses different numbers (-A01), so the Sport Touring rear "
                  "section is trim-specific. Model years: part pages are titled 2022-2024."))
P("audio.exhaust_layout", "Stock exhaust layout, front to rear (Honda illustration T404B0200)", "text",
  "medium",
  db.record(value="front pipe A with flexible section (ref 1) -> centre pipe with one in-line "
                  "resonator/silencer and a Y-split (ref 9, sold with the right rear muffler as "
                  "18307-T47-A51 'MUFFLER, R- EX') -> two rear mufflers, right (ref 9) and left "
                  "(ref 8, 18305-T47-A51, flange-joined with gasket ref 6), each with a finisher "
                  "(refs 10, 11)",
            unit="text", status="confirmed", cls="A", source_id="hpn-18307-T47-A51",
            locator="part page 'Ref No.' lines + diagram image T404B0200",
            evidence="18307-T47-A51 MUFFLER, R- EX is Ref No. 9 in the diagram below … "
                     "(18305-T47-A51 page:) 18305-T47-A51 MUFFLER, L- EX is Ref No. 8 in the diagram "
                     "below … (related parts:) Honda 18310-T47-A52 FINISHER, R- EX; diagram: ref 9 "
                     "drawn as centre pipe with a cylindrical in-line silencer, Y-junction and a rear "
                     "box; ref 8 a second rear box; refs 10/11 tip finishers",
            as_printed="Ref No. 9 / Ref No. 8 (diagram T404B0200)",
            applicability=APP_ST_US, confidence="medium",
            notes="Topology read from the drawing (not to scale). The drawing is the one the "
                  "retailer shows for 18307-T47-A51/18305-T47-A51; whether its finisher shapes are "
                  "Sport Touring-specific is not established. Pipe diameters are not in the catalog."))
P("audio.catalytic_converter", "Catalytic converter part and sharing across 1.5T trims", "text", "low",
  db.record(value="one 'CONVERTER ASSY' 18150-64A-L00 listed for all 2024 1.5T trims incl. Si and "
                  "hatch Sport Touring 6MT; position not established from this page",
            unit="text", status="confirmed", cls="A", source_id="hpn-2024-civic-exhaust-pipe",
            locator="listing row 18150-64A-L00",
            evidence="2024 Honda Civic CONVERTER ASSY Part Number: 18150-64A-L00 … Fits the following "
                     "2024 Honda Civic Submodels: 4 Door 1.5T EX, 4 Door 1.5T Touring, 4 Door Si, "
                     "5 Door 1.5T EX-L, 5 Door 1.5T Sport Touring | 6MT, CVT",
            as_printed="18150-64A-L00", applicability=APP_15T_ALL, confidence="medium",
            notes="The part page says 'Ref No. 4' but ref 4 in drawing T404B0200 is a small bracket "
                  "(related part 11942-5AA-A00 'Stay L,Converter'); the converter itself is not drawn "
                  "there (diagram points to E-4 at the manifold end), so its exact position and the "
                  "count of catalyst bricks are UNKNOWN. A commenter on the reference clip mentions a "
                  "'Secondary cat' (unverified)."))
P("audio.front_pipe_shared", "Front exhaust pipe A shared with Si and sedan", "text", "low",
  db.record(value="PIPE A ASSY- EX 18200-T20-A01 shared by all 2024 1.5T trims incl. Si",
            unit="text", status="confirmed", cls="A", source_id="hpn-2024-civic-exhaust-pipe",
            locator="listing row 18200-T20-A01",
            evidence="2024 Honda Civic PIPE A ASSY- EX … 18200-T20-A01 … Fits the following 2024 Honda "
                     "Civic Submodels: 4 Door 1.5T EX, 4 Door 1.5T Touring, 4 Door Si, 5 Door 1.5T "
                     "EX-L, 5 Door 1.5T Sport Touring | 6MT, CVT",
            as_printed="18200-T20-A01", applicability=APP_15T_ALL, confidence="high",
            notes="Only the front pipe and converter are shared with the Si; the Si has its own "
                  "mufflers (18305-T22-A01 / 18307-T22-A01), so Si exhaust sound is not equivalent."))
P("audio.exhaust_pipe_diameter", "Stock exhaust pipe outside diameter", "m", "medium",
  db.unknown("m", searches=["hondapartsnow 2024 exhaust pipe and muffler listings (no dimensions)",
                            "honda.oempartsonline.com (Cloudflare 403)",
                            "hondapartsconnection.com (Cloudflare challenge)",
                            "aftermarket cat-back pages (see products; diameters given are for the "
                            "aftermarket systems)"],
             how_to_measure="Calipers or a tape around the centre pipe ahead of the resonator and "
                            "at a muffler inlet (circumference / pi), car on ramps; +/-1 mm.",
             notes="A reference-clip commenter wrote 'I know the stock ones are “2”' "
                   "(unverified forum lead, not a source)."))

# ==== SAVE (keep last) ====
os.makedirs(os.path.dirname(OUT), exist_ok=True)
db.save(d, OUT)
errs = db.check_domain(d)
print(OUT, "OK" if not errs else errs)
