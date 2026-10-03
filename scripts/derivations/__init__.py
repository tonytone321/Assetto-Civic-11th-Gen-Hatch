"""Derivation registry. Every computed (class D, or computed class E) number in the
database is produced here by code, then written by scripts/derive.py into
vehicle_data/derived.json and recomputed by scripts/validate_db.py.

Each module scripts/derivations/<domain>.py defines

DERIVATIONS = [
    dict(
        key="mass.fuel_mass_full",            # namespaced parameter key
        description="Fuel mass with a full tank",
        unit="kg", impact="medium",            # impact: critical|high|medium|low
        cls="D",                               # D derived by script; E engineering estimate
        status="estimated",                    # 'confirmed' only for exact arithmetic on confirmed inputs
        inputs={"volume": "mass.fuel_capacity", "density": "mass.fuel_density"},  # arg -> parameter key
        fn=lambda volume, density: volume * density,           # SI in, SI out
        range_fn=lambda volume, density: [volume * 0.72e3, volume * 0.76e3],  # [lo, hi]; required
        confidence="high",
        how_to_measure="Weigh the car with full and near-empty tank.",
        notes="Formula and basis (cite source ids for empirical relationships here).",
        basis_sources=["mass:nhtsa-inertia-1999"],  # optional: source ids for formulas/coefficients
    ),
]

and optionally

TABLES = [
    dict(path="vehicle_data/gear_speed_table.csv",
         inputs={"g1": "transmission.gear_1", ...},
         fn=lambda **kw: [ {col: value, ...}, ... ],   # list of row dicts
         description="..."),
]

derive.py resolves inputs from vehicle_data/_resolved.json (user measurements first),
runs the derivations in dependency order (a derivation may consume another derivation's
key), and records inputs, input values and the module/function in each record.
If an input is unknown the output is recorded as unknown, listing the missing inputs.
"""
