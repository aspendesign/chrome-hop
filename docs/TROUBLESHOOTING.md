# Troubleshooting

## A setup page opens when I click

Install the Windows helper from the [official release](https://github.com/aspendesign/chrome-hop/releases/latest).
If it is already installed, run that installer again to repair its Firefox
registration. The helper and Firefox must run under the same Windows account.
Do not run Firefox as another user or as administrator.

## Chrome is missing

Install Google Chrome **Stable** from [Google](https://www.google.com/chrome/).
Chrome Hop recognizes `Google\Chrome\Application\chrome.exe` inside Windows’
Program Files, Program Files (x86), or your local application-data directory.
Custom paths, junctions beneath those roots, Chrome Beta/Canary, Chromium, Edge
and portable browsers are intentionally unsupported. It does not search PATH
or accept a custom executable.

## This page can’t hop

Use an `http://` or `https://` web address. Browser settings, files, extension
pages, `about:`/`data:`/`javascript:` links, malformed addresses and URLs with
embedded credentials or control characters are rejected. URL length is limited
to 16 KiB in UTF-8. Localhost and loopback IP addresses are supported.

## Chrome opened, but I’m not signed in to the website

Each browser has its own cookies and login sessions. Chrome Hop sends the web
address only. Sign in to the site in Chrome normally. Forms, scrolling position,
unsaved edits, POST bodies and page state are not transferred.

## Repeated clicks / already-running Chrome

The helper opens the address in Chrome’s normal profile. Chrome decides which
window handles it. An in-progress click and rapid double clicks are suppressed;
wait a second before deliberately opening the same tab again. The green tick
means Windows accepted the Chrome launch, not that the remote page finished
loading. Chrome enterprise policy may change its behavior.

## Windows blocks an unsigned download

The helper installer has no purchased code-signing certificate. Download only
from this project’s GitHub Releases. Check the SHA-256 with PowerShell:

```powershell
Get-FileHash .\ChromeHop-Setup-1.0.0-windows-x64.exe -Algorithm SHA256
```

Compare the result to `SHA256SUMS.txt` from the same release. Respect your
organization’s application-control policy. Checksums detect file changes;
they are not a publisher identity certificate.

## Advanced read-only diagnosis

The only native host is `io.github.aspendesign.chrome_hop`. Its default registry
value at `HKCU\Software\Mozilla\NativeMessagingHosts\io.github.aspendesign.chrome_hop`
points to an absolute JSON descriptor in `%LOCALAPPDATA%\Programs\Chrome Hop`.
That descriptor must allow only `chrome-hop@aspendesign.github.io` and point to
the installed absolute `chrome-hop.exe` path. Repair with the installer rather
than copying commands from third-party helper packages.

No URL logs exist to upload. Report the error heading, Windows/Firefox/Chrome
versions and helper version at [GitHub Issues](https://github.com/aspendesign/chrome-hop/issues).
Omit browsing data, access tokens and private links.
