"use strict";
(() => {
  const messages = {
    setup: ["One quick install. Then you’re ready to hop.", "Install the small Chrome Hop helper once so Firefox can open your pages in Google Chrome."],
    helper: ["One quick install. Then you’re ready to hop.", "Download and open the Chrome Hop installer below. Already installed? Run it again to repair the connection."],
    chrome: ["Let’s find Google Chrome.", "The helper is installed, but Google Chrome Stable wasn’t found. Install Chrome in its normal location, then try again."],
    unsupported: ["This page can’t hop.", "Open a normal HTTP or HTTPS web page and click Chrome Hop there. Firefox settings, extension pages, local files, and links with embedded passwords can’t be sent."],
    launch: ["Chrome couldn’t be opened.", "Try opening Google Chrome yourself, then click Chrome Hop again. If that doesn’t help, use the download below to repair the helper."],
    permission: ["Opening all tabs needs your permission.", "Right-click Chrome Hop and choose Open all tabs in this window, then allow access to tab addresses in Firefox’s prompt. Left-click still opens just the current tab without that extra permission."],
    empty: ["No web pages to open in this window.", "Chrome Hop can send HTTP and HTTPS web pages. Firefox settings, extension pages, files and other unsupported tabs are skipped. Your Firefox tabs stay open."]
  };
  let platform;
  const byId = id => document.getElementById(id);
  function render() {
    const requested = location.hash.slice(1);
    const code = Object.hasOwn(messages, requested) ? requested : "setup";
    const message = messages[code];
    byId("heading").textContent = message[0];
    byId("detail").textContent = message[1];
    const needsHelper = ["setup", "helper", "launch"].includes(code);
    const supported = !platform || (platform.os === "win" && platform.arch === "x86-64");
    byId("windows-setup").hidden = !needsHelper || !supported;
    byId("platform-note").hidden = !needsHelper || supported;
    byId("page-help").hidden = code !== "unsupported" && code !== "empty";
    byId("chrome-help").hidden = code !== "chrome";
    if (needsHelper && !supported) {
      const name = platform.os === "mac" ? "macOS" : platform.os === "linux" ? "Linux" : platform.os === "win" ? "this Windows architecture" : "this platform";
      byId("heading").textContent = "A helper for " + name + " isn’t available yet.";
      byId("detail").textContent = "Chrome Hop currently works on Windows 11 x64. See GitHub for supported platforms and release details.";
    }
  }
  addEventListener("hashchange", render);
  render();
  // Local platform information stays here. No native app or network is called.
  browser.runtime.getPlatformInfo().then(info => { platform = info; render(); }).catch(() => {});
})();
