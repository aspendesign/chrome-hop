# Threat model and security review

Review date: October 20, 2026. Scope: extension, Go native helper, per-user
installer, development tools and release workflows. This is an engineering
review with automated adversarial tests, not an independent third-party audit
or a proof that every vulnerability has been excluded.

## Assets and trust boundaries

Protect the clicked URL (including query tokens), the browser profiles, the
Windows account, and executable selection. Treat webpages and native input as
untrusted. Trust Firefox’s user-gesture permission enforcement, Windows’ known
folder APIs, the installed Chrome executable at standard paths, and reviewed
source/tooling obtained through official TLS endpoints and pinned hashes.

The page-to-native paths are explicit Firefox toolbar gestures. A left-click
uses `activeTab` for that clicked tab’s URL and requests no extra access. The
toolbar-only `menus` context adds **Open all tabs in this window** in 1.1.0.
That handler synchronously requests optional `tabs` permission, and only after
approval queries the clicked tab’s exact `windowId`. The grant persists in
Firefox until revoked, but this implementation performs no background polling
or tab queries outside that handler. There is no content script, page message
listener, external-message listener, persistent website access or injection.
The extension validates HTTP(S), rejects dangerous schemes/controls/credentials,
and sends exactly `{op: "open", url: "…"}` to one fixed native host. Error UI
uses predefined codes and text; raw URLs and native error strings are not shown.

Bulk handoff snapshots supported tabs in tab order and sends sequential,
unchanged one-URL messages. It shares the single-action busy guard, so another
bulk or left-click cannot create overlapping native launches. Errors stop the
remaining batch and report counts without URLs. Already-opened Chrome tabs
are not rolled back; retrying a batch can create duplicates. Unsupported URLs
are skipped before native messaging. Optional permission denial or revocation
does not fall back to host permissions or disable normal single-tab opening.

The native manifest permits only `chrome-hop@aspendesign.github.io`. Firefox
passes the initiating ID as a command-line argument; the host checks it again.
That extra argument check cannot authenticate other same-user native programs;
such a program could already rewrite HKCU or run Chrome directly.

## Message parsing and URL/argument injection

The native host reads one four-byte little-endian size header. It rejects zero
or over-32-KiB payloads before allocating, reads exactly that bounded payload,
and rejects invalid UTF-8, non-object JSON, unknown/duplicate/case-variant keys,
non-string fields, trailing JSON, missing fields and operations other than
`open`. It launches at most once, even when multiple frames are supplied.
A 10-second whole-process deadline bounds incomplete-frame/blocked-host life.
Stdout carries one framed sanitized response. No logging API receives a URL.

URLs must be at most 16 KiB, absolute HTTP(S), with a real parsed nonempty host.
Controls, whitespace, backslashes, raw double quotes, encoded ASCII controls,
invalid percent escapes, opaque URLs, userinfo, invalid host/port syntax,
IPv6 zone identifiers and unsupported schemes are refused. Localhost, IPv4,
IPv6, IDNs, normal queries, fragments and encoded text are supported. Browser
and Go checks differ slightly in strictness; native validation is authoritative
and a rejection opens a sanitized help page.

Chrome discovery uses `SHGetKnownFolderPath`, not environment variables, PATH,
arbitrary App Paths registry values or message-supplied paths. Only
`Google\Chrome\Application\chrome.exe` beneath Program Files, Program Files
(x86), or LocalAppData is considered. Relative paths, empty/nonregular files
and symlinks/junctions beneath those roots are rejected. Custom executables,
shell associations, scripts and shortcuts are unsupported.

`exec.Command(absoluteChromePath, validatedURL)` passes exactly one URL
argument. There are no user-controlled options, templates, command strings,
`cmd.exe`, PowerShell, shell expansion or `exec.LookPath`. A URL that happens
to contain `&`, `|`, quotes encoded as `%22`, Unicode or `--switch` in a path
cannot become a command. Leading-switch inputs fail URL validation.

The GUI-subsystem helper creates no console. Chrome is deliberately allowed
to show its requested GUI; its launch uses Windows’ no-console creation flag.
It receives no inherited Firefox stdin/stdout pipes. Chrome is launched with
`CREATE_BREAKAWAY_FROM_JOB` so Firefox’s native-host job cleanup does not kill
the browser after the helper responds. The helper releases the Chrome process
handle rather than waiting for the browser’s lifetime. This follows
[Mozilla’s documented Windows process behavior](https://bugzilla.mozilla.org/show_bug.cgi?id=1573469).

## Installer and update boundaries

Inno Setup uses `PrivilegesRequired=lowest`, Windows 11 x64, LocalAppData and
HKCU only. Its one native registry entry points to an absolute generated
UTF-8 descriptor. JSON paths escape backslashes/quotes. Only the one extension
ID is authorized. No service, scheduled task, startup item, browser default,
profile edit, other browser registration, runtime downloader or installer
`[Run]` command is present. Same-AppId repair/upgrade and clean uninstall are
tested with the compiled installer, including a Unicode path with spaces.

Firefox updates use Mozilla’s listed signing/review infrastructure after
approval. The helper has no updater or network client. Download new helper
versions from the release page and verify checksums. There is no purchased
Authenticode certificate. SHA-256 detects corruption/tampering relative to a
trusted checksum; it is not a publisher certificate or detached signature.

## Supply chain

The released native executable uses only Go’s standard library, Windows system
DLLs and installed Chrome. The extension ships readable handwritten source
and PNGs, with no runtime npm dependencies or transformed code. The installer
bundles only those reviewed files. Official Go/Inno downloads have pinned
SHA-256 checks; npm tooling has a committed integrity lockfile and lifecycle
scripts are disabled. Official GitHub Actions are pinned to full commits.
Untrusted PR jobs have read-only tokens; release creation is a separate tag-only
job. AMO submission is manual, public/listed, and uses a separate environment.

The full development `npm audit` currently reports **GHSA-86w9-cpqp-85rv** in
`node-forge` 1.4.0 through Mozilla `web-ext`’s Android adb tooling, with no
published fix at review time. It is build/development-only, never shipped and
not used by the Firefox desktop lint/build/sign paths in this project. The
production-only audit reports zero advisories. This advisory is recorded,
not hidden or “fixed” by downgrading Mozilla tooling or replacing its crypto.
Review it when updating tools. See the [official advisory](https://github.com/advisories/GHSA-86w9-cpqp-85rv).

## Residual risks and practical limits

- A compromised Windows account, known-folder registration, installed Chrome,
  GitHub maintainer account, Mozilla account, compiler or signed add-on update
  is outside this helper’s sandbox guarantees. Chrome is identified by fixed
  installation location, not an embedded Google signing-certificate pin.
- File path checks and process creation are separate OS operations. A process
  already able to replace an allowed executable could race them. It already
  has equivalent per-user execution authority.
- Opening a URL can trigger normal website actions, browser downloads, Chrome
  extensions, history/sync and redirects. Chrome Hop does not inspect or proxy
  those operations. Clicking is consent to open that address in Chrome.
- URLs can carry private tokens. They exist briefly in memory and in Chrome’s
  command-line launch as required by this architecture. They are never written
  to Chrome Hop diagnostics, but same-user OS tools/Chrome may observe them.
- A reported `opened` status means Windows accepted process creation, not that
  Chrome loaded the page or was permitted by enterprise policy to show it.
- Crash, power loss or a malicious same-user program can disrupt installation
  or native messaging. Repair is a bounded re-run of the same installer.

## Tests and evidence

Parser tests cover sizes, truncation, duplicate keys/frames, invalid UTF-8/JSON,
surrogates, schemes, percent/control input, credentials, CLI injection, path
discovery, missing Chrome and sanitized responses. Fuzzing checks parser/serve
agreement and launch count. Extension tests check the permission budget,
clicked-tab handling, missing helper, native errors and duplicate-click
suppression. Installer tests use the actual compiled payload/registry readback.
The separate Firefox integration test uses the unchanged release extension and
binary. See [verification results](../verification/RESULTS.md) for actual run
results and the scope of browser evidence.

## Authoritative references checked

- [activeTab](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/activeTab_permission)
- [Toolbar action event](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/action/onClicked)
- [Mozilla native messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)
- [Mozilla native-data disclosure rule](https://extensionworkshop.com/documentation/develop/best-practices-for-collecting-user-data-consents/)
- [Built-in data consent](https://extensionworkshop.com/documentation/develop/firefox-builtin-data-consent/)
- [AMO public submission](https://extensionworkshop.com/documentation/publish/submitting-an-add-on/)
- [Mozilla web-ext reference](https://extensionworkshop.com/documentation/develop/web-ext-command-reference/)
- [Go process execution](https://pkg.go.dev/os/exec)
- [Windows known folders](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)
- [Inno per-user mode](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm)
- [Inno supply chain and reproducibility](https://jrsoftware.org/ishelp/topic_securitymeasures.htm)
- [GitHub workflow hardening](https://docs.github.com/en/actions/reference/security/secure-use)
