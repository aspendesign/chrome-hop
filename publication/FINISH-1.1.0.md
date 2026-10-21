# Mozilla 1.1.0 submission completed

Completed October 21, 2026 through the existing authenticated Developer Hub.
The final **Submit Version** and source-upload steps completed, and Mozilla
displayed **Version Submitted**. Version **6602520**, file **5146641**, is
**Awaiting Review** for public/listed distribution, with **0 errors / 0 warnings**.
The source archive was downloaded back and matched the upload byte for byte.
Listing details, the privacy policy and updated setup screenshot/caption are saved.

[Current status](https://addons.mozilla.org/en-US/developers/addon/chrome-hop-open-in-chrome/versions)
requires the owner's Mozilla account. Mozilla review/signing and public
availability remain pending. Do not create a duplicate submission. No software
was installed on the owner's PC during this submission run.

Evidence: [submission receipt](../verification/amo-1.1.0.json),
[Version Submitted](../verification/amo-1.1.0-submitted.jpg),
[Awaiting Review](../verification/amo-1.1.0-awaiting-review.jpg).
The following text is saved on the submitted version.

## Release Notes

Left-click still opens the current tab immediately. Right-click the Chrome Hop
toolbar button and choose Open all tabs in this window to open its web tabs
in order, keeping Firefox tabs open. The bulk option asks for optional
tab-address access; declining leaves single-tab use unchanged. Setup now has
a direct Download for Windows button and a separate View on GitHub button,
three clear steps, and correct error messages.

## Notes to Reviewer

Windows 11 x64. Version 1.1.0 preserves immediate activeTab left-click opening
and adds a toolbar-only menus context: Open all tabs in this window. It calls
permissions.request for optional tabs synchronously from that explicit menu
gesture, queries only its windowId after approval, skips unsupported URLs and
sends sequential single-URL messages to the unchanged strict native helper.
No automatic scanning, host permissions, injected scripts, telemetry or network
APIs. Permission denial leaves ordinary left-click working. The local URL
handoff is disclosed as browsingActivity.

Raw extension files are readable and untransformed. Full source, tests, threat
model and installer: https://github.com/aspendesign/chrome-hop/tree/v1.1.0 .
Reproduce on Windows with Go 1.27.3, Node 24.15.0, Inno 7.1.0 and Python 3.11+:
python scripts/bootstrap.py; python scripts/build.py. Install the helper from
the matching GitHub release. Left-click https://example.com/; Chrome opens it
and Firefox stays open. Create two safe web tabs; right-click the action and
select Open all tabs in this window, then allow optional tab access. Actual
Firefox/Chrome smoke tests and 39 unit tests passed on ASUS. Missing helper
shows a packaged direct-download page. The helper binary is byte-identical to
the previously supplied 1.0.0 helper. Every Firefox source file is in the XPI;
there is no minification, compilation or external extension code to reconstruct.
