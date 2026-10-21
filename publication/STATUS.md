# Publication status

## 1.1.0 toolbar menu improvement

Version 1.1.0 includes direct downloads and adds **Open all tabs in this window**
to the toolbar’s right-click menu. Left-click still opens only the current tab.
`menus` is required for the context menu, and `tabs` is optional and requested
only for that explicit bulk action. Native helper code/security is unchanged.
**GitHub release: [1.1.0 is public](https://github.com/aspendesign/chrome-hop/releases/tag/v1.1.0).**
The [release workflow](https://github.com/aspendesign/chrome-hop/actions/runs/39546456333)
and [Windows CI](https://github.com/aspendesign/chrome-hop/actions/runs/39546450269)
passed at source `a909247caf6488a1ccd7b8265f89e1b9fb475fc5`.
All seven assets were downloaded anonymously and verified against SHA-256.
The helper, extension, versioned installer and stable Setup alias match the
ASUS-tested builds byte for byte. GitHub attestations for the Setup alias and
checksum file were verified. Actual Firefox clicked the packaged Download
button and downloaded the exact public installer.

**Mozilla 1.1.0: uploaded and validated, final submission unfinished.**
The listed update reached version **6602520**, with **0 errors / 0 warnings**.
Browser control disconnected on the Describe Version step before the release
notes/reviewer notes were entered or **Submit Version** was clicked. This is
a validated draft, not a completed submission or a public signed add-on.
The original 1.0.0 submission remains awaiting review; no 1.0.1 Mozilla version
was submitted. [Finish the draft](https://addons.mozilla.org/en-US/developers/addon/chrome-hop-open-in-chrome/versions/submit/6602520/details)
with the text in [FINISH-1.1.0.md](FINISH-1.1.0.md). No API credentials were
created/exported; the protected optional API workflow has no configured AMO secrets.

Evidence: [browser tests](../verification/BULK-1.1.0.md),
[release hashes](../verification/release-1.1.0.json),
[actual button download](../verification/download-1.1.0.json).

## 1.0.1 setup improvement

Version 1.0.1 adds direct installer downloads, a separate GitHub button,
first-install guidance, platform availability and correct help-tab updates.
The Windows helper security boundary and two API permissions are unchanged.
The [download link](https://github.com/aspendesign/chrome-hop/releases/latest/download/ChromeHop-Setup-windows-x64.exe)
uses a stable Setup filename; its bytes match the versioned installer and it
is included in checksums and build attestations.

The [1.0.1 GitHub release](https://github.com/aspendesign/chrome-hop/releases/tag/v1.0.1)
was published by [the passing workflow](https://github.com/aspendesign/chrome-hop/actions/runs/39545589623).
It is superseded by 1.1.0 above. Its Mozilla upload was replaced with 1.1.0
before creating a version, so no separate 1.0.1 AMO submission is claimed.

## 1.0.0 verified release and initial submission

Verified October 20, 2026 (America/Chicago). Mozilla’s dashboard uses October 21
for this submission’s UTC date. Submission, approval, signing and public
availability are separate states.

| Deliverable | Verified result |
| --- | --- |
| Public source | [aspendesign/chrome-hop](https://github.com/aspendesign/chrome-hop) |
| Production release | [v1.0.0, published](https://github.com/aspendesign/chrome-hop/releases/tag/v1.0.0) |
| Release source commit | `ab80f2c10da90f34ffa86d431ee0ed462f5bb886` |
| Automated release | [Passed, including Windows tests/builds and signed provenance](https://github.com/aspendesign/chrome-hop/actions/runs/39539792041) |
| Windows installer | Public download; install/repair/upgrade/reinstall/uninstall passed without elevation on ASUS |
| Public downloads | Downloaded anonymously, checked against SHA-256; helper/installer/extension identical to ASUS-tested copies |
| Build provenance | GitHub attestations verified for the installer and checksum file; all six release assets are signed subjects |
| Native helper | Standalone Go executable; no external runtime modules; no Authenticode certificate |
| Firefox package | Exact tested, unsigned submission ZIP released for reviewers/development |
| Mozilla distribution | **Public/listed submission completed** through the existing authenticated Developer Hub |
| Mozilla identifiers | Add-on `3102983`; version `6602368`; file `5146489`; stable ID `chrome-hop@aspendesign.github.io` |
| Mozilla validation | **0 errors, 0 warnings** |
| Mozilla status | **Awaiting Review** |
| Listing assets | Original icon and two actual Firefox screenshots saved; captions verified after reopening the form |
| Listing details | Tabs category, description, support/homepage URLs, privacy policy, MIT license and version notes saved |
| Reviewer source | Complete version-tagged source archive uploaded; byte-exact reproduction instructions saved |
| Public signed XPI / approved listing | **Pending Mozilla approval; not claimed available** |

[Manage submission/status](https://addons.mozilla.org/en-US/developers/addon/chrome-hop-open-in-chrome/versions)
(requires the owner’s Mozilla account).
[Public listing target](https://addons.mozilla.org/en-US/firefox/addon/chrome-hop-open-in-chrome/)
will become installable only after Mozilla approves/publishes the version.
An HTTP 200 from the public website shell does not prove availability; the
anonymous add-on API still returned 401 during the final check.

The submitted ZIP SHA-256 is
`e4d9e258df0d224ea40b86300cb8f79d43acc3dbfd9041c470fa46405de5b5c3`.
The uploaded source archive SHA-256 is
`9d0a707b28b5280ffc2ad04dc81164d06b7a7735f3a9c6dec1231dc0a40ec5f3`.
The installer SHA-256 is
`99345bc04c98cc863760997901a07c4c9029e9425a31e143499600543b69b4e6`.

Mozilla’s stored ZIP was downloaded and compared: all nine non-manifest files
are byte-identical to the tested release and the manifest JSON is semantically
identical. Mozilla changed JSON formatting/ZIP compression only. That stored
ZIP hashes to `af31d35c9a8a1cdcdad57cbf5535faf85420a7aba46723409db1e3ee471e00dd`
and contains no Mozilla signature files yet.

The only remaining external gate for this version is Mozilla review/signing
and publication. No account/MFA action is currently required from the owner.
No background monitoring or approval-time promise is made.

GitHub tag releases are implemented and exercised. The optional manual AMO
API workflow is present and protected by the `mozilla-production` environment
with owner review and a main-branch rule. Future API-driven submissions require
`AMO_API_KEY` and `AMO_API_SECRET`; no credentials were exported or created in
this run. This initial submission used the existing browser session.

Evidence: [test results](../verification/RESULTS.md),
[release verification](../verification/release.json),
[actual Mozilla status capture](../verification/amo-awaiting-review.png).
