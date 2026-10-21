# Verification results — 1.0.0

Tested on ASUS Windows 11 on October 20, 2026. These are actual local runs.
GitHub CI/release evidence is recorded separately once those runs finish.

| Check | Result |
| --- | --- |
| Extension automated tests | 25 passed, 0 failed |
| Mozilla `web-ext` 10.8.0 lint | 0 errors, 0 warnings, 0 notices |
| Required API permissions | Exactly `activeTab`, `nativeMessaging` |
| Optional / host permissions, content scripts | None |
| Go 1.27.3 unit tests and vet | Passed |
| Go parser fuzz run | 110,111 executions in the initial 20-second run; passed |
| Go `govulncheck` 1.9.0 | No vulnerabilities found |
| Runtime Go/npm modules shipped | Zero external modules |
| Production-only npm audit | Zero advisories |
| Full development npm audit | One reviewed, unpatched upstream advisory; details in security review |
| Helper, extension ZIP and installer reproducibility | Rebuilt twice, byte-identical |
| Compiled installer lifecycle | Install, repair, test-version upgrade, uninstall, reinstall and final uninstall passed |
| Elevated privileges during lifecycle test | False; HKCU-only per-user installation |
| Unicode install path with spaces | Exact descriptor, executable and registry readback passed |
| Compiled helper invalid-operation / wrong-extension checks | Correct framed sanitized rejections |
| Firefox 159.0 real toolbar click | Passed using unchanged release ZIP in a temporary profile |
| Chrome 155.0.8059.85 real localhost handoff | Exact test path/query requested once by Chrome; original Firefox tab kept |
| HTTPS example.com handoff | Production launch acknowledged; remote page completion not asserted |
| Missing-helper case | Actual click opened packaged actionable help |
| Native registration after tests | Removed; test helper uninstalled |
| Native console show/foreground observation | Zero events during 20.05-second successful browser test; hidden WinEvent control received |

The browser test used Mozilla geckodriver 0.37.1 and loopback-only temporary
WebDriver/fixture endpoints. Firefox’s personal profiles and existing tabs
were not controlled. Chrome received only harmless test URLs in its normal
profile because the production helper intentionally has no profile or argument
override. The test did not close or inspect other Chrome tabs.

Receipts: [browser](firefox-chrome.json), [installer](installer.json),
[native window events](window-events.json). The native window-event control
was hidden and sent no keyboard or mouse input. Only terminal class/event
metadata was observed; no user window titles or content were collected.

Actual screenshots: [Firefox toolbar handoff](../publication/screenshots/toolbar-handoff.png)
and [missing-helper instructions](../publication/screenshots/setup-help.png).
The toolbar screenshot is Firefox’s UI after the native response, not a
fabricated screenshot of Chrome. The server receipt supplies independent
evidence that the destination browser made the expected localhost request.

The initial integration run exposed Firefox’s native-host Windows Job lifetime
behavior. The final helper uses `CREATE_BREAKAWAY_FROM_JOB`; subsequent real
handoff tests passed. No failure was waived by weakening URL validation.

This is an engineering security review and automated testing, not an external
penetration-test certificate. Mozilla signing/review and public listing status
are reported in [publication status](../publication/STATUS.md).
