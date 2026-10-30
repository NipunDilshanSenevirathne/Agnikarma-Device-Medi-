"""Exercise the actual MicroPython app with deterministic hardware adapters.
This tests software integration, not execution on an RP2040 or physical circuitry.
"""
import json,math,os,tempfile,types,unittest
from unittest.mock import patch,mock_open
from pathlib import Path
from firmware.core import encode_frame,resistance_from_temperature
from firmware.app import run

class AppIntegration(unittest.TestCase):
    def run_role(self,role,dock_at=None,tip_removed_at=None,config_record=None):
        clock=types.SimpleNamespace(k=0)
        pins={};events=[]
        class Pin:
            OUT,IN,PULL_UP,PULL_DOWN=1,0,2,3
            def __init__(self,n,*args,**kw):self.n=n;self.v=kw.get('value',0);pins[n]=self
            def value(self,v=None):
                if v is not None:self.v=v;events.append((clock.k,'pin',self.n,v));return v
                if self.n==19:return clock.k%2
                if self.n==14:return 0 if clock.k==8 else 1  # COOL
                if self.n==15:return 0 if clock.k>=5 else 1  # HEAT remains held after COOL
                if self.n==16:return 0 if clock.k==2 else 1  # ARM edge
                if self.n==17:return 0 if clock.k==dock_at else 1
                if self.n==18:return 1 if clock.k==tip_removed_at else 0
                return 1
        class PWM:
            def __init__(self,p):self.p=p
            def freq(self,v):pass
            def duty_u16(self,v):events.append((clock.k,'pwm',21,v))
        class SPI:
            def __init__(self,*a,**k):self.reg=0
            def write(self,b):self.reg=b[0]
            def read(self,n):
                events.append((clock.k,'spi_read',0,n))
                if self.reg==1:
                    code=round(resistance_from_temperature(25)/4300*32768)<<1
                    return bytes((code>>8,code&255))
                return bytes(n)
        class UART:
            def __init__(self,*a,**kw):pass
            def read(self,n):return encode_frame('S' if role=='main' else 'M',clock.k,50,25,True)
            def write(self,b):return len(b)
        class ADC:
            def __init__(self,n):self.n=n
            def read_u16(self):return round((7.2/(3.3*(139/39)) if self.n==26 else .5)*65535)
        class I2C:
            def __init__(self,*a,**kw):pass
            def writeto(self,*a):pass
        class WDT:
            def __init__(self,*a,**kw):pass
            def feed(self):pass
        class FrameBuffer:
            def __init__(self,*a):pass
            def fill(self,*a):pass
            def text(self,*a):pass
        def sleep(ms):
            clock.k+=1
            if clock.k>=11:raise KeyboardInterrupt
        fake_time=types.SimpleNamespace(ticks_ms=lambda:clock.k*100,ticks_diff=lambda a,b:a-b,sleep_ms=sleep)
        fake_machine=types.SimpleNamespace(Pin=Pin,PWM=PWM,SPI=SPI,UART=UART,ADC=ADC,I2C=I2C,WDT=WDT)
        fake_fb=types.SimpleNamespace(FrameBuffer=FrameBuffer,MONO_VLSB=0)
        cfg=json.dumps({'role':role,'bench_enabled':True,'calibration_record':'MOCK-TEST-ONLY'} if config_record is None else config_record)
        with patch('builtins.open',mock_open(read_data=cfg)):
            with patch.dict('sys.modules',{'machine':fake_machine,'time':fake_time,'framebuf':fake_fb}):
                with self.assertRaises(KeyboardInterrupt):run(role)
        return events

    def test_main_app_heat_cool_and_no_automatic_restart(self):
        events=self.run_role('main');out=[e for e in events if e[1]=='pwm']
        self.assertTrue(any(e[3]>0 for e in out if 5<=e[0]<8))
        self.assertTrue(all(e[3]==0 for e in out if e[0]>=8))
        self.assertEqual(out[-1][3],0)

    def test_supervisor_app_relay_cool_and_exception_shutdown(self):
        events=self.run_role('supervisor');out=[e for e in events if e[1]=='pin' and e[2]==21]
        self.assertTrue(any(e[3]==1 for e in out if 5<=e[0]<8))
        self.assertTrue(all(e[3]==0 for e in out if e[0]>=8))
        self.assertEqual(out[-1][3],0)

    def test_dock_shutdown_precedes_spi_acquisition(self):
        events=self.run_role('main',dock_at=6)
        index=next(i for i,e in enumerate(events) if e[0]==6 and e[1]=='spi_read')
        self.assertEqual([e for e in events[:index] if e[1]=='pwm'][-1][3],0)

    def test_tip_removal_shutdown_precedes_spi_acquisition(self):
        events=self.run_role('main',tip_removed_at=6)
        index=next(i for i,e in enumerate(events) if e[0]==6 and e[1]=='spi_read')
        self.assertEqual([e for e in events[:index] if e[1]=='pwm'][-1][3],0)

    def test_malformed_or_unprovisioned_config_never_energizes(self):
        for record in ([],{}, {'role':'main','bench_enabled':True,'calibration_record':None}):
            with self.subTest(record=record):
                events=self.run_role('main',config_record=record)
                self.assertTrue(all(e[3]==0 for e in events if e[1]=='pwm'))
