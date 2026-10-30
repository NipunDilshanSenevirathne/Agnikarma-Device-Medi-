"""Generate the P3R1 low-current Pico breakout carrier and matched schematic.

No heater power, battery voltage, branch resistors or power switch is on this PCB.
Native KiCad checks are a separate required step, see tools/native_cad.py.
"""
from pathlib import Path
import csv,json,re,uuid

ROOT=Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
OUT=ROOT/'hardware/kicad'
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'agni-carrier-p3r1/'+s))
def write(name,text):
    (OUT/name).write_text(text+'\n',encoding='utf-8')

def main():
    rows=list(csv.DictReader((ROOT/'hardware/pinmap.csv').open()))
    ground=(3,8,13,18,23,28,33,38)
    maps={role:{int(r['Physical_header_pin']):r['Net'] for r in rows if r['Controller']==role} for role in ('MAIN','SUP')}
    for role,mp in maps.items():
        mp.update({n:'GND' for n in ground});mp.update({39:'5V',36:'3V3_'+role})
    net_set={n for mp in maps.values() for n in mp.values()}
    for idx,role in enumerate(('MAIN','SUP')):
        for pin in range(1,41):
            if pin not in maps[role]:
                net_set.add(f'unconnected-(A{idx+1}-NC-Pad{pin})')
                jref=f'J{idx*2+(1 if pin<=20 else 2)}';jpin=pin if pin<=20 else 41-pin
                net_set.add(f'unconnected-({jref}-NC-Pad{jpin})')
    nets=sorted(net_set)
    ids={n:i+1 for i,n in enumerate(nets)}
    pcb=['(kicad_pcb (version 20240108) (generator "pcbnew") (general (thickness 1.6)) (paper "A4")',
      '(layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "user.drawings") (44 "Edge.Cuts" user) (49 "F.Fab" user) (47 "F.CrtYd" user))',
      '(setup (pad_to_mask_clearance 0)) (net 0 "")']
    pcb += [f'(net {i} "{n if n.startswith("unconnected-") else "/"+n}")' for n,i in ids.items()]
    pcb.append('(gr_rect (start 0 0) (end 160 100) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))')
    components=[];terminal=[]
    def net(n):return f'(net {ids[n]} "{n if n.startswith("unconnected-") else "/"+n}")' if n else ''
    def track(a,b,n,layer='F.Cu',width=.35):
        pcb.append(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width {width}) (layer "{layer}") (net {ids[n]}) (uuid "{uid(str((a,b,n,layer)))}"))')
    def poly(points,n,layer='B.Cu',width=.6):
        for a,b in zip(points,points[1:]):track(a,b,n,layer,width)
    def footprint(ref,value,x,y,pads,rect):
        components.append({'ref':ref,'value':value,'pins':{str(p[0]):p[3] for p in pads}})
        body=[f'(footprint "AGNI:{value}" (layer "F.Cu") (at {x} {y}) (attr through_hole) (uuid "{uid(ref)}")',
         f'(fp_text reference "{ref}" (at 0 -3.2) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
         f'(path "/{uid("schematic")}/{uid("sch"+ref)}")',
         f'(fp_text value "{value}" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
         f'(fp_rect (start {rect[0]} {rect[1]}) (end {rect[2]} {rect[3]}) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))',
         f'(fp_rect (start {rect[0]-.5} {rect[1]-.5}) (end {rect[2]+.5} {rect[3]+.5}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))']
        for number,px,py,n in pads:
            diameter,drill=(2.5,1.3) if ref=='J5' else (1.7,1)
            padnet=n or f'unconnected-({ref}-NC-Pad{number})'
            body.append(f'(pad "{number}" thru_hole {"rect" if number==1 else "circle"} (at {px} {py:.3f}) (size {diameter} {diameter}) (drill {drill}) (layers "*.Cu" "*.Mask") {net(padnet)})')
        body.append(')');pcb.extend(body)
        lib=OUT/'AGNI.pretty';lib.mkdir(exist_ok=True)
        fp='\n'.join(body).replace(f'(footprint "AGNI:{value}"',f'(footprint "{value}" (version 20240108) (generator "pcbnew")')
        fp=fp.replace(f'(at {x} {y}) (attr','(attr',1)
        fp=re.sub(r'\(net \d+ "[^"]+"\)','',fp)
        fp=re.sub(r'\(path "[^"]+"\)','',fp)
        (lib/(value+'.kicad_mod')).write_text(fp+'\n')
    for idx,(role,x) in enumerate([('MAIN',35),('SUP',105)]):
        mp=maps[role];ref=f'A{idx+1}'
        pp=[(n,0 if n<=20 else 17.78,(n-1)*2.54 if n<=20 else (40-n)*2.54,mp.get(n)) for n in range(1,41)]
        footprint(ref,'Pico_2x20_17.78mm',x,20,pp,(-1.5,-1.5,19.28,49.76))
        for side,cx in [('L',x-10),('R',x+27.78)]:
            ref=f'J{idx*2+(1 if side=="L" else 2)}'
            pins=[j if side=='L' else 41-j for j in range(1,21)]
            pads=[(j,0,(j-1)*2.54,mp.get(pin)) for j,pin in enumerate(pins,1)]
            footprint(ref,'Breakout_1x20_P2.54',cx,20,pads,(-1.3,-1.3,1.3,49.56))
            for j,pin in enumerate(pins,1):
                n=mp.get(pin)
                if n:
                    py=20+(j-1)*2.54;px=x if side=='L' else x+17.78
                    track((px,py),(cx,py),n,width=.6 if n in ('GND','5V') else .35)
                terminal.append({'Connector':ref,'Pin':j,'Pico':role,'Pico_header_pin':pin,'Net':n or 'NC','Note':'No pack/heater current; unused pad isolated' if not n else '3.3V GPIO unless supply/ground'})
        for py in (25.08,37.78,50.48,63.18):poly([(x,py),(x+17.78,py)],'GND')
        poly([(x+8.89,25.08),(x+8.89,76)],'GND')
        poly([(x+17.78,22.54),(x+21,22.54),(x+21,12.7)],'5V')
    footprint('J5','Power_1x02_P5.08',70,84,[(1,0,0,'GND'),(2,5.08,0,'5V')],(-2.54,-4.9,7.62,4.9))
    poly([(43.89,76),(113.89,76)],'GND');poly([(70,76),(70,84)],'GND')
    poly([(56,12.7),(138,12.7),(138,84),(75.08,84)],'5V')
    for i,(x,y) in enumerate([(5,5),(155,5),(5,95),(155,95)],1):
        fp=f'(footprint "AGNI:MountingHole_3.2mm" (layer "F.Cu") (at {x} {y}) (attr board_only exclude_from_pos_files exclude_from_bom) (uuid "{uid("H"+str(i))}") (fp_text reference "H{i}" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15)))) (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask")))'
        pcb.append(fp)
        fp=fp.replace('(footprint "AGNI:MountingHole_3.2mm"','(footprint "MountingHole_3.2mm" (version 20240108) (generator "pcbnew")').replace(f'(at {x} {y}) (attr','(attr',1)
        (OUT/'AGNI.pretty/MountingHole_3.2mm.kicad_mod').write_text(fp+'\n')
    for text,x,y,size in [('AGNI P3R1  LOW CURRENT CARRIER',80,5,1.2),('MAIN',44,74,1),('SUPERVISOR',114,74,1),('J5: 1 GND | 2 REGULATED 5V',83,91,1),('NO PACK VOLTAGE / NO HEATER CURRENT',80,97,1),('1',22,20,.8),('1',66,20,.8),('1',92,20,.8),('1',136,20,.8)]:
        pcb.append(f'(gr_text "{text}" (at {x} {y}) (layer "F.SilkS") (effects (font (size {size} {size}) (thickness 0.15))))')
    pcb.append(')');write('agni-controller-carrier.kicad_pcb','\n'.join(pcb))
    with (ROOT/'hardware/carrier_connectors.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(terminal[0]));w.writeheader();w.writerows(terminal)
    root=uid('schematic');libs=[];inst=[];labels=[]
    for i,c in enumerate(components):
        ref=c['ref'];name='Carrier_'+ref;pins=list(c['pins'].items());h=(len(pins)+1)*2.54
        pt=[]
        for j,(number,n) in enumerate(pins):
            pt.append(f'(pin passive line (at 40.64 {-2.54*(j+1):.3f} 180) (length 5.08) (name "{n or "NC"}" (effects (font (size 0.8 0.8)))) (number "{number}" (effects (font (size 0.8 0.8)))))')
        libs.append(f'(symbol "AGNI:{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5 0) (effects (font (size 1 1)))) (property "Value" "{ref}" (at 0 2 0) (effects (font (size 1 1)))) (symbol "{name}_0_1" (rectangle (start 0 0) (end 35.56 {-h:.3f}) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{name}_1_1" {"".join(pt)}))')
        x=25.4+(i%4)*101.6;y=38.1+(i//4)*127
        inst.append(f'(symbol (lib_id "AGNI:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid("sch"+ref)}") (property "Reference" "{ref}" (at {x+10} {y-5} 0) (effects (font (size 1.2 1.2)))) (property "Value" "{c["value"]}" (at {x+15} {y-2} 0) (effects (font (size 0.8 0.8)))) (property "Footprint" "AGNI:{c["value"]}" (at {x} {y} 0) (effects (font (size 1 1)) hide)) {"".join(f"(pin \"{n}\" (uuid \"{uid(ref+str(n))}\"))" for n,_ in pins)} (instances (project "agni-controller-carrier" (path "/{root}" (reference "{ref}") (unit 1)))))')
        for j,(_,n) in enumerate(pins):
            yy=y+2.54*(j+1)
            if n is None:
                labels.append(f'(no_connect (at {x+40.64} {yy:.3f}) (uuid "{uid(ref+"NC"+str(j))}"))')
                continue
            labels.append(f'(wire (pts (xy {x+40.64} {yy:.3f}) (xy {x+45.72} {yy:.3f})) (stroke (width 0) (type default)) (uuid "{uid(ref+"wire"+str(j))}")) (label "{n}" (at {x+45.72} {yy:.3f} 0) (effects (font (size 0.8 0.8)) (justify left bottom)) (uuid "{uid(ref+"label"+str(j))}"))')
    write('agni-controller-carrier.kicad_sch',f'(kicad_sch (version 20231120) (generator "eeschema") (uuid "{root}") (paper "A3") (title_block (title "AGNI P3R1 low-current breakout carrier") (date "2026-10-31") (rev "0.5.0")) (lib_symbols {"".join(libs)}) {"".join(inst)} {"".join(labels)})')
    write('fp-lib-table','(fp_lib_table (version 7) (lib (name "AGNI") (type "KiCad") (uri "${KIPRJMOD}/AGNI.pretty") (options "") (descr "Project-local P3R1 prototype footprints")))')
    from tools.eda_library import generate as library_generate
    library_generate()
    write('agni-controller-carrier.kicad_pro',json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.25,'min_through_hole_diameter':.3,'min_hole_clearance':.25,'min_copper_edge_clearance':.5}}},'meta':{'filename':'agni-controller-carrier.kicad_pro','version':1},'net_settings':{'classes':[{'name':'Default','description':'Low current breakout only','clearance':.2,'track_width':.35,'via_diameter':.8,'via_drill':.4,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25}],'meta':{'version':4}}},indent=2))
    print('Generated routed carrier, matched passive schematic and connector schedule.')
if __name__=='__main__':main()
