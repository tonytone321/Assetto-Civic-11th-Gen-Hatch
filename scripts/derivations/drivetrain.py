"""Drivetrain derivations (domain 5): overall ratios, road speed per engine speed,
predicted cruise rpm for cross-checking against observations, rpm after an upshift
from redline, and the gear-speed table. All SI: rolling circumference in m, speeds m/s.

Ratios come from transmission.json and are never adjusted to hit a target.
"""

KMH = 1 / 3.6
MPH = 1609.344 / 3600.0
GEARS = [1, 2, 3, 4, 5, 6]


def speed_per_rpm(gear_ratio, final_drive, circumference):
    """Road speed (m/s) per engine rpm in a gear, no tyre slip."""
    return circumference / (gear_ratio * final_drive * 60.0)


def rpm_at_speed(speed_ms, gear_ratio, final_drive, circumference):
    return speed_ms * gear_ratio * final_drive * 60.0 / circumference


# Rolling circumference uncertainty used for ranges: +/-1.5 % (tyre wear, pressure,
# speed growth, loaded vs unloaded) -- a stated assumption, not a measurement.
CIRC_TOL = 0.015

DERIVATIONS = []

for _spd, _name, _unit_desc in ((100 * KMH, "100kmh", "100 km/h"), (70 * MPH, "70mph", "70 mph")):
    DERIVATIONS.append(dict(
        key=f"drivetrain.pred_rpm_at_{_name}_6th",
        description=f"Predicted engine speed at {_unit_desc} in 6th (no slip), for comparison with observed tach readings",
        unit="rpm", impact="high", cls="D", status="estimated",
        inputs={"g6": "transmission.gear_6", "fd": "transmission.final_drive", "circ": "tires.rolling_circumference"},
        fn=(lambda g6, fd, circ, _s=_spd: rpm_at_speed(_s, g6, fd, circ)),
        range_fn=(lambda g6, fd, circ, _s=_spd: [rpm_at_speed(_s, g6, fd, circ * (1 + CIRC_TOL)),
                                                 rpm_at_speed(_s, g6, fd, circ * (1 - CIRC_TOL))]),
        confidence="high",
        how_to_measure=f"Hold a GPS-verified {_unit_desc} in 6th on level road and log engine rpm via OBD-II (PID 0x0C).",
        notes="rpm = v * g6 * FD * 60 / C_roll. Range = +/-1.5 % rolling circumference. Compare with drivetrain.obs_* records.",
    ))

for _k in range(1, 6):
    DERIVATIONS.append(dict(
        key=f"drivetrain.rpm_after_upshift_{_k}_{_k + 1}_from_redline",
        description=f"Engine speed after a {_k}-{_k + 1} upshift taken at redline (road speed held)",
        unit="rpm", impact="medium", cls="D", status="estimated",
        inputs={"ga": f"transmission.gear_{_k}", "gb": f"transmission.gear_{_k + 1}", "red": "engine.redline_rpm"},
        fn=(lambda ga, gb, red: red * gb / ga),
        range_fn=(lambda ga, gb, red: [red * gb / ga * 0.97, red * gb / ga]),
        confidence="high",
        how_to_measure="Datalog rpm and wheel speed through full-throttle upshifts.",
        notes="rpm_after = redline * g(k+1)/g(k). Lower bound allows ~3 % road-speed loss during the shift gap.",
    ))
    DERIVATIONS.append(dict(
        key=f"drivetrain.ratio_step_{_k}_{_k + 1}",
        description=f"Ratio step g{_k}/g{_k + 1}",
        unit="1", impact="low", cls="D", status="confirmed",
        inputs={"ga": f"transmission.gear_{_k}", "gb": f"transmission.gear_{_k + 1}"},
        fn=(lambda ga, gb: ga / gb),
        range_fn=(lambda ga, gb: [ga / gb, ga / gb]),
        confidence="high", how_to_measure=None,
        notes="Exact arithmetic on confirmed ratios.",
    ))


def _gear_speed_rows(g1, g2, g3, g4, g5, g6, gr, fd, circ, redline, limiter):
    rows = []
    for name, g in (("1", g1), ("2", g2), ("3", g3), ("4", g4), ("5", g5), ("6", g6), ("R", gr)):
        if g is None:
            continue
        v = speed_per_rpm(g, fd, circ)  # m/s per rpm
        rows.append({
            "gear": name,
            "ratio": g,
            "overall_ratio": round(g * fd, 4),
            "kmh_per_1000rpm": round(v * 1000 / KMH, 3),
            "mps_per_1000rpm": round(v * 1000, 4),
            "kmh_at_redline": None if redline is None else round(v * redline / KMH, 1),
            "kmh_at_limiter": None if limiter is None else round(v * limiter / KMH, 1),
            "redline_rpm": redline, "limiter_rpm": limiter,
            "rolling_circumference_m": circ, "final_drive": fd,
        })
    return rows


TABLES = [dict(
    path="vehicle_data/gear_speed_table.csv",
    inputs={"g1": "transmission.gear_1", "g2": "transmission.gear_2", "g3": "transmission.gear_3",
            "g4": "transmission.gear_4", "g5": "transmission.gear_5", "g6": "transmission.gear_6",
            "gr": "transmission.gear_reverse", "fd": "transmission.final_drive",
            "circ": "tires.rolling_circumference", "redline": "engine.redline_rpm",
            "limiter": "engine.limiter_rpm"},
    optional=["limiter", "redline"],  # columns left blank while these are unknown
    fn=_gear_speed_rows,
    description="Speed per 1000 rpm and at redline/limiter per gear, from resolved ratios and tyre rolling "
                "circumference (no slip). Reverse row included. Ratios are never tuned to match observations.",
)]
