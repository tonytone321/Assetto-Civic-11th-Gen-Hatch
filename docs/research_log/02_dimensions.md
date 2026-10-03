# 02 Dimensions — research log

Files: `vehicle_data/dimensions.json`, `vehicle_data/proportions.json` (written by `scripts/domains/photo_measure_side.py`), `scripts/derivations/dimensions.py`.

## Sources opened (cached text under cache/pages/)
- Honda Canada newsroom spec releases (hondanews.ca, class A): 2024 (`41e62125b9f268de`), 2023 (`374416cf6bc6db5d`), 2022 (`344bc90bb36560a9`). The 2024 table covers Sport and Sport Touring; 2022/2023 tables add length **with/without licence bracket (4547/4529 mm)** and **width mirrors open/folded (2081/1900 mm)**, which the 2024 table omits.
- hondanews.com US spec releases 2024 (`dd2e2052fcb1a220`) and 2022 (`fb1d5790fd3bfda8`): inches; agree with Canada except length 179.0 in (= 4547 mm, i.e. the with-bracket figure).
- hondainfocenter.com 2024 hatchback specs (`b67f7f855816944e`): agrees except **Length 184.0 in**, which equals the Civic **Sedan** length on the same site (`67adc76510e3bc91`). Recorded as a rejected low-confidence candidate (conflict for CONFLICTS.md).
- Model-year check: length (w/o bracket), height, wheelbase, track, ground clearance, interior dimensions are identical 2022, 2023, 2024 in Honda Canada tables. Track varies by wheel: 16/17-in LX 1546/1575, 18-in Sport/Sport Touring 1536/1565.

## Values (Canadian, Sport Touring)
Length 4529 mm (w/o bracket; 4547 with), width 1802 mm, width mirrors 2081 mm (2022/2023 only), height 1415, wheelbase 2735, track 1536/1565, ground clearance (no-load) 134 mm (single source; US tables do not print it). Interior SAE dimensions and cargo/passenger volume recorded for cockpit work.

## Overhangs
Unpublished in all Honda NA tables. Derived in `scripts/derivations/dimensions.py` as (length − wheelbase) × photo-measured scale-free fraction front/(front+rear) = 0.522 ± 0.011 → front ≈ 0.936 m (0.897–0.976), rear ≈ 0.858 m (0.818–0.897).
Approach/departure angles: unknown.

## Photo measurement
- Only straight-on manufacturer view found: Honda Information Center profile header `22_CivicHatchback_STRG_Header_RR` (2022 Sport Touring render, 620×200 RGBA, ~8.6 mm/px). Downloaded to cache/photos (git-ignored).
- hondanews.com/.ca 2022 launch galleries (25 photos) contain only 3/4 and action shots — no straight-on side/front/rear views. automobiles.honda.com configurator is 403. No straight-on front/rear image → mirror position, front-view ratios recorded unknown.
- Algorithms: rim Hough + least-squares circle; tyre radius from alpha-edge rays on lower-side arcs (the render flattens the contact patch, so ground = flat opaque bottom); 3-segment continuous line fits on the top profile (alpha ≥ 128 because glass is semi-transparent); arch lip by Lab colour match to a door-box median.
- QA: wheelbase scale 8.645 mm/px vs tyre scale 8.451 (2.3 %), front/rear tyre size ratio 1.001, rim aspect 0.995. Photo reproduces published height to 0.7 % but length only to 3.6 % short (consistent with a finite-distance camera magnifying the near-side wheels relative to centreline bumper ends); that error is folded into every horizontal range, and the direct photo overhangs (sum 1631 mm vs 1794 published) are kept low confidence.
- Ride-height-type values (arch gap ≈ 0.39 m, sill 0.199 m, wheel centre 0.314 m) come from a CGI pose → low confidence; need real-car measurement.

## Blocked / not obtained
- Owner's manual: honda.ca manuals selector did not render a document list headlessly; its API needs a private `consumerId` header — not worked around. owners.honda.com redirects to a login app.
- NHTSA crash-test database (nrd.nhtsa.dot.gov): egress proxy 502.
- auto123.com spec pages: 404/502.

## Leads for other domains
- Steering (6): Honda Canada prints "Turning radius – (curb-to-curb) (m) 11.6", but US prints Turning Diameter 38.1 ft (= 11.61 m) → the Canadian "radius" is a diameter. CA steering ratio 11.4:1, 2.2 turns; US 11.41:1, 2.21 turns (18-in trims). Stabilizer bars 26.5/17.5 mm (CA 2024).
- Mass (3): Info Center 2024 ST "Weight Distribution (front/rear, 6MT) 59% / 41%"; CA curb MT/CVT 1382/1412 kg.
- Identity/paint (1, 9): 2023 CA table lists "Sonic Grey Pearl NH-877P" with Black Leather for Sport Touring.
- Visual (9): Info Center profile/jelly renders under `/-/media/Honda-Sales-Tool-Media-Folder/Images/2022-Civic-Hatchback/` (Profile-Headers, 3-4-Headers, Wheels).

## Open questions / capture requests
Straight-on long-lens side, front and rear photos of the real car with a floor tape; arch-lip heights and hub-to-arch gaps at curb weight; bumper extremes by plumb bob; mirror position.
