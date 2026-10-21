## [↓ Download for Windows](https://github.com/aspendesign/chrome-hop/releases/download/v1.1.0/ChromeHop-Setup-windows-x64.exe)

**[View source code](https://github.com/aspendesign/chrome-hop)** ·
**[Installation guide](https://github.com/aspendesign/chrome-hop/blob/main/docs/INSTALL.md)** ·
**[SHA-256 checksums](https://github.com/aspendesign/chrome-hop/releases/download/v1.1.0/SHA256SUMS.txt)**

1. **Download** using the link above.
2. **Open ChromeHop-Setup-windows-x64.exe** from your downloads and follow the installer.
3. **Click Chrome Hop in Firefox** on any web page. Your Firefox tab stays open.

Free, per-user installation. No administrator access, terminal commands,
runtime downloads or background service. Requires **Windows 11 x64**, Firefox
142 or later, Google Chrome Stable and the separate Chrome Hop Firefox add-on.
macOS, Linux and Windows ARM helpers are not available yet.

### What’s new in 1.1.0

- **Left-click once** to open just the current tab immediately.
- **Right-click → Open all tabs in this window** to open the window’s web tabs
  in order. Firefox tabs stay open; unsupported pages are skipped.
- The bulk action asks for optional tab-address access. Normal single-tab use
  doesn’t request it. The toolbar menu adds the `menus` API permission.

- The add-on’s setup page now has **Download for Windows** and **View on GitHub**
  buttons. Download goes straight to the installer.
- Three clear setup steps, first-install guidance and expandable help.
- Correct messages when the same help tab changes between errors.
- Clear platform availability instead of an incompatible download.

The two **Setup** files in Assets are identical. The standalone helper and ZIPs
are for developers/reviewers; ordinary Windows users need only the Setup file.

**Firefox / Mozilla:** public approval and signing remain a separate step.
See the [verified submission status](https://github.com/aspendesign/chrome-hop/blob/main/publication/STATUS.md).
The `amo-submission.zip` is unsigned and cannot be installed in normal Firefox.

The add-on uses `activeTab`, `nativeMessaging`, `menus`, and optional `tabs` for
the explicit bulk action. The Windows helper security boundary is unchanged.
No tracking or website scripts. The installer
is not Authenticode-signed; source, checksums and build provenance are public.
