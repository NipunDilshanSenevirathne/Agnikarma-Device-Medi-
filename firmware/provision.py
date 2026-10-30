"""Validate commissioning records without trusting JSON types or record names.
An accepted record is still not evidence that a real calibration occurred.
"""
from firmware.core import finite

DEFAULTS = {
    "role": "", "bench_enabled": False, "sensor_offset_c": 0.0,
    "battery_scale": 1.0, "reference_resistor_ohm": 4300.0,
    "display_address": 60, "calibration_record": "UNMEASURED",
}

def validate(record, role):
    cfg = dict(DEFAULTS)
    if role not in ("main", "supervisor") or not isinstance(record, dict):
        return False, cfg
    ok = record.get("role") == role and record.get("bench_enabled") is True
    cfg["role"] = role
    cfg["bench_enabled"] = record.get("bench_enabled") is True
    calibration = record.get("calibration_record")
    if not isinstance(calibration, str) or not calibration.strip() or calibration.strip() == "UNMEASURED" or len(calibration) > 128:
        ok = False
    else:
        cfg["calibration_record"] = calibration.strip()
    for key, low, high in (("sensor_offset_c", -5.0, 5.0),
                           ("battery_scale", .8, 1.2),
                           ("reference_resistor_ohm", 4000.0, 4500.0)):
        value = record.get(key, DEFAULTS[key])
        if not finite(value) or not low <= value <= high:
            ok = False
        else:
            cfg[key] = value
    address = record.get("display_address", 60)
    if type(address) is not int or address not in (60, 61):
        ok = False
    else:
        cfg["display_address"] = address
    return bool(ok), cfg
