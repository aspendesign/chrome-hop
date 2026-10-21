"""Real per-user installer/repair/reinstall/uninstall, preserving prior installs.

Runs only on Windows and refuses an existing Chrome Hop registration or install.
The test uses a task-owned path with spaces and Unicode, verifies exact HKCU
readback, and leaves no helper installed when finished.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import time
import winreg

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run import ROOT, run
from build import VERSION

HOST='io.github.aspendesign.chrome_hop'
ID='chrome-hop@aspendesign.github.io'
KEY='Software\\Mozilla\\NativeMessagingHosts\\'+HOST
UNINSTALL='Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{811C254E-68FA-4C2D-B271-91EC8EA8731F}_is1'
TARGET=ROOT/'.local'/'Installer test é with spaces'

def registry(key=KEY, hive=winreg.HKEY_CURRENT_USER):
    try:
        with winreg.OpenKey(hive,key,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as h:return winreg.QueryValueEx(h,'')[0]
    except FileNotFoundError:return None

def installed():
    assert registry()==str(TARGET/(HOST+'.json')), 'Host registration differs'
    manifest=json.loads((TARGET/(HOST+'.json')).read_text(encoding='utf-8'))
    assert manifest=={'name':HOST,'description':'Chrome Hop: open one HTTP(S) URL in Google Chrome','path':str(TARGET/'chrome-hop.exe'),'type':'stdio','allowed_extensions':[ID]}, 'Manifest differs'
    assert (TARGET/'unins000.exe').is_file(), 'Uninstaller missing'
    assert (TARGET/'chrome-hop.exe').read_bytes()==(ROOT/f'dist/chrome-hop-{VERSION}-windows-x64.exe').read_bytes(), 'Installed binary differs'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,UNINSTALL) as h:
        assert 'Chrome Hop' in winreg.QueryValueEx(h,'DisplayName')[0]
    return manifest

def native_message(exe, body, args=None, timeout=15):
    result=run([exe,*(args or [str(TARGET/(HOST+'.json')),ID])],input=struct.pack('<I',len(body))+body,timeout=timeout)
    data=result.stdout
    assert len(data)>=4 and struct.unpack('<I',data[:4])[0]==len(data)-4, 'Invalid stdout framing or extra output'
    return json.loads(data[4:])

def main():
    if os.name!='nt':raise SystemExit('Windows only')
    if registry() is not None or TARGET.exists() or (Path(os.environ['LOCALAPPDATA'])/'Programs/Chrome Hop').exists():
        raise SystemExit('An existing install/registration or prior test directory is present; refusing to overwrite it.')
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    setup=ROOT/f'dist/ChromeHop-Setup-{VERSION}-windows-x64.exe'
    results={'elevated':bool(ctypes.windll.shell32.IsUserAnAdmin()),'installation_mode':'per-user','phases':[]}
    try:
        for phase in ['install','repair']:
            run([setup,'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-', '/DIR='+str(TARGET)])
            installed();results['phases'].append(phase)
        # Actual upgrade through the identical AppId, using a test-only version.
        upgrade_dir=ROOT/'.local/upgrade';upgrade_dir.mkdir(exist_ok=True)
        parts=VERSION.split('.');upgrade_version='.'.join([*parts[:2],str(int(parts[2])+1)])
        run([ROOT/'.tools/inno/ISCC.exe','/Qp','/DAppVersion='+upgrade_version,'/O'+str(upgrade_dir),'/FChromeHop-Upgrade-Fixture',ROOT/'installer/chrome-hop.iss'])
        run([upgrade_dir/'ChromeHop-Upgrade-Fixture.exe','/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-','/DIR='+str(TARGET)])
        installed()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,UNINSTALL) as h:assert winreg.QueryValueEx(h,'DisplayVersion')[0]==upgrade_version
        results['phases'].append('upgrade_fixture_'+upgrade_version)
        # Actual compiled executable parser/caller checks. These never open URLs.
        exe=TARGET/'chrome-hop.exe'
        assert native_message(exe,b'{"op":"run","url":"https://example.com/"}')=={'ok':False,'code':'invalid_message'}
        assert native_message(exe,b'{}',args=['manifest','another-extension@example.invalid'])=={'ok':False,'code':'unauthorized'}
        results['native_binary_rejections']=True
        for phase in ['uninstall','reinstall','final_uninstall']:
            if phase=='reinstall':
                run([setup,'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-', '/DIR='+str(TARGET)])
                installed()
            else:
                run([TARGET/'unins000.exe','/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'])
                deadline=time.monotonic()+15
                while TARGET.exists() and time.monotonic()<deadline:time.sleep(.1)
                assert not TARGET.exists(), 'Install directory remains'
                assert registry() is None, 'Host registry remains'
                try:winreg.OpenKey(winreg.HKEY_CURRENT_USER,UNINSTALL)
                except FileNotFoundError:pass
                else:raise AssertionError('Uninstall registry remains')
            results['phases'].append(phase)
        results['success']=True
    finally:
        if (TARGET/'unins000.exe').exists():run([TARGET/'unins000.exe','/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],check=False)
        (ROOT/'.local/install-receipt.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
