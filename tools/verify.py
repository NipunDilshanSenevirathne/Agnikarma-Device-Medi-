"""Run public host checks and save an auditable result record. No hardware tests."""
from pathlib import Path
import subprocess,sys,json,re,time
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=[['-m','unittest','discover','-s','tests','-v'],['tools/check_repository.py'],['tools/check_cad_evidence.py'],
          ['-m','tools.simulate'],['-m','tools.deploy','main','--out','build/verification-upload'],
          ['-m','tools.deploy','supervisor','--out','build/verification-upload']]
def main():
    records=ROOT/'docs/records';records.mkdir(parents=True,exist_ok=True)
    (records/'verification.json').write_text(json.dumps({'passed':None,'status':'running','scope':'host only'})+'\n')
    results=[];log=['Host source verification. Target hardware, native EDA and clinical tests are not included.\n']
    overall=True;count=None
    for args in COMMANDS:
        start=time.monotonic();p=subprocess.run([sys.executable]+args,cwd=ROOT,capture_output=True,text=True)
        output=(p.stdout+p.stderr).replace(str(ROOT),'<repo>').replace(str(ROOT).replace('\\','/'),'<repo>')
        results.append({'command':'python '+' '.join(args),'exit_code':p.returncode,'seconds':round(time.monotonic()-start,4)})
        log+=['COMMAND: '+results[-1]['command'],output,'EXIT: '+str(p.returncode),'']
        if args[0]=='-m' and args[1]=='unittest':
            match=re.search(r'Ran (\d+) tests',output);count=int(match.group(1)) if match else None
        if p.returncode:overall=False;break
    version=(ROOT/'VERSION').read_text().strip()
    result={'version':version,'scope':'CPython host / simulated hardware adapters','passed':overall,
            'test_methods':count,'commands':results,'not_performed':['RP2040 target execution','rerun of native KiCad/OpenSCAD tools by this host command','manufactured hardware tests','medical validation']}
    (records/'host-checks.txt').write_text('\n'.join(log),encoding='utf-8')
    (records/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(('PASS' if overall else 'FAIL')+': '+str(count)+' host test methods; '+str(len(results))+' commands. See docs/records.')
    if not overall:raise SystemExit(1)
if __name__=='__main__':main()
