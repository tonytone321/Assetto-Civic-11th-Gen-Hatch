"""Steering derivations (domain 6).

Turning-circle definition used: Honda's 'curb-to-curb' figure = diameter of the circle
traced by the OUTER edge of the outer FRONT tyre's contact patch at full lock (the
Canadian table labels the same 11.6 m figure 'turning radius'; see steering.json).
The turn centre is assumed to lie on the rear-axle line (no rear compliance steer, no
tyre slip, low speed), so the outer front wheel angle follows from geometry alone and
does not depend on Ackermann.

Published ratio: Honda prints one 'steering ratio' for a variable-ratio rack. It is
treated here as the overall ratio, i.e. handwheel angle at lock / MEAN road-wheel angle
at lock; the cross-check below tests that interpretation.

Stated assumptions (not measurements):
  HALF_TREAD = 0.105 m, range 0.090-0.118 m: distance from wheel-centre plane to the
  outer edge of the contact patch of a 235/40R18 tyre (half of 235 mm section = 0.1175;
  contact-patch edge is inboard of the sidewall bulge).
  Turning-circle rounding: published 11.6 m / 38.1 ft -> +/-0.05 m on the diameter.
All angles in rad.
"""
import math

HALF_TREAD = 0.105
HALF_TREAD_RANGE = (0.090, 0.1175)
D_TOL = 0.05


def _outer(D, L, h):
    r = D / 2.0 - h          # outer front wheel-centre-plane radius
    return math.asin(min(1.0, L / r))


def _inner_ackermann(D, L, tf, h):
    r = D / 2.0 - h
    do = math.asin(min(1.0, L / r))
    x_outer = r * math.cos(do)        # lateral distance turn-centre -> outer front wheel (on rear-axle line)
    return math.atan(L / (x_outer - tf))


def _mean_lock_from_ratio(turns, ratio):
    return math.radians(turns * 360.0 / 2.0 / ratio)


def _ackermann_pct(D, L, tf, turns, ratio, h):
    do = _outer(D, L, h)
    di_ack = _inner_ackermann(D, L, tf, h)
    di_act = 2.0 * _mean_lock_from_ratio(turns, ratio) - do
    return 100.0 * (di_act - do) / (di_ack - do)


def _corners(f, D, *rest):
    vals = []
    for dD in (-D_TOL, D_TOL):
        for h in HALF_TREAD_RANGE:
            vals.append(f(D + dD, *rest, h))
    return [min(vals), max(vals)]


def _ack_range(D, L, tf, turns, ratio):
    lo, hi = _corners(lambda D_, L_, tf_, h: _ackermann_pct(D_, L_, tf_, turns, ratio, h) / 100.0, D, L, tf)
    return [min(0.6, lo), max(1.0, hi)]


IN_GEOM = {"D": "steering.turning_circle_diameter", "L": "dimensions.wheelbase"}

DERIVATIONS = [
    dict(
        key="steering.max_angle_outer",
        description="Outer front road-wheel angle at full lock, from the curb-to-curb turning circle",
        unit="rad", impact="high", cls="D", status="estimated",
        inputs=dict(IN_GEOM),
        fn=lambda D, L: _outer(D, L, HALF_TREAD),
        range_fn=lambda D, L: _corners(lambda D_, L_, h: _outer(D_, L_, h), D, L),
        confidence="medium",
        how_to_measure="Turn plates at full lock left and right (alignment rig turning-angle readout); +/-0.5 deg.",
        notes="delta_o = asin(L / (D/2 - h)), h = contact-patch half width (0.105 m, range 0.090-0.1175). Turn centre on rear-axle line.",
    ),
    dict(
        key="steering.max_angle_inner",
        description="Inner front road-wheel angle at full lock assuming 100 % Ackermann (pure geometry from the turning circle)",
        unit="rad", impact="high", cls="D", status="estimated",
        inputs=dict(IN_GEOM, tf="dimensions.track_front"),
        fn=lambda D, L, tf: _inner_ackermann(D, L, tf, HALF_TREAD),
        range_fn=lambda D, L, tf: _corners(lambda D_, L_, tf_, h: _inner_ackermann(D_, L_, tf_, h), D, L, tf),
        confidence="low",
        how_to_measure="Turn plates at full lock; read the inner wheel angle directly.",
        notes="delta_i = atan(L / (sqrt((D/2-h)^2 - L^2) - track_f)). Assumes 100 % Ackermann, which the published turning circle cannot verify; compare steering.ackermann_pct_estimate.",
    ),
    dict(
        key="steering.mean_lock_angle_from_ratio",
        description="Mean front road-wheel angle at lock implied by turns lock-to-lock and published ratio",
        unit="rad", impact="medium", cls="D", status="estimated",
        inputs={"turns": "steering.turns_lock_to_lock", "ratio": "steering.ratio_overall"},
        fn=_mean_lock_from_ratio,
        range_fn=lambda turns, ratio: [_mean_lock_from_ratio(turns - 0.005, ratio + 0.005),
                                       _mean_lock_from_ratio(turns + 0.005, ratio - 0.005)],
        confidence="medium",
        how_to_measure="Turn plates at full lock (average of inner and outer).",
        notes="theta = turns*360/2/ratio. Valid only if Honda's ratio is the overall (lock) ratio; range covers rounding of the printed figures only.",
    ),
    dict(
        key="steering.crosscheck_ratio_vs_turning_circle",
        description="Cross-check: mean lock angle from ratio / mean lock angle from turning circle at 100 % Ackermann (1.00 = consistent)",
        unit="1", impact="low", cls="D", status="estimated",
        inputs=dict(IN_GEOM, tf="dimensions.track_front", turns="steering.turns_lock_to_lock", ratio="steering.ratio_overall"),
        fn=lambda D, L, tf, turns, ratio: _mean_lock_from_ratio(turns, ratio) / (
            0.5 * (_outer(D, L, HALF_TREAD) + _inner_ackermann(D, L, tf, HALF_TREAD))),
        range_fn=lambda D, L, tf, turns, ratio: _corners(
            lambda D_, L_, tf_, h: _mean_lock_from_ratio(turns, ratio) / (0.5 * (_outer(D_, L_, h) + _inner_ackermann(D_, L_, tf_, h))),
            D, L, tf),
        confidence="medium",
        how_to_measure="Turn plates at full lock.",
        notes="Values within ~0.9-1.1 support reading Honda's ratio as an overall ratio; a value well above 1 would mean the printed ratio is slower than the true lock-average (e.g. an on-centre ratio).",
    ),
    dict(
        key="steering.ackermann_pct_estimate",
        description="Ackermann percentage estimate: (inner_actual - outer) / (inner_100% - outer), inner_actual = 2*mean_lock(ratio) - outer",
        unit="1", impact="medium", cls="E", status="estimated",
        inputs=dict(IN_GEOM, tf="dimensions.track_front", turns="steering.turns_lock_to_lock", ratio="steering.ratio_overall"),
        fn=lambda D, L, tf, turns, ratio: _ackermann_pct(D, L, tf, turns, ratio, HALF_TREAD) / 100.0,
        range_fn=_ack_range,
        confidence="low",
        how_to_measure="Turn plates: inner and outer angles at full lock and at 20 deg outer (toe-out-on-turns spec on an alignment printout).",
        notes="Fraction (1.0 = 100 % Ackermann). Very sensitive: it rests on the published ratio being the exact lock-average and on the contact-patch assumption. Range is widened to include 0.6-1.0, the usual road-car band, because the inputs cannot rule it out.",
    ),
]
