# 09 Visual references, paint and cluster — research log

Thread: domain 9. Files: `references/manifest.json`, `references/COVERAGE.md`, `vehicle_data/paint.json`,
`vehicle_data/dashboard.json`, `scripts/domains/visual_build.py` (builds the three JSON files from cached pages and
aborts if any quote is not found in the cache), `scripts/domains/paint_analyze.py` (scripted colour statistics), this log.
Rebuild: `python3 scripts/domains/visual_build.py && python3 scripts/domains/paint_analyze.py`.

## Sources opened
- hondanews.ca 2024 Civic Hatchback Specifications (Apr 4 2024): ST has `10.2" colour TFT full digital driver meter display`, `9" colour touchscreen` with navigation; Sport has the 7" centre meter + 7" screen. Exterior temperature indicator, Maintenance Minder. No colour table; no HUD row.
- hondanews.ca 2023 Civic Hatchback Specifications: colour table `Sonic Grey Pearl NH-877P`, Sport Touring = Black Leather.
- hondainfocenter.com 2024 Colors and hondanews.com 2024 Specs & Features (US): `Sonic Gray Pearl (NH-877P)`, Sport Touring Black leather, no "CVT only" restriction; `10.2-Inch Digital Instrument Cluster` ST only.
- hondanews.com 2022 Civic Hatchback press kit: Digital Instrumentation section (10.2-inch display modes and zones; lower trims' 7-inch display with physical speedometer); 6MT console description; 32 press photos (928x522 previews; larger sizes 403).
- Hybrid Racing touch-up listing NH877PAH, fitment 2017-2024 Civic (class C cross-check of the code).
- Car and Driver 2022 Hatchback test: "Sonic Gray Civic Sport Touring test car", six-speed manual, "Options: Sonic Gray paint, $395".
- Wikimedia Commons category "Honda Civic (2021) liftback": free-licensed Sport Touring photos incl. a Canadian ST (Sault Ste. Marie, ON).

## Blocked / not obtained
- Owner's manual (indicator lamps, MT gear/shift indicator, Canadian units): techinfo.honda.com PDFs/HTML fail via the egress proxy (TLS verify error with requests; 502 "upstream request failed" in Chromium) — not worked around; owners.honda.com needs login; manualslib.com robots.txt disallows ClaudeBot. `dashboard.json` indicators table is therefore empty and says why.
- hips.hearstapps.com (C&D photos): robots.txt disallows Claude-User — catalogued by link only.
- cdn.civicxi.com (owner Sonic Gray Pearl ST photos): connection reset by the egress proxy.
- Commons API rate-limited (429) intermittently; retried with backoff.
- Dealer listings found by search had expired (KBB redirect, AutoNation 410, cuv.honda.ca 404). No Canadian dealer photo set of a 2024 ST MT in Sonic Grey Pearl was obtained.
- YouTube walkarounds not searched (playback bot wall known from preflight); none catalogued.

## Paint analysis (what was actually done)
Only Honda's 74x74 colour-orb render is a label-confirmed Sonic Gray Pearl image that could be downloaded. Its masked pixels give
sRGB median ~(117,122,131), L*a*b* ~(51, 0, -5), chroma ~5, i.e. a mid grey with a slight blue cast — recorded as class E,
low confidence. Four grey press photos (colour not captioned) were run through the same pipeline as context: their deltaE to the
three Honda grey swatches ranges 6-48 and the nearest swatch flips with lighting, which demonstrates that uncalibrated photos
cannot identify or quantify this paint. No sun/shade/overcast/indoor comparison of confirmed Sonic Grey Pearl photos was possible.
Clearcoat IOR/roughness and base roughness are class E judgements with ranges; layer structure, pearl flop and flake are unknown.

## Open questions
- 6MT cluster: gear number vs shift-up arrow; km/h scale maximum; red-zone start; lamp set.
- Whether NH-877P is a 2-coat or tri-coat refinish.
- 2024 Canadian colour availability for ST MT (identity thread; 2024 HCI spec sheet has no colour table).

## Leads for other domains
- Dimensions (02): Commons `2022 Honda Civic Hatchback EX-L in Platinum White Pearl, front right/rear right` (70/67 mm full-frame, low distortion) and `2022 Honda Civic Sport Touring liftback, rear 6.18.22` (~100 mm equiv.); no straight side profile found.
- Wheels/brakes (07): press photo 20 (ST wheel face, front caliper sliver); Commons `22 Honda Civic Hatchback Sport Touring` (wheel face, 26 mm equiv. so distorted). C&D test car: Continental ContiProContact 235/40R-18 on the ST 6MT.
- Identity (01): press kit text — 6MT console: cupholders behind the shifter, drive-mode and parking-brake buttons left of the shifter; CVT shift knob tilted 5 deg; ST wheel "18-inch split 5-spoke design with a dark clear-coated machined face and Berlina Black inserts".
- Performance (08): C&D 2022 ST 6MT: 0-60 mph 7.3 s, quarter 15.5 s @ 91 mph (from the cached article text line 93).
