# 05 Drivetrain — research log

Files: `vehicle_data/transmission.json`, `vehicle_data/drivetrain.json`, `scripts/derivations/drivetrain.py` (DERIVATIONS + TABLES → `vehicle_data/gear_speed_table.csv`, built by the coordinator after resolution; not written here).

## Sources opened
- hondanews.com 2024 / 2023 / 2022 Civic Hatchback Specifications & Features (US, class A): 6MT 3.643 / 2.080 / 1.361 / 1.024 / 0.830 / 0.686, R 3.673, FD 4.100 (2022 prints 4.10). Columns checked in raw HTML (Sport and Sport Touring). **No change 2022→2024.**
- hondainfocenter.com 2024 and 2022 spec pages (US, class A, same publisher): same values, trailing zeros dropped (2.08, 0.83, 4.1). 2023 page is 404.
- hondanews.ca 2024 Civic Hatchback Specifications (CA, class A): 6MT "Available" on Sport Touring only; **no gear ratios printed**; AHA, Hill Start Assist and Idle-stop marked for both trims.
- hondanews.ca 2022 Civic Hatchback global debut release (June 23, 2021, class A): "A new dual-mass flywheel helps reduce noise and vibration…"; "improved shift rigidity and shorter shift throws"; "new standard idle-stop system (CVT only)" (said about the 2.0L CVT).
- hondapartsnow.com 2024 Civic flywheel and differential listings (OEM EPC data via retailer, class C): ST 6MT flywheel 22100-5CD-018 (distinct from Si single-mass 22100-65P-003); ST 6MT differential 41100-57A-000 "Differential Complete" — the Si (41200-5CD-003) and Type R (41200-R3P-003) are the helical LSDs. → **open differential.**
- CivicXI forum clutch thread (class C, low): OEM disc has no damper springs, damping in the DMF; hydraulic actuation with in-line clutch damper.
- tractionlife.com 2022 ST manual review (class C): "some rev hang", not quantified.

## Blocked / not found
- No Canadian source prints ratios; US values recorded with US applicability (no evidence of a CA difference).
- Clutch disc OD/ID, clamp load/torque capacity, flywheel and driveline inertia, gearbox code, rev-match, shift indicator, observed cruise rpm, quantified rev hang: **unknown** (searches listed in records). prlmotorsports Exedy kit page 404; hondapartsnow clutch-disc/pressure-plate category URLs 404; autotrader.ca editorial blocked (preflight).
- Owner's manual not opened (would settle idle-stop on MT, rev-match, shift indicator).

## Conflicts
- Idle-stop on 6MT: 2024 spec tables mark Idle-stop for every trim column vs 2022 Honda Canada release "(CVT only)". Recorded as class E low confidence; needs owner's manual or the real car.

## Open questions
- Lead (not verified): aftermarket Exedy Stage 2 kit for 11th-gen 1.5T uses a 230 mm disc, 24T spline.

## Leads for other domains
- Engine (04): redline 6600 rpm printed in US and CA 2022 spec tables; turbo page says "negligible turbo lag" (hondainfocenter 2024 Turbocharged-1-5-liter-Engine page, cache 2b07d05f0cfc9da1).
- Identity (01): 2024 Canada 6MT on Sport Touring only; 2022 Canada 6MT optional on LX/Sport/ST; US 2024 6MT on Sport (2.0L) and Sport Touring. ST flywheel part 22100-5CD-018.
- Dashboard (09): check MT shift-up indicator and idle-stop lamp behaviour on the MT.
- Wheels/tires (07): gear_speed_table needs `tires.rolling_circumference`.
