"""Integration-level derivations added by the coordinator."""
MILE = 1609.344

DERIVATIONS = [
    dict(key="tires.rolling_circumference_from_revs",
         description="Rolling circumference from published revs per mile (cross-check of the size-based value)",
         unit="m", impact="medium", cls="D", status="estimated",
         inputs={"rpm_": "tires.revs_per_mile"},
         fn=lambda rpm_: MILE / rpm_,
         range_fn=lambda rpm_: [MILE / (rpm_ + 0.5), MILE / (rpm_ - 0.5)],
         confidence="low",
         how_to_measure="Roll the car 10 wheel turns at rated pressure and normal load; measure distance.",
         notes="1 mile / revs-per-mile; range covers rounding of the printed integer only. Retailer figure for "
               "the tire on Car and Driver's 2022 test car."),
]
