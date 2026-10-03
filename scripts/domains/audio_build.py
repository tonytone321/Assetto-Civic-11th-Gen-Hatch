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

# ------------------------------------------------------------------ cat-back products
src("magnaflow-19652", "MagnaFlow 2022-2024 Honda Civic Sport Touring 1.5L NEO Series Cat-Back 19652",
    "https://www.magnaflow.com/products/19652-magnaflow-2022-2024-honda-civic-sport-touring-1-5l-neo-series-cat-back-performance-exhaust-system-19652",
    "MagnaFlow (manufacturer)", "C", "cache/pages/0f73df1c8cf3b232.txt",
    appl="2022-2024 Civic Sport Touring hatchback 1.5L (gearbox not stated)")
src("borla-140966", "Borla 2022-2024 Honda Civic Sport Touring Cat-Back Exhaust System S-Type Part # 140966",
    "https://www.borla.com/products/honda-civic-sport-touring-cat-back-exhaust-system-140966",
    "Borla Performance Industries (manufacturer)", "C", "cache/pages/3d25cfbd239bb6ec.txt",
    method="rendered (static fetch returned 403; rendered page 200)",
    appl="2022-2024 Civic Sport Touring 1.5L Turbo, Automatic/Manual, FWD hatchback")
src("prl-remark-st", "Remark 2022+ Honda Civic Hatchback Sport Touring Link Loop Exhaust (retailer)",
    "https://prlmotorsports.com/products/remark-2022-honda-civic-hatchback-sport-touring-link-loop-exhaust",
    "PRL Motorsports (retailer)", "C", "cache/pages/d6172a8c76fd185c.txt",
    appl="2022+ Civic Hatchback Sport Touring 1.5T")
src("kami-remark-st", "Remark 2022+ Honda Civic Hatchback Sport Touring FL1 (Link Loop) Catback RK-C4063H-07 (retailer)",
    "https://www.kamispeed.com/products/remark-2022-honda-civic-hatchback-sport-touring-fl1-link-loop-catback-exhaust-stainless-steel-tip",
    "Kami Speed (retailer)", "C", "cache/pages/c1832d013c0eed6c.txt",
    appl="FL1 / 1.5L L15 Turbocharged, Sport Touring hatchback")
src("redline360-plm", "PLM Exhaust Honda Civic 1.5T (2022-2025) Muffler Delete (retailer)",
    "https://shop.redline360.com/products/plm-exhaust-honda-civic-1-5t-2023-2024-muffler-delete-w-polished-or-blue-burnt-tips",
    "Redline360 (retailer)", "C", "cache/pages/3e3e21d350231b57.txt", appl="2022-2025 Civic 1.5T")

d["products"] = [
    {"brand": "MagnaFlow", "product": "NEO Series cat-back", "part_number": "19652",
     "source_id": "magnaflow-19652", "fits_as_stated": "2022-2024 Honda Civic Sport Touring Hatchback 1.5L",
     "piping": "2.25 in main piping (MAIN PIPING DIAMETER 2.25IN)",
     "mufflers": "3: one 14 in round straight-through + two 11 in oval straight-through after a Y-pipe",
     "tips": "none; retains factory fascia tips ('EXHAUST TIP QUANTITY 0')",
     "replaces": "'all OEM exhaust components from near the catalytic converter on back'",
     "sound_claims": "'No-Drone-Technology allows for a quiet cabin'; page badges Exterior Sound AGGRESSIVE, Interior Sound MODERATE",
     "evidence": "#19652 features 2.25\" mandrel bent main piping that passes through a 14\" round straight-through performance muffler, a smooth Y-pipe single-to-dual transition and two 11\" oval straight-through performance mufflers before terminating in a dual split rear exit.",
     "hosted_sound_clip": {"url": "https://www.magnaflow.com/cdn/shop/videos/c/vp/d69556730b4d4f0898305a378b816257/d69556730b4d4f0898305a378b816257.HD-720p-1.6Mbps-93195281.mp4",
                            "license": "not stated on the page (all rights reserved assumed)",
                            "analyzed": False, "notes": "Catalogued by link only; no license permitting download/analysis."},
     "relevance": "high: bolt-on, retains catalysts and factory tips, the 'tasteful cat-back' class the user targets"},
    {"brand": "Borla", "product": "S-Type cat-back", "part_number": "140966",
     "source_id": "borla-140966",
     "fits_as_stated": "2022-2024 Honda Civic Sport Touring 1.5L 4 CYL Turbo Automatic/ Manual Transmission Front Wheel Drive 4 Door Hatchback",
     "piping": "conflicting on the same page: '2.5\" diameter' in the description vs '2.25\" Diameter System' in the feature list; 2.5 in tail pipes",
     "mufflers": "Polyphonic Harmonizer units (count not stated)",
     "tips": "none; 'exit thru the Original Equipment (O.E.) tips/ valance'",
     "sound_claims": "'Our classic S-Type sound level delivers a sporty sound that enhances the driving experience without any drone inside the vehicle.'",
     "evidence": "This 2.5\" diameter BORLA® Cat-Back™ system … System Features: … 2.25\" Diameter System S-Type Sound Level No Drone",
     "hosted_sound_clip": {"url": "https://www.youtube.com/watch?v=KQF8Gg2yBpY", "license": "YouTube standard license",
                            "analyzed": False},
     "notes": "A retailer (twostepperformance.com, cache/pages/7a6e2ea17b0ee4d1.txt) titles the same SKU BOR140966 'ATAK' while its text says S-Type; Borla's own page says S-Type.",
     "relevance": "high: bolt-on, retains catalysts and OE tips; a reference-clip commenter reports a 2023 ST 6MT with a Borla S-Type sounding 'just like this' (unverified)"},
    {"brand": "Remark", "product": "Sports Touring / Link Loop cat-back", "part_number": "RK-C4063H-07 (RK-C4063H-07T burnt tips)",
     "source_id": "kami-remark-st", "fits_as_stated": "Fits all 2022+ Honda Civic Hatchback Sport Touring 1.5T (PRL); FL1 / 1.5L L15 Turbocharged (Kami)",
     "piping": "'2.5\" neck expanded to 3\" piping mandrel bent piping to Y-pipe 2.5\" to REMARK Link Loop design'",
     "mufflers": "'Mid-Pipe: Resonated'; Link Loop rear section; no conventional rear mufflers stated",
     "tips": "'Quad 3.5inch exit slant cut tips (two on each side)' (replaces factory centre finishers)",
     "sound_claims": "manufacturer prose only ('spirited sound'); no dB figure",
     "evidence": "Piping Diameter: 2.5\" neck expanded to 3\" piping mandrel bent piping to Y-pipe 2.5\" to REMARK Link Loop design … Mid-Pipe: Resonated … Quad 3.5inch exit slant cut tips (two on each side)",
     "hosted_sound_clip": {"url": "https://www.youtube.com/watch?v=gqB11p-61UI", "license": "YouTube standard license", "analyzed": False},
     "relevance": "medium: louder, changes visible tips (quad) — visual difference from the stock car"},
    {"brand": "PLM", "product": "Axle-back muffler delete", "part_number": "n/a",
     "source_id": "redline360-plm", "fits_as_stated": "Honda Civic 1.5T (2022-2025)",
     "evidence": "Not compatible with the Sport Touring Hatchback due to the extended length of the exhaust tips.",
     "relevance": "excluded: retailer states it does not fit the Sport Touring hatchback"},
]

# ------------------------------------------------------------------ reference clip (user's)
src("yt-BDuJz3FTOpU", "11th Gen Civic 1.5L muffler and resonator delete. Burbles. (YouTube Short)",
    "https://www.youtube.com/shorts/BDuJz3FTOpU", "nycivic (@goku1495062), YouTube", "C",
    "cache/pages/oembed_BDuJz3FTOpU.json",
    method="oEmbed JSON + rendered watch page (comments with replies expanded: cache/pages/a189ed58f517a54d.txt)",
    appl="11th-gen Civic 1.5L hatchback (per title/comments); trim and gearbox not stated by the creator",
    notes="Video playback NOT accessed (bot wall). The first rendered watch-page text (views/subscribers/no "
          "description) was later overwritten in cache by a 429 response; those metadata are also in "
          "docs/PREFLIGHT.md.")

d["reference_clip"] = {
    "url": "https://www.youtube.com/shorts/BDuJz3FTOpU",
    "source_id": "yt-BDuJz3FTOpU",
    "title": "11th Gen Civic 1.5L muffler and resonator delete. Burbles.",
    "uploader": "nycivic (@goku1495062), 325 subscribers",
    "metadata_as_rendered": "639K views, '3y ago', 'No description has been added to this video.', 351 Comments",
    "license": "YouTube standard license (no Creative Commons marking seen)",
    "documented": {
        "exhaust_modification": "Muffler and resonator delete (title). Creator replies: 'i still have cats. mine isn’t straight piped. i wouldn’t recommend removing the cats. only the mufflers and resonators'; 'i didn’t touch my cats'.",
        "tips": "Creator reply: 'i dont have exhaust tips lmao. stock exhaust. check out the new short' (i.e. factory piping/finishers retained after the deletes).",
        "other_exterior": "Creator replies: 'oem hpd spoiler from honda'; 'its the HPD spoiler from factory'.",
        "build_list": "Creator reply: 'Build break down on my other video' -> '11th Gen Civic 35k Mile walk around and cosmetic mod list.' (https://www.youtube.com/watch?v=CMy8wWQr7Cg); its visible description is a single character 'l' and the title says cosmetic mods; no powertrain mods listed in text.",
        "companion_clip": "'11th Gen civic Muffler and Resonator delete cold start. Stock Exhaust.' (https://www.youtube.com/shorts/4oS-fpb4DsM), description: 'Follow my IG for more of the build or questions. @nyc.ivic'.",
        "body": "Hatchback: channel titles say '11th Gen Civic Hatch' (other shorts); several commenters call it a hatch. Engine 1.5L per title.",
    },
    "not_documented": {
        "gearbox": "NOT stated by the creator. Commenters disagree: '@thecivic215: This is a CVT not a manual'; '@Augie..: …seeing the reverse light flash it’s cvt obviously…'; '@RestfulRhythms0: I think it’s manual because it’s 1.5T'. Several asked 'Is this cvt or manual' without a creator answer. Unverified either way; the CVT reading is a weak lead that would make the clip a non-target gearbox.",
        "trim": "Not stated (a commenter asking about Sport vs Touring got no creator answer). US 1.5T hatch trims are EX-L and Sport Touring; the PLM note shows ST finishers differ.",
        "tune_ecu": "Not stated. Questions 'are the burbles stock or did u tune the car?', 'does that have a tune??', 'Is it tuned ?', 'Muffler and resonator delete only? Or do you have a tune as well?' have no creator reply in the expanded thread text.",
        "intake_downpipe": "Not stated (creator only states cats retained).",
        "mic_position": "Not stated.",
        "model_year": "Not stated; upload ~3 years before 2026-10 (so a 2022 or 2023 car).",
    },
    "difference_from_target": "Muffler + resonator DELETE (straight pipe after the catalysts, factory finishers), not a bolt-on silenced cat-back; gearbox possibly CVT; tune status unknown. Expect it to be louder and less damped than MagnaFlow/Borla cat-backs; a commenter with a MagnaFlow cat-back on a Sport Touring wrote it 'sounds similar but doesn’t pop as much' (unverified).",
    "audio_analysis": NOT_ANALYZED,
    "burble_parameters": {"rpm_range": None, "pop_count": None, "pop_spacing_s": None, "duration_s": None,
                          "tone": None, "level": None, "delay_after_throttle_close_s": None,
                          "status": "unknown — not analyzed"},
    "what_user_must_supply": "A recording you made yourself, or a file you have the rights to (e.g. the creator's permission, or a manufacturer clip with a licence allowing analysis), placed in user_supplied/audio/ as WAV/FLAC (>=44.1 kHz, no music), ideally with a synced OBD/throttle/rpm log. A script can then extract pop onsets, spacing, burst duration, spectral centroid, level relative to idle and delay after throttle close.",
    "comments_read": "cache/pages/a189ed58f517a54d.txt (reply threads expanded by scripts/domains/audio_yt_comments.py; not every reply thread of the 351 comments is guaranteed loaded)",
}

# ------------------------------------------------------------------ other clips (text-only catalog)
STD = "YouTube standard license (no Creative Commons marking checked/seen)"


def clip(cid, url, uploader, kind, title, car, mods, weight, reasons, text_source, notes=""):
    d["clips"].append({
        "id": cid, "url": url, "uploader": uploader, "kind": kind, "title": title,
        "car_as_stated": car, "modifications_as_stated": mods,
        "microphone_position": "not stated", "events_with_timestamps": "none given in text",
        "quality_indicators": "unknown (not played)", "license": STD,
        "weight": weight, "weight_reasons": reasons, "text_source": text_source,
        "audio_analyzed": False, "notes": notes})


clip("borla-KQF8Gg2yBpY", "https://www.youtube.com/watch?v=KQF8Gg2yBpY", "Borla Performance Industries (manufacturer)",
     "cat-back (manufacturer demo)", "Borla Exhaust for 2022-2024 Honda Civic Sport Touring Hatchback 1.5L",
     "2022+ Civic Sport Touring Hatchback 1.5L; gearbox not stated",
     "Borla S-Type cat-back 140966 (description: 'Check out Borla's S-Type exhaust for 2022+ Honda Civic Sport Touring Hatchback 1.5L!')",
     "high", "exact body/engine/trim; mods listed by the maker; gearbox unknown; manufacturer edit (possible music unknown)",
     "cache/pages/5e128092d29ddc16.txt + oEmbed")
clip("remark-gqB11p-61UI", "https://www.youtube.com/watch?v=gqB11p-61UI", "REMARK EXHAUST (manufacturer)",
     "cat-back (manufacturer demo)", "REMARK Sports Touring (LINK LOOP) Catback Exhaust - Honda Civic Hatchback Sport Touring FL1 (2022+)",
     "FL1 Civic Hatchback Sport Touring 2022+; gearbox not stated",
     "Remark Link Loop cat-back (resonated mid-pipe, quad tips); other mods not stated",
     "medium", "exact body/engine/trim; louder straight-through design; gearbox and other mods unknown",
     "cache/pages/4e7e75f08d0b5643.txt + oEmbed")
clip("mbrp-WzQMqZRkwtA", "https://www.youtube.com/watch?v=WzQMqZRkwtA", "MBRP (manufacturer)",
     "cat-back (manufacturer demo)", "2022-2024 Honda Civic, Sport Touring // 3-Inch/2.5-Inch Cat-Back Exhaust Quad Rear Exit",
     "2022-2024 Civic Sport Touring (title); gearbox not stated", "MBRP 3 in/2.5 in cat-back, quad rear exit (title)",
     "medium", "title only (watch page returned 429); gearbox unknown", "oEmbed (cache/pages/oembed_WzQMqZRkwtA.json)")
clip("artya-my1tjNfJ9Aw", "https://www.youtube.com/shorts/my1tjNfJ9Aw", "ItsArtyA",
     "cat-back + downpipe (owner)", "2024 Honda Civic Sport Touring 1.5T 6sp mt w/ PRL downpipe and Remark Link loop exhaust #automobile",
     "2024 Civic Sport Touring 1.5T 6-speed manual (title)", "PRL downpipe (catted or catless not stated) + Remark Link Loop cat-back; tune not stated",
     "low", "exact car and gearbox, but downpipe changes the catalyst/flow and possibly needs a tune: down-weighted per spec",
     "oEmbed + related-video list in cache/pages/5e128092d29ddc16.txt")
clip("axion-6T5TRwYG1Fc", "https://www.youtube.com/watch?v=6T5TRwYG1Fc", "Axion Industries",
     "cat-back (shop)", "Remark exhaust for the 2022 Honda Civic 1.5t. The perfect exhaust with the right sound",
     "2022 Civic 1.5T; body and gearbox not stated", "Remark exhaust (title)", "low",
     "body/gearbox unknown", "oEmbed")
clip("christime-hHsfUWwPl6E", "https://www.youtube.com/watch?v=hHsfUWwPl6E", "Chris Time",
     "cat-back (owner)", "REMARK EXHAUST NOTE 11TH GEN HONDA CIVIC 1.5T CVT", "11th gen Civic 1.5T CVT (title)",
     "Remark exhaust (title)", "excluded", "CVT (spec: down-weight CVTs; no manual shift/rev-hang behaviour)", "oEmbed")
clip("stillen-lm91I12Zrrs", "https://www.youtube.com/watch?v=lm91I12Zrrs", "STILLEN (manufacturer)",
     "cat-back + dyno (manufacturer)", "2022+ Civic Hatchback Roars: STILLEN Exhaust + DYNO",
     "2022+ Civic Hatchback; engine/trim/gearbox not stated in title", "STILLEN exhaust (title)", "low",
     "engine/trim/gearbox unknown", "oEmbed")
clip("afe-ZaUuBQLx268", "https://www.youtube.com/watch?v=ZaUuBQLx268", "aFe POWER (manufacturer)",
     "cat-back (manufacturer)", "aFe POWER Honda Civic Sport Hatchback Takeda Cat-Back Exhaust System",
     "Civic Sport Hatchback (US Sport hatch is 2.0 L)", "aFe Takeda cat-back", "excluded",
     "US Sport hatch = 2.0 L NA engine unless stated otherwise", "oEmbed")
clip("unity-v3NB3zi9uCY", "https://www.youtube.com/watch?v=v3NB3zi9uCY", "Unity Performance",
     "cat-back install vlog", "VLOG: Intro to “UNITYFL1” + MBRP Exhaust Install on our 2022 Honda Civic Sport Hatch!",
     "2022 Civic Sport Hatch (US Sport = 2.0 L unless stated)", "MBRP exhaust", "excluded", "probably 2.0 L; vlog format", "oEmbed")
clip("27won-sNnys3h4MRE", "https://www.youtube.com/watch?v=sNnys3h4MRE", "27WON (manufacturer)",
     "exhaust (manufacturer)", "2022-2025 Honda Civic 1.5T & 2.0L Single Exit Performance Exhaust System",
     "mixed 1.5T/2.0L, single exit (title)", "27WON single-exit exhaust", "low",
     "car shown not identified; single exit differs from the ST", "oEmbed")
clip("nycivic-4oS-fpb4DsM", "https://www.youtube.com/shorts/4oS-fpb4DsM", "nycivic (@goku1495062)",
     "muffler+resonator delete cold start (owner)", "11th Gen civic Muffler and Resonator delete cold start. Stock Exhaust.",
     "same car as the reference clip (same channel); gearbox not stated", "muffler and resonator delete; cats retained (creator replies on the reference clip)",
     "low", "same undocumented car as reference clip; cold start only", "cache/pages/7b4dc9b9abb1f0b1.* (later overwritten by a static fetch) + oEmbed")
clip("thetopher-8BXG6ojA4l8", "https://www.youtube.com/watch?v=8BXG6ojA4l8", "TheTopher",
     "stock POV drive", "2022 Honda Civic Sport Touring Manual Hatchback - POV Review",
     "2022 Civic Sport Touring manual hatchback (title)", "none stated (presumed stock: not verified)",
     "medium", "exact car/gearbox; only possible stock-exhaust candidate found; POV review likely has voice-over/cabin mic (not verified)",
     "oEmbed + related-video list")
clip("carsconv-OpgDjHqgM3g", "https://www.youtube.com/watch?v=OpgDjHqgM3g", "Cars & Conversation",
     "tuned vs stock comparison", "Honda Civic FL1| Stage 2 tuned and stock comparison",
     "FL1 Civic (hatch); trim/gearbox not stated", "Stage 2 tune (contents not stated)", "low",
     "tune; a stock segment may exist but is not documented in text", "oEmbed + related-video list")

# ------------------------------------------------------------------ observation sources (general)
src("wiki-engine-braking", "Engine braking", "https://en.wikipedia.org/wiki/Engine_braking", "Wikipedia",
    "C", "cache/pages/b490262fed0d512f.txt", appl="general gasoline engines (not Honda-specific)")
src("wiki-antilag", "Antilag system", "https://en.wikipedia.org/wiki/Antilag_system", "Wikipedia",
    "C", "cache/pages/e35ddc6f95231e3f.txt", appl="general turbocharged engines (motorsport)")
src("hpa-pop-bang", "pop and bang tuning (forum thread)",
    "https://www.hpacademy.com/forum/general-tuning-discussion/show/pop-and-bang-tuning/",
    "HP Academy forum (tuner community)", "C", "cache/pages/e6601fb97b565b38.txt",
    appl="general aftermarket ECU tuning", notes="Forum posts: lead-quality, used only for general mechanism.")
src("hpa-pops-bangs", "exhaust pops and bangs (forum thread)",
    "https://www.hpacademy.com/forum/general-tuning-discussion/show/exhaust-pops-and-bangs/",
    "HP Academy forum (tuner community)", "C", "cache/pages/a885367f3d8510e8.txt",
    appl="general aftermarket ECU tuning", notes="Forum posts: lead-quality.")

P("audio.overrun_fuel_cut_this_car", "Stock ECU overrun (DFCO) behaviour on this engine", "text", "high",
  db.unknown("text", searches=["hondata.mobi 'Fuel overrun cutoff' thread (robots.txt disallows; not fetched)",
                               "KTuner/Hondata 11th gen 1.5T overrun or burble feature (no documentation found)",
                               "civicx/civicxi FlashPro threads (search snippets only)",
                               "engine thread (04_engine.md) also found nothing"],
             how_to_measure="OBD-II log (>=10 Hz) of rpm, throttle/pedal, short-term fuel trim or injector "
                            "pulse, O2/lambda, coolant temp and gear during lift-offs from 2000-6000 rpm in "
                            "3rd-4th gear, plus clutch-in upshifts; DFCO shows as lambda going full lean / "
                            "injector pulse 0. Record entry rpm, delay after pedal release, and re-entry rpm.",
             notes="Evidence that some stock-ECU cars of this type pop on overrun is anecdotal only (see "
                   "audio/OBSERVATIONS.md)."))

# ==== SAVE (keep last) ====
os.makedirs(os.path.dirname(OUT), exist_ok=True)
db.save(d, OUT)
errs = db.check_domain(d)
print(OUT, "OK" if not errs else errs)
