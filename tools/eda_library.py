"""Extract embedded AGNI symbols into a matching portable project library."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def form_end(text,start):
    level=0;quoted=False;escape=False
    for i in range(start,len(text)):
        c=text[i]
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='(':level+=1
        elif c==')':
            level-=1
            if level==0:return i+1
    raise ValueError('Unclosed S-expression')

def generate():
    folder=ROOT/'hardware/kicad';symbols={}
    for sch in sorted(folder.glob('*.kicad_sch')):
        t=sch.read_text();start=t.index('(lib_symbols');end=form_end(t,start)
        pos=start+len('(lib_symbols')
        while pos<end-1:
            while pos<end and t[pos].isspace():pos+=1
            if pos>=end-1:break
            stop=form_end(t,pos);s=t[pos:stop]
            match=re.match(r'\(symbol "AGNI:([^"\n]+)"',s)
            if not match:raise ValueError('Unexpected library symbol '+s[:100])
            name=match.group(1);s=s.replace('"AGNI:'+name+'"','"'+name+'"',1)
            if name in symbols and symbols[name]!=s:raise ValueError('Conflicting symbol '+name)
            symbols[name]=s;pos=stop
    (folder/'AGNI.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+'\n'.join(symbols.values())+'\n)\n')
    (folder/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "AGNI") (type "KiCad") (uri "${KIPRJMOD}/AGNI.kicad_sym") (options "") (descr "Project-local generic passive terminal symbols")))\n')
if __name__=='__main__':generate()
