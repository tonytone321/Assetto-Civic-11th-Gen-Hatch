# 04 Engine and turbo — research log

Builder: `scripts/domains/engine_db.py` (writes `vehicle_data/engine.json`, `vehicle_data/turbo.json`, `engine_curves/*.json`; aborts if any A–C evidence fragment is not in the cached page text). Derivations: `scripts/derivations/engine.py`.

## Sources opened (all text cached under cache/pages/)
- hondanews.ca 2022, 2023, 2024 Civic Hatchback spec sheets (Honda Canada, class A): 180 hp @ 6000, 177 lb-ft @ 1700-4500, 1498 cc, 73 x 89.5 mm, 10.3:1, regular fuel, SAE J1349 net. **Identical in all three years** (model-year check). No redline, no split by gearbox.
- hondainfocenter.com 2024 and 2022 hatchback specs (American Honda, A): same figures plus **Redline 6600 rpm** and **Boost 16.5 psi** (Sport Touring column). 2023 page is 404.
- hondanews.com "Honda 1.5-Liter Turbo Engine" (May 16, 2024, A): Civic Hatchback 2022-2024 EX-L/Sport Touring = **L15B7 (w/VTEC)**; exhaust-cam VTEC, dual VTC, 4-into-2 manifold cast in head, **MHI TD03 small single-scroll turbo, electric wastegate**, reshaped 11-blade turbine with diagonal entry, front-low intercooler, 16.5 psi on regular. Si is L15CA (excluded).
- hondainfocenter 2022/2024 "Turbocharged 1.5-liter Engine" feature: "negligible turbo lag".
- Stock dyno (all CVT, none 6MT hatch): Hondata 2022 EX sedan 162.46 whp / 163.63 lb-ft (via The Drive); PRL 2022 Touring sedan CVT 168.6 whp avg peak (DynoJet 224X, speed x-axis) and 171 whp; TSP 154 whp / 163 lb-ft (CVT). Recorded as peak-only run files, `use_for_curve: false`.

## Blocked / not done
- hondata.com: robots.txt disallows ClaudeBot — not fetched. knfilters.com: 403. autos.yahoo.com (syndicated C/D test): robots-disallowed. hondanews.com channel page: HTTP error.
- **No stock 6MT hatch dyno with an rpm curve was found**, so no chart was digitized and `engine_curve.csv` has no rows. This is the main gap.
- Limiter rpm, limiter behaviour, DFCO behaviour, boost taper and per-gear torque management: unknown (no public stock datalogs). Idle 750 rpm is class E.

## Conflicts
None among class A sources. Stock CVT wheel figures (154-171 whp) imply 5-14 % below the 180 hp rating at typical FWD losses; they are CVT/sedan and not comparable to the target, so no conflict was raised.

## Open questions / capture requests
1. Stock 6MT WOT pull on a chassis dyno (3rd or 4th gear, SAE correction) with OBD log: torque curve, MAP vs rpm (boost onset/taper), limiter.
2. Lift-off/overrun log: rpm, throttle, fuel trim/injector to find DFCO thresholds (needed for burble modelling).
3. Free-rev decay log for engine+flywheel inertia.

## Leads for other domains
- Drivetrain: owner reports rev hang on stock-tune 6MT reduced via KTuner (civicxi "Chilly's 2023 Civic FL1 Sport Touring 6MT Build"), i.e. calibration-related. No flywheel type evidence found.
- Mass: Honda Canada 2022/2023/2024 sheets: curb weight Sport Touring MT/CVT 1382/1412 kg; fuel tank 46 L. US 2022: Sport Touring 3036 lbs (6MT) / 3102 lbs (CVT).
- Steering (2024 CA sheet): 2.2 turns, 11.4:1 ratio, turning radius curb-to-curb 11.6 m; stabilizer bars 26.5/17.5 mm; tires P235/40 R18 91W.
- Identity: Honda Canada 2024 hatch trims are Sport and Sport Touring (both 1.5T); 6MT only on Sport Touring. Canadian 6MT fuel consumption 8.5/6.3/7.5 L/100 km.
- Audio: US Info Center CARB rating for Sport Touring 6MT is LEV3-ULEV50 vs SULEV30 for CVT (different emissions calibration between gearboxes).
