"""Create board-specific MicroPython upload folders. No device flashing is implicit."""
import argparse,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("role",choices=["main","supervisor"]);ap.add_argument("--out",type=Path,default=ROOT/"build");ap.add_argument("--reset-provision",action="store_true",help="Explicitly replace local commissioning record with disabled defaults");a=ap.parse_args()
    dest=a.out/a.role;dest.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/"firmware",dest/"firmware",dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","boot_*.py","provision.example.json"))
    shutil.copy2(ROOT/"firmware"/("boot_main.py" if a.role=="main" else "boot_supervisor.py"),dest/"main.py")
    record=dest/"provision.json"
    if not record.exists() or a.reset_provision:
        cfg=json.loads((ROOT/"firmware/provision.example.json").read_text());cfg["role"]=a.role
        record.write_text(json.dumps(cfg,indent=2)+"\n")
        print("Prepared",dest,"with disabled defaults. See docs/firmware.md.")
    else:
        print("Prepared",dest,"and preserved existing provision.json. Review that record before uploading.")
if __name__=="__main__":main()
