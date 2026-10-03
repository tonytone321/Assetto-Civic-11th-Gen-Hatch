#!/usr/bin/env python3
"""Decode VINs / VIN patterns with NHTSA vPIC (DecodeVinValuesExtended) and cache the raw JSON
under cache/vpic/ (git-ignored). Used by identity_build.py.

Usage: python3 scripts/domains/identity_vin_decode.py VIN_OR_PATTERN [...]
"""
import json, os, sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "cache", "vpic")
KEYS = ["ErrorText", "ModelYear", "Make", "Model", "Trim", "BodyClass", "Doors", "DriveType",
        "TransmissionStyle", "TransmissionSpeeds", "EngineModel", "DisplacementL", "EngineHP",
        "Turbo", "PlantCity", "PlantState", "PlantCountry", "Manufacturer", "VehicleDescriptor",
        "GVWR", "TPMS"]


def url(v):
    return f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{v}?format=json"


def decode(v, refresh=False):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, v.replace("*", "_") + ".json")
    if refresh or not os.path.exists(p):
        r = requests.get(url(v), timeout=60)
        r.raise_for_status()
        open(p, "w").write(r.text)
    res = json.load(open(p))["Results"][0]
    return {k: res.get(k) for k in KEYS}, os.path.relpath(p, ROOT)


if __name__ == "__main__":
    for v in sys.argv[1:]:
        d, p = decode(v, refresh=True)
        print(v, p)
        for k, x in d.items():
            print(f"  {k}: {x}")
