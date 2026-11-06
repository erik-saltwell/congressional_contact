#!/usr/bin/env python3
"""Check a Jekyll build of a site that contains the dist/jekyll/ files.

Usage: python3 -I tools/check_site.py BUILT_SITE_DIR
Build the site with the pinned GitHub Pages Jekyll first (see
research/jekyll-integration.md, "Reproduce"). Prints PASS/FAIL per check and
exits non-zero on any failure.
"""
import html.parser
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


class Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts, self.metas, self.links, self.ids, self.title = [], {}, [], [], ""
        self._cur, self._in_title = None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "script":
            self._cur = (a, [])
        elif tag == "meta" and (a.get("name") or a.get("property")):
            self.metas[a.get("name") or a.get("property")] = a.get("content", "")
        elif tag == "link":
            self.links.append(a.get("href", ""))
        elif tag == "title":
            self._in_title = True

    def handle_data(self, d):
        if self._cur:
            self._cur[1].append(d)
        if self._in_title:
            self.title += d

    def handle_endtag(self, tag):
        if tag == "script" and self._cur:
            self.scripts.append((self._cur[0], "".join(self._cur[1])))
            self._cur = None
        if tag == "title":
            self._in_title = False


def main(out):
    out = pathlib.Path(out)
    data = json.loads((ROOT / "data" / "congress.json").read_text(encoding="utf-8"))
    page = out / "congress" / "index.html"
    check("page built at /congress/", page.exists())
    s = Scan()
    s.feed(page.read_text(encoding="utf-8"))
    blobs = [b for a, b in s.scripts if a.get("id") == "cc-data"]
    check("exactly one data element", len(blobs) == 1, str(len(blobs)))
    check("data round-trips identically through Jekyll's YAML reader", json.loads(blobs[0]) == data)
    dup = sorted({i for i in s.ids if s.ids.count(i) > 1})
    check("no duplicate element ids", not dup, ",".join(dup))
    check("app ids present", {"cc-app", "cc-form", "cc-zip", "cc-results", "cc-data"} <= set(s.ids))
    check("description meta is set from front matter", s.metas.get("description", "").startswith("Look up"),
          s.metas.get("description", "")[:80])
    check("og:description is short", len(s.metas.get("og:description", "")) < 300)
    check("title is fixed", s.title.strip().startswith("Your Congress"), s.title.strip())
    srcs = [a.get("src", "") for a, _ in s.scripts if a.get("src")]
    check("congress.js loads after the theme's scripts", bool(srcs) and srcs[-1].endswith("/assets/js/congress.js"))
    check("congress.css linked", any(h.endswith("/assets/css/congress.css") for h in s.links))
    for rel in ("assets/js/congress.js", "assets/css/congress.css"):
        check(f"{rel} copied byte for byte", (out / rel).read_bytes() == (ROOT / "dist" / "jekyll" / rel).read_bytes())
    check("_data is not published", not (out / "_data").exists())
    corpus = json.loads((out / "assets" / "data" / "searchcorpus.json").read_text(encoding="utf-8"))
    check("site search corpus parses and lists the page", any("/congress" in e["url"] for e in corpus))
    check("page size", True, f"{page.stat().st_size:,} bytes")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main(sys.argv[1])
