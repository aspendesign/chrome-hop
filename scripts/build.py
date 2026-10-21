"""Reproducible extension ZIP and Windows helper; pinned Inno Setup packaging."""
import hashlib
import json
import os
import pathlib
import shutil
import zipfile
from run import ROOT, run

DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True)
VERSION=json.loads((ROOT/'extension/manifest.json').read_text(encoding='utf-8'))['version']

def deterministic_zip(target, entries):
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,path in sorted(entries):
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_STORED
            info.external_attr=0o100644 << 16
            archive.writestr(info,path.read_bytes())

def checksums():
    rows=[]
    for path in sorted(DIST.iterdir()):
        if path.is_file() and path.name not in ('SHA256SUMS.txt',):
            rows.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}')
    (DIST/'SHA256SUMS.txt').write_text('\n'.join(rows)+'\n',encoding='ascii')

def main():
    local=ROOT/'.tools/go/bin/go.exe'
    go=local if local.exists() else shutil.which('go')
    if not go:raise RuntimeError('Go 1.27.3 is required')
    actual=run([go,'version']).stdout.decode()
    if 'go1.27.3 ' not in actual: raise RuntimeError('Expected pinned Go 1.27.3')
    env=os.environ.copy();env.update(GOOS='windows',GOARCH='amd64',GOAMD64='v1',CGO_ENABLED='0',GOTOOLCHAIN='local')
    staging=ROOT/'.local/build';staging.mkdir(parents=True,exist_ok=True)
    helper=staging/'chrome-hop.exe'
    command=[go,'build','-trimpath','-buildvcs=false','-ldflags=-s -w -buildid= -H=windowsgui','-o',helper,'./cmd/chrome-hop']
    run(command,env=env)
    first=helper.read_bytes()
    run(command,env=env)
    if first!=helper.read_bytes():raise RuntimeError('Helper reproducibility failed')
    shutil.copy2(helper,DIST/f'chrome-hop-{VERSION}-windows-x64.exe')
    extension=ROOT/'extension'
    entries=[(str(p.relative_to(extension)).replace('\\','/'),p) for p in extension.rglob('*') if p.is_file()]
    target=DIST/f'chrome-hop-{VERSION}-amo-submission.zip'
    deterministic_zip(target,entries)
    first=target.read_bytes();deterministic_zip(target,entries)
    if first!=target.read_bytes():raise RuntimeError('Extension reproducibility failed')
    iscc=ROOT/'.tools/inno/ISCC.exe'
    if not iscc.exists():
        candidate=os.environ.get('ISCC') or shutil.which('iscc')
        if not candidate:raise RuntimeError('Pinned Inno Setup 7.1.0 is required')
        iscc=pathlib.Path(candidate)
    output=run([iscc,'/Qp','/DAppVersion='+VERSION,ROOT/'installer/chrome-hop.iss']).stdout.decode(errors='replace')
    installer=DIST/f'ChromeHop-Setup-{VERSION}-windows-x64.exe'
    first=installer.read_bytes()
    run([iscc,'/Qp','/DAppVersion='+VERSION,ROOT/'installer/chrome-hop.iss'])
    installer_reproducible=first==installer.read_bytes()
    # Stable filename supports a permanent, direct latest-release download link.
    shutil.copyfile(installer,DIST/'ChromeHop-Setup-windows-x64.exe')
    metadata={'version':VERSION,'go':'1.27.3','web-ext':'10.8.0','inno':'7.1.0',
      'extension_id':'chrome-hop@aspendesign.github.io','host':'io.github.aspendesign.chrome_hop',
      'helper_reproducible':True,'extension_reproducible':True,
      'installer_reproducible':installer_reproducible,
      'authenticode_signed':False,'amo_signed':False,
      'runtime_dependencies':[]}
    (DIST/'BUILD-INFO.json').write_text(json.dumps(metadata,indent=2)+'\n')
    checksums()
    print(json.dumps(metadata,indent=2))
    print(output[-2500:])
    if not installer_reproducible:raise RuntimeError('Installer reproducibility failed')

if __name__=='__main__':main()
