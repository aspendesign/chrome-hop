# Security policy

Version 1.0.x is the supported release line. Use the latest published helper
installer and approved Mozilla add-on version.

Please report a potential vulnerability through
[GitHub private vulnerability reporting](https://github.com/aspendesign/chrome-hop/security/advisories/new).
Do not include personal URLs, access tokens, cookies or browser-profile data.
Include the affected version, a harmless reproduction and expected impact.
No paid bounty or response-time guarantee is offered.

The native host is single-purpose and per-user. It is not a boundary against
malware already running as your Windows account, a compromised Chrome install,
or a compromised Firefox/add-on update. See the
[threat model](docs/SECURITY-REVIEW.md) for details.

An API permission increase, host allowlist change, custom executable support,
website messaging, telemetry or arbitrary argument support must be treated as
a security-sensitive product redesign, not a routine feature addition.
