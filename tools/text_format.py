"""Keep authored/CAD text byte-identical across Windows/Linux Git checkouts."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS={'.py','.md','.json','.toml','.csv','.txt','.yml','.yaml','.svg','.xml','.scad','.stl','.step','.sha256',
 '.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod','.gtl','.gbl','.gto','.gts','.gbs','.gm1','.drl','.gbrjob'}
TEXT_NAMES={'VERSION','LICENSE','sym-lib-table','fp-lib-table','.gitattributes','.gitignore','.editorconfig'}

def canonicalize(paths):
    count=0
    for p in paths:
        if not p.is_file() or p.suffix not in TEXT_EXTENSIONS and p.name not in TEXT_NAMES:continue
        data=p.read_bytes()
        if b'\x00' in data:raise ValueError('Expected text, found binary: '+str(p))
        canonical=data.replace(b'\r\n',b'\n')
        if canonical!=data:p.write_bytes(canonical);count+=1
    return count

def main():
    paths=[p for p in ROOT.rglob('*') if not any(part in {'build','dist','.git','__pycache__','.venv'} for part in p.relative_to(ROOT).parts)]
    print('Canonical LF normalization:',canonicalize(paths),'text files changed.')
if __name__=='__main__':main()
