<p align="center"><img src="assets/chrome-hop-512.png" width="112" alt="Chrome Hop icon"></p>
<h1 align="center">Chrome Hop</h1>
<p align="center"><b>One click. Your Firefox tab in Chrome.</b></p>

Chrome Hop is a small Firefox toolbar extension for Windows 11. Click the
button and the current web address opens in Google Chrome. Your Firefox tab
stays open. No preferences to configure, website scripts, tracking or services.

**[↓ Download for Windows](https://github.com/aspendesign/chrome-hop/releases/latest/download/ChromeHop-Setup-windows-x64.exe)**
· **[View releases on GitHub](https://github.com/aspendesign/chrome-hop/releases/latest)**
· **[Installation](docs/INSTALL.md)** · **[Privacy](docs/PRIVACY.md)**

> **Firefox distribution status, verified October 20, 2026:** version **1.0.0**
> was submitted for **public/listed** Mozilla distribution and is **Awaiting Review**.
> The original icon, two actual screenshots, privacy policy, MIT license, reviewer
> notes and full source package are saved. Public approval and a signed XPI remain
> pending. The submission ZIP is a reviewer/development artifact, not an installable
> public Firefox release. See [publication status](publication/STATUS.md).

## Get started

1. Install **Chrome Hop — Open in Chrome** from Mozilla Add-ons when the listed
   version is available.
2. Click **[Download for Windows](https://github.com/aspendesign/chrome-hop/releases/latest/download/ChromeHop-Setup-windows-x64.exe)**.
   Open the downloaded **ChromeHop-Setup-windows-x64.exe** and follow the installer.
   It installs just for you, with no administrator access or runtime downloads.
3. Pin Chrome Hop to Firefox’s toolbar, open a web page, and click the icon.

The add-on’s setup screen has the same direct download and a separate **View on
GitHub** button for source, release details and checksums. No terminal commands
or developer tools are needed. Firefox downloads the installer; you open it once
to approve the local installation.

## Supported platforms

| Platform | Availability |
| --- | --- |
| Windows 11 x64 | Ready: use the direct installer above |
| macOS | Helper not available yet |
| Linux | Helper not available yet |
| Windows ARM64 / 32-bit | No tested native helper yet |

Requires Firefox 142 or later and Google Chrome **Stable** in its normal
installation directory. HTTP, HTTPS and localhost are supported. Custom Chrome
paths and other Chromium browsers are outside version 1’s supported scope.

## A deliberately small boundary

| Component | What it can do |
| --- | --- |
| Firefox add-on | Read the tab URL you click using `activeTab`; send one native message using `nativeMessaging` |
| Native helper | Validate one HTTP(S) URL and launch a fixed installed Chrome executable with that URL as one argument |
| Windows installer | Install under your local application directory, register one Firefox host under HKCU, and provide uninstall |

Those are the add-on’s **only two API permissions**. It has no host permissions,
content scripts, cookies/history access, tab scanning, shell execution, network
client, downloaded runtime, telemetry, background service or automatic routing.

Mozilla additionally requires the `browsingActivity` **data disclosure** because
the selected address is passed to a program outside Firefox. That transfer
stays on your computer until Chrome loads the address normally. The developer
receives nothing. [Read exactly what happens](docs/PRIVACY.md).

The helper is written in Go with **zero external runtime modules**. It reads
one bounded, strictly validated message, returns a sanitized status, and exits.
It cannot accept executable names, command-line flags or shell commands. Its
native-host allowlist contains only this add-on’s stable ID.

## Source, builds and security

- [Build and release instructions](docs/BUILDING.md), including pinned tools,
  reproducibility checks and SHA-256 checksums.
- [Threat model and security review](docs/SECURITY-REVIEW.md), including trust
  boundaries and limits of a per-user local helper.
- [Verification evidence](verification/RESULTS.md) for automated tests and ASUS
  integration testing; [changelog](CHANGELOG.md).
- [Report vulnerabilities privately](SECURITY.md).

Build tools are development dependencies only. No Node.js, Python or Inno
Setup runtime is needed by users. The installer is not Authenticode-signed;
no signing certificate or paid service was purchased. Firefox signing and
public availability depend on Mozilla’s submission and review process.

Chrome Hop is independent of Mozilla and Google and is not endorsed by either.
Its icon is original artwork; no Firefox or Chrome trademark artwork is bundled.

MIT licensed. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
