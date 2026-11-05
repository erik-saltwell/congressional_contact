"""Verify the built Jekyll output byte-for-byte against the sources.

Throwaway research fixture. Usage: python3 -I check_output.py DATA.json BUILT_SITE_DIR
Prints one PASS/FAIL line per check and exits non-zero on any failure.
"""
import html.parser
import json
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / "src"
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


class Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts, self.styles, self.metas, self.links, self.ids = [], [], {}, [], []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "script":
            self._cur = ("script", a, [])
        elif tag == "style":
            self._cur = ("style", a, [])
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas[key] = a.get("content", "")
        elif tag == "link":
            self.links.append(a.get("href", ""))

    def handle_data(self, data):
        if self._cur:
            self._cur[2].append(data)

    def handle_endtag(self, tag):
        if self._cur and tag == self._cur[0]:
            kind, a, buf = self._cur
            (self.scripts if kind == "script" else self.styles).append((a, "".join(buf)))
            self._cur = None


def scan(path):
    s = Scan()
    s.feed(path.read_text(encoding="utf-8"))
    return s


def main(data_path, out):
    out = pathlib.Path(out)
    data = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    js_src = (SRC / "congress.js").read_text(encoding="utf-8")
    css_src = (SRC / "congress.css").read_text(encoding="utf-8")

    for v in ("a", "b"):
        page = out / f"congress-{v}" / "index.html"
        s = scan(page)
        blobs = [b for a, b in s.scripts if a.get("id") == "cc-data"]
        check(f"{v}: exactly one data element", len(blobs) == 1, str(len(blobs)))
        try:
            parsed = json.loads(blobs[0])
            check(f"{v}: data round-trips identically", parsed == data)
            if parsed != data:
                for k in data:
                    if parsed.get(k) != data[k]:
                        print("   differs at top-level key", k)
        except Exception as e:  # noqa: BLE001 - report any parse failure
            check(f"{v}: data parses", False, repr(e)[:200])
        dup = [i for i in set(s.ids) if s.ids.count(i) > 1]
        check(f"{v}: no duplicate element ids", not dup, ",".join(dup))
        check(f"{v}: app ids present", {"cc-form", "cc-zip", "cc-results"} <= set(s.ids))
        check(f"{v}: description meta is the subtitle, not page content",
              s.metas.get("description", "").startswith("Look up") or
              s.metas.get("description", "").startswith("Save your"),
              s.metas.get("description", "")[:80])
        check(f"{v}: og:description is short", len(s.metas.get("og:description", "")) < 300,
              str(len(s.metas.get("og:description", ""))))
        check(f"{v}: page size", True, f"{page.stat().st_size:,} bytes")

    a = scan(out / "congress-a" / "index.html")
    inline_js = [b for at, b in a.scripts if not at.get("src") and not at.get("type")]
    check("a: inline JS identical to source (Liquid probes intact)",
          any(b.strip() == js_src.strip() for b in inline_js))
    check("a: inline CSS identical to source", any(b.strip() == css_src.strip() for _, b in a.styles))

    b = scan(out / "congress-b" / "index.html")
    check("b: congress.js loaded after theme scripts",
          [x.get("src", "") for x, _ in b.scripts if x.get("src")][-1].endswith("/assets/js/congress.js"))
    check("b: congress.css linked", any(h.endswith("/assets/css/congress.css") for h in b.links))
    check("b: asset JS copied byte-for-byte",
          (out / "assets/js/congress.js").read_bytes() == (SRC / "congress.js").read_bytes())
    check("b: asset CSS copied byte-for-byte",
          (out / "assets/css/congress.css").read_bytes() == (SRC / "congress.css").read_bytes())
    check("b: _data not published", not (out / "_data").exists())

    corpus = json.loads((out / "assets/data/searchcorpus.json").read_text(encoding="utf-8"))
    urls = [e["url"] for e in corpus]
    check("search corpus still parses and lists both pages",
          any("congress-a" in u for u in urls) and any("congress-b" in u for u in urls))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main(*sys.argv[1:])
