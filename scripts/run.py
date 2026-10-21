"""Development command runner: bounded, redirected, and windowless on Windows."""
import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')

ROOT = pathlib.Path(__file__).resolve().parents[1]

def run(args, *, timeout=300, cwd=ROOT, env=None, check=True, input=None):
    argv=[str(a) for a in args]
    resolved=shutil.which(argv[0])
    if resolved:argv[0]=str(pathlib.Path(resolved).resolve())
    elif not pathlib.Path(argv[0]).is_absolute():argv[0]=str((pathlib.Path(cwd)/argv[0]).resolve())
    result = subprocess.run(
        argv, cwd=cwd, env=env, input=input,
        stdin=subprocess.DEVNULL if input is None else None,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        timeout=timeout, check=False,
    )
    if check and result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {args[0]}\n{result.stdout.decode('utf-8', 'replace')[-16000:]}")
    return result

if __name__ == "__main__":
    result = run(sys.argv[1:], timeout=600, check=False)
    sys.stdout.buffer.write(result.stdout)
    sys.exit(result.returncode)
