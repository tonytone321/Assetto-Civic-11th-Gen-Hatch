"""Domain 4 derivations (engine). SI in, SI out. See scripts/derivations/__init__.py."""
import glob
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RPM2RADS = 2 * math.pi / 60.0

DERIVATIONS = [
    dict(key="engine.displacement_from_bore_stroke",
         description="Swept volume computed from bore, stroke and 4 cylinders (cross-check of published 1498 cc)",
         unit="m3", impact="low", cls="D", status="confirmed",
         inputs={"bore": "engine.bore", "stroke": "engine.stroke"},
         fn=lambda bore, stroke: 4 * math.pi / 4 * bore ** 2 * stroke,
         range_fn=lambda bore, stroke: [4 * math.pi / 4 * (bore - 5e-5) ** 2 * (stroke - 5e-5),
                                        4 * math.pi / 4 * (bore + 5e-5) ** 2 * (stroke + 5e-5)],
         confidence="high", how_to_measure="n/a (geometry)",
         notes="Range from +/-0.05 mm print rounding. Should match engine.displacement (1.498e-3 m3) within ~0.1%."),
    dict(key="engine.torque_at_power_peak",
         description="Crank torque implied by rated peak power at its rpm (T = P / omega)",
         unit="N*m", impact="high", cls="D", status="confirmed",
         inputs={"p": "engine.power_max", "n": "engine.power_max_rpm"},
         fn=lambda p, n: p / (n * RPM2RADS),
         range_fn=lambda p, n: [p * 0.995 / (n * RPM2RADS), p * 1.005 / (n * RPM2RADS)],
         confidence="high", how_to_measure="Engine dyno or corrected chassis dyno at 6000 rpm.",
         notes="Exact arithmetic on class A ratings; range covers rounding of '180 hp'."),
    dict(key="engine.power_at_torque_plateau_end",
         description="Crank power at the end of the rated torque plateau (T_max * omega at torque_max_rpm_high)",
         unit="W", impact="medium", cls="D", status="confirmed",
         inputs={"t": "engine.torque_max", "n": "engine.torque_max_rpm_high"},
         fn=lambda t, n: t * n * RPM2RADS,
         range_fn=lambda t, n: [t * 0.995 * n * RPM2RADS, t * 1.005 * n * RPM2RADS],
         confidence="high", how_to_measure="As torque_at_power_peak.", notes="Rated-figure arithmetic."),
    dict(key="engine.power_at_torque_plateau_start",
         description="Crank power at the start of the rated torque plateau",
         unit="W", impact="low", cls="D", status="confirmed",
         inputs={"t": "engine.torque_max", "n": "engine.torque_max_rpm_low"},
         fn=lambda t, n: t * n * RPM2RADS,
         range_fn=lambda t, n: [t * 0.995 * n * RPM2RADS, t * 1.005 * n * RPM2RADS],
         confidence="high", how_to_measure="As torque_at_power_peak.", notes="Rated-figure arithmetic."),
    dict(key="engine.bmep_at_torque_peak",
         description="Brake mean effective pressure at rated peak torque (4-stroke: 4*pi*T/Vd)",
         unit="Pa", impact="low", cls="D", status="confirmed",
         inputs={"t": "engine.torque_max", "vd": "engine.displacement"},
         fn=lambda t, vd: 4 * math.pi * t / vd,
         range_fn=lambda t, vd: [4 * math.pi * t * 0.995 / vd, 4 * math.pi * t * 1.005 / vd],
         confidence="high", how_to_measure="n/a", notes="Plausibility check (~1.86 MPa)."),
    dict(key="engine.mean_piston_speed_at_redline",
         description="Mean piston speed at redline (2*stroke*n/60)",
         unit="m/s", impact="low", cls="D", status="confirmed",
         inputs={"s": "engine.stroke", "n": "engine.redline_rpm"},
         fn=lambda s, n: 2 * s * n / 60.0,
         range_fn=lambda s, n: [2 * s * n / 60.0 * 0.999, 2 * s * n / 60.0 * 1.001],
         confidence="high", how_to_measure="n/a", notes="Plausibility check."),
]


def _curve_rows(loss):
    """Rows from engine_curves/*.json runs that carry digitized rpm points and are flagged
    use_for_curve. Raw points only: no smoothing, interpolation or invented points."""
    rows = []
    for p in sorted(glob.glob(os.path.join(ROOT, "engine_curves", "*.json"))):
        with open(p, encoding="utf-8") as f:
            run = json.load(f)
        if not run.get("use_for_curve") or not run.get("points"):
            continue
        for pt in run["points"]:   # each: {"rpm", "wheel_torque_Nm"} and/or {"wheel_power_W"}
            n = pt["rpm"]
            wt = pt.get("wheel_torque_Nm")
            wp = pt.get("wheel_power_W")
            if wt is None and wp is not None:
                wt = wp / (n * RPM2RADS)
            if wp is None and wt is not None:
                wp = wt * n * RPM2RADS
            rows.append(dict(rpm=n, wheel_torque_Nm=wt, wheel_power_W=wp,
                             crank_torque_Nm=wt / (1 - loss), crank_power_W=wp / (1 - loss),
                             assumed_loss=loss, source_run=run["run_id"]))
    return rows


TABLES = [
    dict(path="vehicle_data/engine_curve.csv",
         inputs={"loss": "engine.driveline_loss_assumed"},
         columns=["rpm", "wheel_torque_Nm", "wheel_power_W", "crank_torque_Nm", "crank_power_W",
                  "assumed_loss", "source_run"],
         fn=lambda loss: _curve_rows(loss),
         description="Stock dyno points from engine_curves/ runs flagged use_for_curve (wheel measured, crank = wheel/(1-loss)). "
                     "As of Phase 1 no stock 6MT hatch run with rpm-resolved points was found, so the table has no rows."),
]
