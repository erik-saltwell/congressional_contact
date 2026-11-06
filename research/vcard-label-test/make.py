#!/usr/bin/env python3
"""Build the label test page: one card per way of writing custom labels.

Variants B (TYPE=X-label only), D (TYPE=label) and E (vCard 2.1 TEL;X-label) were
dropped after the owner's import into desktop Google Contacts (2026-11-06): B and D
showed "Other" for every label, and E imported with no phones or addresses.
A and C both kept the labels there.

Usage: python3 -I research/vcard-label-test/make.py
Writes research/vcard-label-test/site/ (index.html plus one .vcf per variant).
Serve that folder on the LAN and open it on the phone; save each card and
note which labels the contacts app shows.

Every card is Patty Murray's real DC office, Seattle office and two links,
under the name "Test <letter> Murray" so the test contacts are easy to find
and delete.
"""
import html
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "site"

PHONES = [("+12022242621", "DC office"), ("+18664819186", "DC office"), ("+12065535545", "Seattle office")]
ADDRS = [
    (["154 Russell Senate Office Building"], "Washington", "DC", "20510", "DC office"),
    (["2988 Jackson Federal Building, 915 2nd Avenue"], "Seattle", "WA", "98174", "Seattle office"),
]
URLS = [("https://www.murray.senate.gov", "Website"),
        ("https://www.murray.senate.gov/write-to-patty/", "Share your views")]


def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def adr(a):
    lines, city, region, pc, _ = a
    return ";".join(["", "", esc(", ".join(lines)), city, region, pc, "US"])


def card(letter, version, tel, address, url):
    """tel/address/url(value, label, n) return the lines for one entry."""
    out = ["BEGIN:VCARD", f"VERSION:{version}"]
    if version == "3.0":
        out.append("PRODID:-//Congressional Contact label test//EN")
    out += [f"N:Murray;Test {letter};;;", f"FN:Test {letter} Murray", "ORG:U.S. Senate",
            "TITLE:U.S. Senator for Washington"]
    n = 0
    for num, label in PHONES:
        n += 1
        out += tel(num, label, n)
    for a in ADDRS:
        n += 1
        out += address(adr(a), a[-1], n)
    for u, label in URLS:
        n += 1
        out += url(u, label, n)
    out += ["NOTE:U.S. Senator for Washington", "END:VCARD"]
    return "\r\n".join(out) + "\r\n"


def ab(prop):
    """Apple's form: an itemN group with an X-ABLabel line."""
    return lambda v, label, n: [f"item{n}.{prop}:{v}", f"item{n}.X-ABLabel:{label}"]


VARIANTS = [
    ("A", "Current cards: Apple item groups with X-ABLabel, TYPE=WORK", "3.0",
     ab("TEL;TYPE=WORK,VOICE"), ab("ADR;TYPE=WORK"), ab("URL")),
    ("C", "Both: item groups with X-ABLabel and TYPE=X-label", "3.0",
     lambda v, l, n: [f"item{n}.TEL;TYPE=X-{l}:{v}", f"item{n}.X-ABLabel:{l}"],
     lambda v, l, n: [f"item{n}.ADR;TYPE=X-{l}:{v}", f"item{n}.X-ABLabel:{l}"],
     lambda v, l, n: [f"item{n}.URL;TYPE=X-{l}:{v}", f"item{n}.X-ABLabel:{l}"]),
]


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for letter, desc, version, tel, address, url in VARIANTS:
        name = f"test-{letter.lower()}.vcf"
        (OUT / name).write_bytes(card(letter, version, tel, address, url).encode("utf-8"))
        rows.append(f'<h2>{letter}. {html.escape(desc)}</h2>\n'
                    f'<a class="btn" href="{name}">Save Test {letter} Murray</a>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>vCard label test</title>
<style>
 body {{ font: 16px/1.4 system-ui, sans-serif; max-width: 34rem; margin: 1rem auto; padding: 0 1rem; }}
 h2 {{ font-size: 1rem; margin: 1.5rem 0 .25rem; }}
 a.btn {{ display: block; padding: .9rem; text-align: center; border: 1px solid #888; border-radius: .5rem;
   background: #f2f2f2; color: #000; text-decoration: none; }}
</style></head><body>
<h1>vCard label test</h1>
<p>Each button saves Patty Murray's card under the name <b>Test A Murray</b> or <b>Test C Murray</b>.
The goal: the phones read <b>DC office</b> and <b>Seattle office</b>, and the second link reads
<b>Share your views</b>. Search "Test" in Contacts to delete them afterwards.</p>
{chr(10).join(rows)}
</body></html>
"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({len(VARIANTS)} cards)")


if __name__ == "__main__":
    main()
