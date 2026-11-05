"""Write the Jekyll test variants (and a standalone file) from one source.

Throwaway research fixture for the Jekyll integration research.
Usage: python3 -I build_variants.py DATA.json SITE_DIR STANDALONE_OUT [BOOTSTRAP_CSS]

Variants written into SITE_DIR (a local clone of the Jekyll site):
  congress-a0.html  single file, everything inline, NO {% raw %}  (negative control)
  congress-a.html   single file, everything inline, wrapped in {% raw %}
  congress-b.html   Jekyll-native: page + _data/congress.json + assets/js + assets/css
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent / "src"
JS = (HERE / "congress.js").read_text(encoding="utf-8")
CSS = (HERE / "congress.css").read_text(encoding="utf-8")
BODY = (HERE / "body.html").read_text(encoding="utf-8")

FRONT = """---
layout: page
title: "Contact Your Congress ({v})"
subtitle: "Save your senators and representative to your phone"
share-description: "Look up your two senators and House representative by ZIP and save them as contacts."
description: "Look up your two senators and House representative by ZIP and save them as contacts."
permalink: /congress-{v}/
{extra}---
"""


def inline_json(data):
    # Keep the data safe inside <script>: "</" would end the element early.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main(data_path, site, standalone_out, bootstrap_css=None):
    site = pathlib.Path(site)
    raw_data = pathlib.Path(data_path).read_text(encoding="utf-8")
    data = json.loads(raw_data)
    blob = inline_json(data)
    inline = (f"<style>\n{CSS}</style>\n{BODY}"
              f'<script type="application/json" id="cc-data">{blob}</script>\n'
              f"<script>\n{JS}</script>\n")
    for bad in ("{% endraw %}", "{%endraw%}"):
        assert bad not in inline, "content would close the raw block early"

    (site / "congress-a0.html").write_text(FRONT.format(v="a0", extra="") + inline, encoding="utf-8")
    (site / "congress-a.html").write_text(
        FRONT.format(v="a", extra="") + "{% raw %}\n" + inline + "{% endraw %}\n", encoding="utf-8")

    assert "</" not in raw_data, "jsonify does not escape '</'; the data script must avoid it"
    (site / "_data").mkdir(exist_ok=True)
    (site / "_data" / "congress.json").write_text(raw_data, encoding="utf-8")
    (site / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "js" / "congress.js").write_text(JS, encoding="utf-8")
    (site / "assets" / "css" / "congress.css").write_text(CSS, encoding="utf-8")
    extra = 'css:\n  - "/assets/css/congress.css"\njs:\n  - "/assets/js/congress.js"\n'
    (site / "congress-b.html").write_text(
        FRONT.format(v="b", extra=extra) + BODY +
        '<script type="application/json" id="cc-data">{{ site.data.congress | jsonify }}</script>\n',
        encoding="utf-8")

    boot = pathlib.Path(bootstrap_css).read_text(encoding="utf-8") if bootstrap_css else ""
    pathlib.Path(standalone_out).write_text(
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Contact Your Congress</title>\n"
        f"<style>\n{boot}\n</style>\n</head><body><main class=\"container\">\n"
        "<h1>Contact Your Congress</h1>\n" + inline + "</main></body></html>\n",
        encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
