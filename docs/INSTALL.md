# Install Chrome Hop

Chrome Hop opens the current Firefox web page in Google Chrome on Windows 11.
There are two small installations: the Firefox add-on and its Windows helper.

1. Install **Chrome Hop — Open in Chrome** from Mozilla Add-ons when its listed release is available. The [release page](https://github.com/aspendesign/chrome-hop/releases/latest) records the current Mozilla status. An unsigned submission ZIP is for reviewers/development and cannot be installed in normal Firefox.
2. Download **ChromeHop-Setup-1.0.0-windows-x64.exe** from the [official release](https://github.com/aspendesign/chrome-hop/releases/latest) and run it. This installs just for your Windows account, with no administrator prompt.
3. In Firefox, open the extensions menu (the puzzle piece), find Chrome Hop, open its settings menu, and choose **Pin to Toolbar**.
4. Open any HTTP or HTTPS page and click the Chrome Hop button. Chrome opens the same address. The Firefox tab stays open.

Google Chrome **Stable** must already be installed in a normal Windows location.
Local development pages, such as `http://localhost:3000/`, work too.
Firefox settings, local files, special browser pages and links with embedded
usernames/passwords are not supported.

## What the prompts mean

Firefox requests only `activeTab` (the tab you click) and `nativeMessaging`
(talk to the installed helper). Mozilla also displays **browsing activity**
in its data disclosure because the selected URL leaves Firefox for a local
program. That handoff happens only when you click. Chrome Hop sends no data
to a developer server and has no telemetry.

Chrome loads the selected URL normally, using its own profile, cookies and
settings. URLs may include private query strings or access tokens. Chrome
Hop does not transfer your Firefox login session, passwords or page content.

The installer is not Authenticode-signed; no signing certificate was purchased.
Windows may show an unknown-publisher/SmartScreen message. Obtain the installer
only from this repository and verify its SHA-256 against `SHA256SUMS.txt` if you
need to check the download. Organization-managed machines may disallow it.

## Update, repair and remove

Run the latest installer again to upgrade or repair the connection. The
Firefox add-on updates through Mozilla once approved and publicly listed.
The helper has no background updater; download updates from GitHub Releases.

To remove it, use **Windows Settings → Apps → Installed apps → Chrome Hop
Windows Helper → Uninstall**. Remove the Firefox add-on separately using
Firefox’s Add-ons Manager. Browser profiles, bookmarks and settings are untouched.

See [troubleshooting](TROUBLESHOOTING.md) if a button click opens a help page.
