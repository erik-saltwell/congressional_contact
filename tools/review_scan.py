#!/usr/bin/env python3
"""Scan officials' websites to focus a review batch (helper for the review skill).

    python3 -I tools/review_scan.py data/reviews/<batch> [--ids A,B] [--workers N]   # default 2; more trips site firewalls
    python3 -I tools/review_scan.py data/reviews/<batch> --show ID REGEX   # text around a match

For each official in the batch it fetches the homepage, the upstream contact-form
candidate and the site's contact, office and location pages (with curl, which
Senate firewalls accept more often than Python's HTTP client). It writes
scan.json in the batch directory and prints only what needs judgment:

  - published phone numbers not found on any fetched page;
  - numbers on the site that we do not publish (fax-labelled numbers are skipped);
  - published street addresses not found;
  - pages with a message form, with words that suggest feedback or casework;
  - mailboxes printed on the pages.

The scan is a pointer, never evidence: read the page before proposing anything.
"""
import concurrent.futures as cf
import html
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
LINK_WORDS = re.compile(r"contact|office|location|email|e-mail|write|message|share|opinion|feedback|comment|reach", re.I)
SKIP_WORDS = re.compile(r"newsletter|unsubscribe|subscribe|tour|flag|internship|intern|appearance|meeting|schedul|"
                        r"press|media|website-problem|accessib|privacy|grant|academy|nominat|casework|"
                        r"federal-agency|agency|services|help-with|\.pdf$", re.I)
POSITIVE = re.compile(r"issue|topic|opinion|legislation|share your|your thoughts|views|comment|concern|voice", re.I)
NEGATIVE = re.compile(r"privacy release|privacy act|casework|federal agency|case number|tour request|flag request|"
                      r"meeting request|newsletter", re.I)
PHONE = re.compile(r"(?<!\d)\(?([2-9]\d{2})\)?[\s.\-‐-—]*([2-9]\d{2})[\s.\-‐-—]*(\d{4})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.(?:gov|com|org|net|us)")
MAX_PAGES = 10


def fetch(url):
    try:
        out = subprocess.run(["curl", "-sSL", "--compressed", "-m", "40", "-A", UA,
                              "-w", "\n%{url_effective} %{http_code}", url],
                             capture_output=True, timeout=60).stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return {"url": url, "status": 0, "final": url, "raw": ""}
    raw, _, tail = out.rpartition("\n")
    final, _, code = tail.rpartition(" ")
    return {"url": url, "status": int(code) if code.isdigit() else 0, "final": final or url, "raw": raw}


def text_of(raw):
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def links_of(raw, base):
    host = urllib.parse.urlparse(base).netloc.replace("www.", "")
    out = []
    for href, label in re.findall(r"<a[^>]+href=\"([^\"#]+)\"[^>]*>(.*?)</a>", raw, re.S | re.I):
        url = urllib.parse.urljoin(base, html.unescape(href.strip()))
        label = text_of(label)
        if urllib.parse.urlparse(url).netloc.replace("www.", "") != host:
            continue
        if LINK_WORDS.search(url + " " + label) and not SKIP_WORDS.search(url):
            out.append(url.split("?")[0].rstrip("/") + "/" if not url.endswith((".html", ".htm")) else url)
    return list(dict.fromkeys(out))


def phones_in(text):
    voice, fax = set(), set()
    for m in PHONE.finditer(text):
        n = "+1" + "".join(m.groups())
        before = text[max(0, m.start() - 14):m.start()].lower()
        (fax if "fax" in before else voice).add(n)
    return voice, fax - voice


def street_key(line):
    m = re.match(r"\s*(\d+[A-Za-z]?)\s+(?:(?:N|S|E|W|North|South|East|West)\.?\s+)?([A-Za-z0-9]+)", line)
    return (m.group(1), m.group(2).lower()) if m else None


def scan_official(bid, packet):
    pub = packet["published"]
    site = next((l["url"] for l in pub["links"] if l["purpose"] == "website"), None)
    cand = packet["upstreamCandidates"].get("contactForm")
    queue = [u for u in (site, cand) if u]
    pages, seen = [], set()
    while queue and len(pages) < MAX_PAGES:
        u = queue.pop(0)
        key = u.rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        p = fetch(u)
        p["text"] = text_of(p["raw"]) if p["status"] == 200 else ""
        p["hasForm"] = p["status"] == 200 and bool(
            re.search(r"<textarea", p["raw"], re.I)
            or re.search(r"<iframe[^>]+title=\"[^\"]*(contact|form)", p["raw"], re.I)
            or (len(re.findall(r"\bissue", p["raw"], re.I)) >= 3 and "<select" in p["raw"].lower()
                and re.search(r"contact|email|write|message", p["final"], re.I)))
        # House forms often sit behind a ZIP or address check that must be passed first.
        p["gated"] = p["status"] == 200 and not p["hasForm"] and bool(
            re.search(r"_authentication", p["final"]) or
            re.search(r"<form[^>]+action=\"[^\"]*(contact|email|form)[^\"]*\"", p["raw"], re.I)
            and re.search(r"zip", p["text"], re.I))
        pages.append(p)
        if p["status"] != 200 and len(pages) == 1 and site:
            root = site.rstrip("/")
            queue = [root + s for s in ("/contact/", "/contact/offices/", "/offices/", "/office-locations/")] + queue
        if p["status"] == 200 and len(pages) <= 3:
            queue += [l for l in links_of(p["raw"], p["final"]) if l.rstrip("/") not in seen]
    alltext = " ".join(p["text"] for p in pages)
    voice, fax = phones_in(alltext)
    published = {ph["number"] for o in pub["offices"] for ph in o["phones"]}
    missing_addr = []
    norm = re.sub(r"[^a-z0-9 ]", " ", alltext.lower())
    for o in pub["offices"]:
        if o["address"]:
            k = street_key(o["address"]["lines"][-1]) or street_key(o["address"]["lines"][0])
            if k and not re.search(rf"\b{re.escape(k[0])}\b[^.]{{0,40}}\b{re.escape(k[1][:5])}", norm):
                missing_addr.append(f"{o['label']}: {', '.join(o['address']['lines'])}")
    forms = []
    for p in pages:
        if p["gated"]:
            forms.append({"url": p["final"], "positive": ["(behind a ZIP or address check)"], "negative": []})
        elif p["hasForm"]:
            pos = sorted({m.group(0).lower() for m in POSITIVE.finditer(p["text"])})
            neg = sorted({m.group(0).lower() for m in NEGATIVE.finditer(p["text"])})
            forms.append({"url": p["final"], "positive": pos[:6], "negative": neg[:6]})
    emails = sorted({e for p in pages for e in EMAIL.findall(p["raw"])
                     if not re.search(r"example\.|@domain|@email\.|yourname|name@|sentry|wixpress|^webmaster@|^press|"
                               r"^media|^no-?reply|^communications@", e, re.I)})
    return {
        "id": bid, "name": pub["name"]["full"], "seat": packet["seat"],
        "pages": [{"url": p["url"], "final": p["final"], "status": p["status"], "hasForm": p["hasForm"],
                   "gated": p["gated"]} for p in pages],
        "blocked": [p["url"] for p in pages if p["status"] != 200],
        "publishedPhonesNotFound": sorted(published - voice - fax),
        "publishedPhonesShownAsFax": sorted(published & fax),
        "sitePhonesNotPublished": sorted(voice - published),
        "publishedAddressesNotFound": missing_addr,
        "forms": forms,
        "emails": emails,
    }


def show(d, bid, pattern):
    """Print the text around PATTERN on every page the scan fetched for BID."""
    scan = json.loads((d / "scan.json").read_text(encoding="utf-8"))[bid]
    rx = re.compile(pattern, re.I)
    for pg in scan["pages"]:
        if pg["status"] != 200:
            continue
        text = text_of(fetch(pg["final"])["raw"])
        hits = [m.start() for m in rx.finditer(text)][:3]
        for h in hits:
            print(f"[{pg['final']}] ...{text[max(0, h - 160):h + 220]}...")


def main(args):
    d = pathlib.Path(args[0])
    if "--show" in args:
        i = args.index("--show")
        return show(d, args[i + 1], args[i + 2])
    packets = json.loads((d / "packets.json").read_text(encoding="utf-8"))["officials"]
    ids = args[args.index("--ids") + 1].split(",") if "--ids" in args else list(packets)
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 2
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda b: scan_official(b, packets[b]), ids))
    out = d / "scan.json"
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    old.update({r["id"]: r for r in results})
    out.write_text(json.dumps(old, indent=1) + "\n", encoding="utf-8")
    for r in results:
        print(f"== {r['id']} {r['name']} ({r['seat']}) pages={len(r['pages'])}"
              + (f" BLOCKED={r['blocked']}" if r["blocked"] else ""))
        for k in ("publishedPhonesNotFound", "publishedPhonesShownAsFax", "sitePhonesNotPublished",
                  "publishedAddressesNotFound", "emails"):
            if r[k]:
                print(f"   {k}: {r[k]}")
        for f in r["forms"]:
            print(f"   form: {f['url']} +{f['positive']} -{f['negative']}")
        if not r["forms"]:
            print("   form: NONE FOUND")


if __name__ == "__main__":
    main(sys.argv[1:])
