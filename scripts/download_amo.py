"""Fetch and verify one existing public release for the AMO submission job."""
import hashlib
import os
import re
import zipfile
from run import ROOT,run

tag=os.environ.get('RELEASE_TAG','')
if not re.fullmatch(r'v\d+\.\d+\.\d+',tag):raise SystemExit('Invalid release tag')
target=ROOT/'.local/amo-download';target.mkdir(parents=True,exist_ok=True)
run(['gh','release','download',tag,'--repo',os.environ.get('GITHUB_REPOSITORY','aspendesign/chrome-hop'),'--dir',target,'--pattern','*amo-submission.zip','--pattern','SHA256SUMS.txt'])
package=target/f'chrome-hop-{tag[1:]}-amo-submission.zip'
rows=(target/'SHA256SUMS.txt').read_text().splitlines()
expected=next(row.split()[0] for row in rows if row.endswith('  '+package.name))
if hashlib.sha256(package.read_bytes()).hexdigest()!=expected:raise SystemExit('Submission checksum mismatch')
with zipfile.ZipFile(package) as archive:
    for item in archive.infolist():
        path=(ROOT/'.local/amo-extension'/item.filename).resolve()
        if not path.is_relative_to((ROOT/'.local/amo-extension').resolve()):raise SystemExit('Unsafe archive path')
    archive.extractall(ROOT/'.local/amo-extension')
print('Verified release package ready for listed AMO submission:',tag)
