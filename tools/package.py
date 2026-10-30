"""Create a distributable source ZIP with a SHA-256 content manifest."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'dist/agni-karma-v0.5.0.zip');a=ap.parse_args()
    excluded={'.git','__pycache__','build','dist','.venv'}
    files=[]
    for p in sorted(ROOT.rglob('*')):
        relative=p.relative_to(ROOT)
        if not p.is_file() or any(q in excluded or q.endswith('-backups') for q in relative.parts):continue
        if p.name in ('SOURCE_MANIFEST.json','provision.json') or p.name.startswith(('.env','secrets.')):continue
        if p.suffix.lower() in ('.pyc','.zip','.pem','.key','.p12','.pfx','.kicad_prl','.kicad_pcb-bak','.lck'):continue
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Refusing external/symlink source: '+str(relative))
        files.append(p)
    records=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,'agni-karma/'+str(p.relative_to(ROOT)).replace('\\','/'))
        z.writestr('agni-karma/SOURCE_MANIFEST.json',json.dumps(records,indent=2)+'\n')
    with zipfile.ZipFile(a.out) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist())), 'Duplicate archive paths'
        for row in records:
            assert hashlib.sha256(z.read('agni-karma/'+row['path'])).hexdigest()==row['sha256']
    print('Verified',len(records),'source files + manifest:',a.out)
if __name__=='__main__':main()
