import unittest,math
from firmware import config as C
from firmware.core import *

def inp(now=0,**kw):
    a=dict(now=now,sample=Sample(25,now),peer_temp=25,peer_age_ms=0,
           heartbeat_age_ms=0,peer_target=50,peer_allow=True,pack_v=7.2,pack_c=25,
           provisioning_ok=True)
    a.update(kw);return Inputs(**a)

def armed_controller():
    c=Controller();c.step(inp(0));c.step(inp(100,arm=True));return c

class ControllerTests(unittest.TestCase):
    def test_startup_requires_release_and_new_arm_edge(self):
        c=Controller();self.assertEqual(c.step(inp(0,arm=True,heat=True)),0)
        c.step(inp(100,arm=True));self.assertFalse(c.armed)
        c.step(inp(200));c.step(inp(300,arm=True));self.assertTrue(c.armed)
    def test_no_heating_without_hold(self):
        c=armed_controller();self.assertEqual(c.step(inp(200)),0)
    def test_heating_is_bounded(self):
        c=armed_controller();d=c.step(inp(200,heat=True));self.assertGreater(d,0);self.assertLessEqual(d,C.MAX_DUTY)
    def test_cool_preempts_heat_and_arm(self):
        c=armed_controller();self.assertEqual(c.step(inp(200,cool=True,heat=True,arm=True)),0);self.assertFalse(c.armed)
    def test_release_cool_does_not_resume(self):
        c=armed_controller();c.step(inp(200,cool=True));self.assertEqual(c.step(inp(300,heat=True)),0)
    def test_invalid_temperature_values(self):
        for v in (float('nan'),float('inf'),-100,316):
            with self.subTest(value=v):
                c=armed_controller();self.assertEqual(c.step(inp(200,sample=Sample(v,200),heat=True)),0);self.assertFalse(c.armed)
    def test_all_independent_fault_inputs_remove_output(self):
        for change in [dict(pack_v=0),dict(pack_v=9),dict(pack_c=60),dict(pack_c=float('nan')),
                       dict(tip_present=False),dict(tip_id='T99'),dict(dock=True),dict(sensor_fault=True),
                       dict(peer_age_ms=351),dict(peer_age_ms=-1),dict(heartbeat_age_ms=351),
                       dict(peer_target=100),dict(peer_temp=40),dict(provisioning_ok=False),
                       dict(sample=Sample(25,-1000)),dict(sample=Sample(25,500))]:
            with self.subTest(change=change):
                c=armed_controller();self.assertEqual(c.step(inp(200,heat=True,**change)),0);self.assertFalse(c.armed)
    def test_absolute_and_setting_overtemp(self):
        c=armed_controller();self.assertEqual(c.step(inp(200,sample=Sample(61,200),peer_temp=61,heat=True)),0)
    def test_lost_supervisor_permit_removes_pwm(self):
        c=armed_controller();self.assertEqual(c.step(inp(200,peer_allow=False,heat=True)),0)
    def test_long_control_gap_disarms(self):
        c=armed_controller();self.assertEqual(c.step(inp(1000,heat=True)),0);self.assertEqual(c.fault,'CONTROL_GAP')
    def test_setpoint_change_requires_rearm(self):
        c=armed_controller();c.select(100);self.assertFalse(c.armed)
    def test_bad_setpoint_rejected(self):
        c=armed_controller();c.select(51);self.assertFalse(c.armed)
    def test_removed_300c_preset_is_rejected(self):
        self.assertEqual(C.PRESETS,(50,100,150,200,250))
        c=armed_controller();c.select(300);self.assertFalse(c.armed)
        with self.assertRaises(ValueError):encode_frame('M',1,300,25,False)
    def test_every_preset(self):
        for t in C.PRESETS:
            c=Controller();c.select(t);c.step(inp(0,peer_target=t));c.step(inp(100,peer_target=t,arm=True))
            d=c.step(inp(200,peer_target=t,heat=True));self.assertGreater(d,0)
    def test_cool_unknown_sensor_never_cooled(self):
        c=armed_controller();c.step(inp(200,cool=True,sample=Sample(float('nan'),200,False)))
        self.assertEqual(c.state,'HOT_UNKNOWN')
    def test_power_cap(self):
        c=armed_controller();d=c.step(inp(200,pack_v=8.4,heat=True));self.assertLessEqual(d*8.4**2/C.HEATER_OHMS,C.MAX_POWER_W)

class SupervisorTests(unittest.TestCase):
    def test_no_relay_before_arm(self):self.assertFalse(Supervisor().step(inp(0,heat=True)))
    def test_relay_needs_heat_after_arm(self):
        s=Supervisor();s.step(inp(0));self.assertFalse(s.step(inp(100,arm=True)));self.assertTrue(s.step(inp(200,heat=True)))
    def test_fault_and_cool_latch_off(self):
        for kw in (dict(cool=True),dict(sensor_fault=True),dict(heartbeat_age_ms=999)):
            s=Supervisor();s.step(inp(0));s.step(inp(100,arm=True));self.assertFalse(s.step(inp(200,heat=True,**kw)))
            self.assertFalse(s.step(inp(300,heat=True)))
    def test_main_temperature_disagreement(self):self.assertFalse(Supervisor().step(inp(0,peer_temp=300,heat=True)))
    def test_selected_setting_changed_disarms(self):
        s=Supervisor();s.step(inp(0));s.step(inp(100,arm=True));s.select(100);self.assertFalse(s.armed)

class ProtocolTests(unittest.TestCase):
    def test_crc_reference(self):self.assertEqual(crc16(b'123456789'),0x29B1)
    def test_roundtrip_and_split_packets(self):
        f=encode_frame('S',1,50,42.25,True);l=Link('S');l.feed(f[:4],10);l.feed(f[4:],20)
        self.assertEqual((l.temp,l.target,l.allow,l.stamp),(42.25,50,True,20))
    def test_crc_damage_does_not_refresh(self):
        l=Link('S');f=encode_frame('S',1,50,25,False);l.feed(f,1);l.feed(f.replace(b'25',b'26'),20);self.assertEqual(l.stamp,1)
    def test_replay_and_wrong_role(self):
        l=Link('S');f=encode_frame('S',1,50,25,False);l.feed(f,1);l.feed(f,100);self.assertEqual(l.stamp,1)
        l.feed(encode_frame('M',2,50,25,True),200);self.assertEqual(l.stamp,1)
    def test_sequence_wrap(self):
        l=Link('S');l.feed(encode_frame('S',65535,50,25,False),1);l.feed(encode_frame('S',0,50,26,True),2);self.assertEqual(l.temp,26)
    def test_oversized_bad_input_bounded(self):
        l=Link('S');l.feed(b'x'*10000,0);self.assertLessEqual(len(l.buffer),80);self.assertIsNone(l.stamp)
    def test_unset_link_is_stale(self):self.assertGreater(Link('S').age(0),C.STALE_MS)
    def test_nan_encode_rejected(self):
        with self.assertRaises(ValueError):encode_frame('S',0,50,float('nan'),True)

class SensorMathTests(unittest.TestCase):
    def test_roundtrip_each_preset(self):
        for t in C.PRESETS:self.assertAlmostEqual(temperature_from_resistance(resistance_from_temperature(t)),t,places=7)
    def test_out_of_range(self):
        for x in (0,100,float('nan'),float('inf'),10000):
            with self.assertRaises(ValueError):temperature_from_resistance(x)

if __name__=='__main__':unittest.main()
