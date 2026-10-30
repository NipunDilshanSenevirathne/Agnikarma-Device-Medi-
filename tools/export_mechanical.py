"""Compile real OpenSCAD meshes and record geometric checks; no physical fit claim."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.text_format import canonicalize

def vertices(path):
    # OpenSCAD 2021 CLI's ASCII STL, deliberately fail if the format changes.
    text=path.read_text(encoding='ascii')
    return [tuple(map(float,m)) for m in re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',text)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--openscad',required=True);ap.add_argument('--render',action='store_true');a=ap.parse_args()
    out=ROOT/'mechanical/exports';out.mkdir(exist_ok=True)
    canonicalize((ROOT/'mechanical').glob('*'))
    version=subprocess.run([a.openscad,'--version'],capture_output=True,text=True,check=True)
    tasks=[('controller-base','bench_enclosure.scad','part="base"'),('controller-lid','bench_enclosure.scad','part="lid"'),('harness-clamp','bench_enclosure.scad','part="clamp"')]
    tasks += [(f'T{i:02d}-shape','tips.scad',f'tip_id={i}') for i in range(1,6)]
    results=[]
    for name,source,setting in tasks:
        path=out/(name+'.stl')
        r=subprocess.run([a.openscad,'-D',setting,'-o',str(path),str(ROOT/'mechanical'/source)],capture_output=True,text=True)
        log=(r.stdout+r.stderr).strip()
        if r.returncode or 'ERROR:' in log or 'WARNING:' in log or not path.exists():raise RuntimeError(name+'\n'+log)
        canonicalize([path])
        vv=vertices(path);assert len(vv)>=12 and len(vv)%3==0,name
        low=[min(v[j] for v in vv) for j in range(3)];high=[max(v[j] for v in vv) for j in range(3)]
        # Verify one watertight closed triangle surface without relying only on CLI status.
        edges={}
        for i in range(0,len(vv),3):
            tri=vv[i:i+3]
            for j in range(3):
                edge=tuple(sorted((tri[j],tri[(j+1)%3])));edges[edge]=edges.get(edge,0)+1
        assert all(count==2 for count in edges.values()),name+' is not a closed 2-manifold triangle surface'
        row={'part':name,'source':source,'define':setting,'triangles':len(vv)//3,'bounds_min_mm':low,'bounds_max_mm':high,'closed_edge_count_check':'PASS','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_log':log}
        results.append(row);print(name, 'PASS',len(vv)//3,'triangles',low,high,flush=True)
    p=json.loads((ROOT/'mechanical/assembly_parameters.json').read_text())
    ox,oy,_=p['carrier_origin_in_housing']
    assert [[x+ox,y+oy] for x,y in p['carrier_mounts_in_board_coordinates']]==p['housing_carrier_mounts']
    assert results[0]['bounds_max_mm']==p['housing_outer']
    if a.render:
        for source,name in [('bench_enclosure.scad','controller-assembly-native.png'),('tips.scad','tip-family-native.png')]:
            r=subprocess.run([a.openscad,'--render','--imgsize=1600,1000','--viewall','--autocenter','--projection=o','-o',str(ROOT/'docs/images'/name),str(ROOT/'mechanical'/source)],capture_output=True,text=True)
            if r.returncode or not (ROOT/'docs/images'/name).exists():raise RuntimeError(r.stdout+r.stderr)
            print(name,'native render exported',flush=True)
    sources=[ROOT/'mechanical'/name for name in ('bench_enclosure.scad','tips.scad','assembly_parameters.json')]
    record={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':(version.stdout+version.stderr).strip(),'scope':'Native OpenSCAD compilation, closed mesh edge incidence, bounds and mounting-coordinate arithmetic. No physical fit, thermal, material or medical evidence.','source_hashes':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'parts':results}
    (ROOT/'docs/records/mechanical-checks.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
if __name__=='__main__':main()
