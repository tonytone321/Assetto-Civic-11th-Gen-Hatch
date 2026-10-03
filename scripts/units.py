#!/usr/bin/env python3
"""Unit conversion to SI. Every SI value in vehicle_data/ that came from a printed
figure is computed here, never typed, and validate_db.py recomputes it.

to_si(value, unit) -> (si_value, si_unit)

Exact definitions: inch = 0.0254 m, lb = 0.45359237 kg, mechanical hp = 745.69987158227 W
(SAE J1349 rating), PS = 735.49875 W, lbf = 4.4482216152605 N, US gal = 3.785411784 L,
Imp gal = 4.54609 L, mile = 1609.344 m, psi = 6894.757293168 Pa.
"""
import math

IN = 0.0254
FT = 0.3048
LB = 0.45359237
LBF = 4.4482216152605
HP = 745.69987158227
PS = 735.49875
MILE = 1609.344
USGAL = 3.785411784e-3
IMPGAL = 4.54609e-3
PSI = 6894.757293168
G0 = 9.80665

# unit string -> (factor, offset, si_unit). si = value*factor + offset
_TABLE = {
    # length
    "m": (1.0, 0, "m"), "mm": (1e-3, 0, "m"), "cm": (1e-2, 0, "m"), "km": (1e3, 0, "m"),
    "in": (IN, 0, "m"), "ft": (FT, 0, "m"), "mi": (MILE, 0, "m"),
    # mass
    "kg": (1.0, 0, "kg"), "g": (1e-3, 0, "kg"), "lb": (LB, 0, "kg"), "lbs": (LB, 0, "kg"),
    # power
    "W": (1.0, 0, "W"), "kW": (1e3, 0, "W"), "hp": (HP, 0, "W"), "PS": (PS, 0, "W"),
    # torque / force
    "N*m": (1.0, 0, "N*m"), "Nm": (1.0, 0, "N*m"), "lb-ft": (LBF * FT, 0, "N*m"),
    "kgf*m": (G0, 0, "N*m"), "N": (1.0, 0, "N"), "lbf": (LBF, 0, "N"), "kgf": (G0, 0, "N"),
    # spring / stiffness
    "N/m": (1.0, 0, "N/m"), "N/mm": (1e3, 0, "N/m"), "lb/in": (LBF / IN, 0, "N/m"),
    "kgf/mm": (G0 * 1e3, 0, "N/m"),
    "N*m/rad": (1.0, 0, "N*m/rad"), "N*m/deg": (180.0 / math.pi, 0, "N*m/rad"),
    # speed / rotation
    "m/s": (1.0, 0, "m/s"), "km/h": (1 / 3.6, 0, "m/s"), "mph": (MILE / 3600.0, 0, "m/s"),
    "rpm": (1.0, 0, "rpm"), "rad/s": (1.0, 0, "rad/s"),
    # volume
    "m3": (1.0, 0, "m3"), "L": (1e-3, 0, "m3"), "US gal": (USGAL, 0, "m3"),
    "Imp gal": (IMPGAL, 0, "m3"), "cc": (1e-6, 0, "m3"), "ft3": (FT ** 3, 0, "m3"),
    # area
    "m2": (1.0, 0, "m2"), "ft2": (FT ** 2, 0, "m2"), "cm2": (1e-4, 0, "m2"), "in2": (IN ** 2, 0, "m2"),
    # pressure
    "Pa": (1.0, 0, "Pa"), "kPa": (1e3, 0, "Pa"), "bar": (1e5, 0, "Pa"), "psi": (PSI, 0, "Pa"),
    # angle
    "rad": (1.0, 0, "rad"), "deg": (math.pi / 180.0, 0, "rad"),
    "arcmin": (math.pi / 10800.0, 0, "rad"),
    # time
    "s": (1.0, 0, "s"), "ms": (1e-3, 0, "s"), "min": (60.0, 0, "s"), "h": (3600.0, 0, "s"),
    # inertia
    "kg*m2": (1.0, 0, "kg*m2"), "lb*ft2": (LB * FT ** 2, 0, "kg*m2"), "lb*in2": (LB * IN ** 2, 0, "kg*m2"),
    # temperature
    "C": (1.0, 273.15, "K"), "F": (5.0 / 9.0, 273.15 - 32 * 5.0 / 9.0, "K"), "K": (1.0, 0, "K"),
    # acceleration
    "g": None,  # ambiguous with gram; use "g0" for standard gravity
    "g0": (G0, 0, "m/s2"), "m/s2": (1.0, 0, "m/s2"),
    # fuel economy (kept in printed form; converted where needed)
    "L/100km": (1.0, 0, "L/100km"),
    # dimensionless
    "1": (1.0, 0, "1"), "ratio": (1.0, 0, "1"), "%": (0.01, 0, "1"), "turns": (1.0, 0, "turns"),
    "count": (1.0, 0, "count"), "text": None, "bool": None,
}

# speed-per-thousand-rpm and similar compound units
_TABLE["km/h/1000rpm"] = (1 / 3.6, 0, "m/s/1000rpm")
_TABLE["mph/1000rpm"] = (MILE / 3600.0, 0, "m/s/1000rpm")


def si_unit(unit):
    if unit not in _TABLE or _TABLE[unit] is None:
        return unit
    return _TABLE[unit][2]


def to_si(value, unit):
    """Convert a number (or list of numbers) printed in `unit` to SI."""
    if unit not in _TABLE:
        raise KeyError(f"unknown unit {unit!r}; add it to scripts/units.py")
    spec = _TABLE[unit]
    if spec is None:
        return value, unit
    f, o, u = spec
    if isinstance(value, (list, tuple)):
        return [None if v is None else v * f + o for v in value], u
    if value is None:
        return None, u
    return value * f + o, u


def is_known(unit):
    return unit in _TABLE


if __name__ == "__main__":
    import sys
    v, u = to_si(float(sys.argv[1]), sys.argv[2])
    print(f"{v!r} {u}")
