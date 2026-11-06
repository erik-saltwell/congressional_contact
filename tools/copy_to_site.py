#!/usr/bin/env python3
"""Copy the built Jekyll files into a local checkout of the site.

Usage (from the repository root, after python3 -I tools/build.py):
    python3 -I tools/copy_to_site.py SITE_CHECKOUT

It places the four files from dist/jekyll/ at the same paths in the site:
    congress.html, _data/congress.json, assets/js/congress.js, assets/css/congress.css

It refuses to change anything unexpected:
  - SITE_CHECKOUT must be a Jekyll site (it has _config.yml);
  - a file that already exists is replaced only if it is one of ours from an earlier copy;
  - no other page in the site may already use the permalink /congress/.
It never edits _config.yml (the menu entry is a one-time manual edit), and it never
commits or pushes: the owner reviews, commits and publishes.
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "jekyll"
FILES = ["congress.html", "_data/congress.json", "assets/js/congress.js", "assets/css/congress.css"]
# How to recognise a file an earlier copy put there.
OURS = {
    "congress.html": 'id="cc-data"',
    "_data/congress.json": '"zipMatches"',
    "assets/js/congress.js": "Congressional Contact",
    "assets/css/congress.css": "Congressional Contact",
}


def fail(msg):
    print(f"ERROR: {msg}\nNothing was copied.", file=sys.stderr)
    sys.exit(1)


def main(site):
    site = pathlib.Path(site).resolve()
    if not (site / "_config.yml").is_file():
        fail(f"{site} has no _config.yml; give the path to the site checkout")
    missing = [f for f in FILES if not (DIST / f).is_file()]
    if missing:
        fail(f"dist/jekyll is missing {missing}; run python3 -I tools/build.py first")

    permalink = re.search(r"^permalink:\s*(\S+)", (DIST / "congress.html").read_text(encoding="utf-8"), re.M).group(1)
    for page in list(site.rglob("*.html")) + list(site.rglob("*.md")):
        rel = page.relative_to(site).as_posix()
        if rel == "congress.html" or rel.startswith(("_site/", "vendor/", "node_modules/", ".")):
            continue
        head = page.read_text(encoding="utf-8", errors="replace")[:2000]
        if re.search(rf"^permalink:\s*['\"]?{re.escape(permalink)}['\"]?\s*$", head, re.M):
            fail(f"{rel} already uses the permalink {permalink}")

    plan = []
    for f in FILES:
        src, dst = DIST / f, site / f
        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                plan.append((f, "unchanged"))
                continue
            if OURS[f] not in dst.read_text(encoding="utf-8", errors="replace"):
                fail(f"{f} already exists in the site and is not from Congressional Contact; move it first")
            plan.append((f, "updated"))
        else:
            plan.append((f, "added"))

    for f, action in plan:
        if action != "unchanged":
            (site / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(DIST / f, site / f)
        print(f"  {action:9} {f}")
    print(f"\nThe page will be at {permalink}. _config.yml was not changed, so nothing links to it yet.")
    print("Next: review with git status in the site checkout, then commit and push to publish.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
