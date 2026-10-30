"""Cross-file checks. These do not perform native EDA ERC/DRC or hardware validation."""
from pathlib import Path
import ast,csv,json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
def check():
    required=['README.md','BUILD_GUIDE.md','BUILD_COMPLETENESS.md','AUDIT_REPORT.md','VERSION',
              'hardware/BOM.csv','hardware/design.json','hardware/pinmap.csv',
              'hardware/component_connections.csv','hardware/net_schedule.csv',
              'hardware/procurement_checklist.csv','docs/requirements_traceability.csv',
              '.github/workflows/check.yml']
    for name in required:assert (ROOT/name).is_file(),'Missing required deliverable: '+name
    for p in ROOT.rglob('*.py'):
        if 'build' not in p.relative_to(ROOT).parts:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    for p in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):continue
            path=(p.parent/target.split('#')[0]).resolve()
            if not path.exists():raise AssertionError('Broken link: '+str(p)+' -> '+target)
    design=json.loads((ROOT/'hardware/design.json').read_text())
    refs=[c['ref'] for c in design['components']]
    assert len(refs)==len(set(refs)), 'Duplicate component references'
    for c in design['components']:
        assert c['pins'] and all(c['pins'].values()),c['ref']
    expected={(c['ref'],pin,net) for c in design['components'] for pin,net in c['pins'].items()}
    exported={(r['Reference'],r['Pin_or_terminal'],r['Net']) for r in csv.DictReader((ROOT/'hardware/component_connections.csv').read_text().splitlines())}
    assert expected==exported,'Exported connections differ from design.json'
    bom=list(csv.DictReader((ROOT/'hardware/BOM.csv').read_text().splitlines()))
    assert {r['Reference'] for r in bom}==set(refs),'BOM/reference mismatch'
    assert len(bom)==len(refs),'Duplicate BOM rows'
    from firmware import config
    assert config.PRESETS==(50,100,150,200,250),'Preset list drift'
    assert len(config.BUTTON_PINS)==len(config.PRESETS)
    rows=list(csv.DictReader((ROOT/'hardware/pinmap.csv').read_text().splitlines()))
    for role in ('MAIN','SUP'):
        pins=[r['GPIO'] for r in rows if r['Controller']==role]
        assert len(pins)==len(set(pins)), 'GPIO conflict '+role
        assert [r['Net'] for r in rows if r['Controller']==role and r['GPIO']=='21']==(['PWM_INPUT'] if role=='MAIN' else ['SUP_RELAY_OUTPUT'])
    tc=next(c for c in design['components'] if c['ref']=='U1')['pins']
    assert tc['1']==tc['8']=='5V' and tc['4']==tc['5']=='GND' and tc['6']==tc['7']=='DRIVE'
    q=next(c for c in design['components'] if c['ref']=='Q1')['pins']
    assert q['3_SOURCE']=='GND' and q['2_DRAIN']=='HEAT_MINUS'
    for p in (ROOT/'hardware/kicad').glob('*.kicad_*'):
        # Check structure only; this is not a KiCad parser.
        stripped=re.sub(r'"(?:\\.|[^"\\])*"','',p.read_text())
        level=0
        for c in stripped:
            if c=='(':level+=1
            if c==')':level-=1
            assert level>=0,p
        assert level==0,p
    for p in (ROOT/'docs/images').glob('*.svg'):ET.parse(p)
    version=(ROOT/'VERSION').read_text().strip()
    assert 'version = "'+version+'"' in (ROOT/'pyproject.toml').read_text(),'Version metadata drift'
    assert 'C:\\Users\\' not in (ROOT/'README.md').read_text(), 'README contains local-only paths'
    print('PASS: Python syntax, local Markdown links, GPIO ownership, selected circuit invariants, EDA structure and SVG XML.')
    print('NOT RUN BY THIS COMMAND: target MicroPython, native EDA tools, hardware or medical validation. Stored native evidence is checked separately.')
if __name__=='__main__':check()
