import json
import os
import re
from run import ROOT

version=json.loads((ROOT/'extension/manifest.json').read_text(encoding='utf-8'))['version']
tag=os.environ.get('GITHUB_REF_NAME','')
if not re.fullmatch(r'v\d+\.\d+\.\d+',tag) or tag!='v'+version:raise SystemExit('Release tag must match manifest version exactly.')
if json.loads((ROOT/'package.json').read_text())['version']!=version:raise SystemExit('Package version mismatch')
print('Release tag matches source version:',tag)
