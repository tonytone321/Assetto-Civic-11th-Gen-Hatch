# 08 Performance targets — research log

Builder and target table: `python3 scripts/domains/perf_targets.py` → `vehicle_data/validation_targets.json` (checks every evidence string against the cached page before writing).

## Sources opened
- **Car and Driver, "Tested: 2022 Honda Civic Hatchback Brings Stick-Shift Fun"** (Rich Ceppos, 2021-10-12), a37936938 — 2022 Civic **Sport Touring Hatchback 6MT**, Sonic Gray, Continental ContiProContact 235/40R-18 91W M+S, curb 3024 lb (C/D scales, full fuel). 0-60 7.3 s, 1/4 15.5 s @ 91 mph, 0-100 19.0 s, 0-120 30.9 s, rollout 0.4 s, 5-60 8.3 s, top-gear 30-50 12.1 s / 50-70 9.4 s, top speed 130 mph (C/D **estimate**), 70-0 173 ft, skidpad 0.90 g (text; ESC intervened). Cache `cache/pages/2df590f6625a05ee.txt`; same box on `caranddriver.com/honda/civic-2022` (`e2b19c8e54228dee.txt`). C/D's 2023/2024 Civic pages repeat this same 2022 test — no newer hatch test.
- **C/D "How we test"** (`8c550355c08b8a10.txt`): 1-ft rollout omitted, correction to 60 F / sea level, two-direction average, second-best of six 70-0 stops, skidpad "usually" 300 ft, weighed after topping off fuel.
- **MotorTrend 2022 Civic Sport Touring Hatchback First Test** (2021-11-24, `/reviews/…first-test-review`, allowed by robots): test car was a **CVT** → excluded (kept in `excluded_tests` for context only).
- MotorWeek first impressions 2022 hatch: manual tester, no figures.

## Blocked / not available
- autos.yahoo.com (C/D syndication): robots.txt disallows ClaudeBot — not fetched.
- Edmunds review pages 2022/23/24: HTTP 403 — not worked around.
- Consumer Reports: paywalled — not bypassed.
- MotorTrend /roadtests/ disallowed by robots (not needed; the /reviews/ test was a CVT anyway).
- No Canadian outlet instrumented figures found (Guide Auto, Motor Illustrated, Driving.ca searches gave none); no Honda 0-100 km/h claim found.

## Result
Only **one** qualifying instrumented test (C/D). Every target is n=1 and flagged as such; nothing widened. Unknown: 0-100 km/h, Honda 0-100 claim, 100-0 km/h, 60-0 mph (6MT), 0-30 mph. Top speed is a C/D estimate, governor status unknown.

## Open questions
- A second independent 6MT Sport Touring test (Edmunds, CR, Canadian magazine) would turn n=1 into ranges.

## Leads for other domains
- **Mass (03):** C/D curb weight 3024 lb (1372 kg), 2022 ST 6MT, full fuel, no driver; F/R % not printed.
- **Tires (07):** C/D test car wore Continental ContiProContact 235/40R-18 91W M+S (all-season) — check vs factory fitment.
- **Brakes (07):** C/D lists 11.1-in vented front / 10.2-in solid rear discs.
- **Drivetrain/engine (04/05):** top-gear 30-50 in 12.1 s vs 50-70 in 9.4 s shows weak response at very low rpm in 6th (boost onset); 5-60 is 1.0 s slower than 0-60 (rollout omitted).
- **Identity (01):** MotorTrend 2022 ST hatch CVT tester was Morning Mist Blue Metallic; C/D tester Sonic Gray ($395 option, US).
