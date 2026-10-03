"""Brakes and aero derivations (domain 7).

Brake bias: hydraulic front share of brake torque with equal line pressure, equal pad
mu front/rear, one piston per caliper (press kit: single-piston front and rear) and
effective radius = rotor radius - assumed half pad height. EBD/ABS modulation ignored.
Unknown until piston diameters are known.

Frontal area: A = k * width * height with a shape fill factor k (assumption, see notes).
"""
import math

PAD_HALF_F, PAD_HALF_R = 0.025, 0.020   # assumed half pad radial height, m
PAD_TOL = 0.005


def _share(df, dr, rf, rr, hf, hr):
    tf = math.pi / 4 * df ** 2 * (rf / 2 - hf)
    tr = math.pi / 4 * dr ** 2 * (rr / 2 - hr)
    return tf / (tf + tr)


K_FILL, K_LO, K_HI = 0.83, 0.80, 0.86

DERIVATIONS = [
    dict(key="brakes.front_effective_radius", description="Front rotor effective (pad centroid) radius, estimated",
         unit="m", impact="medium", cls="E", status="estimated",
         inputs={"d": "brakes.front_rotor_diameter"},
         fn=lambda d: d / 2 - PAD_HALF_F,
         range_fn=lambda d: [d / 2 - PAD_HALF_F - PAD_TOL, d / 2 - PAD_HALF_F + PAD_TOL],
         confidence="low", how_to_measure="Measure pad radial height and rotor OD; r_eff ~ OD/2 - pad height/2.",
         notes="Half pad height 25 mm front is an assumption."),
    dict(key="brakes.rear_effective_radius", description="Rear rotor effective radius, estimated",
         unit="m", impact="medium", cls="E", status="estimated",
         inputs={"d": "brakes.rear_rotor_diameter"},
         fn=lambda d: d / 2 - PAD_HALF_R,
         range_fn=lambda d: [d / 2 - PAD_HALF_R - PAD_TOL, d / 2 - PAD_HALF_R + PAD_TOL],
         confidence="low", how_to_measure="Measure pad radial height and rotor OD.",
         notes="Half pad height 20 mm rear is an assumption."),
    dict(key="brakes.bias_front_hydraulic", description="Front share of brake torque at equal line pressure (no EBD)",
         unit="1", impact="high", cls="D", status="estimated",
         inputs={"df": "brakes.front_piston_diameter", "dr": "brakes.rear_piston_diameter",
                 "rf": "brakes.front_rotor_diameter", "rr": "brakes.rear_rotor_diameter"},
         fn=lambda df, dr, rf, rr: _share(df, dr, rf, rr, PAD_HALF_F, PAD_HALF_R),
         range_fn=lambda df, dr, rf, rr: sorted([_share(df, dr, rf, rr, PAD_HALF_F + PAD_TOL, PAD_HALF_R - PAD_TOL),
                                                 _share(df, dr, rf, rr, PAD_HALF_F - PAD_TOL, PAD_HALF_R + PAD_TOL)]),
         confidence="low", how_to_measure="Measure piston diameters and pad heights; or log front/rear line pressure.",
         notes="Equal pad mu front/rear assumed; real bias also set by EBD. Torque share, not force at the tire."),
    dict(key="aero.frontal_area_est", description="Frontal area estimate from body width x height x fill factor",
         unit="m2", impact="high", cls="E", status="estimated",
         inputs={"w": "dimensions.width_body", "h": "dimensions.height"},
         fn=lambda w, h: K_FILL * w * h,
         range_fn=lambda w, h: [K_LO * w * h, K_HI * w * h],
         confidence="low", how_to_measure="Head-on long-lens photo with a scale; integrate the silhouette (incl. mirrors and tires) by script.",
         notes="k = 0.83 (0.80-0.86) is an engineering assumption for passenger cars, from general recollection of aero texts (not opened); excludes mirrors and includes ground clearance gap error."),
]
