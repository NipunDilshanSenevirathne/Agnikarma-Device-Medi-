"""Pure Python safety/control logic, shared by host tests and MicroPython.
No machine imports. Caller supplies monotonic millisecond timestamps.
"""
import math
from firmware import config as C

def finite(x):
    return type(x) in (int, float) and math.isfinite(x)

def temperature_from_resistance(r):
    if not finite(r) or not 900.0 <= r <= 2500.0:
        raise ValueError("RTD resistance out of range")
    a, b = 0.0039083, -0.0000005775
    return (-a + math.sqrt(a*a - 4*b*(1-r/C.R0))) / (2*b)

def resistance_from_temperature(t):
    return C.R0 * (1 + 0.0039083*t - 0.0000005775*t*t)

class Sample:
    def __init__(self, temp, stamp, valid=True):
        self.temp, self.stamp, self.valid = temp, stamp, valid

class Inputs:
    def __init__(self, now, sample, peer_temp, peer_age_ms, heartbeat_age_ms,
                 peer_target, peer_allow, pack_v, pack_c, tip_id="T01",
                 heat=False, cool=False, arm=False, dock=False,
                 tip_present=True, sensor_fault=False, provisioning_ok=False):
        self.now, self.sample = now, sample
        self.peer_temp, self.peer_age_ms = peer_temp, peer_age_ms
        self.heartbeat_age_ms, self.peer_target = heartbeat_age_ms, peer_target
        self.peer_allow = peer_allow
        self.pack_v, self.pack_c, self.tip_id = pack_v, pack_c, tip_id
        self.heat, self.cool, self.arm, self.dock = heat, cool, arm, dock
        self.tip_present, self.sensor_fault = tip_present, sensor_fault
        self.provisioning_ok = provisioning_ok

def fault_reason(i, target):
    if not i.provisioning_ok: return "UNPROVISIONED"
    if target not in C.PRESETS: return "BAD_SETPOINT"
    s = i.sample
    if i.sensor_fault or not s.valid or not finite(s.temp): return "SENSOR"
    if not finite(s.stamp) or not 0 <= i.now-s.stamp <= C.STALE_MS: return "STALE_SENSOR"
    if not -10 <= s.temp <= C.ABSOLUTE_LIMIT_C: return "ABSOLUTE_TEMP"
    if s.temp > target+C.LIMIT_MARGIN_C: return "SETPOINT_OVERTEMP"
    if not i.tip_present or i.tip_id not in ("T01", "T02"): return "TIP"
    if i.dock: return "DOCKED"
    if not finite(i.pack_v) or not C.PACK_MIN_V <= i.pack_v <= C.PACK_MAX_V: return "PACK_VOLTAGE"
    if not finite(i.pack_c) or not -5 <= i.pack_c <= C.PACK_MAX_C: return "PACK_TEMP"
    if not finite(i.peer_age_ms) or not 0 <= i.peer_age_ms <= C.STALE_MS: return "STALE_LINK"
    if not finite(i.heartbeat_age_ms) or not 0 <= i.heartbeat_age_ms <= C.HEARTBEAT_MS: return "HEARTBEAT"
    if i.peer_target != target: return "SETPOINT_MISMATCH"
    if not finite(i.peer_temp) or abs(s.temp-i.peer_temp) > C.SENSOR_DISAGREE_C: return "SENSOR_DISAGREE"
    return ""

class Supervisor:
    """Independent software monitor. Relay permit never follows main request alone."""
    def __init__(self):
        self.target = 50
        self.armed = False
        self.fault = "STARTUP"
        self._arm_was = True  # Require release before first rising edge.

    def select(self, target):
        if target not in C.PRESETS:
            self.fault, self.armed = "BAD_SETPOINT", False
            return
        if target != self.target:
            self.target, self.armed, self.fault = target, False, "REARM"

    def step(self, i):
        edge = i.arm and not self._arm_was
        self._arm_was = i.arm
        reason = fault_reason(i, self.target)
        if i.cool:
            self.armed, self.fault = False, "COOL"
        elif reason:
            self.armed, self.fault = False, reason
        elif edge and not i.heat:
            self.armed, self.fault = True, ""
        return bool(self.armed and not self.fault and i.heat and not i.cool and i.peer_allow)

class Controller:
    """Temperature loop; this does not replace independent hardware interruption."""
    def __init__(self):
        self.target, self.state, self.fault = 50, "LOCKED", "STARTUP"
        self.armed, self.integral = False, 0.0
        self._arm_was, self._last = True, None

    def select(self, target):
        if target not in C.PRESETS:
            self.armed, self.state, self.fault = False, "FAULT", "BAD_SETPOINT"
            return
        if target != self.target:
            self.target, self.armed, self.integral = target, False, 0.0
            self.state, self.fault = "LOCKED", "REARM"

    def step(self, i):
        edge = i.arm and not self._arm_was
        self._arm_was = i.arm
        gap = self._last is not None and not 0 < i.now-self._last <= C.CONTROL_GAP_MS
        dt = 0.1 if self._last is None else max(0.001, (i.now-self._last)/1000.0)
        self._last = i.now
        reason = fault_reason(i, self.target)
        if i.cool:
            self.armed, self.integral, self.fault = False, 0.0, "COOL"
            self.state = "COOLING" if i.sample.valid and finite(i.sample.temp) else "HOT_UNKNOWN"
            return 0.0
        if reason or gap:
            self.armed, self.integral = False, 0.0
            self.state, self.fault = "FAULT", reason or "CONTROL_GAP"
            return 0.0
        if edge and not i.heat:
            self.armed, self.fault = True, ""
        if not self.armed:
            # Only a bench display status; it does not authorize touch or re-arm.
            self.state = "COOLED_LOCKED" if self.fault == "COOL" and i.sample.temp <= C.COOLED_DISPLAY_C else "LOCKED"
            return 0.0
        if not i.heat:
            self.integral, self.state = 0.0, "ARMED"
            return 0.0
        if not i.peer_allow:
            self.integral, self.state = 0.0, "WAIT_PERMIT"
            return 0.0
        err = self.target-i.sample.temp
        cap = min(C.MAX_DUTY, C.MAX_POWER_W*C.HEATER_OHMS/(i.pack_v*i.pack_v))
        proposed = self.integral+C.KI*err*dt
        raw = C.KP*err+proposed
        if 0 < raw < cap or (raw >= cap and err < 0) or (raw <= 0 and err > 0):
            self.integral = proposed
        duty = min(cap, max(0.0, C.KP*err+self.integral))
        self.state = "HOLDING" if abs(err) <= 2 else "HEATING" if err > 0 else "ABOVE_TARGET"
        return duty

def crc16(data):
    crc = 0xFFFF
    for v in data:
        crc ^= v << 8
        for _ in range(8): crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def encode_frame(role, seq, target, temp, allow):
    if role not in ("M", "S") or not finite(temp) or target not in C.PRESETS: raise ValueError("bad frame")
    payload = ("%s,%d,%d,%d,%d" % (role, seq & 0xFFFF, target, round(temp*100), bool(allow))).encode()
    return payload + ("*%04X\n" % crc16(payload)).encode()

class Link:
    def __init__(self, expected_role):
        self.expected_role = expected_role
        self.buffer, self.last_seq, self.stamp = b"", None, None
        self.target, self.temp, self.allow = 50, 0.0, False

    def feed(self, data, now):
        for ch in data:
            if ch == 10:
                raw, self.buffer = self.buffer, b""
                try:
                    body, check = raw.split(b"*")
                    if crc16(body) != int(check, 16): continue
                    role, seq, target, tc, allow = body.decode().split(",")
                    seq, target, tc, allow = int(seq), int(target), int(tc), int(allow)
                    if role != self.expected_role or not 0 <= seq <= 65535: continue
                    if target not in C.PRESETS or allow not in (0,1) or not -1000 <= tc <= 40000: continue
                    if self.last_seq is not None and not 0 < ((seq-self.last_seq) & 0xFFFF) < 32768: continue
                    self.last_seq, self.target, self.temp, self.allow, self.stamp = seq, target, tc/100.0, bool(allow), now
                except (ValueError, UnicodeError): pass
            elif len(self.buffer) < 80:
                self.buffer += bytes((ch,))
            else:
                self.buffer = b""  # Oversize input never grows memory without bound.

    def age(self, now): return 1000000 if self.stamp is None else now-self.stamp
