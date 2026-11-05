// Throwaway research fixture: ZIP lookup plus per-official vCard blob links.
// Plain JS with no jQuery dependency, so it works whether it runs before or
// after the theme's scripts. The probes below must survive Jekyll unchanged:
// LIQUID_PROBE_1 = "{{ site.title }}"; LIQUID_PROBE_2 = "{% raw_probe %}";
(function () {
  "use strict";
  var LIQUID_PROBE = ["{{ site.title }}", "{% if true %}x{% endif %}"];
  function start() {
    var el = document.getElementById("cc-data");
    var data = JSON.parse(el.textContent);
    var form = document.getElementById("cc-form");
    var input = document.getElementById("cc-zip");
    var out = document.getElementById("cc-results");
    window.ccProbe = LIQUID_PROBE;

    function esc(s) {
      return String(s).replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/([,;])/g, "\\$1");
    }
    function vcard(o) {
      var lines = ["BEGIN:VCARD", "VERSION:3.0",
        "N:" + esc(o.name.family) + ";" + esc(o.name.given) + ";;;",
        "FN:" + esc(o.name.full)];
      o.offices.forEach(function (of) {
        of.phones.forEach(function (p) {
          lines.push("TEL;TYPE=" + (p.type === "fax" ? "FAX" : "VOICE") + ":" + p.number);
        });
        if (of.address) {
          var a = of.address;
          lines.push("ADR;TYPE=WORK:;;" + esc(a.lines.join(", ")) + ";" + esc(a.city) + ";" +
            esc(a.region) + ";" + esc(a.postalCode) + ";" + esc(a.country));
        }
      });
      o.links.forEach(function (l) { lines.push("URL:" + l.url); });
      lines.push("END:VCARD");
      return lines.join("\r\n") + "\r\n";
    }
    function row(id) {
      var o = data.officials[id];
      var li = document.createElement("li");
      li.className = "cc-official";
      var a = document.createElement("a");
      a.className = "btn btn-primary btn-sm cc-save";
      a.textContent = "Save contact";
      a.download = o.name.family.replace(/[^A-Za-z0-9]+/g, "-") + ".vcf";
      a.href = URL.createObjectURL(new Blob([vcard(o)], { type: "text/vcard;charset=utf-8" }));
      li.appendChild(document.createTextNode(o.name.full + " (" + o.role + ", " + o.state + ") "));
      li.appendChild(a);
      return li;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      out.textContent = "";
      var cands = data.zipMatches[input.value.trim()];
      if (!cands) { out.textContent = "No match for that ZIP."; return; }
      var seen = {};
      cands.forEach(function (c) {
        [c.representativeId].concat(data.states[c.state].senatorIds).forEach(function (id) {
          if (!seen[id]) { seen[id] = 1; out.appendChild(row(id)); }
        });
      });
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
