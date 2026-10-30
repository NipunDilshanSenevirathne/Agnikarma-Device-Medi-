import unittest,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HardwareAuditTests(unittest.TestCase):
    def setUp(self):
        self.d=json.loads((ROOT/'hardware/design.json').read_text())
        self.c={c['ref']:c for c in self.d['components']}
    def test_both_rtd_elements_and_four_leads_are_defined(self):
        for role in ('MAIN','SUP'):
            sensor=self.c['SENSOR_'+role]['pins'];interface=self.c['RTD_'+role]['pins']
            self.assertEqual(len(sensor),4)
            self.assertEqual(set(sensor.values()),{interface[x] for x in ('F+','RTD+','RTD-','F-')})
    def test_all_gpio_records_exist_on_controller_component(self):
        for row in csv.DictReader((ROOT/'hardware/pinmap.csv').read_text().splitlines()):
            c=self.c['A1' if row['Controller']=='MAIN' else 'A2']['pins']
            key=row['Physical_header_pin']+'_GP'+row['GPIO']
            self.assertEqual(c[key],row['Net'])
    def test_ordered_main_to_supervisor_links(self):
        for ref,first,second in [('R_LINK_M','MAIN_TX','SUP_RX'),('R_LINK_S','SUP_TX','MAIN_RX'),
                                 ('R_PULSE_M','MAIN_PULSE_OUT','SUP_PULSE_IN'),('R_PULSE_S','SUP_PULSE_OUT','MAIN_PULSE_IN')]:
            self.assertEqual(self.c[ref]['pins'],{'1':first,'2':second})
    def test_no_live_300c_buttons_remain(self):
        self.assertFalse(any('300' in r for r in self.c))
        self.assertFalse(any('KEY_300' in n or n=='B300' for c in self.c.values() for n in c['pins'].values()))
    def test_net_schedule_covers_every_component_pin(self):
        expected={(c['ref']+'.'+pin,net) for c in self.c.values() for pin,net in c['pins'].items()}
        found=set()
        for row in csv.DictReader((ROOT/'hardware/net_schedule.csv').read_text().splitlines()):
            found.update((p,row['Net']) for p in row['Connected_terminals'].split('; '))
        self.assertEqual(expected,found)
