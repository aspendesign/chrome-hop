# Contributing

Keep Chrome Hop small. Open an issue before adding a capability or changing
the extension ID, host name, message format, permissions or installer scope.
Use harmless fixture URLs and never attach browser data or credentials.

Run the checks in [BUILDING.md](docs/BUILDING.md). New input-validation behavior
needs parser and extension tests. Changes at the native boundary need a real
Windows integration test and updated security notes. Tests must not control
personal browser profiles or leave services, listeners or console windows.

The CI and release workflows build from public source. Pull requests have
read-only tokens and no AMO secrets. Tag publication and Mozilla submission
are separate operations. Do not claim a ZIP is signed or an AMO listing is live
without verifying the corresponding result.
