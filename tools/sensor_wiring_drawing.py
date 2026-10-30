"""Deterministic two-interface/four-wire sensor illustration from audited net data."""
from pathlib import Path
import json,os,shutil,subprocess
from reportlab.graphics.shapes import Drawing,Rect,Line,Circle,String,PolyLine
from reportlab.graphics import renderSVG,renderPDF
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
def main():
    parts={c['ref']:c for c in json.loads((ROOT/'hardware/design.json').read_text())['components']}
    d=Drawing(1400,1050);d.add(Rect(0,0,1400,1050,fillColor=colors.white,strokeColor=None))
    def text(x,y,s,size=15,col='#173649',bold=False):d.add(String(x,y,s,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=colors.HexColor(col)))
    def line(pts,col='#087F83'):d.add(PolyLine(pts,strokeColor=colors.HexColor(col),strokeWidth=2))
    text(40,1000,'Two separate interfaces and two four-wire Pt1000 elements',27,bold=True)
    text(40,965,'Net/terminal diagram; physical sensor lead colours and package must be verified with the supplier.',16)
    for role,ref,base in [('MAIN','A1',850),('SUP','A2',430)]:
        m=parts['RTD_'+role]['pins'];p=parts[ref]['pins'];sensor=parts['SENSOR_'+role]['pins']
        d.add(Rect(45,base-230,260,270,fillColor=colors.HexColor('#EFF5F8'),strokeColor=colors.HexColor('#087F83')))
        d.add(Rect(430,base-240,330,280,fillColor=colors.HexColor('#EFF5F8'),strokeColor=colors.HexColor('#087F83')))
        text(60,base+12,role+' PICO',20,bold=True);text(450,base+12,'MAX31865 / Pt1000 board',18,bold=True)
        pairs=[('9_GP6','SCK'),('10_GP7','SDI'),('6_GP4','SDO'),('7_GP5','CS'),('36_3V3_OUT','VIN'),('38_GND','GND')]
        for i,(pp,mp) in enumerate(pairs):
            assert p[pp]==m[mp],(role,pp,mp)
            y=base-30-i*30;text(60,y,pp,13);text(450,y,mp,13)
            line([305,y+5,430,y+5]);text(310,y+12,p[pp],10)
        text(450,base-220,'3Vo: leave unused',13,col='#A33E40')
        # Four distinct leads, joined in pairs at each end of ONE sensor element.
        for terminal,sp,y in [('F+','END_A_FORCE',base-35),('RTD+','END_A_SENSE',base-75),('RTD-','END_B_SENSE',base-155),('F-','END_B_FORCE',base-195)]:
            assert m[terminal]==sensor[sp]
            text(660,y,terminal,13);line([760,y+5,930,y+5]);text(780,y+13,sp,11)
        line([930,base-30,965,base-30,965,base-70,930,base-70])
        line([930,base-150,965,base-150,965,base-190,930,base-190])
        line([965,base-50,1010,base-50,1010,base-85])
        d.add(Rect(998,base-135,24,50,fillColor=colors.white,strokeColor=colors.HexColor('#A56C23'),strokeWidth=2))
        line([1010,base-135,1010,base-170,965,base-170])
        text(1050,base-105,'ONE Pt1000 element',15,bold=True)
        text(1050,base-130,'Two leads per end',13)
        text(60,base-280,'Do not join the MAIN and SUP 3V3_OUT nets. Grounds are common; sensors and interfaces remain separate.',14)
    text(40,60,'This drawing defines circuit connections. Sensor retention, insulation, face temperature mapping and physical wiring tests remain open.',14,col='#A33E40')
    out=ROOT/'docs/images/sensor-wiring';renderSVG.drawToFile(d,str(out.with_suffix('.svg')))
    work=ROOT/'build';work.mkdir(exist_ok=True);pdf=work/'sensor-wiring.pdf';renderPDF.drawToFile(d,str(pdf))
    pop=os.environ.get('AGNI_PDFTOPPM') or shutil.which('pdftoppm')
    if not pop:raise RuntimeError('Install Poppler or set AGNI_PDFTOPPM')
    subprocess.run([pop,'-scale-to','2300','-png','-singlefile',str(pdf),str(out)],check=True)
    print('Checked and generated two-controller/four-wire sensor diagram.')
if __name__=='__main__':main()
