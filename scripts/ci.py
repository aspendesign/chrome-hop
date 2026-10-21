"""Single fail-fast CI entry point; native command failures cannot be masked."""
import os
import sys
from run import ROOT,run

def step(args,**kwargs):
    print('Running:', ' '.join(str(a) for a in args),flush=True)
    result=run(args,**kwargs)
    print(result.stdout.decode('utf-8','replace'),end='',flush=True)

if '--release' in sys.argv:step([sys.executable,ROOT/'scripts/check_tag.py'])
step([sys.executable,ROOT/'scripts/bootstrap.py'],timeout=600)
step([sys.executable,ROOT/'scripts/npm.py','ci','--ignore-scripts','--no-fund','--no-audit'],timeout=600)
step(['node','--test','--test-isolation=none',ROOT/'tests/extension.test.cjs',ROOT/'tests/help.test.cjs'])
step(['node',ROOT/'node_modules/web-ext/bin/web-ext.js','lint','--source-dir',ROOT/'extension','--no-config-discovery','--warnings-as-errors'])
step([sys.executable,ROOT/'scripts/security_check.py'])
go=ROOT/'.tools/go/bin/go.exe'
step([go,'test','./cmd/...','./internal/...','-cover'])
step([go,'vet','./cmd/...','./internal/...'])
step([go,'test','./internal/host','-run=^$','-fuzz=FuzzMessage','-fuzztime=20s','-parallel=2'])
step([sys.executable,ROOT/'scripts/audit_tools.py'])
step([sys.executable,ROOT/'scripts/build.py'])
step([sys.executable,ROOT/'tests/windows_install.py'])
step([sys.executable,ROOT/'scripts/package_submission.py'])
