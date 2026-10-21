"""Record the one unpatched upstream dev-tool advisory; reject new advisories."""
import json
import os
import sys
from run import ROOT,run

result=run([sys.executable,ROOT/'scripts/npm.py','audit','--json'],check=False)
data=json.loads(result.stdout)
advisories={entry['url'].rsplit('/',1)[-1] for v in data.get('vulnerabilities',{}).values() for entry in v.get('via',[]) if isinstance(entry,dict)}
known={'GHSA-86w9-cpqp-85rv'}
if advisories-known:raise SystemExit('New build-tool advisories require review: '+str(sorted(advisories-known)))
prod=run([sys.executable,ROOT/'scripts/npm.py','audit','--omit=dev','--json'])
if json.loads(prod.stdout)['metadata']['vulnerabilities']['total']:raise SystemExit('Production dependency advisory')
out=ROOT/'.local';out.mkdir(exist_ok=True)
(out/'npm-audit.json').write_text(json.dumps(data,indent=2)+'\n')
print('Production npm advisories: 0. Reviewed development-only advisory IDs:',', '.join(sorted(advisories)) or 'none')
env=os.environ.copy()
env['GOBIN']=str(ROOT/'.tools/go-tools')
env['PATH']=str(ROOT/'.tools/go/bin')+os.pathsep+env['PATH']
result=run([ROOT/'.tools/go/bin/go.exe','install','golang.org/x/vuln/cmd/govulncheck@v1.9.0'],env=env)
result=run([ROOT/'.tools/go-tools/govulncheck.exe','./cmd/...','./internal/...'],env=env)
print(result.stdout.decode('utf-8','replace').strip())
