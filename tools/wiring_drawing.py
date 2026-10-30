"""Exact terminal labels generated from design.json; not a hardware photograph."""
from pathlib import Path
import json,os,shutil,subprocess
from reportlab.graphics.shapes import Drawing,Rect,Line,Circle,String
from reportlab.graphics import renderSVG,renderPDF
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
def main():
    components={c['ref']:c for c in json.loads((ROOT/'hardware/design.json').read_text())['components']}
    selected=['F1','K1','H_TEST','Q1','U1','R1','R2','R3','C1','C2','C3','Q2','R4','R5','D1','S_COOL','S_DOCK','S_TIP']
    d=Drawing(1400,2200)
    d.add(Rect(0,0,1400,2200,fillColor=colors.white,strokeColor=None))
    def text(x,y,s,size=14,bold=False,col='#163447'):
        d.add(String(x,y,s,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=colors.HexColor(col)))
    text(40,2140,'P3.1 power assembly - terminal-level wiring',30,True)
    text(40,2100,'Generated from hardware/design.json. Equal net labels mean electrical connection. NC_* terminals remain unconnected.',17)
    text(40,2065,'These are defined electrical connections, not photographed wires or a validated manufacturing release.',16,col='#A33E40')
    for i,ref in enumerate(selected):
        c=components[ref];x=40+(i%3)*455;y=1760-(i//3)*330
        d.add(Rect(x,y,410,245,rx=8,ry=8,fillColor=colors.HexColor('#F1F6F8'),strokeColor=colors.HexColor('#087F83'),strokeWidth=2))
        text(x+12,y+220,ref,21,True)
        text(x+12,y+198,c['value'][:49],12)
        for k,(pin,net) in enumerate(c['pins'].items()):
            yy=y+170-k*19
            text(x+12,yy,pin,11)
            d.add(Circle(x+120,yy+4,3,fillColor=colors.HexColor('#087F83'),strokeColor=None))
            d.add(Line(x+123,yy+4,x+156,yy+4,strokeColor=colors.HexColor('#087F83'),strokeWidth=1.5))
            text(x+164,yy,net,12,False,'#9C421D')
    text(40,65,'Main/supervisor GPIO, sensors, ADC and button branches: hardware/pinmap.csv and component_connections.csv.',15)
    out=ROOT/'docs/images/terminal-wiring';renderSVG.drawToFile(d,str(out.with_suffix('.svg')))
    work=ROOT/'build';work.mkdir(exist_ok=True);pdf=work/'terminal-wiring.pdf';renderPDF.drawToFile(d,str(pdf))
    pop=os.environ.get('AGNI_PDFTOPPM') or shutil.which('pdftoppm')
    if not pop:raise RuntimeError('Install Poppler or set AGNI_PDFTOPPM')
    subprocess.run([pop,'-scale-to','3300','-png','-singlefile',str(pdf),str(out)],check=True)
    print('Terminal wiring diagram generated from',len(selected),'component records.')
if __name__=='__main__':main()
