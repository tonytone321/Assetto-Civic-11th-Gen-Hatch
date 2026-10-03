# 03 Mass and inertia — research log

Thread: domain 3. Files: `vehicle_data/mass_inertia.json`, `scripts/derivations/mass_inertia.py`, this log.

## Sources opened
- **hondanews.ca** 2022, 2023, 2024 Civic Hatchback spec releases (Honda Canada, rendered): Sport Touring MT curb weight **1382 kg** in all three years (no model-year change); fuel tank **46 L**. No GVWR, GAWR or weight distribution in the Canadian sheets.
- **hondanews.com** 2022 and 2024 (and two 2023) hatchback Specifications & Features releases (US): ST 6MT **3036 lb** (= 1377.1 kg) in every year; distribution 6MT **59/41** (2023/2024), **59.1 % / 40.9 %** (2022); fuel 12.4 gal.
- **hondainfocenter.com** 2022 and 2024 spec tables (American Honda): same 3036 lb, 59/41 (2024), 59.1/40.9 (2022), 12.39 gal. Column-to-trim mapping checked in raw HTML.
- **NHTSA Safercar_data.csv** (static.nhtsa.gov) + READ ME: 2024 Civic Hatchback row gives **SSF 1.48**, rollover possibility 0.095, "No Tip", min/max gross weight **3946 / 4056 lb**. The same SSF appears on the Sedan, Si and Type R rows; the crash-test VINs are 2022 Civic Sedans, so the SSF test car is probably a sedan. api.nhtsa.gov VehicleId 19595 agrees (0.095, No Tip).
- **68 FR 59250 (2003) Appendix II** (govinfo PDF, p.42): NHTSA's no-tip-up rollover risk model. Feeding it SSF 1.48 gives 0.0951, which matches the published 0.095.
- **PSU ME481 notes p.5**: a table of NHTSA VIPD class means taken from Heydinger et al. 1999 (SAE 1999-01-1336), plus the Jyy/Jxx and Jzz/Jxx bands. The SAE paper itself is paywalled and was not opened.
- **eCFR 49 CFR 571.3**: curb weight includes "maximum capacity of engine fuel", so the tank is taken as full (class E inference for Honda's figure).
- **Wikipedia, Gasoline**: specific gravity 0.71–0.77, European reference density 0.755 kg/L.

## Results
- Curb mass 1382 kg (A, CA, high). US 1377.1 kg kept as a second candidate. Not a conflict: the difference is 0.4 %, probably market equipment or rounding.
- Front fraction 0.591 (A, US 2022, preferred for its precision) and 0.59 (A, US 2024). No Canadian figure is published.
- Derived (scripts/derivations/mass_inertia.py): fuel mass, axle masses, CG Y = −(1−f)L, CG height = T_avg/(2·SSF) ≈ 0.52 m (range ±~17 mm), yaw/pitch/roll inertia from VIPD radius-of-gyration ratios (≈ 0.54 L, 0.52 L, 0.45 T; ±8 % on k), and cross-checks for rollover risk, Izz/Ixx and axle sum.

## Unknown / blocked
- GVWR for this exact trim and gearbox, and both GAWRs: not in any Honda spec sheet. owners.honda.com redirects to a login portal (mygarage.honda.com), and no owner's-manual PDF or door-jamb label photo was found. GVWR is bounded to 1789.9–1839.8 kg by the NHTSA lineup min/max.
- Corner weights, lateral CG, unsprung masses: unpublished.
- Magazine "as tested" weights were not collected, to stay economical. They are left to the performance thread (lead below).

## Leads for other domains
- Dimensions: hondanews.com 2024 US prints Length 179.0 in, while hondainfocenter prints 184.0 in and Canada prints 4529 mm. Tracks: ST 60.5/61.6 in (US) vs CA 1536/1565 mm.
- Steering/suspension (hondanews.com 2024 US, ST column): steering ratio 11.41:1, 2.21 turns, turning diameter 38.1 ft curb-to-curb; stabilizer bars "26.5 x 4.5 (tubular)" front, "17.5 (solid)" rear (mm). Canada: 11.4:1, 2.2 turns, "Turning radius (curb-to-curb) 11.6 m".
- Engine: hondanews.com 2024 US prints Boost Pressure 16.5 psi and Redline 6,600 rpm for the 1.5T.
- Performance: C/D and MotorTrend test sheets often print test weight and % front. Record them as perf/test-weight items.
