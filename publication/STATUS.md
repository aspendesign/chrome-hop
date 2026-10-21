# Publication status

## 1.1.0 toolbar menu improvement

Version 1.1.0 includes direct downloads and adds **Open all tabs in this window**
to the toolbar’s right-click menu. Left-click still opens only the current tab.
`menus` is required for the context menu, and `tabs` is optional and requested
only for that explicit bulk action. Native helper code/security is unchanged.
Local unit and real Firefox/Chrome verification passed; tagged release and
Mozilla submission details will be recorded here after completion.

## 1.0.1 setup improvement

Version 1.0.1 adds direct installer downloads, a separate GitHub button,
first-install guidance, platform availability and correct help-tab updates.
The Windows helper security boundary and two API permissions are unchanged.
The [download link](https://github.com/aspendesign/chrome-hop/releases/latest/download/ChromeHop-Setup-windows-x64.exe)
uses a stable Setup filename; its bytes match the versioned installer and it
is included in checksums and build attestations.

The update is prepared and locally tested. Its tagged public release and AMO
update submission will be recorded here after their actual completion.

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
