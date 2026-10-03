"""Suspension derivations (domain 6): wheel rates, ride frequencies, anti-roll-bar
stiffness and conservative damping coefficients. SI in/out.

Conventions
  motion ratio MR = spring (or damper / bar-link) travel per unit wheel travel
  wheel rate        k_w = k_s * MR^2
  corner sprung mass m_s = curb_mass * axle_fraction / 2 - unsprung_corner
  ride frequency    f = sqrt(k_w / m_s) / (2 pi)   (tyre compliance ignored; with the tyre
                    in series the true frequency is ~3-6 % lower - included in the range)
  ARB torsion       K_t = G * J / L_active,  J = pi/32 * (D^4 - d_i^4),  G = 79.3 GPa (spring steel)
  ARB wheel rate    k_arb_wheel = K_t / lever^2 * MR_link^2   (per wheel, opposite wheel fixed)
  ARB roll stiffness K_phi = k_arb_wheel * track^2 / 2   [N*m/rad] (bar only, rigid links/bushings:
                    an upper bound; real bars lose 10-30 % to bushing/link compliance)
  critical damping  c_crit = 2 sqrt(k_w * m_s) (wheel-referred). Road cars typically run
                    zeta ~0.2-0.4 bump / higher rebound: we give zeta = 0.3 with range 0.2-0.45.
                    This is an inferred class E figure, NOT a damper curve.
Ranges are corner-evaluated over the inputs' recorded ranges where the inputs are estimates
(those ranges are repeated here as constants because derive.py passes only values).
"""
import math

G_STEEL = 79.3e9
TYRE_SERIES = (0.94, 1.0)       # tyre-in-series factor on frequency
# input ranges (copied from the class E records in vehicle_data/suspension.json; keep in sync)
RNG = {
    "kf": (22.0e3, 32.0e3), "kr": (24.0e3, 60.0e3),
    "mrf": (0.90, 1.00), "mrr": (0.62, 0.85),
    "muf": (40.0, 60.0), "mur": (32.0, 50.0),
    "Lf": (0.70, 1.00), "af": (0.15, 0.27), "mlf": (0.85, 1.00),
    "Lr": (0.80, 1.10), "ar": (0.12, 0.25), "mlr": (0.55, 0.95),
}


def wheel_rate(k, mr):
    return k * mr * mr


def sprung_corner(m, frac, mu):
    return m * frac / 2.0 - mu


def ride_freq(k, mr, m, frac, mu):
    return math.sqrt(wheel_rate(k, mr) / sprung_corner(m, frac, mu)) / (2.0 * math.pi)


def J_tube(D, t):
    di = max(D - 2.0 * t, 0.0)
    return math.pi / 32.0 * (D ** 4 - di ** 4)


def J_solid(D):
    return math.pi / 32.0 * D ** 4


def arb_wheel_rate(Kt, lever, mr):
    return Kt / lever ** 2 * mr ** 2


def _span(f, **ranges):
    """min/max of f over the corners of the given (lo, hi) ranges."""
    import itertools
    keys = list(ranges)
    vals = [f(**dict(zip(keys, c))) for c in itertools.product(*[ranges[k] for k in keys])]
    return [min(vals), max(vals)]


HTM_RIDE = "Bounce test: accelerometer on the body over each axle, push-and-release or drive over a single bump; or compute from measured spring rate, motion ratio and corner weights."

DERIVATIONS = [
    dict(key="suspension.wheel_rate_front", description="Front spring wheel rate (k_s * MR^2)",
         unit="N/m", impact="high", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_front", "mr": "suspension.motion_ratio_front"},
         fn=wheel_rate,
         range_fn=lambda k, mr: _span(wheel_rate, k=RNG["kf"], mr=RNG["mrf"]),
         confidence="low", how_to_measure="Measure spring rate and motion ratio (see those records), or load the corner with known weights and measure wheel-centre deflection.",
         notes="Inputs are class E estimates; range spans their ranges."),
    dict(key="suspension.wheel_rate_rear", description="Rear spring wheel rate (k_s * MR^2)",
         unit="N/m", impact="high", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_rear", "mr": "suspension.motion_ratio_rear"},
         fn=wheel_rate,
         range_fn=lambda k, mr: _span(wheel_rate, k=RNG["kr"], mr=RNG["mrr"]),
         confidence="low", how_to_measure="As for the front.",
         notes="Inputs are class E estimates; range spans their ranges (wide because the rear spring-rate leads disagree 2x)."),
    dict(key="suspension.ride_frequency_front", description="Front ride frequency (body bounce, tyre compliance ignored)",
         unit="Hz", impact="high", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_front", "mr": "suspension.motion_ratio_front", "m": "mass.curb_mass",
                 "frac": "mass.front_fraction", "mu": "suspension.unsprung_mass_corner_front"},
         fn=ride_freq,
         range_fn=lambda k, mr, m, frac, mu: [x * s for x, s in zip(
             _span(lambda k, mr, mu: ride_freq(k, mr, m, frac, mu), k=RNG["kf"], mr=RNG["mrf"], mu=RNG["muf"]), TYRE_SERIES)],
         confidence="low", how_to_measure=HTM_RIDE,
         notes="f = sqrt(k_s MR^2 / (m*frac/2 - m_u)) / 2pi; lower bound also x0.94 for tyre in series."),
    dict(key="suspension.ride_frequency_rear", description="Rear ride frequency (body bounce, tyre compliance ignored)",
         unit="Hz", impact="high", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_rear", "mr": "suspension.motion_ratio_rear", "m": "mass.curb_mass",
                 "frac": "mass.front_fraction", "mu": "suspension.unsprung_mass_corner_rear"},
         fn=lambda k, mr, m, frac, mu: ride_freq(k, mr, m, 1.0 - frac, mu),
         range_fn=lambda k, mr, m, frac, mu: [x * s for x, s in zip(
             _span(lambda k, mr, mu: ride_freq(k, mr, m, 1.0 - frac, mu), k=RNG["kr"], mr=RNG["mrr"], mu=RNG["mur"]), TYRE_SERIES)],
         confidence="low", how_to_measure=HTM_RIDE,
         notes="Rear axle fraction = 1 - mass.front_fraction."),
    dict(key="suspension.arb_front_polar_moment", description="Front anti-roll bar section polar moment J (tube 26.5 x 4.5 mm)",
         unit="m4", impact="medium", cls="D", status="confirmed",
         inputs={"D": "suspension.arb_front_diameter", "t": "suspension.arb_front_wall_thickness"},
         fn=J_tube, range_fn=lambda D, t: [J_tube(D - 0.0002, t - 0.0002), J_tube(D + 0.0002, t + 0.0002)],
         confidence="high", how_to_measure="Calipers on the bar OD; wall thickness from the bar end.",
         notes="J = pi/32 (D^4 - (D-2t)^4). Exact arithmetic on Honda's printed size; range +/-0.2 mm manufacturing/rounding."),
    dict(key="suspension.arb_rear_polar_moment", description="Rear anti-roll bar section polar moment J (solid 17.5 mm)",
         unit="m4", impact="medium", cls="D", status="confirmed",
         inputs={"D": "suspension.arb_rear_diameter"},
         fn=J_solid, range_fn=lambda D: [J_solid(D - 0.0002), J_solid(D + 0.0002)],
         confidence="high", how_to_measure="Calipers on the bar.", notes="J = pi/32 D^4."),
    dict(key="suspension.arb_front_torsional_stiffness", description="Front bar torsional stiffness of the active length, K_t = G J / L",
         unit="N*m/rad", impact="medium", cls="D", status="estimated",
         inputs={"D": "suspension.arb_front_diameter", "t": "suspension.arb_front_wall_thickness", "L": "suspension.arb_front_active_length"},
         fn=lambda D, t, L: G_STEEL * J_tube(D, t) / L,
         range_fn=lambda D, t, L: _span(lambda L: G_STEEL * J_tube(D, t) / L, L=RNG["Lf"]),
         confidence="low", how_to_measure="Measure bushing-to-bushing length on the car.",
         notes="G = 79.3 GPa. Active length is a class E estimate."),
    dict(key="suspension.arb_rear_torsional_stiffness", description="Rear bar torsional stiffness of the active length, K_t = G J / L",
         unit="N*m/rad", impact="medium", cls="D", status="estimated",
         inputs={"D": "suspension.arb_rear_diameter", "L": "suspension.arb_rear_active_length"},
         fn=lambda D, L: G_STEEL * J_solid(D) / L,
         range_fn=lambda D, L: _span(lambda L: G_STEEL * J_solid(D) / L, L=RNG["Lr"]),
         confidence="low", how_to_measure="Measure bushing-to-bushing length on the car.", notes="G = 79.3 GPa."),
    dict(key="suspension.arb_front_roll_stiffness", description="Front anti-roll bar roll stiffness at the wheels (bar only, rigid links)",
         unit="N*m/rad", impact="high", cls="D", status="estimated",
         inputs={"D": "suspension.arb_front_diameter", "t": "suspension.arb_front_wall_thickness", "L": "suspension.arb_front_active_length",
                 "a": "suspension.arb_front_lever_arm", "mr": "suspension.arb_front_motion_ratio", "tw": "dimensions.track_front"},
         fn=lambda D, t, L, a, mr, tw: arb_wheel_rate(G_STEEL * J_tube(D, t) / L, a, mr) * tw ** 2 / 2.0,
         range_fn=lambda D, t, L, a, mr, tw: [x * s for x, s in zip(_span(
             lambda L, a, mr: arb_wheel_rate(G_STEEL * J_tube(D, t) / L, a, mr) * tw ** 2 / 2.0,
             L=RNG["Lf"], a=RNG["af"], mr=RNG["mlf"]), (0.7, 1.0))],
         confidence="low", how_to_measure="Measure bar length, lever arms and link motion ratio; or measure roll angle under a known lateral load with and without the bar links connected.",
         notes="K_phi = (K_t / a^2) MR^2 * track^2 / 2. Lower bound also x0.7 for bushing/link compliance. Treats the bar as a pure torsion member (arm bending ignored, which overstates stiffness)."),
    dict(key="suspension.arb_rear_roll_stiffness", description="Rear anti-roll bar roll stiffness at the wheels (bar only, rigid links)",
         unit="N*m/rad", impact="high", cls="D", status="estimated",
         inputs={"D": "suspension.arb_rear_diameter", "L": "suspension.arb_rear_active_length",
                 "a": "suspension.arb_rear_lever_arm", "mr": "suspension.arb_rear_motion_ratio", "tw": "dimensions.track_rear"},
         fn=lambda D, L, a, mr, tw: arb_wheel_rate(G_STEEL * J_solid(D) / L, a, mr) * tw ** 2 / 2.0,
         range_fn=lambda D, L, a, mr, tw: [x * s for x, s in zip(_span(
             lambda L, a, mr: arb_wheel_rate(G_STEEL * J_solid(D) / L, a, mr) * tw ** 2 / 2.0,
             L=RNG["Lr"], a=RNG["ar"], mr=RNG["mlr"]), (0.7, 1.0))],
         confidence="low", how_to_measure="As for the front bar.", notes="As for the front bar."),
    dict(key="suspension.spring_roll_stiffness_front", description="Front roll stiffness from springs alone (k_w * track^2 / 2)",
         unit="N*m/rad", impact="medium", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_front", "mr": "suspension.motion_ratio_front", "tw": "dimensions.track_front"},
         fn=lambda k, mr, tw: wheel_rate(k, mr) * tw ** 2 / 2.0,
         range_fn=lambda k, mr, tw: _span(lambda k, mr: wheel_rate(k, mr) * tw ** 2 / 2.0, k=RNG["kf"], mr=RNG["mrf"]),
         confidence="low", how_to_measure="From measured spring rate and motion ratio.", notes=""),
    dict(key="suspension.spring_roll_stiffness_rear", description="Rear roll stiffness from springs alone (k_w * track^2 / 2)",
         unit="N*m/rad", impact="medium", cls="D", status="estimated",
         inputs={"k": "suspension.spring_rate_rear", "mr": "suspension.motion_ratio_rear", "tw": "dimensions.track_rear"},
         fn=lambda k, mr, tw: wheel_rate(k, mr) * tw ** 2 / 2.0,
         range_fn=lambda k, mr, tw: _span(lambda k, mr: wheel_rate(k, mr) * tw ** 2 / 2.0, k=RNG["kr"], mr=RNG["mrr"]),
         confidence="low", how_to_measure="From measured spring rate and motion ratio.", notes=""),
    dict(key="suspension.damping_wheel_front_inferred", description="Inferred front wheel-referred damping coefficient at zeta 0.3 (low-speed, average bump/rebound) - NOT measured",
         unit="N*s/m", impact="high", cls="E", status="estimated",
         inputs={"k": "suspension.spring_rate_front", "mr": "suspension.motion_ratio_front", "m": "mass.curb_mass",
                 "frac": "mass.front_fraction", "mu": "suspension.unsprung_mass_corner_front"},
         fn=lambda k, mr, m, frac, mu: 0.3 * 2.0 * math.sqrt(wheel_rate(k, mr) * sprung_corner(m, frac, mu)),
         range_fn=lambda k, mr, m, frac, mu: [0.2 * 2.0 * math.sqrt(RNG["kf"][0] * RNG["mrf"][0] ** 2 * sprung_corner(m, frac, RNG["muf"][1])),
                                              0.45 * 2.0 * math.sqrt(RNG["kf"][1] * RNG["mrf"][1] ** 2 * sprung_corner(m, frac, RNG["muf"][0]))],
         confidence="low", how_to_measure="Shock-dyno a stock front strut (0.025-1.0 m/s, bump and rebound) and divide by MR^2.",
         notes="c = zeta * 2 sqrt(k_w m_s). Conservative linear placeholder for Phase 2 damper curves (real dampers are digressive, rebound > bump). zeta range 0.2-0.45 is an engineering judgment for road cars."),
    dict(key="suspension.damping_wheel_rear_inferred", description="Inferred rear wheel-referred damping coefficient at zeta 0.3 - NOT measured",
         unit="N*s/m", impact="high", cls="E", status="estimated",
         inputs={"k": "suspension.spring_rate_rear", "mr": "suspension.motion_ratio_rear", "m": "mass.curb_mass",
                 "frac": "mass.front_fraction", "mu": "suspension.unsprung_mass_corner_rear"},
         fn=lambda k, mr, m, frac, mu: 0.3 * 2.0 * math.sqrt(wheel_rate(k, mr) * sprung_corner(m, 1.0 - frac, mu)),
         range_fn=lambda k, mr, m, frac, mu: [0.2 * 2.0 * math.sqrt(RNG["kr"][0] * RNG["mrr"][0] ** 2 * sprung_corner(m, 1.0 - frac, RNG["mur"][1])),
                                              0.45 * 2.0 * math.sqrt(RNG["kr"][1] * RNG["mrr"][1] ** 2 * sprung_corner(m, 1.0 - frac, RNG["mur"][0]))],
         confidence="low", how_to_measure="Shock-dyno a stock rear damper and divide by the damper MR^2.",
         notes="As front."),
]
