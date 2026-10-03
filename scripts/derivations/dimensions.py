"""Dimension derivations (domain 2): pure arithmetic on the published dimensions, plus the
split of the published total overhang using the scale-free front/rear overhang fraction measured
by scripts/domains/photo_measure_side.py (proportions.overhang_front_fraction).

Vehicle frame: origin on the ground at the centreline below the front axle, +Y forward, metres.
Published figures are rounded to 1 mm, so exact-arithmetic results carry +-1-2 mm ranges.
"""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MM = 1e-3


def _fraction_range():
    """+-2 sigma range of the photo overhang fraction, read from the photo script's output."""
    try:
        with open(os.path.join(_ROOT, "vehicle_data", "proportions.json"), encoding="utf-8") as f:
            p = json.load(f)
        return tuple(p["parameters"]["proportions.overhang_front_fraction"]["candidates"][0]["range"])
    except (OSError, KeyError, IndexError):
        return None


def _split(total, f, front=True):
    return total * f if front else total * (1 - f)


def _split_range(L, wb, f, front=True):
    rg = _fraction_range() or (f - 0.03, f + 0.03)
    tot_lo, tot_hi = L - wb - 2 * MM, L - wb + 2 * MM
    if front:
        return [tot_lo * rg[0], tot_hi * rg[1]]
    return [tot_lo * (1 - rg[1]), tot_hi * (1 - rg[0])]


DERIVATIONS = [
    dict(
        key="dimensions.overhang_total",
        description="Sum of front and rear overhangs = length - wheelbase",
        unit="m", impact="medium", cls="D", status="confirmed",
        inputs={"L": "dimensions.length", "wb": "dimensions.wheelbase"},
        fn=lambda L, wb: L - wb,
        range_fn=lambda L, wb: [L - wb - 2 * MM, L - wb + 2 * MM],
        confidence="high",
        how_to_measure="Plumb bobs at both bumper extremes and both hub centres; measure on the floor.",
        notes="Exact arithmetic on published figures (each rounded to 1 mm).",
    ),
    dict(
        key="dimensions.overhang_front",
        description="Front overhang: front axle to foremost body point",
        unit="m", impact="high", cls="D", status="estimated",
        inputs={"L": "dimensions.length", "wb": "dimensions.wheelbase", "f": "proportions.overhang_front_fraction"},
        fn=lambda L, wb, f: _split(L - wb, f, True),
        range_fn=lambda L, wb, f: _split_range(L, wb, f, True),
        confidence="medium",
        how_to_measure="Plumb bob from the front bumper's foremost point and from the front hub centre; measure the floor distance (+-5 mm).",
        notes="Manufacturer does not publish overhangs (Honda Canada/US 2022-2024 spec tables searched). "
              "(length - wheelbase) x photo-measured scale-free fraction front/(front+rear) from the Honda side render; "
              "range from the fraction's +-2 sigma range in proportions.json.",
    ),
    dict(
        key="dimensions.overhang_rear",
        description="Rear overhang: rear axle to rearmost body point",
        unit="m", impact="high", cls="D", status="estimated",
        inputs={"L": "dimensions.length", "wb": "dimensions.wheelbase", "f": "proportions.overhang_front_fraction"},
        fn=lambda L, wb, f: _split(L - wb, f, False),
        range_fn=lambda L, wb, f: _split_range(L, wb, f, False),
        confidence="medium",
        how_to_measure="Plumb bob from the rear bumper's rearmost point and from the rear hub centre; measure the floor distance (+-5 mm).",
        notes="As dimensions.overhang_front, complement of the fraction.",
    ),
    dict(
        key="dimensions.front_bumper_y",
        description="Y coordinate of the foremost body point (vehicle frame)",
        unit="m", impact="medium", cls="D", status="estimated",
        inputs={"L": "dimensions.length", "wb": "dimensions.wheelbase", "f": "proportions.overhang_front_fraction"},
        fn=lambda L, wb, f: _split(L - wb, f, True),
        range_fn=lambda L, wb, f: _split_range(L, wb, f, True),
        confidence="medium",
        how_to_measure="As dimensions.overhang_front.",
        notes="Equal to the front overhang because the origin is below the front axle.",
    ),
    dict(
        key="dimensions.rear_bumper_y",
        description="Y coordinate of the rearmost body point (vehicle frame)",
        unit="m", impact="medium", cls="D", status="estimated",
        inputs={"L": "dimensions.length", "wb": "dimensions.wheelbase", "f": "proportions.overhang_front_fraction"},
        fn=lambda L, wb, f: -(wb + _split(L - wb, f, False)),
        range_fn=lambda L, wb, f: sorted([-(wb + x) for x in _split_range(L, wb, f, False)]),
        confidence="medium",
        how_to_measure="As dimensions.overhang_rear.",
        notes="-(wheelbase + rear overhang).",
    ),
    dict(
        key="dimensions.rear_axle_y",
        description="Y coordinate of the rear axle (vehicle frame)",
        unit="m", impact="high", cls="D", status="confirmed",
        inputs={"wb": "dimensions.wheelbase"},
        fn=lambda wb: -wb,
        range_fn=lambda wb: [-wb - 1 * MM, -wb + 1 * MM],
        confidence="high",
        how_to_measure="Measure hub-centre to hub-centre on both sides.",
        notes="-wheelbase by definition of the frame.",
    ),
    dict(
        key="dimensions.mirror_protrusion_per_side",
        description="Lateral protrusion of each (open) mirror beyond the body width",
        unit="m", impact="low", cls="D", status="confirmed",
        inputs={"wm": "dimensions.width_mirrors", "wbody": "dimensions.width_body"},
        fn=lambda wm, wbody: (wm - wbody) / 2,
        range_fn=lambda wm, wbody: [(wm - wbody) / 2 - 1 * MM, (wm - wbody) / 2 + 1 * MM],
        confidence="medium",
        how_to_measure="Measure mirror-to-mirror width with two squares and a tape (+-3 mm).",
        notes="Mirror width is from the 2022/2023 Canadian tables (not reprinted for 2024).",
    ),
    dict(
        key="dimensions.licence_bracket_depth",
        description="Length added by the front licence-plate bracket",
        unit="m", impact="low", cls="D", status="confirmed",
        inputs={"Lb": "dimensions.length_with_licence_bracket", "L": "dimensions.length"},
        fn=lambda Lb, L: Lb - L,
        range_fn=lambda Lb, L: [Lb - L - 2 * MM, Lb - L + 2 * MM],
        confidence="high",
        how_to_measure="Measure the bracket depth ahead of the bumper face.",
        notes="Honda Canada prints both lengths (with/without bracket).",
    ),
    dict(
        key="dimensions.front_tyre_outer_margin_per_side",
        description="Cross-check: (body width - front track - tyre section width) / 2; must be > 0",
        unit="m", impact="low", cls="D", status="estimated",
        inputs={"w": "dimensions.width_body", "t": "dimensions.track_front", "s": "tires.section_width"},
        fn=lambda w, t, s: (w - t - s) / 2,
        range_fn=lambda w, t, s: [(w - t - s) / 2 - 5 * MM, (w - t - s) / 2 + 5 * MM],
        confidence="medium",
        how_to_measure="Measure from the tyre sidewall's outer face to the body side (plumb) at axle height.",
        notes="Nominal section width; real tyre bulge differs by a few mm (+-5 mm range). Negative means inconsistent inputs.",
    ),
    dict(
        key="dimensions.rear_tyre_outer_margin_per_side",
        description="Cross-check: (body width - rear track - tyre section width) / 2; must be > 0",
        unit="m", impact="low", cls="D", status="estimated",
        inputs={"w": "dimensions.width_body", "t": "dimensions.track_rear", "s": "tires.section_width"},
        fn=lambda w, t, s: (w - t - s) / 2,
        range_fn=lambda w, t, s: [(w - t - s) / 2 - 5 * MM, (w - t - s) / 2 + 5 * MM],
        confidence="medium",
        how_to_measure="As front.",
        notes="As front.",
    ),
]
