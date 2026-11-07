#!/usr/bin/env python3
"""Build the published page from src/ and data/congress.json.

Usage (from the repository root):
    python3 -I tools/build.py            # writes dist/jekyll/

dist/jekyll/ mirrors the site root and holds the four files the site needs:
    congress.html            the page (front matter + markup + a Liquid data tag)
    _data/congress.json      the data, compact
    assets/js/congress.js    copied byte for byte
    assets/css/congress.css  copied byte for byte

The standalone single file (phase 8) will be another output of this script; the
shared parts are read once in load_parts().

Every hard rule from research/jekyll-integration.md is asserted before anything
is written: valid data, no "</" in the data, no exponent-form numbers, no front
matter in the asset files, no Liquid in the page markup, cc- prefixes on every id
and app class, and no URL, title, network or analytics calls in the script.
"""
import base64
import html.parser
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT / "tools"))
import build_data  # noqa: E402

# Classes the markup may borrow from Bootstrap 4 and Beautiful Jekyll.
THEME_CLASSES = {"form-control", "form-control-lg", "btn", "btn-primary", "btn-lg",
                 "box-note", "sr-only", "is-invalid"}
# congress.css may style these theme classes (it loads only on this page), and may
# size the theme's page header on phones.
CSS_THEME_SELECTORS = THEME_CLASSES | {"intro-header", "page-heading", "page-subheading", "disabled"}
# Things the script must never do: change the URL or title, fetch, or send analytics.
# The page may read the URL (for #help and Copy link) but never change it.
FORBIDDEN_JS = [r"\bhistory\.", r"\blocation\s*=[^=]", r"\blocation\.\w+\s*=[^=]",
                r"\blocation\.(assign|replace|reload)\b", r"document\.title", r"\bfetch\(", r"XMLHttpRequest",
                r"sendBeacon", r"\bgtag\b", r"dataLayer", r"localStorage", r"sessionStorage", r"document\.cookie"]

FRONT_MATTER = """---
layout: page
title: Your Congress
subtitle: Add your lawmakers to your contacts
share-description: Look up your U.S. senators and House representative by ZIP code and add them to your contacts.
description: Look up your U.S. senators and House representative by ZIP code and add them to your contacts.
permalink: /congress/
css:
  - "/assets/css/congress.css"
js:
  - "/assets/js/congress.js"
---
"""
DATA_TAG = '<script type="application/json" id="cc-data">{{ site.data.congress | jsonify }}</script>\n'


class BuildError(Exception):
    pass


def check(ok, msg):
    if not ok:
        raise BuildError(msg)


class Markup(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.classes = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        self.classes += (a.get("class") or "").split()


def inline_shots(body):
    """Replace each src="cc-shot:NAME" with src/help-shots/NAME.webp as a data URI.

    The page carries its help screenshots inline, with no separate image files
    (owner, 2026-11-07). tools/help_shots.py makes the WebP files.
    """
    shots = SRC / "help-shots"
    names = re.findall(r'src="cc-shot:([\w-]+)"', body)
    files = {p.stem for p in shots.glob("*.webp")}
    check(not set(names) - files, f"help screenshots missing from src/help-shots/: {sorted(set(names) - files)}")
    check(not files - set(names), f"src/help-shots/ files the page does not use: {sorted(files - set(names))}")
    for name in names:
        uri = "data:image/webp;base64," + base64.b64encode((shots / f"{name}.webp").read_bytes()).decode("ascii")
        body = body.replace(f'src="cc-shot:{name}"', f'src="{uri}"')
    check("cc-shot:" not in body, "an unresolved cc-shot: placeholder is left in body.html")
    return body


def load_parts():
    parts = {n: (SRC / n).read_text(encoding="utf-8") for n in ("body.html", "congress.js", "congress.css")}
    parts["body.html"] = inline_shots(parts["body.html"])
    data = json.loads((ROOT / "data" / "congress.json").read_text(encoding="utf-8"))
    config = json.loads(build_data.CONFIG.read_text(encoding="utf-8"))
    build_data.validate(data, config)
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    check("</" not in compact, "'</' in the data would end the data element early")
    check(not re.search(r'(?<![\w"])-?\d+(?:\.\d+)?[eE][+-]?\d+', compact),
          "exponent-form number in the data; Jekyll's YAML reader turns it into a string")
    check(json.loads(compact) == data, "compact data does not round-trip")

    body, js, css = parts["body.html"], parts["congress.js"], parts["congress.css"]
    for name in ("congress.js", "congress.css"):
        check(not parts[name].lstrip().startswith("---"), f"{name} must never get front matter")
    check("{{" not in body and "{%" not in body, "body.html must not contain Liquid ({{ or {%)")
    m = Markup()
    m.feed(body)
    check(all(i.startswith("cc-") for i in m.ids), f"ids without cc-: {[i for i in m.ids if not i.startswith('cc-')]}")
    check(len(m.ids) == len(set(m.ids)), "duplicate ids in body.html")
    js_classes = re.findall(r'\bel\("\w+", "([^"]*)"', js) + re.findall(r'className \+= "([^"]*)"', js)
    classes = set(m.classes) | {c for s in js_classes for c in s.split()}
    bad = sorted(c for c in classes if not c.startswith("cc-") and c not in THEME_CLASSES)
    check(not bad, f"classes that are neither cc- nor known theme classes: {bad}")
    css_classes = set(re.findall(r"\.([A-Za-z][\w-]*)", re.sub(r"/\*.*?\*/", "", css, flags=re.S)))
    stray = sorted(c for c in css_classes if not c.startswith("cc-") and c not in CSS_THEME_SELECTORS)
    check(not stray, f"congress.css styles classes that are neither cc- nor known theme classes: {stray}")
    check(":root" not in css and not re.search(r"(?<![\w-])--(?!cc-)[\w-]+\s*:", css),
          "congress.css must not set theme variables")
    for pat in FORBIDDEN_JS:
        check(not re.search(pat, js), f"congress.js must not use {pat} (privacy and no-URL rules)")
    return parts, data, compact


def build_jekyll(parts, compact):
    out = DIST / "jekyll"
    if out.exists():
        shutil.rmtree(out)
    (out / "_data").mkdir(parents=True)
    (out / "assets" / "js").mkdir(parents=True)
    (out / "assets" / "css").mkdir(parents=True)
    (out / "congress.html").write_text(FRONT_MATTER + parts["body.html"] + DATA_TAG, encoding="utf-8")
    (out / "_data" / "congress.json").write_text(compact + "\n", encoding="utf-8")
    shutil.copyfile(SRC / "congress.js", out / "assets" / "js" / "congress.js")
    shutil.copyfile(SRC / "congress.css", out / "assets" / "css" / "congress.css")
    for f in sorted(p for p in out.rglob("*") if p.is_file()):
        print(f"  {f.relative_to(ROOT)}  {f.stat().st_size:,} bytes")


def main():
    parts, data, compact = load_parts()
    print("Checks passed. Writing dist/jekyll/:")
    build_jekyll(parts, compact)


if __name__ == "__main__":
    try:
        main()
    except (BuildError, build_data.DataError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
