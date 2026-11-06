// Browser check for the built page. Run it in the page with Chrome DevTools
// evaluate_script (sourcePath), at a phone viewport (390x844). It looks up each
// sample ZIP through the real form and returns a JSON report: what was shown,
// which offices each card carries, the vCard text of the first card, layout
// overflow, and whether the URL or title ever changed.
async () => {
  const ZIPS = ["98101", "10003", "42223", "82001", "20001", "00901", "96799", "33068", "99999", "12"];
  const startUrl = location.href, startTitle = document.title;
  const form = document.getElementById("cc-form");
  const zip = document.getElementById("cc-zip");
  const out = { zips: {} };
  for (const z of ZIPS) {
    zip.value = z;
    form.requestSubmit();
    const res = document.getElementById("cc-results");
    const r = {
      error: document.getElementById("cc-zip-error").hidden ? null : document.getElementById("cc-zip-error").textContent,
      chambers: [...res.querySelectorAll(".cc-chamber-title")].map(e => e.textContent),
      notes: [...res.querySelectorAll(".cc-message")].map(e => e.textContent),
      groups: [],
      houseLinks: [...res.querySelectorAll("a.cc-house-link")].map(a => a.target + " " + a.rel + " " + a.href),
    };
    for (const g of res.querySelectorAll(".cc-group")) {
      const entries = [];
      for (const li of g.querySelectorAll(".cc-official")) {
        const a = li.querySelector("a.cc-save");
        const e = { name: (li.querySelector(".cc-name") || {}).textContent || null, role: (li.querySelector(".cc-role") || {}).textContent || null, message: (li.querySelector(".cc-message") || {}).textContent || null };
        if (a) {
          const vcf = await (await fetch(a.href)).text();
          e.file = a.download;
          e.blob = a.href.startsWith("blob:");
          e.crlfOnly = !/[^\r]\n/.test(vcf);
          // A physical line ending in an odd number of backslashes means a fold split an escape.
          e.splitEscape = vcf.split("\r\n").some(l => /(^|[^\\])(\\\\)*\\$/.test(l));
          e.maxLineOctets =Math.max(...vcf.split("\r\n").map(l => new TextEncoder().encode(l).length));
          e.labels = vcf.split("\r\n").filter(l => /X-ABLabel/.test(l)).map(l => l.split(":").slice(1).join(":"));
          e.tels = vcf.split("\r\n").filter(l => /\.TEL/.test(l)).map(l => l.split(":")[1]);
          if (!out.firstCard) out.firstCard = vcf;
        }
        entries.push(e);
      }
      r.groups.push({ state: (g.querySelector(".cc-state") || {}).textContent || null, entries });
    }
    r.horizontalOverflow = document.documentElement.scrollWidth > window.innerWidth;
    out.zips[z] = r;
  }
  // A new search replaces the previous results (there is no Start over).
  zip.value = "10003"; form.requestSubmit();
  zip.value = "98101"; form.requestSubmit();
  out.newSearchReplaces = document.querySelectorAll("#cc-results .cc-official").length === 3;
  out.urlUnchanged = location.href === startUrl;
  out.titleUnchanged = document.title === startTitle;
  out.bodyFont = getComputedStyle(document.body).fontFamily.split(",")[0];
  out.pageBg = getComputedStyle(document.body).backgroundColor;
  out.nameFont = (() => { zip.value = "98101"; form.requestSubmit();
    const h = document.querySelector(".cc-name"); const c = getComputedStyle(h);
    return c.fontFamily.split(",")[0] + " " + c.fontWeight + " " + c.fontSize; })();
  out.colors = ["#cc-form button", ".cc-save", ".cc-name", ".cc-state", ".cc-chamber-title"].map(s => {
    const e = document.querySelector(s); if (!e) return [s, null];
    const c = getComputedStyle(e); return [s, c.color, c.backgroundColor];
  });
  out.saveButtonHeight = document.querySelector(".cc-save").getBoundingClientRect().height;
  out.submitHeight = form.querySelector("button").getBoundingClientRect().height;
  out.resources = performance.getEntriesByType("resource").map(e => new URL(e.name).host).filter((h, i, a) => a.indexOf(h) === i);
  return out;
}
