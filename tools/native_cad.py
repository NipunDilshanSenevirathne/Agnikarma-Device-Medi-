"""Run native KiCad checks, then export inspectable prototype manufacturing data.

The carrier is a passive low-current module breakout. Clean native checks do
not qualify a medical device or prove external power-circuit safety.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.text_format import canonicalize

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kicad-cli',default='kicad-cli');ap.add_argument('--render',action='store_true');a=ap.parse_args()
    records=ROOT/'docs/records';draw=ROOT/'hardware/drawings';fab=ROOT/'hardware/fabrication/P3R1'
    for p in (records,draw,fab,ROOT/'build/cad-config',ROOT/'build/cad-documents'):p.mkdir(parents=True,exist_ok=True)
    canonicalize((ROOT/'hardware/kicad').rglob('*'))
    env=os.environ.copy();env['KICAD_CONFIG_HOME']=str(ROOT/'build/cad-config');env['KICAD_DOCUMENTS_HOME']=str(ROOT/'build/cad-documents')
    commands=[]
    def run(args):
        r=subprocess.run([a.kicad_cli]+list(map(str,args)),cwd=ROOT,env=env,capture_output=True,text=True)
        cleaned=(r.stdout+r.stderr).replace(str(ROOT),'<repo>').replace(str(ROOT).replace('\\','/'),'<repo>')
        display='kicad-cli '+' '.join(str(x).replace(str(ROOT),'<repo>') for x in args)
        commands.append({'command':display,'exit_code':r.returncode,'output':cleaned.strip()})
        if r.returncode:raise RuntimeError(display+'\n'+cleaned)
        print(cleaned.strip(),flush=True)
        return r.stdout.strip()
    version=run(['version'])
    board=ROOT/'hardware/kicad/agni-controller-carrier.kicad_pcb'
    carrier=board.with_suffix('.kicad_sch');system=board.parent/'agni-module-system.kicad_sch'
    checks={}
    for name,sch in [('carrier',carrier),('module-system',system)]:
        report=records/(name+'-erc.json')
        run(['sch','erc','--format','json','--severity-all','--exit-code-violations','--output',report,sch])
        data=json.loads(report.read_text());violations=[v for sheet in data['sheets'] for v in sheet['violations']]
        if violations:raise RuntimeError(name+' has ERC findings')
        checks[name+'_erc_violations']=len(violations)
    report=records/'carrier-drc.json'
    run(['pcb','drc','--format','json','--severity-all','--schematic-parity','--exit-code-violations','--output',report,board])
    data=json.loads(report.read_text())
    for key in ('violations','unconnected_items','schematic_parity'):
        checks['carrier_'+key]=len(data[key])
        if data[key]:raise RuntimeError('Carrier has '+key)
    # Native documentation/fabrication exports are emitted only after the above pass.
    run(['pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,Edge.Cuts','--output',str(fab)+os.sep,board])
    run(['pcb','export','drill','--excellon-separate-th','--generate-map','--map-format','svg','--generate-report','--report-path',fab/'drill-report.txt','--output',str(fab)+os.sep,board])
    for name,sch in [('carrier',carrier),('module-system',system)]:
        run(['sch','export','pdf','--exclude-pdf-property-popups','--output',draw/(name+'-schematic.pdf'),sch])
    run(['sch','export','netlist','--format','kicadxml','--output',draw/'carrier-netlist.xml',carrier])
    for side,layers in [('top','F.Cu,F.SilkS,Edge.Cuts'),('bottom','B.Cu,Edge.Cuts'),('routing','F.Cu,B.Cu,F.SilkS,Edge.Cuts')]:
        args=['pcb','export','svg','--mode-single','--page-size-mode','2','--layers',layers,'--output',ROOT/f'docs/images/carrier-{side}.svg',board]
        run(args)
    run(['pcb','export','pdf','--mode-multipage','--no-property-popups','--layers','F.Cu,B.Cu,F.SilkS,Edge.Cuts','--output',draw/'carrier-layers.pdf',board])
    run(['pcb','export','step','--board-only','--force','--output',ROOT/'mechanical/exports/carrier-board-only.step',board])
    if a.render:
        for side in ('top','bottom'):
            run(['pcb','render','--width','1800','--height','1200','--side',side,'--quality','high','--background','transparent','--output',ROOT/f'docs/images/carrier-{side}-native.png',board])
    # Remove author-machine paths from netlist metadata, preserving electrical nodes.
    p=draw/'carrier-netlist.xml';p.write_text(p.read_text().replace(str(ROOT),'[repo]').replace(str(ROOT).replace('\\','/'),'[repo]'))
    sources=sorted([p for p in board.parent.rglob('*') if p.is_file() and p.suffix in ('.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod')]+[board.parent/'sym-lib-table',board.parent/'fp-lib-table'])
    inputs=[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
    outputs=sorted([p for folder in (fab,draw) for p in folder.iterdir() if p.is_file() and p.suffix!='.md']+list((ROOT/'docs/images').glob('carrier-*'))+[ROOT/'mechanical/exports/carrier-board-only.step'])
    canonicalize(outputs);canonicalize(records.glob('*-?rc.json'))
    result={'version':(ROOT/'VERSION').read_text().strip(),'tool':version,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'scope':'Native parsing, generic passive-symbol ERC, carrier DRC and schematic parity, CAD and candidate fabrication exports. Not a medical manufacturing release.',
      'passed':True,'checks':checks,'source_hashes':inputs,'output_hashes':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],'commands':commands,
      'limitations':['Generic passive symbols do not check power or signal pin directions inside modules.',
        'Default KiCad ignored-check categories remain listed in the individual raw reports.',
        'External MOSFET/relay/ADC/switch/sensor circuits are not routed on this carrier.',
        'Native checks do not establish purchased footprint fit, independent circuit review, CAM acceptance or physical/medical performance.',
        'Sandbox can log denied optional Windows registry preference access; successful reports and explicit counts determine the check result.']}
    (records/'native-cad-checks.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print('PASS: native ERC, DRC, parity and exports. Physical review and tests remain required.')
if __name__=='__main__':main()
