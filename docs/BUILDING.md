# Build and release

## Pinned tools

Windows builds use Go **1.27.3**, Node.js **24.15.0**, Mozilla `web-ext`
**10.8.0**, and Inno Setup **7.1.0 x64**. Python 3.11 or later orchestrates
development commands with the standard library. Pillow is optional, used only
to regenerate already-committed original icons; it is not part of the build.

`python scripts/bootstrap.py` downloads the exact official Go and Inno Setup
versions to `.tools/`, checks their SHA-256 against constants committed in the
script (verified against official release metadata), and installs Inno Setup per-user there.
No tool is downloaded or executed by the product installer.

```powershell
python scripts/bootstrap.py
python scripts/npm.py ci --ignore-scripts --no-fund --no-audit
python scripts/run.py node.exe --test --test-isolation=none tests/extension.test.cjs
python scripts/run.py node.exe node_modules/web-ext/bin/web-ext.js lint --source-dir extension --no-config-discovery --warnings-as-errors
python scripts/security_check.py
python scripts/run.py .tools/go/bin/go.exe test ./cmd/... ./internal/... -cover
python scripts/run.py .tools/go/bin/go.exe vet ./cmd/... ./internal/...
python scripts/run.py .tools/go/bin/go.exe test ./internal/host -run=^$ -fuzz=FuzzMessage -fuzztime=20s -parallel=2
python scripts/build.py
python tests/windows_install.py
python scripts/package_submission.py
```

The install test refuses an existing Chrome Hop install/host registration,
uses a task-owned Unicode path with spaces, and uninstalls its changes in a
`finally` scope. The browser integration test is intentionally separate:

```powershell
python tests/firefox_e2e.py
```

It requires the pinned Mozilla geckodriver 0.37.1 under `.tools/geckodriver/`
and Firefox Developer Edition. It creates an isolated headless Firefox profile,
installs the exact release ZIP temporarily, clicks the actual toolbar widget,
uses the actual release installer/helper, and checks a benign localhost request
from real Chrome. Its WebDriver and HTTP fixture endpoints bind loopback only
and close at test completion. A second case acknowledges an `https://example.com/`
launch; the test makes no claim to verify that remote page’s completed load.
Chrome receives those URLs in its normal profile because production deliberately
has no test-only profile flags. Existing tabs/profile data are not inspected.

## Reproducibility

The helper is built with `CGO_ENABLED=0`, `GOAMD64=v1`, `-trimpath`,
`-buildvcs=false`, empty build ID, stripped symbols and Windows GUI subsystem.
It has zero external Go modules. The extension is raw readable JavaScript/HTML
with no transpiler, bundler or minifier. ZIP entries have fixed timestamps,
permissions and order. Inno Setup file entries omit input timestamps.
The build compares two independent helper, extension and installer compilations
and fails if bytes differ. CI builds the same tag on a fresh Windows runner.
For 1.0.0, the fresh Windows CI artifacts and the public release downloads also
matched the ASUS builds byte for byte.

`dist/` contains the versioned installer, standalone helper, unsigned AMO
submission ZIP, `BUILD-INFO.json`, submission assets and `SHA256SUMS.txt`.
The standalone helper does not register itself; ordinary users need the installer.

Checksums provide integrity, not a purchased publisher identity certificate.
No release checksum signature is claimed unless an independently verifiable
signature is actually verified. Version 1.0.0 has verified GitHub/Sigstore build
attestations covering the binaries, ZIPs, metadata and checksum file. Verify:

```powershell
gh attestation verify .\SHA256SUMS.txt --repo aspendesign/chrome-hop
gh attestation verify .\ChromeHop-Setup-1.0.0-windows-x64.exe --repo aspendesign/chrome-hop
```

These attest the tagged GitHub build; they are separate from Windows
Authenticode signing. No certificate or private signing-key service was bought.

## GitHub releases

`Test and package` runs for main-branch pushes and pull requests, with read-only
permissions. `Release` runs only for a version tag matching the manifest, rebuilds
and tests the artifacts, then publishes through the official GitHub CLI in a
separate job with only `contents: write`. Every action is an official `actions/`
action pinned to a full commit. No self-hosted runner or paid service is used.

Update the manifest/package version, changelog and release notes; test and commit.
Push `vX.Y.Z` after reviewing the source. The workflow rejects a mismatched tag.
Do not retag a published release. Use a new version for a correction.

## Mozilla public submission

The `Submit listed Firefox add-on` workflow is manual and separate from ordinary
pushes and GitHub publication. It downloads the exact release submission ZIP,
checks its SHA-256, and uses `--channel listed`. It needs existing authorized
AMO API credentials in `AMO_API_KEY` and `AMO_API_SECRET`, preferably stored in
the `mozilla-production` environment, which is configured with owner review
and a main-branch rule. No credentials are in this repository or were exported
in this run. Without those secrets the optional API workflow fails before
submission. The 1.0.0 listed submission was completed through the existing
authenticated browser session and is awaiting Mozilla review.

The same package may be submitted through the authenticated AMO Developer Hub.
The listing text, privacy policy, original icon, screenshots and reviewer notes
are in `publication/`. Check AMO’s dashboard after submission. Submitted,
approved, signed and publicly listed are separate states. Do not advertise an
install link before the listing is actually available.
