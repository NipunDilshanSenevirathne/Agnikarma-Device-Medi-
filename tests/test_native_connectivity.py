"""Compare native-exported connectivity to separate firmware/physical pin data."""
from pathlib import Path
import csv,json,unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

class NativeConnectivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc=ET.parse(ROOT/'hardware/drawings/carrier-netlist.xml')
        cls.nodes={}
        for net in doc.findall('./nets/net'):
            for node in net.findall('node'):
                key=(node.attrib['ref'],node.attrib['pin'])
                if key in cls.nodes:raise AssertionError('Duplicate native netlist pin '+str(key))
                cls.nodes[key]=net.attrib['name']

    def test_native_pico_pin_assignment_matches_independent_gpio_schedule(self):
        for row in csv.DictReader((ROOT/'hardware/pinmap.csv').read_text().splitlines()):
            ref='A1' if row['Controller']=='MAIN' else 'A2'
            self.assertEqual(self.nodes[(ref,row['Physical_header_pin'])],'/'+row['Net'])

    def test_native_breakout_reversal_and_isolated_unused_pads(self):
        for row in csv.DictReader((ROOT/'hardware/carrier_connectors.csv').read_text().splitlines()):
            key=(row['Connector'],row['Pin']);pico='A1' if row['Pico']=='MAIN' else 'A2'
            pico_key=(pico,row['Pico_header_pin'])
            if row['Net']=='NC':
                self.assertTrue(self.nodes[key].startswith('unconnected-'))
                self.assertTrue(self.nodes[pico_key].startswith('unconnected-'))
                self.assertNotEqual(self.nodes[key],self.nodes[pico_key])
            else:self.assertEqual(self.nodes[key],self.nodes[pico_key])

    def test_native_supplies_and_all_ground_pins(self):
        for ref in ('A1','A2'):
            for pin in ('3','8','13','18','23','28','33','38'):self.assertEqual(self.nodes[(ref,pin)],'/GND')
            self.assertEqual(self.nodes[(ref,'39')],'/5V')
            self.assertTrue(self.nodes[(ref,'40')].startswith('unconnected-'))
        self.assertNotEqual(self.nodes[('A1','36')],self.nodes[('A2','36')])
        self.assertEqual(self.nodes[('J5','1')],'/GND');self.assertEqual(self.nodes[('J5','2')],'/5V')

    def test_native_carrier_mounts_match_housing_coordinates(self):
        p=json.loads((ROOT/'mechanical/assembly_parameters.json').read_text())
        ox,oy,_=p['carrier_origin_in_housing']
        self.assertEqual([[x+ox,y+oy] for x,y in p['carrier_mounts_in_board_coordinates']],p['housing_carrier_mounts'])
        self.assertTrue(p['carrier_size'][0]<p['housing_outer'][0]-2*p['wall'])
        self.assertTrue(p['carrier_size'][1]<p['housing_outer'][1]-2*p['wall'])
