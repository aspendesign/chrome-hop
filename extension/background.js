/* Chrome Hop: no content scripts, messages from websites, or network requests. */
"use strict";
(() => {
  const HOST = "io.github.aspendesign.chrome_hop";
  const MAX_URL = 16384;
  const OPEN_ALL = "open-all-tabs";
  let busy = false;
  let lastTab;
  let lastOpened = 0;
  let helpTab;

  browser.runtime.onInstalled.addListener(async details => {
    if (details.reason === "install" || details.reason === "update") {
      browser.menus.create({id: OPEN_ALL, title: "Open all tabs in this window", contexts: ["action"]});
    }
    if (details.reason !== "install") return;
    try { helpTab = (await browser.tabs.create({url: browser.runtime.getURL("help.html") + "#setup"})).id; } catch {}
  });

  browser.menus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === OPEN_ALL) return openAll(tab);
  });

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
      try {
        const existing = await browser.tabs.get(helpTab);
        if (existing.url?.startsWith(browser.runtime.getURL("help.html") + "#")) {
          await browser.tabs.update(helpTab, {url, active: true}); return;
        }
      } catch {}
      helpTab = undefined;
    }
    helpTab = (await browser.tabs.create({url})).id;
  }

  async function openURL(url) {
    let response;
    try { response = await browser.runtime.sendNativeMessage(HOST, {op: "open", url}); }
    catch { return "helper"; }
    if (response?.ok === true && response?.code === "opened") return;
    return response?.code === "chrome_not_found" ? "chrome" : response?.code === "invalid_message" ? "unsupported" : "launch";
  }

  async function openAll(tab) {
    if (!Number.isInteger(tab?.id) || !Number.isInteger(tab.windowId) || busy) return;
    busy = true;
    let opened = 0;
    try {
      // Request synchronously in the menu's user gesture, never on left-click.
      if (!await browser.permissions.request({permissions: ["tabs"]})) {
        await help("permission", tab.id); return;
      }
      // Snapshot only the explicitly selected window. No background tab polling.
      const tabs = await browser.tabs.query({windowId: tab.windowId});
      const supported = tabs.filter(item => validURL(item.url)).sort((a, b) => a.index - b.index);
      const skipped = tabs.length - supported.length;
      if (!supported.length) { await help("empty", tab.id); return; }
      await browser.action.setBadgeBackgroundColor({color: "#14654d", tabId: tab.id});
      for (const item of supported) {
        await browser.action.setBadgeText({text: "…", tabId: tab.id});
        await browser.action.setTitle({title: `Opening tab ${opened + 1} of ${supported.length} in Chrome…`, tabId: tab.id});
        // The unchanged helper still validates and opens exactly one URL per call.
        const code = await openURL(item.url);
        if (code) {
          await help(code, tab.id);
          await browser.action.setTitle({title: `Opened ${opened} of ${supported.length} tabs; stopped. See Chrome Hop help.`, tabId: tab.id});
          return;
        }
        opened++;
      }
      lastTab = tab.id; lastOpened = Date.now();
      await browser.action.setBadgeText({text: opened > 99 ? "99+" : String(opened), tabId: tab.id});
      await browser.action.setTitle({title: `Opened ${opened} tabs in Chrome; skipped ${skipped} unsupported tabs — Firefox tabs kept open`, tabId: tab.id});
    } catch {
      try { await help("permission", tab.id); } catch {}
    } finally { busy = false; }
  }

  browser.action.onClicked.addListener(async (tab) => {
    if (!Number.isInteger(tab.id) || busy || (lastTab === tab.id && Date.now() - lastOpened < 1000)) return;
    busy = true;
    try {
      await browser.action.setBadgeText({text: "", tabId: tab.id});
      if (!validURL(tab.url)) { await help("unsupported", tab.id); return; }
      const code = await openURL(tab.url);
      if (code) { await help(code, tab.id); return; }
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
