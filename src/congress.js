// Congressional Contact: ZIP lookup and one vCard per official.
// Shared by the Jekyll page and the standalone file. It reads its data from the
// #cc-data element, makes no network requests, never changes the URL or the
// page title, and fires no analytics events. No jQuery: it may run before or
// after the host theme's scripts.
(function () {
  "use strict";

  var SCHEMA_VERSION = 1;
  var HOUSE_LOOKUP = "https://www.house.gov/representatives/find-your-representative";

  var data, zipKeys, form, input, errorEl, results;
  var blobUrls = [];

  // ------------------------------------------------------------ lookup

  function zipIndex(zip) {
    // zipOffices is aligned with the sorted keys of zipMatches.
    var lo = 0, hi = zipKeys.length - 1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (zipKeys[mid] === zip) return mid;
      if (zipKeys[mid] < zip) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
  }

  // The candidate order must match zip_candidates() in tools/build_data.py:
  // the House seat of each matched seat in order, then, for each distinct state
  // in order of first appearance, its senator slots.
  function candidates(zip) {
    var i = zipIndex(zip);
    if (i < 0) return null;
    var seats = data.zipMatches[zip];
    var code = data.zipOffices[i];
    var list = [], states = [];
    seats.forEach(function (seat) {
      var st = seat.split("-")[0];
      list.push({ id: data.houseSeats[seat], chamber: "house", state: st, seat: seat });
      if (states.indexOf(st) < 0) states.push(st);
    });
    states.forEach(function (st) {
      data.states[st].senators.forEach(function (id) {
        list.push({ id: id, chamber: "senate", state: st, seat: null });
      });
    });
    list.forEach(function (c, n) {
      var ch = code.charAt(n);
      c.local = ch === "-" || ch === "" ? null : Number(ch);
    });
    return { states: states, list: list };
  }

  // ------------------------------------------------------------ wording

  function ordinal(n) {
    var s = ["th", "st", "nd", "rd"], v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  }

  function stateName(st) {
    return data.states[st].name;
  }

  // "the District of Columbia" in running text.
  function stateInText(st) {
    var name = stateName(st);
    return /^District /.test(name) ? "the " + name : name;
  }

  // The section heading already says Senator(s), so senators get no role line.
  function roleLine(o) {
    if (o.role === "senator") return null;
    if (o.role === "delegate") return "Delegate to the House";
    if (o.role === "resident-commissioner") return "Resident Commissioner in the House";
    return o.district === 0 ? "At large" : ordinal(o.district) + " district";
  }

  function cardTitle(o) {
    var where = stateInText(o.state);
    if (o.role === "senator") return "U.S. Senator for " + where;
    if (o.role === "delegate") return "Delegate to the U.S. House for " + where;
    if (o.role === "resident-commissioner") return "Resident Commissioner for " + where;
    if (o.district === 0) return "U.S. Representative for " + where + " (at large)";
    return "U.S. Representative for " + where + "'s " + ordinal(o.district) + " district";
  }

  function vacantLine(c) {
    if (c.chamber === "senate") return "One of " + stateInText(c.state) + "'s Senate seats is vacant.";
    var d = Number(c.seat.split("-")[1]);
    return "The House seat for " + stateInText(c.state) +
      (d === 0 ? "" : "'s " + ordinal(d) + " district") + " is vacant.";
  }

  // Card labels avoid commas, which some contacts apps show with their escape.
  function officeLabel(office) {
    if (office.kind === "dc") return "DC office";
    // A delegate's local office in Washington would read too much like "DC office".
    if (office.address && office.address.region === "DC") return "District office";
    return office.label.replace(/,\s*[A-Z]{2}\b/, "").replace(/,/g, "");
  }

  // ------------------------------------------------------------ vCard 3.0

  function esc(s) {
    return String(s).replace(/\\/g, "\\\\").replace(/\r?\n/g, "\\n").replace(/([,;])/g, "\\$1");
  }

  function octets(ch) {
    var c = ch.codePointAt(0);
    return c < 0x80 ? 1 : c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;
  }

  // Fold at 75 octets (RFC 2425), never splitting a UTF-8 character or an
  // escape such as "\,", which some contacts apps misread when split.
  function fold(line) {
    var out = "", used = 0, limit = 75;
    (line.match(/\\[\s\S]|[\s\S]/gu) || []).forEach(function (ch) {
      var n = Array.from(ch).reduce(function (sum, c) { return sum + octets(c); }, 0);
      if (used + n > limit) {
        out += "\r\n ";
        used = 1;
      }
      out += ch;
      used += n;
    });
    return out;
  }

  function cardOffices(o, local) {
    var list = o.offices.filter(function (x) { return x.kind === "dc"; }).slice(0, 1);
    if (local !== null && o.offices[local]) list.push(o.offices[local]);
    return list;
  }

  function vcard(o, local) {
    var lines = ["BEGIN:VCARD", "VERSION:3.0", "PRODID:-//Congressional Contact//EN"];
    var n = 0;
    // Each labelled entry carries its label twice (owner tests, 2026-11-06):
    // X-ABLabel for Apple and desktop Google Contacts, and a custom TYPE=X-label,
    // which Android's contacts import reads. A plain TYPE=WORK showed "Work".
    function item(prop, types, value, label) {
      n += 1;
      var custom = "X-" + label.replace(/[,;:"\\]/g, "");
      lines.push("item" + n + "." + prop + ";TYPE=" + types.concat(custom).join(",") + ":" + value);
      lines.push("item" + n + ".X-ABLabel:" + esc(label));
    }
    var nm = o.name;
    lines.push("N:" + [nm.family, nm.given, "", "", nm.suffix || ""].map(esc).join(";"));
    lines.push("FN:" + esc(nm.full));
    lines.push("ORG:" + (o.role === "senator" ? "U.S. Senate" : "U.S. House of Representatives"));
    lines.push("TITLE:" + esc(cardTitle(o)));

    var seen = {};
    cardOffices(o, local).forEach(function (office) {
      var label = officeLabel(office);
      office.phones.forEach(function (p) {
        if (seen[p.number]) return;
        seen[p.number] = true;
        item("TEL", [], p.number, label);
      });
      var a = office.address;
      if (a) {
        item("ADR", [], ["", "", a.lines.join(", "), a.city, a.region, a.postalCode, a.country]
          .map(esc).join(";"), label);
      }
    });
    o.emails.forEach(function (e) {
      var label = e.purpose === "general" ? "Email" : "Email (" + e.purpose + ")";
      item("EMAIL", ["INTERNET"], e.address, label);
    });
    o.links.forEach(function (l) {
      var label = l.purpose === "website" ? "Website" : "Share your views";
      item("URL", [], l.url, label);
    });
    // The note is only the title (owner, 2026-11-06); REV still dates the card.
    lines.push("NOTE:" + esc(cardTitle(o)));
    lines.push("UID:congressional-contact-" + o.id);
    lines.push("REV:" + data.generatedAt);
    lines.push("END:VCARD");
    return lines.map(fold).join("\r\n") + "\r\n";
  }

  function fileName(o) {
    var s = (o.name.given + "-" + o.name.family).normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return s.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") + ".vcf";
  }

  // ------------------------------------------------------------ rendering

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  var newTabNoted = false;

  // Only the first house.gov link on the page says that it opens a new tab.
  function lookupLink(text) {
    var a = el("a", "cc-house-link", text);
    if (!newTabNoted) {
      newTabNoted = true;
      a.textContent = text + " (opens in a new tab)";
    }
    a.href = HOUSE_LOOKUP;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    return a;
  }

  function para(cls, before, linkText, after) {
    var p = el("p", cls);
    p.appendChild(document.createTextNode(before));
    p.appendChild(lookupLink(linkText));
    p.appendChild(document.createTextNode(after));
    return p;
  }

  function clearBlobs() {
    blobUrls.forEach(function (u) { URL.revokeObjectURL(u); });
    blobUrls = [];
  }

  // The page's structure (owner, 2026-11-06): state, then Senators and
  // Representatives as peer sections, then the people. Burgundy messages
  // (.cc-message) sit directly under the heading they explain.
  function message(before, linkText, after) {
    return linkText ? para("cc-message", before, linkText, after) : el("p", "cc-message", before);
  }

  function officialEntry(c) {
    var li = el("li", "cc-official");
    if (!c.id) {
      li.className += " cc-vacant";
      li.appendChild(message(vacantLine(c)));
      return li;
    }
    var o = data.officials[c.id];
    o.id = c.id;
    var person = el("div", "cc-person");
    person.appendChild(el("h4", "cc-name", o.name.full));
    var role = roleLine(o);
    if (role) person.appendChild(el("p", "cc-role", role));
    li.appendChild(person);
    var a = el("a", "btn btn-primary btn-lg cc-save", "Add to contacts");
    var url = URL.createObjectURL(new Blob([vcard(o, c.local)], { type: "text/vcard;charset=utf-8" }));
    blobUrls.push(url);
    a.href = url;
    a.download = fileName(o);
    a.setAttribute("aria-label", "Add " + o.name.full + " to contacts");
    // Mark cards already opened (owner, 2026-11-06). It records the tap only;
    // the page cannot know whether the contact was actually saved.
    a.addEventListener("click", function () {
      a.classList.add("cc-saved");
      a.setAttribute("aria-label", "Add " + o.name.full + " to contacts again (opened before)");
    });
    li.appendChild(a);
    return li;
  }

  function chamberSection(title, people, note) {
    var sec = el("section", "cc-chamber");
    sec.appendChild(el("h3", "cc-chamber-title", title));
    if (note) sec.appendChild(note);
    if (people.length) {
      var ul = el("ul", "cc-officials");
      people.forEach(function (c) { ul.appendChild(officialEntry(c)); });
      sec.appendChild(ul);
    }
    return sec;
  }

  function showResults(zip) {
    clearBlobs();
    results.textContent = "";
    newTabNoted = false;
    var found = candidates(zip);
    if (!found) {
      results.appendChild(message("No matches for ZIP code " + zip + ". Some real ZIP codes aren't in our data. " +
        "Check it, or ", "find your representative on house.gov", "."));
    } else {
      var stateCount = found.states.length;
      if (stateCount > 1) {
        results.appendChild(message("This ZIP code crosses " + stateCount + " states. Add the officials for the " +
          "state you live in, or check ", "house.gov", "."));
      }
      found.states.forEach(function (st) {
        var group = el("section", "cc-group");
        group.appendChild(el("h2", "cc-state", stateName(st)));
        var mine = found.list.filter(function (c) { return c.state === st; });
        var senate = mine.filter(function (c) { return c.chamber === "senate"; });
        var house = mine.filter(function (c) { return c.chamber === "house"; });
        var none = null;
        if (!senate.length) {
          var text = stateInText(st) + " has no U.S. senators.";
          none = message(text.charAt(0).toUpperCase() + text.slice(1));
        }
        group.appendChild(chamberSection(senate.length === 1 ? "Senator" : "Senators", senate, none));
        var split = house.length > 1 ? message("This ZIP code is split between " + house.length +
          " House districts. Pick yours, or check ", "house.gov", ".") : null;
        group.appendChild(chamberSection(house.length > 1 ? "Representatives" : "Representative", house, split));
        results.appendChild(group);
      });
    }
    results.hidden = false;
    // Scroll so the results start just below any fixed navbar (scroll-margin-top in CSS).
    results.focus({ preventScroll: true });
    results.scrollIntoView({ block: "start" });
  }

  function setError(msg) {
    errorEl.textContent = msg || "";
    errorEl.hidden = !msg;
    input.classList.toggle("is-invalid", !!msg);
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
  }

  function start() {
    form = document.getElementById("cc-form");
    input = document.getElementById("cc-zip");
    errorEl = document.getElementById("cc-zip-error");
    results = document.getElementById("cc-results");
    var source = document.getElementById("cc-data");
    try {
      data = JSON.parse(source.textContent);
    } catch (e) {
      data = null;
    }
    if (!data || data.schemaVersion !== SCHEMA_VERSION) {
      setError("Sorry, this page's data could not be loaded.");
      return;
    }
    zipKeys = Object.keys(data.zipMatches).sort();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var zip = input.value.replace(/\s+/g, "");
      if (!/^[0-9]{5}$/.test(zip)) {
        clearBlobs();
        results.textContent = "";
        results.hidden = true;
        setError("Enter a 5-digit ZIP code.");
        input.focus();
        return;
      }
      setError("");
      showResults(zip);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
