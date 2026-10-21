Chrome Hop 1.0.0 opens the current Firefox web page in Google Chrome with one
toolbar click on Windows 11 x64. Firefox keeps the original tab open.

Download **ChromeHop-Setup-1.0.0-windows-x64.exe** for the per-user Windows
helper. Google Chrome Stable and the separate Firefox add-on are required.
There is no administrator prompt, downloaded runtime, telemetry or service.

**Firefox / Mozilla status:** version **1.0.0 was submitted for public/listed
distribution** (AMO version ID 6602368) and is **Awaiting Review**. Original
artwork, two actual screenshots, privacy policy, MIT license, reviewer notes
and the full source package were saved. A publicly signed XPI and public
availability remain pending Mozilla approval. The `amo-submission.zip` is a
reviewer/development artifact and cannot be installed in normal Firefox.
Track the verified status
in [publication/STATUS.md](https://github.com/aspendesign/chrome-hop/blob/main/publication/STATUS.md).

The add-on requests only `activeTab` and `nativeMessaging`. Mozilla’s additional
browsing-activity disclosure describes the selected URL’s local transfer to
Chrome; no developer server receives it. The helper accepts a single validated
HTTP(S) URL and directly launches a fixed Chrome path with one argument.

Use `SHA256SUMS.txt` to verify downloads. The Windows installer/helper are not
Authenticode-signed. The readable source is MIT licensed. See README, privacy,
security review and verification results before installing.
