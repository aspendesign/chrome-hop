"use strict";
const messages = {
  helper: ["One small setup. Then you’re ready to hop.", "Install the Windows helper below. If you already installed it, run the latest installer again to repair the connection."],
  chrome: ["Let’s find Google Chrome.", "Install Google Chrome Stable from google.com/chrome for this Windows account, then return to your Firefox tab and try again. Custom locations and Chrome Beta/Canary are not supported."],
  unsupported: ["This page can’t hop.", "Chrome Hop opens HTTP and HTTPS web pages, including localhost. Firefox settings, files, special browser pages, credential-in-URL links, and malformed URLs can’t be sent."],
  launch: ["Chrome couldn’t be opened.", "Try opening Google Chrome yourself, then click Chrome Hop again. If the issue continues, reinstall the latest Windows helper."]
};
const message = messages[location.hash.slice(1)] || messages.helper;
document.getElementById("heading").textContent = message[0];
document.getElementById("detail").textContent = message[1];
