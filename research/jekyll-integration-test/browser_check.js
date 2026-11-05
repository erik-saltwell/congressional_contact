// Throwaway research fixture: run in the built page (Chrome DevTools
// evaluate_script with sourcePath). Exercises the ZIP lookup, the vCard blob,
// theme coexistence and phone layout. Returns a JSON-serialisable report.
async () => {
  const r = {};
  r.jquery = typeof window.jQuery;
  r.themeJsLoaded = [...document.scripts].some(s => /beautifuljekyll\.js$/.test(s.src));
  r.themeCssRules = [...document.styleSheets]
    .filter(s => /beautifuljekyll\.css$/.test(s.href || ""))
    .map(s => s.cssRules.length)[0];
  r.probe = window.ccProbe;
  const zip = document.getElementById("cc-zip");
  zip.focus();
  zip.value = "01001";
  document.getElementById("cc-form").requestSubmit();
  const items = [...document.querySelectorAll("#cc-results li")];
  r.officials = items.length;
  const a = items[0] && items[0].querySelector("a");
  r.blobLink = !!a && a.href.startsWith("blob:") && a.download.endsWith(".vcf");
  const vcf = a ? await (await fetch(a.href)).text() : "";
  r.vcardOk = vcf.startsWith("BEGIN:VCARD\r\nVERSION:3.0\r\n") && vcf.endsWith("END:VCARD\r\n");
  document.dispatchEvent(new KeyboardEvent("keyup", { key: "Escape", bubbles: true }));
  r.zipKeepsFocusAfterThemeKeyHandler = document.activeElement === zip && zip.value === "01001";
  const searchLink = document.getElementById("nav-search-link");
  if (searchLink) {
    searchLink.click();
    const overlay = document.getElementById("beautifuljekyll-search-overlay");
    r.siteSearchOpens = getComputedStyle(overlay).display !== "none";
    document.getElementById("nav-search-exit").click();
  }
  r.bodyFont = getComputedStyle(document.body).fontFamily.split(",")[0];
  r.buttonBg = getComputedStyle(document.querySelector(".cc-app .btn-primary")).backgroundColor;
  r.horizontalOverflow = document.documentElement.scrollWidth > window.innerWidth;
  r.navbar = !!document.getElementById("main-navbar");
  r.footer = !!document.querySelector("footer");
  return r;
}
