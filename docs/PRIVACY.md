# Chrome Hop privacy policy

Effective October 21, 2026. Applies to the Firefox add-on and Windows helper.

**Clicking Chrome Hop sends the current tab’s HTTP(S) address to the Chrome
Hop helper on your computer, which passes it to your installed Google Chrome.**
The address can include its path, query string and fragment. Right-clicking
the toolbar button and selecting **Open all tabs in this window** sends the
HTTP(S) addresses of that window’s tabs, one by one, after you allow optional
tab-address access. Other windows are excluded. Unsupported tabs are skipped.
No web address is transferred until you invoke one of these actions.

Chrome Hop does not collect browsing history, read page content, copy cookies,
transfer passwords, monitor tabs in the background, inject scripts into websites, or store
URLs. It has no accounts, analytics, advertising, telemetry, URL logs or crash
reporting. Neither the add-on nor the helper makes network requests. The
developer receives no information through the product.

Mozilla treats the local native-message handoff as data transmission, so the
manifest accurately declares the `browsingActivity` data category. It is needed
to send the address or current-window addresses you explicitly choose to the
local helper and Chrome. Required permissions are `activeTab`, `nativeMessaging`
and `menus`. The optional `tabs` permission is requested only by **Open all tabs**;
Firefox remembers a grant until you revoke it. Left-click does not request it.
Chrome Hop does not read tab titles, page content or historical visits. A tab
snapshot exists in memory for the batch and is not logged, stored or uploaded.

Chrome itself loads the selected address and may keep history, use cookies,
sync data, or contact network services according to your Chrome settings and
Google’s policies. A site may see the same address twice, once in each browser.
Firefox login sessions and page state are not copied. Avoid sending a URL with
a sensitive token unless you want Chrome to receive it. Credentials embedded
as `user:password@host` are rejected.

The installer stores its helper, host descriptor, license, install instructions
and uninstaller under your local application directory. Its HKCU registry
entries register that helper and its uninstaller. It does not scan or modify
browser profiles. Uninstall removes the helper and its registration.

GitHub handles repository visits, downloads and voluntary issue reports under
its own policies. Mozilla handles add-on installation/update requests under its
own policies. Please remove private URLs, tokens and personal data before
posting an issue. For security reports, see [SECURITY.md](../SECURITY.md).
