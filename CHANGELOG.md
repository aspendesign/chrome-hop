# Changelog

## 1.0.1 — 2026-10-21

- Direct **Download for Windows** button on the setup page, with a separate
  **View on GitHub** button. The installer downloads without an asset-list detour.
- Three short setup steps, first-install guidance, and expandable installation,
  repair and platform-support help.
- Correct help content when a reused tab changes from one error to another.
- Clear macOS/Linux/ARM availability instead of an incompatible Windows download.
- Stable installer filename for permanent direct links; versioned installers,
  checksums and build attestations remain available.
- Same two API permissions and unchanged native helper security boundary.

## 1.0.0 — 2026-10-20

- One-click HTTP(S) handoff from Firefox to installed Google Chrome Stable.
- Manifest V3, with only `activeTab` and `nativeMessaging` API permissions.
- Standalone, dependency-free Go helper with strict framing/URL validation,
  fixed Chrome discovery and direct single-argument launch.
- Per-user Windows 11 x64 installer with repair, upgrade and clean uninstall.
- Original icons, accessible local guidance, privacy policy, threat model,
  automated tests, reproducible builds, tagged releases and SHA-256 checksums.
- Submitted to Mozilla for public listing as version 1.0.0 (version ID 6602368).
  Status: Awaiting Review; public approval/signing remain an external step.
