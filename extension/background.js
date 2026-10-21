/* Chrome Hop: no content scripts, messages from websites, or network requests. */
"use strict";
(() => {
  const HOST = "io.github.aspendesign.chrome_hop";
  const MAX_URL = 16384;
  let busy = false;
  let lastTab;
  let lastOpened = 0;
  let helpTab;

  function validURL(raw) {
    if (typeof raw !== "string" || new TextEncoder().encode(raw).length > MAX_URL ||
        /[\u0000-\u0020\u007f-\u009f\\"\s]/u.test(raw) || /%(?:0[0-9a-f]|1[0-9a-f]|7f)/i.test(raw)) return false;
    try {
      const target = new URL(raw);
      return (target.protocol === "http:" || target.protocol === "https:") &&
        /^https?:\/\//.test(raw) && !!target.hostname && !target.username && !target.password;
    } catch { return false; }
  }

  async function help(code, tabId) {
    await browser.action.setBadgeBackgroundColor({color: "#a33828", tabId});
    await browser.action.setBadgeText({text: "!", tabId});
    await browser.action.setTitle({title: "Chrome Hop needs attention — click to retry", tabId});
    const url = browser.runtime.getURL("help.html") + "#" + code;
    if (helpTab !== undefined) {
      try { await browser.tabs.update(helpTab, {url, active: true}); return; } catch { helpTab = undefined; }
    }
    helpTab = (await browser.tabs.create({url})).id;
  }

  browser.action.onClicked.addListener(async (tab) => {
    if (!Number.isInteger(tab.id) || busy || (lastTab === tab.id && Date.now() - lastOpened < 1000)) return;
    busy = true;
    try {
      await browser.action.setBadgeText({text: "", tabId: tab.id});
      if (!validURL(tab.url)) { await help("unsupported", tab.id); return; }
      let response;
      try { response = await browser.runtime.sendNativeMessage(HOST, {op: "open", url: tab.url}); }
      catch { await help("helper", tab.id); return; }
      if (response?.ok !== true || response?.code !== "opened") {
        const code = response?.code === "chrome_not_found" ? "chrome" : response?.code === "invalid_message" ? "unsupported" : "launch";
        await help(code, tab.id);
        return;
      }
      lastTab = tab.id;
      lastOpened = Date.now();
      await browser.action.setBadgeBackgroundColor({color: "#14654d", tabId: tab.id});
      await browser.action.setBadgeText({text: "✓", tabId: tab.id});
      await browser.action.setTitle({title: "Sent to Chrome — Firefox tab kept open", tabId: tab.id});
    } catch {
      // Closed tabs / a disappearing window need no persistent state or logging.
    } finally { busy = false; }
  });
})();
