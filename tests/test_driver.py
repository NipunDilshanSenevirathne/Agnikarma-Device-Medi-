import unittest
from firmware.drivers.max31865 import MAX31865
class Pin:
    def __init__(self):self.v=1
    def value(self,v):self.v=v
class SPI:
    def __init__(self):self.writes=[];self.responses=[]
    def write(self,b):self.writes.append(b)
    def read(self,n):return self.responses.pop(0)
class DriverTests(unittest.TestCase):
    def test_initialization(self):
        s=SPI();p=Pin();MAX31865(s,p);self.assertEqual(s.writes,[b'\x80\xc3',b'\x80\xc1']);self.assertEqual(p.v,1)
    def test_fault_raises_and_cs_released(self):
        s=SPI();p=Pin();d=MAX31865(s,p);s.responses=[b'\x40\x01']
        with self.assertRaises(ValueError):d.temperature()
        self.assertEqual(p.v,1)
    def test_nominal_approx_0c(self):
        s=SPI();p=Pin();d=MAX31865(s,p);v=round(1000/4300*32768)<<1;s.responses=[bytes((v>>8,v&255)),b'\x00']
        self.assertAlmostEqual(d.temperature(),0,delta=.05)
