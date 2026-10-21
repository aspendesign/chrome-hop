"""Fetch pinned official build tools locally, verifying published SHA-256."""
import hashlib
import json
import pathlib
import urllib.request
import zipfile
from run import ROOT, run

TOOLS = ROOT / '.tools'
TOOLS.mkdir(exist_ok=True)

def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent':'chrome-hop-build'})
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)

def download(url, path, expected):
    if not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent':'chrome-hop-build'})
        with urllib.request.urlopen(req, timeout=120) as res, path.open('wb') as out:
            while chunk := res.read(1024*1024): out.write(chunk)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected: raise RuntimeError('Build tool checksum mismatch: '+path.name)
    return actual

if __name__ == '__main__':
    # Pins were checked against official Go metadata and the official GitHub
    # Inno release. Direct asset URLs avoid shared-runner API rate limits.
    archive = TOOLS / 'go1.27.3.windows-amd64.zip'
    expected_go='f26081f438319757f8a1b46d7d0b2c5ec7583d4038e485e0aa725cfde7885fff'
    go_hash = download('https://go.dev/dl/go1.27.3.windows-amd64.zip', archive, expected_go)
    if not (TOOLS/'go/bin/go.exe').exists():
        with zipfile.ZipFile(archive) as z: z.extractall(TOOLS)
    print(run([TOOLS/'go/bin/go.exe','version']).stdout.decode().strip())
    expected='0362a383ed217d4c4239b5933866dd96d3eb2102737da92f80f6057a4b40df2f'
    setup = TOOLS / 'innosetup-7.1.0-x64.exe'
    inno_hash = download('https://github.com/jrsoftware/issrc/releases/download/is-7_1_0/innosetup-7.1.0-x64.exe', setup, expected)
    target = TOOLS/'inno'
    if not (target/'ISCC.exe').exists():
        run([setup,'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-', '/DIR='+str(target)], timeout=180)
    print('Verified official Inno Setup 7.1.0 (SHA-256 pinned).')
    (TOOLS/'receipts.json').write_text(json.dumps({'go': {'version':'1.27.3','sha256':go_hash},'inno':{'version':'7.1.0','sha256':inno_hash}}, indent=2))
