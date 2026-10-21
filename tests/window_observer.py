"""Bounded native console show/foreground observation around a test command.

No window titles, URLs, keyboard input or user content are collected. A hidden,
task-owned fixture emits a native WinEvent to prove the callback is alive.
"""
import ctypes
from ctypes import wintypes as W
import json
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run import ROOT,run

user=ctypes.WinDLL('user32',use_last_error=True)
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
Callback=ctypes.WINFUNCTYPE(None,W.HANDLE,W.DWORD,W.HWND,W.LONG,W.LONG,W.DWORD,W.DWORD)
user.SetWinEventHook.argtypes=[W.DWORD,W.DWORD,W.HMODULE,Callback,W.DWORD,W.DWORD,W.DWORD]
user.SetWinEventHook.restype=W.HANDLE
user.UnhookWinEvent.argtypes=[W.HANDLE]
user.CreateWindowExW.restype=W.HWND
user.CreateWindowExW.argtypes=[W.DWORD,W.LPCWSTR,W.LPCWSTR,W.DWORD,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,W.HWND,W.HMENU,W.HINSTANCE,ctypes.c_void_p]
user.NotifyWinEvent.argtypes=[W.DWORD,W.HWND,W.LONG,W.LONG]
user.DestroyWindow.argtypes=[W.HWND]
user.GetClassNameW.argtypes=[W.HWND,W.LPWSTR,ctypes.c_int]
user.GetWindowThreadProcessId.argtypes=[W.HWND,ctypes.POINTER(W.DWORD)]
user.PeekMessageW.argtypes=[ctypes.POINTER(W.MSG),W.HWND,W.UINT,W.UINT,W.UINT]
user.TranslateMessage.argtypes=[ctypes.POINTER(W.MSG)]
user.DispatchMessageW.argtypes=[ctypes.POINTER(W.MSG)]
events=[];control=[];ready=threading.Event();stop=threading.Event()

def observe():
    @Callback
    def callback(hook,event,hwnd,obj,child,thread,timestamp):
        if obj!=0 or child!=0:return
        name=ctypes.create_unicode_buffer(256)
        user.GetClassNameW(hwnd,name,256)
        if hwnd==fixture:
            control.append(event)
        elif name.value in ['ConsoleWindowClass','CASCADIA_HOSTING_WINDOW_CLASS','WindowsTerminal']:
            pid=W.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
            events.append({'event':'show' if event==0x8002 else 'foreground','class':name.value,'pid':pid.value})
    fixture=user.CreateWindowExW(0,'STATIC','ChromeHopHiddenWinEventFixture',0,0,0,0,0,None,None,None,None)
    hooks=[user.SetWinEventHook(e,e,None,callback,0,0,0) for e in [3,0x8002]]
    if not fixture or not all(hooks):raise OSError('WinEvent setup failed')
    try:
        user.NotifyWinEvent(0x8002,fixture,0,0)
        message=W.MSG()
        while not stop.is_set():
            while user.PeekMessageW(ctypes.byref(message),None,0,0,1):
                user.TranslateMessage(ctypes.byref(message));user.DispatchMessageW(ctypes.byref(message))
            if control:ready.set()
            stop.wait(.01)
    finally:
        for hook in hooks:user.UnhookWinEvent(hook)
        user.DestroyWindow(fixture)

def main():
    worker=threading.Thread(target=observe,daemon=True)
    worker.start()
    if not ready.wait(5):raise SystemExit('Observer control fixture failed')
    started=time.monotonic()
    try:
        result=run(sys.argv[1:],timeout=300,check=False)
        sys.stdout.buffer.write(result.stdout)
    finally:
        stop.set();worker.join(5)
    report={'seconds':round(time.monotonic()-started,2),'hidden_control_events':len(control),'console_show_or_foreground_events':events,'test_exit_code':result.returncode,'success':result.returncode==0 and not events and bool(control)}
    out=ROOT/'.local/window-observer.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['success'] else 1)

if __name__=='__main__':main()
