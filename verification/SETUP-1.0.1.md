# Setup improvement — 1.0.1

- 33 Node tests passed, including the reused help-tab hash regression, fixed
  direct download URL, separate GitHub link, first-install guidance, unsupported
  platforms, and preserving a former help tab navigated to a website.
- Mozilla web-ext lint: zero errors, warnings or notices. Security invariants
  preserve exactly `activeTab` and `nativeMessaging`, no network APIs, no shell,
  no injected page scripts and the original native-helper boundary.
- Production helper, extension and installer each reproduce byte for byte.
  The native helper is byte-identical to the 1.0.0 helper. The new stable Setup
  filename is byte-identical to the versioned installer.
- Actual Firefox Developer Edition 159.0, in a disposable profile, opened the
  packaged setup page on install. The two buttons, error changes, actual
  toolbar click and narrow layout passed. Desktop/narrow/expanded screenshots
  were inspected. Existing Firefox profiles and helper registration were preserved.
- GitHub release, download-byte verification and Mozilla update status are
  recorded in publication/STATUS.md after completion.

![Actual packaged setup page in Firefox](setup-1.0.1.png)

Run the focused UI check with `python tests/setup_firefox.py`. After publication,
add `--download` to click the actual download button and compare Firefox’s
downloaded installer with the production build. This test does not run the
downloaded executable or alter an installed helper.
