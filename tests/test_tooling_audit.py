"""Exercise actual deployment/packaging scripts on isolated workspace fixtures."""
import unittest,tempfile,subprocess,sys,json,zipfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ToolingAuditTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'build/tool-tests';base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=str(base));self.work=Path(self.tmp.name).resolve()
        self.work.relative_to(base.resolve())
    def tearDown(self):self.tmp.cleanup()
    def command(self,*args):
        r=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr);return r
    def test_deploy_preserves_existing_provisioning_unless_reset(self):
        self.command(ROOT/'tools/deploy.py','main','--out',self.work)
        p=self.work/'main/provision.json';cfg=json.loads(p.read_text());cfg['calibration_record']='RETAIN-ME';p.write_text(json.dumps(cfg))
        self.command(ROOT/'tools/deploy.py','main','--out',self.work)
        self.assertEqual(json.loads(p.read_text())['calibration_record'],'RETAIN-ME')
        self.command(ROOT/'tools/deploy.py','main','--out',self.work,'--reset-provision')
        self.assertFalse(json.loads(p.read_text())['bench_enabled'])
    def test_package_has_no_duplicate_manifest_or_private_files(self):
        fixture=self.work/'repo';(fixture/'tools').mkdir(parents=True)
        shutil.copy2(ROOT/'tools/package.py',fixture/'tools/package.py')
        for name,body in [('README.md','fixture'),('SOURCE_MANIFEST.json','old'),('provision.json','private'),('.env','private'),('signing.key','private'),('board.kicad_prl','local CAD preference')]:
            (fixture/name).write_text(body)
        archive=self.work/'out.zip';self.command(fixture/'tools/package.py','--out',archive)
        with zipfile.ZipFile(archive) as z:
            names=z.namelist();self.assertEqual(len(names),len(set(names)))
            self.assertEqual(names.count('agni-karma/SOURCE_MANIFEST.json'),1)
            self.assertFalse(any(x.endswith(('provision.json','.env','signing.key','.kicad_prl')) for x in names))
