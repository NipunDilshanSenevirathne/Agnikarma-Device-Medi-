"""Regression checks added by the 0.4 audit. Hardware behaviour remains unmeasured."""
import unittest,math
from firmware.provision import validate
from firmware.core import finite,Supervisor
from test_core import inp
from firmware.drivers.max31865 import MAX31865
from test_driver import Pin,SPI

def record():return dict(role='main',bench_enabled=True,calibration_record='BENCH-RECORD-001')

class ProvisionTests(unittest.TestCase):
    def test_nominal_record(self):self.assertTrue(validate(record(),'main')[0])
    def test_missing_and_wrong_record_types(self):
        for x in (None,[],True,1,'text'):
            with self.subTest(value=x):self.assertFalse(validate(x,'main')[0])
    def test_empty_invalid_or_unmeasured_calibration(self):
        for x in (None,'','  ','UNMEASURED',False,123,'x'*129):
            d=record();d['calibration_record']=x
            with self.subTest(value=x):self.assertFalse(validate(d,'main')[0])
    def test_wrong_role_or_boolean(self):
        for field,value in [('role','supervisor'),('bench_enabled',1),('bench_enabled','true')]:
            d=record();d[field]=value;self.assertFalse(validate(d,'main')[0])
    def test_bad_numeric_fields_disabled_and_sanitized(self):
        for key in ('sensor_offset_c','battery_scale','reference_resistor_ohm'):
            for value in (None,True,False,'1',float('nan'),float('inf'),-9999):
                d=record();d[key]=value;valid,cfg=validate(d,'main')
                with self.subTest(key=key,value=value):self.assertFalse(valid);self.assertTrue(finite(cfg[key]))
    def test_display_address_rejected(self):
        for value in (True,60.0,62,'60',None):
            d=record();d['display_address']=value;self.assertFalse(validate(d,'main')[0])
    def test_boolean_is_not_a_measurement(self):self.assertFalse(finite(True));self.assertFalse(finite(False))

class SupervisorPermitTests(unittest.TestCase):
    def test_relay_requires_main_armed_permit(self):
        s=Supervisor();s.step(inp(0));s.step(inp(100,arm=True))
        self.assertFalse(s.step(inp(200,heat=True,peer_allow=False)))
        self.assertTrue(s.step(inp(300,heat=True,peer_allow=True)))
        self.assertFalse(s.step(inp(400,heat=True,peer_allow=False)))

class SensorTransportTests(unittest.TestCase):
    def test_incomplete_spi_read_is_a_controlled_fault(self):
        for value in (None,b'',b'\x00'):
            s=SPI();p=Pin();d=MAX31865(s,p);s.responses=[value]
            with self.subTest(value=value):
                with self.assertRaises(ValueError):d.temperature()
                self.assertEqual(p.v,1)
