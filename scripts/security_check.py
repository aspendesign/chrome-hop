"""Fail CI on extra permissions, execution surfaces, unpinned actions or secrets."""
import json
import re
import sys
from pathlib import Path
from run import ROOT

def check():
    failures=[]
    def need(condition,message):
        if not condition:failures.append(message)
    manifest=json.loads((ROOT/'extension/manifest.json').read_text(encoding='utf-8'))
    need(manifest['permissions']==['activeTab','nativeMessaging','menus'],'Permission budget changed')
    need(manifest.get('optional_permissions')==['tabs'],'Bulk-only optional permission changed')
    for field in ['content_scripts','host_permissions','optional_host_permissions','externally_connectable','web_accessible_resources','commands','update_url']:
        need(field not in manifest,'Unexpected manifest capability: '+field)
    need(manifest['browser_specific_settings']['gecko']['id']=='chrome-hop@aspendesign.github.io','ID mismatch')
    need(manifest['browser_specific_settings']['gecko']['data_collection_permissions']=={'required':['browsingActivity']},'Local URL transfer disclosure missing')
    for path in (ROOT/'extension').glob('*.js'):
        text=path.read_text(encoding='utf-8')
        for pattern in [r'\beval\s*\(',r'new\s+Function\s*\(',r'\bfetch\s*\(',r'XMLHttpRequest',r'WebSocket',r'executeScript',r'console\.',r'\.onMessage',r'\.onConnect']:
            need(not re.search(pattern,text),f'Unexpected browser surface: {path.name}: {pattern}')
    background=(ROOT/'extension/background.js').read_text(encoding='utf-8')
    need(background.count('browser.tabs.query(')==1 and 'browser.tabs.query({windowId: tab.windowId})' in background,'Bulk window boundary changed')
    need('browser.permissions.request({permissions: ["tabs"]})' in background,'Bulk permission gesture missing')
    need('contexts: ["action"]' in background,'Menu escaped the toolbar context')
    native='\n'.join(p.read_text() for p in (ROOT/'internal').rglob('*.go') if not p.name.endswith('_test.go'))
    need('exec.Command(path, raw)' in native,'Direct fixed argument launch missing')
    need('CreationFlags: 0x08000000' in native,'Console suppression missing')
    for pattern in ['cmd.exe','powershell','exec.LookPath','os.Getenv','net/http','log.Print','fmt.Print']:
        need(pattern.lower() not in native.lower(),'Unexpected native capability: '+pattern)
    need('require ' not in (ROOT/'go.mod').read_text(),'Unexpected Go runtime dependency')
    installer=(ROOT/'installer/chrome-hop.iss').read_text()
    need('PrivilegesRequired=lowest' in installer,'Installer elevation changed')
    need('Root: HKCU;' in installer and 'HKLM' not in installer,'Installer registry scope changed')
    need('[Run]' not in installer and 'Exec(' not in installer,'Installer executes an external program')
    need('"allowed_extensions": ["{#AddonID}"]' in installer,'Host allowlist changed')
    for path in ROOT.glob('.github/workflows/*.yml'):
        text=path.read_text()
        for action in re.findall(r'uses:\s*([^\s]+)',text):
            need(bool(re.fullmatch(r'actions/[\w-]+@[0-9a-f]{40}',action)),f'Unpinned or nonofficial action: {action}')
        need('pull_request_target' not in text,'Privileged PR trigger')
    sources=[]
    for folder in ['extension','cmd','internal','installer','scripts','docs','.github']:
        sources.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.go','.js','.cjs','.py','.md','.yml','.json','.iss','.txt'])
    for path in sources:
        for pattern in [r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']:
            need(not re.search(pattern,path.read_text(encoding='utf-8')),f'Possible secret: {path.relative_to(ROOT)}')
    if failures:raise RuntimeError('\n'.join(failures))
    print('Security invariants passed: permissions, URL disclosure, native launch, installer, workflow pins, source secret patterns.')

if __name__=='__main__':check()
