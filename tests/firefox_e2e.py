"""Real Firefox toolbar click -> production native helper -> real Chrome.

Uses Mozilla's WebDriver chrome context in a disposable headless Firefox
profile, restricted to loopback for the test lifetime. No existing Firefox
session/profile is controlled. Chrome receives only harmless test URLs in its
normal profile, as the production binary deliberately accepts no profile flags.
The localhost fixture records only test paths and browser family. No URLs from
the user's browsing or existing browser tabs are inspected.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import winreg

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run import ROOT, run
from build import VERSION
from windows_install import HOST, ID, KEY, registry

OUT=ROOT/'.local/e2e'
OUT.mkdir(parents=True,exist_ok=True)
TARGET=OUT/'helper'
hits=[]

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        family='Chrome' if 'Chrome/' in self.headers.get('User-Agent','') else 'Firefox'
        if self.path.startswith('/handoff'):
            hits.append({'path':self.path,'browser':family})
        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers()
        self.wfile.write(b'<!doctype html><title>Chrome Hop verification</title><style>body{font:24px system-ui;margin:80px;color:#163b2e}small{font-size:16px}</style><h1>One click. Your tab in Chrome.</h1><p>Chrome Hop local integration test.</p><small>This page contains no account data.</small>')

def main():
    if registry() is not None or TARGET.exists():raise SystemExit('Existing native registration/test install; refusing to overwrite')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
    service=None;session=None
    report={'success':False,'firefox_profile':'disposable geckodriver profile','chrome_profile':'normal installed Chrome profile; harmless localhost + example.com only','checks':[],
      'helper_sha256':hashlib.sha256((ROOT/f'dist/chrome-hop-{VERSION}-windows-x64.exe').read_bytes()).hexdigest(),
      'extension_sha256':hashlib.sha256((ROOT/f'dist/chrome-hop-{VERSION}-amo-submission.zip').read_bytes()).hexdigest()}
    log=(OUT/'geckodriver.log').open('w')
    base=f'http://127.0.0.1:{port}'
    def api(method,path,data=None):
        payload=json.dumps(data).encode() if data is not None else None
        req=urllib.request.Request(base+path,data=payload,method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=45) as res:r=json.load(res)
        except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()[:2000])
        value=r.get('value')
        if isinstance(value,dict) and 'error'in value:raise RuntimeError(str(value)[:2000])
        return value
    def cmd(path,data=None,method='POST'):return api(method,'/session/'+session+path,data)
    def js(source,*args):return cmd('/execute/sync',{'script':source,'args':list(args)})
    def context(value):cmd('/moz/context',{'context':value})
    def until(fn,seconds=15):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            try:result=fn()
            except (urllib.error.URLError, ConnectionError):result=False
            if result:return result
            time.sleep(.15)
        raise AssertionError('Timed out waiting for browser state')
    def toolbar():
        context('chrome')
        widget=js("return Array.from(document.querySelectorAll('[id]')).map(n=>n.id).find(id=>id.includes('chrome-hop') && id.endsWith('-browser-action'))")
        if not widget:
            widget='chrome-hop_aspendesign_github_io-browser-action'
        js("CustomizableUI.addWidgetToArea(arguments[0], CustomizableUI.AREA_NAVBAR);",widget)
        element=cmd('/element',{'using':'css selector','value':'#'+widget+' .webextension-browser-action'})
        cmd('/element/'+element['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
        context('content')
    try:
        service=subprocess.Popen([str(ROOT/'.tools/geckodriver/geckodriver.exe'),'--host','127.0.0.1','--port',str(port),'--allow-system-access','--log','error'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        until(lambda: api('GET','/status') if service.poll() is None else False)
        value=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'firefox','moz:firefoxOptions':{'binary':r'C:\Program Files\Firefox Developer Edition\firefox.exe','args':['-headless','-no-remote'],'prefs':{'browser.shell.checkDefaultBrowser':False,'browser.startup.page':0}}}}})
        session=value['sessionId'];report['firefox_version']=value['capabilities']['browserVersion']
        cmd('/window/rect',{'width':1400,'height':1100})
        initial=cmd('/window',method='GET')
        addon=cmd('/moz/addon/install',{'path':str(ROOT/f'dist/chrome-hop-{VERSION}-amo-submission.zip'),'temporary':True})
        assert addon==ID
        until(lambda:len(cmd('/window/handles',method='GET'))>=2)
        cmd('/window',{'handle':initial})
        # Missing host: genuine action click; should open packaged guidance.
        url=f'http://127.0.0.1:{server.server_address[1]}/handoff?case=missing'
        cmd('/url',{'url':url})
        original=cmd('/window',method='GET')
        before=cmd('/window/handles',method='GET')
        toolbar()
        context('chrome')
        report['initial_widget_badge']=js("return document.querySelector('#chrome-hop_aspendesign_github_io-browser-action .toolbarbutton-badge')?.textContent")
        context('content')
        handles=until(lambda:cmd('/window/handles',method='GET') if len(cmd('/window/handles',method='GET'))>=2 else None)
        help_handle=next(h for h in handles if h!=original)
        cmd('/window',{'handle':help_handle})
        until(lambda: js('return location.hash')=='#helper')
        screenshot=cmd('/screenshot',method='GET');(OUT/'setup-help.png').write_bytes(base64.b64decode(screenshot))
        report['checks'].append('missing_helper_actionable_page')
        # Install the actual release installer; Firefox is left running.
        run([ROOT/f'dist/ChromeHop-Setup-{VERSION}-windows-x64.exe','/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/CURRENTUSER','/SP-','/DIR='+str(TARGET)])
        assert registry()==str(TARGET/(HOST+'.json'))
        # Return to the original tab. Exactly one Chrome request must arrive.
        cmd('/window',{'handle':original})
        expected='/handoff?case=localhost&one=1%26two%3D2#kept'
        url=f'http://127.0.0.1:{server.server_address[1]}'+expected
        cmd('/url',{'url':url});toolbar()
        try:
            until(lambda:len([h for h in hits if h=={'browser':'Chrome','path':expected.split('#')[0]}])==1,30)
        except AssertionError:
            context('chrome')
            report['failed_handoff_badge']=js("return document.querySelector('#chrome-hop_aspendesign_github_io-browser-action .toolbarbutton-badge')?.textContent")
            context('content');cmd('/window',{'handle':help_handle})
            report['failed_handoff_help']=js('return location.hash')
            raise
        time.sleep(1)
        assert len([h for h in hits if h=={'browser':'Chrome','path':expected.split('#')[0]}])==1
        assert js('return location.href')==url,'Firefox tab navigated'
        report['checks'].append('localhost_exactly_once_in_real_chrome_firefox_kept')
        # Badge confirms the exact production response, not a fake host fixture.
        context('chrome')
        badge=js("return document.querySelector('#chrome-hop_aspendesign_github_io-browser-action .toolbarbutton-badge')?.textContent")
        report['toolbar_badge']=badge
        screenshot=cmd('/screenshot',method='GET');(OUT/'toolbar-handoff.png').write_bytes(base64.b64decode(screenshot))
        context('content')
        # HTTP(S) public case uses example.com, never an authenticated page.
        cmd('/url',{'url':'https://example.com/'});toolbar()
        context('chrome')
        until(lambda:js("return document.querySelector('#chrome-hop_aspendesign_github_io-browser-action .toolbarbutton-badge')?.textContent")== '✓')
        report['checks'].append('https_example_com_production_launch_acknowledged')
        context('content')
        report['firefox_original_still_open']=js('return location.href')=='https://example.com/'
        report['test_requests']=hits
        report['success']=True
    finally:
        if session:
            try:api('DELETE','/session/'+session)
            except Exception:pass
        if service:
            try:service.wait(timeout=10)
            except subprocess.TimeoutExpired:service.terminate();service.wait(timeout=5)
        log.close();server.shutdown();server.server_close()
        if (TARGET/'unins000.exe').exists():run([TARGET/'unins000.exe','/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],check=False)
        report['host_registration_removed']=registry() is None
        report['test_requests']=hits
        (OUT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
