import unittest,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DesignConsistency(unittest.TestCase):
    def test_gpio_definitions_match_firmware(self):
        from firmware import config
        rows=list(csv.DictReader((ROOT/'hardware/pinmap.csv').read_text().splitlines()))
        for role in ('MAIN','SUP'):
            selected={int(r['GPIO']) for r in rows if r['Controller']==role}
            for pin in config.BUTTON_PINS:self.assertIn(pin,selected)
            for name,pin in config.PIN.items():
                if name not in ('spare','sda','scl'):self.assertIn(pin,selected)
    def test_no_pico_regulator_outputs_tied(self):
        d=json.loads((ROOT/'hardware/design.json').read_text())
        a={c['ref']:c for c in d['components']}
        self.assertNotEqual(a['A1']['pins']['36_3V3_OUT'],a['A2']['pins']['36_3V3_OUT'])
    def test_physical_cool_chain_defined(self):
        d=json.loads((ROOT/'hardware/design.json').read_text());a={c['ref']:c for c in d['components']}
        self.assertEqual(a['S_COOL']['pins']['A_NC'],a['S_DOCK']['pins']['A_COM'])
        self.assertEqual(a['S_DOCK']['pins']['A_NC'],a['S_TIP']['pins']['A_COM'])
        self.assertEqual(a['S_TIP']['pins']['A_NO'],a['K1']['pins']['COIL_A'])
    def test_bom_connections_consistent(self):
        d=json.loads((ROOT/'hardware/design.json').read_text());expected={(c['ref'],p,n) for c in d['components'] for p,n in c['pins'].items()}
        rows=list(csv.DictReader((ROOT/'hardware/component_connections.csv').read_text().splitlines()))
        actual={(r['Reference'],r['Pin_or_terminal'],r['Net']) for r in rows};self.assertEqual(expected,actual)
