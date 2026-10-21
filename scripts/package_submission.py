"""Prepare a complete reviewer/listing bundle without secrets or local state."""
import json
import zipfile
from pathlib import Path
from run import ROOT,run
from build import DIST,VERSION,deterministic_zip,checksums

def main():
    DIST.mkdir(exist_ok=True)
    # Independently package with Mozilla's tooling, then compare every entry.
    target=ROOT/'.local/web-ext';target.mkdir(parents=True,exist_ok=True)
    run(['node',ROOT/'node_modules/web-ext/bin/web-ext.js','build','--source-dir',ROOT/'extension','--artifacts-dir',target,'--filename','mozilla-package.zip','--overwrite-dest','--no-config-discovery'])
    with zipfile.ZipFile(target/'mozilla-package.zip') as mozilla,zipfile.ZipFile(DIST/f'chrome-hop-{VERSION}-amo-submission.zip') as ours:
        a={n:mozilla.read(n) for n in mozilla.namelist() if not n.endswith('/')}
        b={n:ours.read(n) for n in ours.namelist() if not n.endswith('/')}
        if a!=b:raise RuntimeError('Mozilla package/source equivalence failed')
    entries=[]
    for folder in ['publication','docs','verification','assets']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix.lower() in ['.md','.json','.png','.svg','.ico']:
                entries.append((p.relative_to(ROOT).as_posix(),p))
    for p in [ROOT/'LICENSE',ROOT/'README.md',DIST/f'chrome-hop-{VERSION}-amo-submission.zip']:
        entries.append((p.name,p))
    deterministic_zip(DIST/f'chrome-hop-{VERSION}-listing-assets.zip',entries)
    checksums()
    print('Mozilla package matches every production extension source file. Listing bundle and checksums ready.')

if __name__=='__main__':main()
