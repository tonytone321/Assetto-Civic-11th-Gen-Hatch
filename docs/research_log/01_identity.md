# 01 Identity — research log (2026-10-03)

Builder: `scripts/domains/identity_build.py` (checks every quote against the cached page text), vPIC helper: `scripts/domains/identity_vin_decode.py` (raw JSON in `cache/vpic/`). Output: `vehicle_data/identity.json`.

## Sources opened
- hondanews.ca (Honda Canada newsroom), Civic Hatchback channel → SPECS tab: 2024 (Apr 4 2024), 2023, 2022 spec tables; 2022 arrival (Sep 2021) and global debut (Jun 2021) releases; 2025 refresh release (May 2024). **Primary source for the target.**
- hondainfocenter.com 2024 Civic Hatchback colours (American Honda, US only): colour/interior/trim matrix with paint codes.
- vPIC DecodeVinValuesExtended: Canadian-serial VINs and patterns 19XFL1G8*RE/PE/NE.
- cuv.honda.ca used Civic Hatchback listings (Canadian VINs, dealer text).

## Findings
- 2024 CA Civic Hatchback = Sport and Sport Touring, both 1.5T; **6MT "Available" only on Sport Touring**; 1382 kg MT curb weight; MT fuel 8.5/6.3/7.5.
- Built at Greensburg, Indiana (Honda Canada release + vPIC). Engine code **L15B7** (vPIC only). Model code FL1 (VIN interpretation, class E). Gearbox code: **unknown**.
- Sonic Grey Pearl = **NH-877P** (Honda Canada 2023 table; American Honda 2024). Offered on CA ST with Black Leather in 2023; **2024 Canada not directly confirmed** (estimated true: 2024 CA page has no colour table; US 2024 offers it on ST incl. MT).
- MT cabin: no paddles, no drive-mode switch (CVT only), EPB + auto brake hold, ACC without Low-Speed Follow, no Traffic Jam Assist/low-speed braking/remote start. Idle-stop on MT and rev-match: unconfirmed.
- No 2022→2024 change found to Sport Touring MT data in the Canadian tables (model-year check recorded).

## Blocked / problems
- `www-demo-showroom-secure.sm360.ca` (egress proxy CONNECT rejected); `carpages.ca` (403 bot wall) — the only Canadian 2024 ST MT VIN (19XFL1G82RE400164) is from a search snippet of that page; decoded but listing not opened.
- autotrader.ca search/offer pages: robots.txt disallows ClaudeBot (not fetched). auto123 spec page 404/502. kijiji listing 404.
- hondanews.ca "2025 Civic Hatchback Specifications" page actually contains **Ridgeline** specs (Honda content error) — unusable.
- vPIC trim decode is unreliable for Canadian VINs (Canadian Sport decodes as "Sport Touring").
- MID (vPIC Part 565 VIN-guide PDFs) located but not mined (time budget).

## Open questions
- Transmission type code; idle-stop on 6MT; rev-match (assume none); TPMS type change 2024 (vPIC: Indirect→Direct); 2024 Canadian colour list.

## Leads for other domains
- Dims (2): 2024 CA: length 4529, width 1802, height 1415, wheelbase 2735, track 1536/1565, ground clearance 134 (no-load); 2022/23: width 2081/1900 mirrors open/folded, length 4547 with licence bracket.
- Mass (3): curb MT 1382 kg ST (2022–2024 CA), fuel tank 46 L; vPIC GVWR class 1C 4,001–5,000 lb.
- Engine (4): redline 6,600 rpm (2021 debut release, key specs table); exhaust-side VTEC; 87 octane.
- Drivetrain (5): "new dual-mass flywheel" (2021 debut release); short-throw 6MT with improved shift rigidity.
- Steering (6): 2024 CA: 2.2 turns lock-to-lock, 11.4:1, turning radius curb-to-curb 11.6 m; stabilizers 26.5/17.5 mm; MacPherson front / multi-link rear; aluminium front subframe.
- Wheels (7): 235/40R18 91W all-season; spare T125/85 D16 99M; front ventilated / rear solid discs; ST wheel "machined with black inserts" (debut release said "Shark Gray inserts").
- Visual/cluster (9): 10.2" full digital meter, round-gauge or bar-graph layouts; 2025 fascia/grille/taillights differ — exclude.
