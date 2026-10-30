from pathlib import Path
import json,csv,uuid,math,subprocess,shutil
from reportlab.graphics.shapes import Drawing,Rect,Line,String,Circle,PolyLine,Polygon
from reportlab.graphics import renderPDF,renderSVG
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1];R=ROOT;W=ROOT/'build';W.mkdir(exist_ok=True)
import os
POP=os.environ.get('AGNI_PDFTOPPM') or shutil.which('pdftoppm')
if not POP: raise RuntimeError('Install Poppler or set AGNI_PDFTOPPM')
def put(n,t):
 p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t+'\n',encoding='utf-8')
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_DNS,'agni-portable-p3-'+s))
def txt(d,x,y,t,s=16,c='#183449',b=False):
 for i,line in enumerate(t.split('\n')):d.add(String(x,y-i*(s+6),line,fontName='Helvetica-Bold' if b else 'Helvetica',fontSize=s,fillColor=colors.HexColor(c)))
def base(title,sub):
 d=Drawing(1400,850);d.add(Rect(0,0,1400,850,fillColor=colors.white,strokeColor=None));txt(d,40,795,title,29,b=True);txt(d,40,760,sub,15,c='#52697A');txt(d,40,25,'P3 MODULE PROTOTYPE | GENERATED ENGINEERING DRAWING | PHYSICAL VALIDATION PENDING',13,c='#A33E40');return d
def box(d,x,y,w,h,t,c='#087F83'):
 d.add(Rect(x,y,w,h,rx=10,ry=10,fillColor=colors.HexColor('#EFF5F8'),strokeColor=colors.HexColor(c),strokeWidth=2));txt(d,x+15,y+h-30,t,16,c)
def wire(d,pts,c='#D07224',w=3):d.add(PolyLine(pts,strokeColor=colors.HexColor(c),strokeWidth=w))
def fig(name,d):
 out=R/'docs/images'/name
 renderSVG.drawToFile(d,str(out.with_suffix('.svg')));tmp=W/(name+'.pdf');renderPDF.drawToFile(d,str(tmp))
 subprocess.run([POP,'-scale-to','2000','-png','-singlefile',str(tmp),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
d=base('Current implementation: dual-controller modular prototype','Main controls PWM; supervisor independently reads RTD2 and controls relay. COOL interrupts the coil supply directly.')
box(d,40,520,230,160,'Qualified 2S pack\nor guarded bench supply\nFuse + 5 V buck\nNo direct pack-to-GPIO')
box(d,365,520,300,160,'Main Pico + RTD1 board\nBounded temperature loop\nDisplay / user controls\nUART + health pulse')
box(d,780,520,300,160,'Supervisor Pico + RTD2\nIndependent acquisition\nSetting / fault checks\nRelay control')
box(d,1130,520,230,160,'Insulated heater\nBrass contact end\nTwo sensors\nLock + identity')
box(d,365,250,300,150,'TC4420 + IRLZ44N\nPWM return switch\nGate pull-downs\n5 V gate drive')
box(d,780,250,300,150,'K1 high-side relay\nPN2222ABU driver\nCOOL/dock/lock contacts\nin coil supply chain')
wire(d,[270,600,365,600]);wire(d,[665,600,780,600],'#2E7CB1');wire(d,[665,570,780,570],'#2E7CB1')
wire(d,[510,520,510,400]);wire(d,[930,520,930,400],'#A33E40')
wire(d,[1080,320,1245,320,1245,520]);wire(d,[365,300,305,300,305,455,1220,455,1220,520])
txt(d,50,150,'Heater power path: fused pack -> normally-open K1 -> heater -> Q1 -> power return.\nTwo sensor interfaces use separate 3V3 regulators; controllers share a defined ground and controls via branch resistors.\nThe module architecture is larger than the future handheld concept. No patient-use or manufacturing release is implied.',18)
fig('architecture',d)
d=base('Defined power-stage circuit and interlocks','Values and package mapping are in hardware/design.json. Verify actual parts before assembly; no high-current solderless breadboard.')
box(d,40,560,190,105,'PACK_FUSED\nF1 from pack entry')
box(d,330,560,240,105,'K1 COM -> NO\nG5LE-1-DC5\nNormally open contact')
box(d,690,560,220,105,'Heater / test load\n2.2 ohm assumption')
box(d,1060,560,260,105,'Q1 IRLZ44NPBF\nDrain -> source\nSource to power GND')
for a,b in [(230,330),(570,690),(910,1060)]:wire(d,[a,610,b,610],w=5)
box(d,690,360,220,110,'TC4420CPA\n5 V supply / bypass\nInput: main GP21')
wire(d,[910,415,990,415,990,580,1060,580])
txt(d,930,380,'10 ohm gate R\n100k gate-source R\n100k driver-input R',14)
box(d,40,160,270,135,'5 V -> COOL NC\n-> dock NC\n-> locked-tip NO\n-> coil positive',c='#A33E40')
box(d,390,160,240,135,'K1 coil\n1N4007 across coil\nCathode at positive',c='#A33E40')
box(d,730,160,240,135,'PN2222ABU\nCollector: coil return\nEmitter: GND',c='#A33E40')
box(d,1090,160,230,135,'Supervisor GP21\n330 ohm to base\n100k base-emitter',c='#A33E40')
wire(d,[310,230,390,230],'#A33E40');wire(d,[630,230,730,230],'#A33E40');wire(d,[1090,230,970,230],'#A33E40')
txt(d,40,85,'Relay release delay (including flyback diode) and fault energy must be measured. Q1 tab is electrically live drain.\nThis schematic defines a bench circuit; no medical safety or sterilization performance has been established.',15)
fig('power-stage',d)
d=base('Brass-tip geometry source','Shape studies: only T01/T02 have electrical identity records. Heater/sensor integration and finished material evaluation remain open.')
labels=['T01 / 2 mm','T02 / 4 mm dome','T03 / 6 mm disc','T04 / 6 x 2 mm','T05 / 3 mm angled']
for j,label in enumerate(labels):
 x=150+j*270;d.add(Rect(x-16,280,32,225,fillColor=colors.HexColor('#B08A3E'),strokeColor=None))
 if j<2:d.add(Circle(x,515,15 if j==0 else 30,fillColor=colors.HexColor('#B08A3E'),strokeColor=None))
 elif j==2:d.add(Rect(x-45,500,90,18,fillColor=colors.HexColor('#B08A3E'),strokeColor=None))
 elif j==3:d.add(Rect(x-45,500,90,24,rx=12,ry=12,fillColor=colors.HexColor('#B08A3E'),strokeColor=None))
 else:
  d.add(Polygon([x-16,490,x+30,555,x+50,540,x+16,475],fillColor=colors.HexColor('#B08A3E'),strokeColor=None));d.add(Circle(x+42,550,20,fillColor=colors.HexColor('#B08A3E'),strokeColor=None))
 txt(d,x-90,620,label,18,b=True);txt(d,x-70,220,'Brass end concept\nNot a machining release',14)
txt(d,80,110,'No tip-to-disease mapping, clinical contact time or injury depth is established by these dimensions.\nCertified alloy, impurity limits, thermal gradients, retention and reprocessing require separate evidence.',18)
fig('brass-tips',d)

# Electrical schematic with real named nets, generated from shared design records.
des=json.loads((R/'hardware/design.json').read_text());components=des['components']
maps=list(csv.DictReader((R/'hardware/pinmap.csv').open()))
root=uid('root');libs=[];inst=[];labels=[]
for idx,c in enumerate(components):
 ref=c['ref'];value=c['value'];pins=list(c['pins'].items());name='Module_'+ref
 h=max(10,(len(pins)+1)*2.54)
 texts=[]
 for pi,(pin,net) in enumerate(pins):
  yy=-2.54*(pi+1)
  texts.append(f'(pin passive line (at 45.72 {yy:.3f} 180) (length 10.16) (name "{pin}" (effects (font (size 1 1)))) (number "{pi+1}" (effects (font (size 1 1)))))')
 libs.append(f'''(symbol "AGNI:{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes)
 (property "Reference" "U" (at 0 5 0) (effects (font (size 1.2 1.2))))
 (property "Value" "{ref}" (at 0 2 0) (effects (font (size 1 1))))
 (symbol "{name}_0_1" (rectangle (start 0 0) (end 35.56 {-h:.3f}) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "{name}_1_1" {''.join(texts)}))''')
 x=25.4+(idx%10)*113.03;y=38.1 if idx//10==0 else 165.1+(idx//10-1)*88.9;u=uid(ref)
 inst.append(f'''(symbol (lib_id "AGNI:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{u}")
 (property "Reference" "{ref}" (at {x+15} {y-5} 0) (effects (font (size 1.2 1.2))))
 (property "Value" "{value[:48]}" (at {x+18} {y-2} 0) (effects (font (size 0.8 0.8))))
 {''.join(f'(pin "{i+1}" (uuid "{uid(ref+str(i))}"))' for i in range(len(pins)))}
 (instances (project "agni-module-system" (path "/{root}" (reference "{ref}") (unit 1)))))''')
 for pi,(pin,net) in enumerate(pins):
  yy=y+2.54*(pi+1)
  if net.startswith('NC_'):
   labels.append(f'(no_connect (at {x+45.72} {yy:.3f}) (uuid "{uid(ref+"NC"+str(pi))}"))')
   continue
  labels.append(f'''(wire (pts (xy {x+45.72} {yy:.3f}) (xy {x+52.07} {yy:.3f})) (stroke (width 0) (type default)) (uuid "{uid(ref+'wire'+str(pi))}"))
 (label "{net}" (at {x+52.07} {yy:.3f} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(ref+'label'+str(pi))}"))''')
sch=f'''(kicad_sch (version 20231120) (generator "eeschema") (uuid "{root}") (paper "A0")
(title_block (title "AGNI P3 module wiring - unverified prototype") (date "2026-10-31") (rev "0.5.0"))
(lib_symbols {''.join(libs)}) {''.join(inst)} {''.join(labels)})'''
put('hardware/kicad/agni-module-system.kicad_sch',sch)
put('hardware/kicad/agni-module-system.kicad_pro',json.dumps({'meta':{'filename':'agni-module-system.kicad_pro','version':1}},indent=2))

# Preserve the routed carrier through regeneration using its dedicated generator.
import sys
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.generate_carrier import main as generate_carrier
generate_carrier()
print('Generated diagrams, module schematic, matched carrier and local libraries. Native checks are separate.')
