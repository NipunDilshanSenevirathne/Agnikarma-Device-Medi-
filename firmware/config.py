"""Bench defaults, NOT clinically established limits. No output enabled until provisioning."""
PRESETS = (50, 100, 150, 200, 250)
RREF = 4300.0
R0 = 1000.0
SAMPLE_MS = 100
STALE_MS = 350
HEARTBEAT_MS = 350
CONTROL_GAP_MS = 400
LIMIT_MARGIN_C = 10.0
ABSOLUTE_LIMIT_C = 265.0  # Provisional bench equipment limit; not a clinical safety limit.
SENSOR_DISAGREE_C = 10.0
PACK_MIN_V = 6.2
PACK_MAX_V = 8.5
PACK_MAX_C = 45.0
COOLED_DISPLAY_C = 40.0  # Bench display threshold only; not safe-to-touch certification.
MAX_POWER_W = 30.0
HEATER_OHMS = 2.2
PWM_HZ = 1000
MAX_DUTY = 0.50  # Restricted commissioning default; low pack cannot meet every target.
KP = 0.015       # Untuned bench starting values: characterize on guarded fixture.
KI = 0.002
PIN = {
 "tx": 0, "rx": 1, "sda": 2, "scl": 3,
 "miso": 4, "cs": 5, "sck": 6, "mosi": 7,
 "cool": 14, "heat": 15, "arm": 16, "dock": 17,
 "tip": 18, "peer_pulse": 19, "local_pulse": 20,
 "output": 21, "spare": 22, "pack_adc": 26, "ntc_adc": 27, "tip_adc": 28,
}
BUTTON_PINS = (8, 9, 10, 11, 12)  # GP13 is unused in the five-preset revision.
TIP_CODES = (("T01", 0.50), ("T02", 0.6154))
TIP_TOLERANCE = 0.025
