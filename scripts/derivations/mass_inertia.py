"""Mass and inertia derivations (domain 3). SI in, SI out.

Inputs are canonical keys: mass.* from vehicle_data/mass_inertia.json, dimensions.* from the
dimensions thread. Vehicle frame: origin on the ground at the centreline below the front axle,
+X right, +Y forward, +Z up; the rear axle is at Y = -wheelbase.

Empirical bases (source ids in vehicle_data/mass_inertia.json):
* mass:nhtsa-safercar-data      NHTSA measured SSF = T/(2h) = 1.48 for the 2022-2024 Civic family.
* mass:fr-2003-rollover-final-rule  68 FR 59291, Appendix II: no-tip-up risk model
      Roll Rate = 1 / (1 + exp(2.8891 + 1.1686 * ln(SSF - 0.90)))  -- used only as a cross-check.
* mass:heydinger1999-via-psu-notes  NHTSA VIPD class means (Heydinger et al., SAE 1999-01-1336), p.5:
      Passenger Small: m 969.0 kg, L 2.524 m, T 1.446 m, Jxx 392.6, Jyy 1632.2, Jzz 1798.8 kg.m2
      Passenger Large: m 1403.0 kg, L 2.679 m, T 1.468 m, Jxx 632.3, Jyy 2749.7, Jzz 2893.3 kg.m2
      "4.15 <= Jyy/Jxx <= 5.68   4.38 <= Jzz/Jxx <= 6.00"
  Normalised radii of gyration are computed from those rows below (not typed), then applied to
  this car's mass and dimensions. Class means carry no per-vehicle scatter, so ranges add +/-8 %
  on the radius of gyration (about +/-17 % on inertia) -- a stated assumption.
"""
import math

# --- VIPD class means as printed (Heydinger 1999 via PSU ME481 notes p.5) ---
VIPD = {
    "passenger_small": dict(m=969.0, L=2.524, T=1.446, h=0.519, Jxx=392.6, Jyy=1632.2, Jzz=1798.8),
    "passenger_large": dict(m=1403.0, L=2.679, T=1.468, h=0.585, Jxx=632.3, Jyy=2749.7, Jzz=2893.3),
}
K_SCATTER = 0.08  # assumed +/- fraction on radius of gyration (class means, not individual cars)


def _ratios(kind):
    """Normalised radius of gyration for each VIPD class: yaw/pitch by wheelbase, roll by track."""
    out = []
    for c in VIPD.values():
        if kind == "yaw":
            out.append(math.sqrt(c["Jzz"] / c["m"]) / c["L"])
        elif kind == "pitch":
            out.append(math.sqrt(c["Jyy"] / c["m"]) / c["L"])
        else:
            out.append(math.sqrt(c["Jxx"] / c["m"]) / c["T"])
    return out


def _inertia(m, length, kind):
    r = _ratios(kind)
    mid = sum(r) / len(r)
    return m * (mid * length) ** 2


def _inertia_range(m, length, kind):
    r = _ratios(kind)
    lo, hi = min(r) * (1 - K_SCATTER), max(r) * (1 + K_SCATTER)
    return [m * (lo * length) ** 2, m * (hi * length) ** 2]


def _tavg(tf, tr):
    return 0.5 * (tf + tr)


FF_TOL = 0.005  # published 59 % / 59.1 % -> allow +/-0.5 percentage point
SSF_LO, SSF_HI = 1.475, 1.485  # printed 1.48
H_BODY_TOL = 0.015  # m, sedan-vs-hatch, 18 in wheels, load state of the SSF test (assumption)

DERIVATIONS = [
    dict(
        key="mass.fuel_mass_full", description="Fuel mass with a full tank", unit="kg", impact="medium",
        cls="D", status="estimated",
        inputs={"vol": "mass.fuel_capacity", "rho": "mass.fuel_density"},
        fn=lambda vol, rho: vol * rho,
        range_fn=lambda vol, rho: [vol * 710.0, vol * 770.0],
        confidence="high",
        how_to_measure="Weigh the car with a full and a near-empty tank.",
        notes="m_fuel = V * rho; range from specific gravity 0.71-0.77.",
        basis_sources=["mass:wikipedia-gasoline"],
    ),
    dict(
        key="mass.front_axle_mass", description="Static front-axle mass at curb", unit="kg", impact="high",
        cls="D", status="estimated",
        inputs={"m": "mass.curb_mass", "ff": "mass.front_fraction"},
        fn=lambda m, ff: m * ff,
        range_fn=lambda m, ff: [m * (ff - FF_TOL), m * (ff + FF_TOL)],
        confidence="high",
        how_to_measure="Axle or corner scales, full tank, no driver.",
        notes="m_f = m * f_front; range +/-0.5 pp on the published distribution.",
    ),
    dict(
        key="mass.rear_axle_mass", description="Static rear-axle mass at curb", unit="kg", impact="high",
        cls="D", status="estimated",
        inputs={"m": "mass.curb_mass", "ff": "mass.front_fraction"},
        fn=lambda m, ff: m * (1 - ff),
        range_fn=lambda m, ff: [m * (1 - ff - FF_TOL), m * (1 - ff + FF_TOL)],
        confidence="high",
        how_to_measure="Axle or corner scales, full tank, no driver.",
        notes="m_r = m * (1 - f_front).",
    ),
    dict(
        key="mass.cg_y", description="Longitudinal CG position (vehicle Y; front axle = 0, rear axle = -wheelbase)",
        unit="m", impact="critical", cls="D", status="estimated",
        inputs={"L": "dimensions.wheelbase", "ff": "mass.front_fraction"},
        fn=lambda L, ff: -(1 - ff) * L,
        range_fn=lambda L, ff: [-(1 - ff + FF_TOL) * L, -(1 - ff - FF_TOL) * L],
        confidence="high",
        how_to_measure="Axle scales: distance behind front axle = L * m_rear / m.",
        notes="Static moment balance: a = L * (1 - f_front) behind the front axle.",
    ),
    dict(
        key="mass.cg_height", description="CG height above ground at curb (from NHTSA SSF)", unit="m",
        impact="critical", cls="D", status="estimated",
        inputs={"tf": "dimensions.track_front", "tr": "dimensions.track_rear", "ssf": "mass.ssf_nhtsa"},
        fn=lambda tf, tr, ssf: _tavg(tf, tr) / (2 * ssf),
        range_fn=lambda tf, tr, ssf: [_tavg(tf, tr) / (2 * SSF_HI) - H_BODY_TOL,
                                      _tavg(tf, tr) / (2 * SSF_LO) + H_BODY_TOL],
        confidence="medium",
        how_to_measure="Axle-lift method: weigh the rear axle with the front raised by >= 0.5 m (wheels on scales, suspension locked); "
                       "h = r + L*dW/(W*tan(theta)). Or use a tilt table.",
        notes="h = T_avg / (2 SSF), with this car's tracks and NHTSA's measured SSF 1.48 (printed to 0.01). The SSF test vehicle "
              "is probably a 2022 Civic Sedan, so +/-15 mm is added for body/wheel/load differences (assumption). "
              "Cross-check: the published NHTSA rollover possibility reproduces from SSF 1.48 (mass.check_rollover_risk_from_ssf).",
        basis_sources=["mass:nhtsa-safercar-data", "mass:fr-2003-rollover-final-rule"],
    ),
    dict(
        key="mass.check_rollover_risk_from_ssf",
        description="Cross-check: NHTSA no-tip-up risk model evaluated at the SSF (compare with mass.rollover_possibility_nhtsa = 0.095)",
        unit="1", impact="low", cls="D", status="estimated",
        inputs={"ssf": "mass.ssf_nhtsa"},
        fn=lambda ssf: 1.0 / (1.0 + math.exp(2.8891 + 1.1686 * math.log(ssf - 0.90))),
        range_fn=lambda ssf: [1.0 / (1.0 + math.exp(2.8891 + 1.1686 * math.log(SSF_HI - 0.90))),
                              1.0 / (1.0 + math.exp(2.8891 + 1.1686 * math.log(SSF_LO - 0.90)))],
        confidence="high",
        how_to_measure="n/a (consistency check of government data).",
        notes="68 FR 59291 no-tip-up model. Agreement with 0.095 confirms the SSF row and the model are consistent.",
        basis_sources=["mass:fr-2003-rollover-final-rule", "mass:nhtsa-safercar-data"],
    ),
    dict(
        key="mass.inertia_yaw", description="Yaw moment of inertia about the CG (whole car, curb)", unit="kg*m2",
        impact="high", cls="E", status="estimated",
        inputs={"m": "mass.curb_mass", "L": "dimensions.wheelbase"},
        fn=lambda m, L: _inertia(m, L, "yaw"),
        range_fn=lambda m, L: _inertia_range(m, L, "yaw"),
        confidence="low",
        how_to_measure="Yaw inertia rig (bifilar/trifilar pendulum or NHTSA IPMD-type facility); not practical at home.",
        notes="Izz = m (c_z L)^2, c_z = mean of sqrt(Jzz/m)/L over the VIPD 'Passenger Small' and 'Passenger Large' class means "
              "(about 0.54). The VIPD table lists sprung mass; applying the ratio to curb mass is an assumption covered by the range.",
        basis_sources=["mass:heydinger1999-via-psu-notes"],
    ),
    dict(
        key="mass.inertia_pitch", description="Pitch moment of inertia about the CG (whole car, curb)", unit="kg*m2",
        impact="medium", cls="E", status="estimated",
        inputs={"m": "mass.curb_mass", "L": "dimensions.wheelbase"},
        fn=lambda m, L: _inertia(m, L, "pitch"),
        range_fn=lambda m, L: _inertia_range(m, L, "pitch"),
        confidence="low",
        how_to_measure="Pitch inertia pendulum test (specialist facility).",
        notes="Iyy(pitch) = m (c_p L)^2 with c_p from VIPD class means (about 0.52).",
        basis_sources=["mass:heydinger1999-via-psu-notes"],
    ),
    dict(
        key="mass.inertia_roll", description="Roll moment of inertia about the CG (whole car, curb)", unit="kg*m2",
        impact="medium", cls="E", status="estimated",
        inputs={"m": "mass.curb_mass", "tf": "dimensions.track_front", "tr": "dimensions.track_rear"},
        fn=lambda m, tf, tr: _inertia(m, _tavg(tf, tr), "roll"),
        range_fn=lambda m, tf, tr: _inertia_range(m, _tavg(tf, tr), "roll"),
        confidence="low",
        how_to_measure="Roll inertia pendulum test (specialist facility).",
        notes="Ixx(roll) = m (c_r T_avg)^2 with c_r = sqrt(Jxx/m)/T from VIPD class means (about 0.45).",
        basis_sources=["mass:heydinger1999-via-psu-notes"],
    ),
    dict(
        key="mass.check_yaw_over_roll", description="Cross-check: Izz/Ixx of the estimates (VIPD: 4.38-6.00)", unit="1",
        impact="low", cls="D", status="estimated",
        inputs={"iz": "mass.inertia_yaw", "ix": "mass.inertia_roll"},
        fn=lambda iz, ix: iz / ix,
        range_fn=lambda iz, ix: [4.38, 6.00],
        confidence="medium",
        how_to_measure="n/a (consistency check).",
        notes="Range shown is the published VIPD band; the value should fall inside it.",
        basis_sources=["mass:heydinger1999-via-psu-notes"],
    ),
    dict(
        key="mass.check_axle_sum", description="Cross-check: front + rear axle mass minus curb mass (should be 0)", unit="kg",
        impact="low", cls="D", status="estimated",
        inputs={"mf": "mass.front_axle_mass", "mr": "mass.rear_axle_mass", "m": "mass.curb_mass"},
        fn=lambda mf, mr, m: mf + mr - m,
        range_fn=lambda mf, mr, m: [-0.5, 0.5],
        confidence="high", how_to_measure="n/a", notes="Arithmetic closure check.",
    ),
]
