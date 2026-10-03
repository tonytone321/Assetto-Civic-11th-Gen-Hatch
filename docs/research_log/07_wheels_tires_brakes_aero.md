# 07 Wheels, tires, brakes and aero — research log

Files: `vehicle_data/{wheels,tires,brakes,aero}.json`, `scripts/derivations/{wheels_tires,brakes_aero}.py`.
(Records built by a one-off builder script kept outside the repo; all values converted by `dbutil.record(printed=...)`; quotes checked against cache with `validate_db.quote_check`: 47/47 found.)

## Sources opened
- hondanews.ca 2024 Civic Hatchback Specifications (Apr 4 2024, Canada, A): ST wheels `18" aluminum-alloy wheels (machined with black inserts)`, tires `P235/40 R18 91W` all-season, ventilated front/solid rear discs, ABS/EBD/Brake Assist, EPB with auto brake hold, spare T125/85 D16 99M. No rotor sizes, no spoiler, no Cd.
- hondainfocenter.com 2024 Civic Hatchback specs (US, A): ST rotors `11.1 in / 10.2 in`, 235/40R18 91W, spare T125/85R16 97M (US/CA spare wording differs).
- hondainfocenter.com 2024 Wheels-and-Tires page (A; page title says 2023): ST has "its own unique 18-inch alloy wheel design".
- honda.ca 2022 Civic Hatchback header spec PDF (CA, A): same tire; wheels "machined-tinted with black inserts".
- hondanews.com 2022 Civic Hatchback press kit (US, A): rotors 11.1 in ventilated (0.9 in thick) front, 10.2 in solid (0.4 in) rear, single-piston calipers front and rear (all 2022 Civic trims); ST wheel "split 5-spoke ... dark clear-coated machined face and Berlina Black inserts"; aero: ~3 % drag reduction (no Cd), bumper corners, mirror vortex generators, tailgate trailing edge; "integrated rear spoiler" (separate spoiler eliminated); floor undercover.
- hondapartsnow.com rims 2022/2023/2024 (C): ST wheel 42700-T20-A31 "W-DISK (18X8J)", 5 Door Sport Touring 6MT/CVT, all three years; "Item Weight 16.30 Pounds" (unreliable field).
- hondapartsnow.com calipers 2024 (C): front seal kit 01463-TXM-A01 "Set, Front (Ad57-15")"; rear caliper 43018-T20-A02 "Actuator, Caliper" (EPB motor on caliper).
- kamispeed.com fitment blog (C, low): "factory 18" wheels ... 18x8" ... +50 offset", 5x114.3.
- tirepressure.com (C aggregator): 235/40R18 33 psi front / 32 psi rear (US).

## Blocked / failed
- tirerack.com (Akamai "page unavailable", rendered) — OE tire listing unavailable.
- wheel-size.com 403; buybrakes.com 403; goodyear.com/goodyear.ca product URLs 404; detroitaxle 404.
- Owner's manual not opened (techinfo.honda.com treated as blocked per coordinator) — placard pressure (kPa), lug torque unverified.

## Unknown (with how_to_measure in JSON)
OE tire make/model (lead: Goodyear Eagle Sport All-Season, retailer text says OE on 2023-24 Civic, trim unstated) and therefore maker OD, revs/km, tire mass, tread depth, UTQG; wheel centre bore; lug torque; piston diameters (lead: 57 mm front from "AD57" code, unconfirmed) so brake bias is not computable; booster type; Cd, frontal area (published), lift, balance, grille shutters, cooling openings.

## Derivations
- `wheels_tires.py`: tires.sidewall_height_nominal (0.094 m), tires.overall_diameter_nominal (0.6452 m), tires.rolling_circumference (0.97 x pi x OD = 1.966 m, range 1.946-1.997; factor is an assumption), tires.loaded_radius (OD/2 - 18 mm, E).
- `brakes_aero.py`: front/rear effective radius (E), brakes.bias_front_hydraulic (needs piston diameters -> unknown now), aero.frontal_area_est (0.83 x W x H, E, ~2.12 m2).

## Leads for other domains
- Identity/visual: ST wheel is unique split 5-spoke, part 42700-T20-A31 2022-2024; Sport hatch wheel is Berlina Black and shared with sedan. Spare designation differs US (T125/85R16 97M) vs CA (T125/85 D16 99M).
- Suspension: Canada lists stabilizer bars 26.5/17.5 mm; US 2024 table prints "26.5 mm x 4.5 mm (tubular) / 17.0 mm (solid)" in some columns and 17.5 in others — check column mapping.
- Visual: press kit says manual cars have parking-brake button left of shifter.
