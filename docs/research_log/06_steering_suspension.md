# 06 Steering and suspension: research log

Files: `vehicle_data/steering.json`, `suspension.json` (with an `architecture` table), `alignment.json`, `hardpoints.json` (written by `scripts/domains/hardpoints_estimate.py`), `scripts/derivations/steering.py`, `scripts/derivations/suspension.py`.

## Sources opened (cache under cache/pages/)
- hondanews.ca 2024 Civic Hatchback Specifications (`22157798d6e48e1c.txt`), plus the 2022 (`344bc90bb36560a9`) and 2023 (`374416cf6bc6db5d`) tables. They give steering type, 2.2 turns, 11.4:1, the turning circle "11.6 m" and bars of 26.5/17.5 mm. The row says "Turning radius", but 11.6 m is the diameter: it equals the US 38.1 ft. The steering-ratio row carries a copy-paste unit "(m)".
- hondanews.com 2024 (`2b1524caf89378a3`) and 2022 (`fb1d5790fd3bfda8`) US spec tables, and hondainfocenter.com 2024 (`b67f7f855816944e`). For Sport Touring they give 2.21 turns, 11.41:1, 38.1 ft curb-to-curb, a 26.5 x 4.5 mm tubular front bar and a 17.5 mm solid rear bar. Model years 2022 to 2024 show no change.
  - Minor disagreement for other trims: hondainfocenter prints the rear bar as 17.0 mm for LX/Sport/EX-L, while hondanews.com prints 17.5 mm for all trims. Both agree on 17.5 mm for Sport Touring, so the target is unaffected.
- hondanews.com 2022 hatch debut release (`6b8fd454f6a040ce`). Gives the chassis narrative: MacPherson struts with low-friction ball joints and damper mount bearings, a larger compliance bushing, new rear lower-arm bushings and an aluminium front subframe.
- hondapartsnow.com control-arm and trailing-arm listings (`e9f731ff6b9e9d47`, `b8b52890c32a91d3`). These give the rear member part numbers that fit the "5 Door 1.5T Sport Touring" (upper arm, lower arm A lateral link, lower arm B, trailing arm) and the front lower arm.
  - The 1.5T EX-L/ST trailing arm (-T20-A10) differs from the 2.0 L part (-A00). The Si and Type R use T22 parts.
- Leads only, not used as target values:
  - Spoon Sports FL1 blog (`bbd81e64ddfb48f3`): JDM FL1 "normal rate F/2.7 R/2.8" kgf/mm. Non-NA market.
  - CivicXI 2023 Si thread (`b0264e7152552462`): Si springs F 27.0 / R 55.9 N/mm, motion ratio (wheel/spring) 1.029 / 1.333. Excluded variant.

## Blocked / not accessed
- hondapartsconnection.com: Cloudflare "Just a moment" challenge (403). Not worked around.
- techinfo.honda.com (service manual, alignment specs): paywalled. Not accessed.
- SPC alignment spec book: paid product.
- Diagram images were not analysed.

## Results
- **Steering:** ratio, turns and turning circle are class A, with Canadian and US sources agreeing within rounding. The angle derivations give:
  - outer lock ≈ 28.7°
  - inner lock (100 % Ackermann) ≈ 38.3°
  - mean lock from ratio ≈ 34.9°
  - ratio vs turning circle: consistent to about 4 % (ratio/geometry 1.04)
  - Ackermann estimate about 129 %. This is low confidence: it is an artefact-prone estimate because the printed ratio of a variable rack may not equal the exact lock average.
- **Unknown:** on-centre and lock ratios, wheel diameter, EPS assist layout (dual-pinion not confirmed).
- **Bars:** class A.
- **Springs, motion ratios, unsprung masses and bar geometry:** class E with wide ranges.
  - The rear spring-rate leads disagree by about 2x (27.5 vs 55.9 N/mm), and the range spans both.
  - Damping is only an inferred linear coefficient (ζ 0.2–0.45). No damper curve was found.
- **Alignment:** all unknown. No public 11th-gen spec chart was found. The 10th-gen chart is noted as a lead only.
- **Hard points:** 0 confirmed, 19 estimated (script, with Monte-Carlo ranges), 8 unknown. Left side only.

## Open questions / capture requests (highest value first)
1. A dealer alignment printout, which would give Honda's spec window.
2. Spring part numbers and a load test, or measurements of wire diameter, coil diameter and number of coils.
3. Underside photos of the rear corner, to confirm spring and damper placement.
4. Hard points measured on a lift.
5. Turn-plate lock angles, to separate the on-centre ratio, the lock ratio and the Ackermann figure.
6. Steering wheel diameter by tape.

## Leads for other domains
- Dimensions/wheels: the Canadian tables print track as 1536/1565 mm for the 18-in cars and 1546/1575 mm for LX.
- Mass: the Si owner thread estimates unsprung mass at 55 kg front and 45 kg rear per corner (Si, low confidence).
- Identity: Sport Touring and EX-L 1.5T hatch share the trailing-arm part (-T20-A10). The Canadian 2023 table lists a "Sport-B" trim.
