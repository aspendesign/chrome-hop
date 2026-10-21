"""Run npm's JS entry point directly; never create a cmd.exe wrapper window."""
import pathlib
import shutil
import sys
from run import run

node=pathlib.Path(shutil.which('node') or '')
entry=node.parent/'node_modules/npm/bin/npm-cli.js'
if not entry.exists():raise SystemExit('Could not locate npm next to Node.js')
result=run([node,entry,*sys.argv[1:]],check=False,timeout=600)
sys.stdout.buffer.write(result.stdout)
raise SystemExit(result.returncode)
