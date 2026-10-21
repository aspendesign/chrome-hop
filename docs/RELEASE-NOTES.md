## [↓ Download for Windows](https://github.com/aspendesign/chrome-hop/releases/download/v1.0.1/ChromeHop-Setup-windows-x64.exe)

**[View source code](https://github.com/aspendesign/chrome-hop)** ·
**[Installation guide](https://github.com/aspendesign/chrome-hop/blob/main/docs/INSTALL.md)** ·
**[SHA-256 checksums](https://github.com/aspendesign/chrome-hop/releases/download/v1.0.1/SHA256SUMS.txt)**

1. **Download** using the link above.
2. **Open ChromeHop-Setup-windows-x64.exe** from your downloads and follow the installer.
3. **Click Chrome Hop in Firefox** on any web page. Your Firefox tab stays open.

Free, per-user installation. No administrator access, terminal commands,
runtime downloads or background service. Requires **Windows 11 x64**, Firefox
142 or later, Google Chrome Stable and the separate Chrome Hop Firefox add-on.
macOS, Linux and Windows ARM helpers are not available yet.

### What’s new in 1.0.1

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

The add-on keeps exactly `activeTab` and `nativeMessaging`. The Windows helper
security boundary is unchanged. No tracking or website scripts. The installer
is not Authenticode-signed; source, checksums and build provenance are public.
