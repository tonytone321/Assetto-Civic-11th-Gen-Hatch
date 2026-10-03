"""Wheels and tires derivations (domain 7): nominal tire geometry from the size
designation (section width, aspect ratio, rim diameter; all SI in from tires.json).

Nominal figures follow the size code (ISO/ETRTO convention: sidewall = width x aspect
ratio). Real tires differ by make/model; maker-published dimensions, once the OE tire
is identified, are recorded as separate candidates in tires.json.
"""
import math

# Rolling circumference / nominal circumference. Stated assumption (not a cited value):
# makers' revs-per-distance figures for passenger radials typically correspond to a
# circumference ~2-4 % below the unloaded geometric one. Range kept wide.
ROLL_FACTOR, ROLL_LO, ROLL_HI = 0.97, 0.96, 0.985
# Static loaded-radius deflection for a 40-series tire at ~4 kN corner load (assumption).
DEFL, DEFL_LO, DEFL_HI = 0.018, 0.012, 0.025


def sidewall(w, ar):
    return w * ar


def od_nominal(w, ar, rim):
    return rim + 2 * sidewall(w, ar)


DERIVATIONS = [
    dict(key="tires.sidewall_height_nominal", description="Nominal sidewall height (width x aspect ratio)",
         unit="m", impact="medium", cls="D", status="confirmed",
         inputs={"w": "tires.section_width", "ar": "tires.aspect_ratio"},
         fn=lambda w, ar: sidewall(w, ar),
         range_fn=lambda w, ar: [sidewall(w, ar) * 0.98, sidewall(w, ar) * 1.02],
         confidence="high", how_to_measure="Measure tire OD and rim flange diameter; (OD - rim)/2.",
         notes="Exact arithmetic on the size code; real tires vary about +/-2 %."),
    dict(key="tires.overall_diameter_nominal", description="Nominal unloaded overall diameter from the size code",
         unit="m", impact="critical", cls="D", status="confirmed",
         inputs={"w": "tires.section_width", "ar": "tires.aspect_ratio", "rim": "tires.rim_diameter"},
         fn=lambda w, ar, rim: od_nominal(w, ar, rim),
         range_fn=lambda w, ar, rim: [rim + 2 * sidewall(w, ar) * 0.98, rim + 2 * sidewall(w, ar) * 1.02],
         confidence="high", how_to_measure="Tape the circumference of an inflated, unloaded tire (/pi), +/-1 mm.",
         notes="OD = rim + 2 x width x aspect ratio. 235/40R18 -> 0.6452 m."),
    dict(key="tires.rolling_circumference", description="Rolling circumference (distance per wheel revolution), estimated from nominal size",
         unit="m", impact="critical", cls="D", status="estimated",
         inputs={"w": "tires.section_width", "ar": "tires.aspect_ratio", "rim": "tires.rim_diameter"},
         fn=lambda w, ar, rim: math.pi * od_nominal(w, ar, rim) * ROLL_FACTOR,
         range_fn=lambda w, ar, rim: [math.pi * od_nominal(w, ar, rim) * ROLL_LO, math.pi * od_nominal(w, ar, rim) * ROLL_HI],
         confidence="medium",
         how_to_measure="Mark the tread and floor, roll the loaded car 5-10 revolutions in a straight line, divide distance by revolutions (+/-0.3 %); or use the OE tire maker's revs/km.",
         notes=f"C_roll = pi x OD_nominal x {ROLL_FACTOR} (range {ROLL_LO}-{ROLL_HI}); the factor is an engineering assumption, not a cited figure. Superseded by maker revs/km once the OE tire is known."),
    dict(key="tires.loaded_radius", description="Static loaded radius (axle to ground), estimated",
         unit="m", impact="high", cls="E", status="estimated",
         inputs={"w": "tires.section_width", "ar": "tires.aspect_ratio", "rim": "tires.rim_diameter"},
         fn=lambda w, ar, rim: od_nominal(w, ar, rim) / 2 - DEFL,
         range_fn=lambda w, ar, rim: [od_nominal(w, ar, rim) / 2 - DEFL_HI, od_nominal(w, ar, rim) / 2 - DEFL_LO],
         confidence="low",
         how_to_measure="With the car at curb weight and placard pressure, measure hub-centre height above the floor at each corner (+/-1 mm).",
         notes=f"r_loaded = OD_nominal/2 - deflection; deflection {DEFL*1000:.0f} mm (range {DEFL_LO*1000:.0f}-{DEFL_HI*1000:.0f} mm) is a judgment for a 40-series tire at placard pressure."),
]
