// Browser check for the help overlay and Copy link (phase 6). Run it with Chrome
// DevTools evaluate_script (sourcePath) on the built page, at 390x844, loaded
// without #help. It searches a ZIP, scrolls, opens and closes help in each way,
// and reports focus, scroll position, URL and title, and what Copy link copies.
async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const out = {};
  const startUrl = location.href, startTitle = document.title;
  const dlg = document.getElementById("cc-help");
  const zip = document.getElementById("cc-zip");
  zip.value = "10003";
  document.getElementById("cc-form").requestSubmit();
  await wait(100);
  out.resultsHelpLink = !!document.querySelector("#cc-results .cc-help-open");
  window.scrollTo(0, 400);
  await wait(50);
  const y = window.scrollY;

  // Open from the link under the results, close with Escape.
  const link = document.querySelector("#cc-results .cc-help-open");
  link.focus();
  link.click();
  await wait(50);
  out.openFromLink = dlg.open;
  out.modal = dlg.matches(":modal");
  out.focusInside = dlg.contains(document.activeElement);
  out.focusOn = document.activeElement.textContent.trim();
  out.urlWhileOpen = location.href === startUrl;
  out.dialogFits = dlg.getBoundingClientRect().width <= window.innerWidth;
  document.activeElement.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
  // Synthetic keys do not trigger the native cancel; use the dialog's own path.
  if (dlg.open) dlg.requestClose ? dlg.requestClose() : dlg.close();
  await wait(50);
  out.closedByCancel = !dlg.open;
  out.focusReturned = document.activeElement === link;
  out.scrollKept = Math.abs(window.scrollY - y) < 2;

  // Close button, done button and backdrop.
  for (const how of ["close", "done", "backdrop"]) {
    link.click();
    await wait(30);
    if (how === "close") dlg.querySelector(".cc-help-close").click();
    if (how === "done") dlg.querySelector(".cc-help-done").click();
    if (how === "backdrop") dlg.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    await wait(30);
    out["closedBy_" + how] = !dlg.open;
  }

  // Copy link: the page link and the help link, with no ZIP.
  const copied = [];
  const orig = navigator.clipboard && navigator.clipboard.writeText;
  if (navigator.clipboard) navigator.clipboard.writeText = t => { copied.push(t); return Promise.resolve(); };
  // The only Copy link is in the overlay (the line under the ZIP form was removed).
  out.onlyCopyInOverlay = [...document.querySelectorAll(".cc-copy")].every(b => dlg.contains(b));
  link.click();
  await wait(30);
  dlg.querySelector(".cc-copy").click();
  await wait(30);
  out.helpStatus = dlg.querySelector(".cc-help-share + .cc-copy-status").textContent;
  // A failed copy shows the link in a box, selected.
  if (navigator.clipboard) navigator.clipboard.writeText = () => Promise.reject(new Error("denied"));
  dlg.querySelector(".cc-copy").click();
  await wait(30);
  const box = dlg.querySelector(".cc-copy-box");
  out.failShowsBox = !!box && box.value === copied[0] && document.activeElement === box;
  if (navigator.clipboard && orig) navigator.clipboard.writeText = orig;
  dlg.close();
  await wait(30);
  out.statusClearedOnClose = dlg.querySelector(".cc-copy-status").textContent === "";
  out.copied = copied;
  out.copiedHasNoZip = copied.every(u => !/10003|\?/.test(u));
  out.urlUnchanged = location.href === startUrl;
  out.titleUnchanged = document.title === startTitle;
  out.horizontalOverflow = document.documentElement.scrollWidth > window.innerWidth;
  return out;
}
