# Finish the validated Mozilla 1.1.0 draft

The public GitHub release and every automated check passed. The AMO listed
update uploaded and validated with zero errors/warnings as version 6602520.
Browser control disconnected before the final Describe Version form could
be filled/submitted. Do not upload another duplicate version.

Open the existing [Describe Version form](https://addons.mozilla.org/en-US/developers/addon/chrome-hop-open-in-chrome/versions/submit/6602520/details),
paste the following two fields, then click **Submit Version**. Confirm the
resulting dashboard status. Approval/signing are later Mozilla decisions.

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
