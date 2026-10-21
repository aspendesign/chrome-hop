"""Real packaged setup UI in a disposable Firefox profile; no user-profile writes.

Leaves existing native registration/helper untouched. A download check may be
run after publication with --download; it verifies the actual button's file.
"""
import base64
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run import ROOT
from build import VERSION

OUT=ROOT/'.local/setup-ui'
OUT.mkdir(parents=True,exist_ok=True)

def main():
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
    base=f'http://127.0.0.1:{port}'
    service=None;session=None;server=None;log=(OUT/'geckodriver.log').open('w')
    report={'version':VERSION,'success':False,'profile':'disposable','checks':[]}
    def api(method,path,data=None):
        req=urllib.request.Request(base+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:value=json.load(r)['value']
        except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode()[:1500])
        if isinstance(value,dict) and 'error' in value:raise RuntimeError(str(value)[:1500])
        return value
    def cmd(path,data=None,method='POST'):return api(method,'/session/'+session+path,data)
    def js(script,*args):return cmd('/execute/sync',{'script':script,'args':list(args)})
    def until(fn,seconds=15):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            try:
                result=fn()
                if result:return result
            except (urllib.error.URLError,ConnectionError):pass
            time.sleep(.15)
        raise AssertionError('Timed out waiting for Firefox setup UI')
    def snapshot(name):
        (OUT/name).write_bytes(base64.b64decode(cmd('/screenshot',method='GET')))
    def toolbar():
        cmd('/moz/context',{'context':'chrome'})
        widget='chrome-hop_aspendesign_github_io-browser-action'
        js('CustomizableUI.addWidgetToArea(arguments[0],CustomizableUI.AREA_NAVBAR)',widget)
        element=cmd('/element',{'using':'css selector','value':'#'+widget+' .webextension-browser-action'})
        cmd('/element/'+element['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
        cmd('/moz/context',{'context':'content'})
    try:
        service=subprocess.Popen([str(ROOT/'.tools/geckodriver/geckodriver.exe'),'--host','127.0.0.1','--port',str(port),'--allow-system-access','--log','error'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        until(lambda:api('GET','/status'))
        value=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'firefox','moz:firefoxOptions':{'binary':r'C:\Program Files\Firefox Developer Edition\firefox.exe','args':['-headless','-no-remote'],'prefs':{'browser.shell.checkDefaultBrowser':False,'ui.systemUsesDarkTheme':1,'browser.download.folderList':2,'browser.download.dir':str(OUT),'browser.download.useDownloadDir':True}}}}})
        session=value['sessionId'];report['firefox_version']=value['capabilities']['browserVersion']
        cmd('/window/rect',{'width':1400,'height':1080})
        cmd('/moz/addon/install',{'path':str(ROOT/f'dist/chrome-hop-{VERSION}-amo-submission.zip'),'temporary':True})
        handles=until(lambda:cmd('/window/handles',method='GET') if len(cmd('/window/handles',method='GET'))>=2 else None)
        for handle in handles:
            cmd('/window',{'handle':handle})
            if js('return location.href').endswith('help.html#setup'):break
        else:raise AssertionError('First-install setup tab absent')
        until(lambda:js('return document.querySelector("#heading").textContent.includes("One quick install")'))
        setup_url=js('return location.href');setup_handle=handle
        expected='https://github.com/aspendesign/chrome-hop/releases/latest/download/ChromeHop-Setup-windows-x64.exe'
        assert js('return document.querySelector("#download").href')==expected
        assert js('return document.querySelector(".secondary").href')=='https://github.com/aspendesign/chrome-hop/releases/latest'
        assert js('return document.querySelector("#windows-setup").hidden') is False
        snapshot('setup-desktop.png');report['checks'].append('first_install_direct_download_and_separate_github')
        js('location.hash="unsupported"')
        until(lambda:js('return document.querySelector("#heading").textContent.includes("can’t hop")'))
        js('location.hash="helper"')
        until(lambda:js('return document.querySelector("#heading").textContent.includes("One quick install")'))
        assert js('return document.querySelector("#windows-setup").hidden') is False
        report['checks'].append('hashchange_regression_in_actual_firefox')
        cmd('/window/rect',{'width':420,'height':1040})
        assert js('return document.documentElement.scrollWidth<=innerWidth')
        snapshot('setup-mobile.png');report['checks'].append('narrow_layout_without_horizontal_overflow')
        cmd('/window/rect',{'width':1400,'height':1080})
        js('document.querySelector("details").open=true')
        snapshot('setup-expanded.png')
        if '--download' in sys.argv:
            existing=set(OUT.glob('ChromeHop-Setup-windows-x64*.exe'))
            element=cmd('/element',{'using':'css selector','value':'#download'})
            cmd('/element/'+element['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
            file=until(lambda:next((p for p in OUT.glob('ChromeHop-Setup-windows-x64*.exe') if p not in existing and p.stat().st_size>1000000 and not p.with_suffix(p.suffix+'.part').exists()),None),45)
            assert file.read_bytes()==(ROOT/f'dist/ChromeHop-Setup-{VERSION}-windows-x64.exe').read_bytes()
            report['download_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            report['checks'].append('actual_firefox_button_download_matches_released_installer')
        # The actual toolbar also rejects this internal page using the same help tab.
        toolbar()
        until(lambda:js('return location.hash')=='#unsupported')
        assert js('return document.querySelector("#page-help").hidden') is False
        report['checks'].append('actual_toolbar_reuses_help_tab_and_updates_message')
        if '--bulk' in sys.argv:
            hits=[]
            class Handler(BaseHTTPRequestHandler):
                def log_message(self,*args):pass
                def do_GET(self):
                    if 'Chrome/' in self.headers.get('User-Agent','') and self.path.startswith('/test-'):
                        hits.append(self.path)
                    self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
                    self.wfile.write(b'<!doctype html><title>Chrome Hop bulk verification</title><h1>Harmless local Chrome Hop test</h1>')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            threading.Thread(target=server.serve_forever,daemon=True).start()
            host=f'http://127.0.0.1:{server.server_address[1]}'
            originals={}
            for path in ['/test-a','/test-b']:
                handle=cmd('/window/new',{'type':'tab'})['handle'];cmd('/window',{'handle':handle});cmd('/url',{'url':host+path});originals[handle]=host+path
            active=handle
            other=cmd('/window/new',{'type':'window'})['handle'];cmd('/window',{'handle':other});cmd('/url',{'url':host+'/test-other-window'})
            cmd('/window',{'handle':active})
            toolbar()
            until(lambda:hits.count('/test-b')==1)
            report['checks'].append('left_click_still_opens_only_current_tab_in_real_chrome')
            time.sleep(.3);hits.clear()
            cmd('/moz/context',{'context':'chrome'})
            widget='chrome-hop_aspendesign_github_io-browser-action'
            element=cmd('/element',{'using':'css selector','value':'#'+widget+' .webextension-browser-action'})
            cmd('/actions',{'actions':[{'type':'pointer','id':'menu-mouse','parameters':{'pointerType':'mouse'},'actions':[{'type':'pointerMove','duration':0,'origin':element,'x':0,'y':0},{'type':'pointerDown','button':2},{'type':'pointerUp','button':2}]}]})
            selector='menuitem[label="Open all tabs in this window"]'
            until(lambda:js('return Array.from(document.querySelectorAll(arguments[0])).some(n=>n.getBoundingClientRect().width>0)',selector))
            report['checks'].append('real_toolbar_right_click_menu_visible')
            item=cmd('/element',{'using':'css selector','value':selector})
            cmd('/element/'+item['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
            time.sleep(.2)
            notification=js('return Array.from(document.querySelectorAll("popupnotification")).filter(n=>n.getBoundingClientRect().width>0).map(n=>({id:n.id,label:n.getAttribute("label"),buttons:Array.from(n.querySelectorAll("button")).map(b=>({class:b.className,label:b.getAttribute("label"),text:b.textContent}))}))')
            report['permission_ui']=notification
            print('Permission UI:',json.dumps(notification),flush=True)
            if notification:
                assert not hits,'Bulk launched before permission approval'
                # Native popup controls have no interactable rectangle in headless
                # Firefox. Invoke the actual prompt's primary control via chrome
                # DOM; do not grant permissions through a test-only extension API.
                js('document.getElementById(arguments[0]).button.click()',notification[0]['id'])
                report['checks'].append('real_optional_permission_prompt_approved_via_chrome_DOM_in_headless_test_profile')
            until(lambda:hits.count('/test-a')==1 and hits.count('/test-b')==1,30)
            time.sleep(.5);assert hits==['/test-a','/test-b'],hits
            cmd('/moz/context',{'context':'content'})
            for handle,url in originals.items():
                cmd('/window',{'handle':handle});assert js('return location.href')==url
            report['checks'].append('bulk_opens_window_web_tabs_once_in_order_skips_other_window_and_keeps_firefox_tabs')
            report['bulk_chrome_requests']=hits
        report['success']=True
    finally:
        if session:
            try:api('DELETE','/session/'+session)
            except Exception:pass
        if service:
            try:service.wait(timeout=10)
            except subprocess.TimeoutExpired:service.terminate();service.wait(timeout=5)
        if server:server.shutdown();server.server_close()
        log.close();(OUT/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
