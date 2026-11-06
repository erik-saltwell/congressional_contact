#!/usr/bin/env python3
"""Build data/congress.json from the upstream sources.

Usage (from the repository root):
    python3 -I tools/build_data.py            # fetch every source, then build
    python3 -I tools/build_data.py --offline  # rebuild from data/cache/ only
    python3 -I tools/build_data.py --fetch census-zcta,census-counties  # fetch only these, then build
    python3 -I tools/build_data.py --check FILE   # validate an existing data file

The schema and its rules are in design_notes/data-schema.md. The HUD token is
read from .env (HUD_API_TOKEN) and is only ever sent in the Authorization
header; it is never printed, logged or written anywhere.

Safety: the new data is validated in full before data/congress.json is
replaced. Any fetch failure or validation failure exits non-zero and leaves
the last good file untouched.
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import math
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "cache"
OUT = DATA / "congress.json"
SUPPLEMENTS = DATA / "supplements.json"
CONFIG = ROOT / "tools" / "data_config.json"
ENV = ROOT / ".env"
UA = "congressional-contact-data-tool"
SCHEMA_VERSION = 1

FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI",
}
NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
    "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia", "PR": "Puerto Rico", "GU": "Guam", "VI": "U.S. Virgin Islands",
    "AS": "American Samoa", "MP": "Northern Mariana Islands",
}
NON_STATES = {"DC", "PR", "GU", "VI", "AS", "MP"}
CLERK_STATE = {"AQ": "AS"}  # the Clerk feed writes American Samoa as AQ
LINK_PURPOSES = {"website", "policy-feedback"}
EMAIL_RE = re.compile(r"^[^@\s<>\"]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ZIP_RE = re.compile(r"^[0-9]{5}$")
SEAT_RE = re.compile(r"^[A-Z]{2}-[0-9]{1,2}$")


class DataError(Exception):
    pass


# ---------------------------------------------------------------- fetching

def hud_token():
    if not ENV.exists():
        raise DataError(".env not found; copy .env.example and set HUD_API_TOKEN")
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("HUD_API_TOKEN="):
            value = line.split("=", 1)[1].strip().strip("'\"")
            if value:
                return value
    raise DataError("HUD_API_TOKEN is missing or empty in .env")


def sources(config):
    hud = config["hud"]
    hud_q = {"year": hud["year"], "quarter": hud["quarter"]}
    q = urllib.parse.urlencode
    base = "https://www.huduser.gov/hudapi/public/usps?"
    gh = "https://unitedstates.github.io/congress-legislators/"
    gaz, gy = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/", config["gazetteer"]["year"]
    return {
        "legislators-current": gh + "legislators-current.json",
        "legislators-district-offices": gh + "legislators-district-offices.json",
        "house-clerk": "https://clerk.house.gov/xml/lists/MemberData.xml",
        "senate": "https://www.senate.gov/general/contact_information/senators_cfm.xml",
        "hud-zip-cd": base + q({"type": 5, "query": "All", **hud_q}),
        "hud-zip-county": base + q({"type": 2, "query": "All", **hud_q}),
        # ZIP (ZCTA) and county centres, used only to choose each card's nearest local office.
        "census-zcta": gaz + f"{gy}_Gazetteer/{gy}_Gaz_zcta_national.zip",
        "census-counties": gaz + f"{gy}_Gazetteer/{gy}_Gaz_counties_national.zip",
    }


def ext_of(sid):
    return ".xml" if sid in ("house-clerk", "senate") else ".zip" if sid.startswith("census-") else ".json"


def fetch_all(config, only=None):
    """Download every source (or only those named) into memory, then write them to the cache.

    Nothing in the cache changes unless every download succeeds."""
    CACHE.mkdir(parents=True, exist_ok=True)
    staged = {}
    all_sources = sources(config)
    if only and set(only) - set(all_sources):
        raise DataError(f"unknown source ids {sorted(set(only) - set(all_sources))}; known: {sorted(all_sources)}")
    for sid, url in all_sources.items():
        if only and sid not in only:
            continue
        headers = {"User-Agent": UA}
        if sid.startswith("hud-"):
            headers["Authorization"] = "Bearer " + hud_token()
            headers["Accept"] = "application/json"
        req = urllib.request.Request(url, headers=headers)
        print(f"fetching {sid} ...", flush=True)
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                body = r.read()
                last_mod = r.headers.get("Last-Modified")
        except (urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", "")
            raise DataError(f"fetch failed for {sid} ({code} {getattr(e, 'reason', e)}); "
                            "last good data and cache left unchanged") from None
        if len(body) < 1000:
            raise DataError(f"fetch for {sid} returned only {len(body)} bytes; refusing to use it")
        meta = {"url": url, "fetchedAt": now_iso(), "lastModified": last_mod,
                "sha256": hashlib.sha256(body).hexdigest()}
        staged[sid] = (body, meta)
    for sid, (body, meta) in staged.items():
        (CACHE / (sid + ext_of(sid))).write_bytes(body)
        (CACHE / (sid + ".meta.json")).write_text(json.dumps(meta, indent=1), encoding="utf-8")


def cached(sid):
    path, meta = CACHE / (sid + ext_of(sid)), CACHE / (sid + ".meta.json")
    if not path.exists() or not meta.exists():
        raise DataError(f"no cached copy of {sid}; run without --offline first, or with --fetch {sid}")
    return path, json.loads(meta.read_text(encoding="utf-8"))


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------- parsing helpers

def phone(raw, where, issues):
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        issues.append(f"{where}: unusable phone number {raw!r} skipped")
        return None
    return "+1" + digits


def dc_address(term, where, issues):
    m = re.match(r"^(.*?)\s+Washington,?\s+DC\s+(\d{5}(?:-\d{4})?)$", term.get("address", ""))
    if not m:
        issues.append(f"{where}: DC address not understood: {term.get('address')!r}")
        return None
    return {"lines": [m.group(1)], "city": "Washington", "region": "DC",
            "postalCode": m.group(2), "country": "US"}


def local_office(o, where, issues):
    # Upstream YAML sometimes turns values such as suite numbers into integers.
    o = {k: str(v).strip() for k, v in o.items() if v is not None and k not in ('latitude', 'longitude')}
    phones = []
    # Fax numbers are left out of the contact data (owner decision, 2026-11-05).
    if o.get("phone"):
        n = phone(o["phone"], where, issues)
        if n:
            phones.append({"number": n, "type": "voice"})
    address = None
    if o.get("address"):
        street = o["address"] + (", " + o["suite"] if o.get("suite") else "")
        lines = ([o["building"]] if o.get("building") else []) + [street]
        address = {"lines": lines, "city": o.get("city", ""), "region": o.get("state", ""),
                   "postalCode": o.get("zip", ""), "country": "US"}
    if not phones and not address:
        return None
    return {"label": f"{o.get('city', 'Local')}, {o.get('state', '')} office", "kind": "local",
            "phones": phones, "address": address}


def upstream_offices(term, local_records, where, issues, coords=None):
    """The office list built from the bulk roster alone: DC first, then local offices.

    If coords is a list, it receives one (lat, lon) or None per office, in the same order.
    Coordinates stay inside the build; they are never published."""
    dc_phones = [{"number": x, "type": "voice"} for x in [phone(term.get("phone"), where, issues)] if x]
    office_list = [{"label": "Washington, DC", "kind": "dc", "phones": dc_phones,
                    "address": dc_address(term, where, issues)}]
    point = []
    for o in local_records:
        lo = local_office(o, where, issues)
        if lo:
            office_list.append(lo)
            lat, lon = o.get("latitude"), o.get("longitude")
            point.append((float(lat), float(lon)) if lat is not None and lon is not None else None)
    if coords is not None:
        coords[:] = [None] + point
    return office_list


def offices_hash(office_list):
    return hashlib.sha256(json.dumps(office_list, sort_keys=True).encode()).hexdigest()


def role_for(term):
    if term["type"] == "sen":
        return "senator"
    if term["state"] == "PR":
        return "resident-commissioner"
    if term["state"] in NON_STATES:
        return "delegate"
    return "representative"


# ---------------------------------------------------------------- supplements

def load_supplements(roster_ids, issues):
    if not SUPPLEMENTS.exists():
        return {}, None
    raw = SUPPLEMENTS.read_bytes()
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as e:
        raise DataError(f"data/supplements.json is not valid JSON: {e}") from None
    entries = doc.get("officials")
    if not isinstance(entries, dict):
        raise DataError("data/supplements.json must have an 'officials' object")
    out = {}
    for bid, e in entries.items():
        where = f"supplements[{bid}]"
        if bid not in roster_ids:
            issues.append(f"{where}: not a serving official; entry ignored (remove it if they left office)")
            continue
        links, emails = [], []
        for l in e.get("links", []):
            if l.get("purpose") not in LINK_PURPOSES:
                raise DataError(f"{where}: link purpose must be one of {sorted(LINK_PURPOSES)}")
            if not str(l.get("url", "")).startswith("https://"):
                raise DataError(f"{where}: link url must start with https://")
            check_verified(l, where)
            links.append({"purpose": l["purpose"], "url": l["url"]})
        for m in e.get("emails", []):
            addr = str(m.get("address", ""))
            if not EMAIL_RE.match(addr):
                raise DataError(f"{where}: {addr!r} is not an email address (form URLs belong in links)")
            if not m.get("purpose"):
                raise DataError(f"{where}: email {addr} needs a purpose, such as general or casework")
            check_verified(m, where)
            emails.append({"address": addr, "purpose": m["purpose"]})
        verified = e.get("verifiedAt")
        if verified is not None and not DATE_RE.match(str(verified)):
            raise DataError(f"{where}: verifiedAt must be YYYY-MM-DD or null")
        offices = e.get("offices")
        if offices is not None:
            check_verified(offices, where + ".offices")
            if not re.match(r"^[0-9a-f]{64}$", str(offices.get("upstreamHash", ""))):
                raise DataError(f"{where}.offices: upstreamHash missing; add office lists with tools/review.py apply")
            check_offices(offices.get("list"), where + ".offices")
        out[bid] = {"links": links, "emails": emails, "verifiedAt": verified, "offices": offices}
    return out, hashlib.sha256(raw).hexdigest()


def check_offices(office_list, where):
    if not isinstance(office_list, list) or not office_list:
        raise DataError(f"{where}: list must be a non-empty array of offices")
    if office_list[0].get("kind") != "dc" or any(o.get("kind") != "local" for o in office_list[1:]):
        raise DataError(f"{where}: the DC office comes first, then local offices")
    for i, o in enumerate(office_list):
        w = f"{where}[{i}]"
        if set(o) != {"label", "kind", "phones", "address"} or not str(o["label"]).strip():
            raise DataError(f"{w}: an office has exactly label, kind, phones and address")
        for ph in o["phones"]:
            if set(ph) != {"number", "type"} or not re.match(r"^\+1\d{10}$", str(ph["number"])) \
                    or ph["type"] != "voice":
                raise DataError(f"{w}: phone must be {{number: +1XXXXXXXXXX, type: voice}}; fax numbers are not published")
        a = o["address"]
        if a is not None:
            if set(a) != {"lines", "city", "region", "postalCode", "country"} or not isinstance(a["lines"], list) \
                    or not all(isinstance(x, str) and x for x in a["lines"]):
                raise DataError(f"{w}: address must have lines, city, region, postalCode and country")
        if not o["phones"] and a is None:
            raise DataError(f"{w}: an office needs a phone or an address")


def check_verified(item, where):
    if not item.get("source", "").startswith("https://"):
        raise DataError(f"{where}: every supplement value needs an https source URL")
    if not DATE_RE.match(str(item.get("verifiedAt", ""))):
        raise DataError(f"{where}: every supplement value needs verifiedAt as YYYY-MM-DD")


# ---------------------------------------------------------------- build

def build(config):
    issues = []
    paths, metas = {}, {}
    for sid in sources(config):
        paths[sid], metas[sid] = cached(sid)

    current = json.loads(paths["legislators-current"].read_text(encoding="utf-8"))
    offices = json.loads(paths["legislators-district-offices"].read_text(encoding="utf-8"))
    clerk = ET.parse(paths["house-clerk"]).getroot()
    senate = ET.parse(paths["senate"]).getroot()

    if config["hud"]["congress"] != config["congress"]:
        raise DataError(f"the configured HUD quarter has {config['hud']['congress']}th Congress districts, but the roster "
                        f"config is the {config['congress']}th; geography and roster must describe the same Congress")

    # Membership comes from the official feeds.
    clerk_congress = int(clerk.findtext("title-info/congress-num"))
    if clerk_congress != config["congress"]:
        raise DataError(f"House Clerk feed is for the {clerk_congress}th Congress; config says {config['congress']}")
    house_seats, clerk_ids = {}, set()
    for m in clerk.find("members").iter("member"):
        sd = m.findtext("statedistrict")
        st = CLERK_STATE.get(sd[:2], sd[:2])
        if st not in NAMES or not sd[2:].isdigit():
            raise DataError(f"unexpected Clerk seat code {sd!r}")
        seat = f"{st}-{int(sd[2:])}"
        bid = (m.findtext("member-info/bioguideID") or "").strip() or None
        if seat in house_seats:
            raise DataError(f"seat {seat} appears twice in the Clerk feed")
        house_seats[seat] = bid
        if bid:
            clerk_ids.add(bid)
    if len(house_seats) != config["houseSeatCount"]:
        raise DataError(f"Clerk feed has {len(house_seats)} seats; expected {config['houseSeatCount']}")
    senate_ids = {m.findtext("bioguide_id").strip() for m in senate.iter("member")}

    roster = {p["id"]["bioguide"]: p for p in current}
    community_house = {b for b, p in roster.items() if p["terms"][-1]["type"] == "rep"}
    community_senate = {b for b, p in roster.items() if p["terms"][-1]["type"] == "sen"}
    if clerk_ids != community_house:
        raise DataError("House membership differs between the Clerk feed and congress-legislators: "
                        f"only Clerk {sorted(clerk_ids - community_house)}, "
                        f"only community {sorted(community_house - clerk_ids)}. "
                        "Wait for the community data to catch up or add the member's record.")
    if senate_ids != community_senate:
        raise DataError("Senate membership differs between senate.gov and congress-legislators: "
                        f"only senate.gov {sorted(senate_ids - community_senate)}, "
                        f"only community {sorted(community_senate - senate_ids)}")

    supplements, supp_hash = load_supplements(clerk_ids | senate_ids, issues)
    local = {p["id"]["bioguide"]: p.get("offices", []) for p in offices}

    officials, office_points = {}, {}
    for bid in sorted(clerk_ids | senate_ids):
        p, term = roster[bid], roster[bid]["terms"][-1]
        where = f"{bid} {p['name'].get('official_full') or p['name']['last']}"
        n = p["name"]
        if bid not in local:
            issues.append(f"{where}: no local-office record upstream")
        coords = []
        office_list = upstream_offices(term, local.get(bid, []), where, issues, coords)
        sup = supplements.get(bid, {"links": [], "emails": [], "verifiedAt": None, "offices": None})
        if sup["offices"]:
            if sup["offices"]["upstreamHash"] != offices_hash(office_list):
                issues.append(f"{where}: upstream offices changed since the reviewed office list was approved on "
                              f"{sup['offices']['verifiedAt']}; the reviewed list is still used. Review this official again.")
            # A reviewed office keeps the roster's coordinates when its street address matches one.
            by_addr = {address_key(o["address"]): c for o, c in zip(office_list, coords) if c and o["address"]}
            office_list = sup["offices"]["list"]
            coords = [by_addr.get(address_key(o["address"])) if o["address"] else None for o in office_list]
        office_points[bid] = coords
        links = [{"purpose": "website", "url": term["url"]}] if term.get("url") else []
        for l in sup["links"]:
            if l["purpose"] == "website":
                links = [x for x in links if x["purpose"] != "website"]
            links.append(l)
        officials[bid] = {
            "name": {"full": n.get("official_full") or f"{n['first']} {n['last']}",
                     "given": n.get("nickname") or n["first"], "family": n["last"],
                     "suffix": n.get("suffix")},
            "role": role_for(term),
            "party": term.get("party"),
            "state": term["state"],
            "district": term.get("district") if term["type"] == "rep" else None,
            "offices": office_list,
            "emails": sup["emails"],
            "links": links,
            "verifiedAt": sup["verifiedAt"],
        }

    # Senators: two slots per state, senior first, null for a vacancy.
    states = {}
    for st, name in NAMES.items():
        ids = sorted((b for b in senate_ids if roster[b]["terms"][-1]["state"] == st),
                     key=lambda b: (roster[b]["terms"][-1].get("state_rank") != "senior", b))
        if st in NON_STATES:
            if ids:
                raise DataError(f"{st} has senators in the roster")
            states[st] = {"name": name, "senators": []}
        else:
            if len(ids) > 2:
                raise DataError(f"{st} has {len(ids)} senators")
            states[st] = {"name": name, "senators": ids + [None] * (2 - len(ids))}

    zip_matches = hud_zip_matches(paths, house_seats, issues, config)
    zip_offices, office_stats = choose_offices(paths, zip_matches, house_seats, states, officials,
                                               office_points, config, issues)

    data = {
        "schemaVersion": SCHEMA_VERSION,
        "congress": config["congress"],
        "generatedAt": now_iso(),
        "sources": [
            {"id": sid, "url": metas[sid]["url"], "version": version_of(sid, metas[sid], config, clerk),
             "fetchedAt": metas[sid]["fetchedAt"]}
            for sid in sources(config)
        ] + ([{"id": "supplements", "url": "data/supplements.json", "version": "sha256:" + supp_hash,
               "fetchedAt": now_iso()}] if supp_hash else []),
        "states": states,
        "houseSeats": dict(sorted(house_seats.items())),
        "zipMatches": zip_matches,
        "zipOffices": zip_offices,
        "officials": officials,
    }
    contact_forms = sum(1 for b in officials if roster[b]["terms"][-1].get("contact_form"))
    return data, issues, {"communityContactForms": contact_forms, "offices": office_stats}


def version_of(sid, meta, config, clerk):
    if sid.startswith("hud-"):
        return f"{config['hud']['year']}Q{config['hud']['quarter']}"
    if sid.startswith("census-"):
        return f"Gazetteer {config['gazetteer']['year']}; sha256:{meta['sha256'][:16]}"
    if sid == "house-clerk":
        return f"publish-date {clerk.get('publish-date')}, congress {clerk.findtext('title-info/congress-num')}"
    return f"Last-Modified {meta.get('lastModified')}; sha256:{meta['sha256'][:16]}"


def hud_payload(path, config, name):
    doc = json.loads(path.read_text(encoding="utf-8"))
    data = doc.get("data", doc)
    if isinstance(data, list):
        data = data[0]
    want = (str(config["hud"]["year"]), str(config["hud"]["quarter"]))
    got = (str(data.get("year")), str(data.get("quarter")).lstrip("Q"))
    if got != want:
        raise DataError(f"HUD {name} response is for {got[0]} Q{got[1]}, not the configured {want[0]} Q{want[1]}")
    if not data.get("results"):
        raise DataError(f"HUD {name} response has no results")
    return data


def hud_zip_matches(paths, house_seats, issues, config):
    cd = hud_payload(paths["hud-zip-cd"], config, "zip-cd")
    county = hud_payload(paths["hud-zip-county"], config, "zip-county")
    seats = {}
    dropped = {"unassigned": 0, "no-seat": 0}
    for r in cd["results"]:
        z, g = str(r["zip"]), str(r["geoid"])
        if not ZIP_RE.match(z):
            raise DataError(f"HUD returned a malformed ZIP {z!r}")
        st = FIPS.get(g[:2])
        if g.endswith("**"):
            dropped["unassigned"] += 1
            continue
        if st is None or not g[2:].isdigit():
            dropped["no-seat"] += 1
            continue
        seat = f"{st}-{int(g[2:])}"
        if seat not in house_seats:
            raise DataError(f"HUD district {g} ({seat}) is not a seat in the Clerk feed. Seat keys are the same "
                            "for the 119th and 120th Congresses, so this check cannot detect a change of district "
                            "vintage; see the congressNote in tools/data_config.json")
        seats.setdefault(z, set()).add(seat)
    # ZIPs HUD's district file omits, in places with a single seat (for example
    # American Samoa and the Northern Mariana Islands), come from its county file.
    single = {}
    for seat in house_seats:
        st = seat.split("-")[0]
        single[st] = seat if st not in single else None
    by_zip = {}
    for r in county["results"]:
        by_zip.setdefault(str(r["zip"]), set()).add(FIPS.get(str(r["geoid"])[:2]))
    added = []
    for z, sts in by_zip.items():
        if z in seats or not ZIP_RE.match(z) or None in sts or len(sts) != 1:
            continue
        seat = single.get(next(iter(sts)))
        if seat:
            seats[z] = {seat}
            added.append(z)
    issues.append(f"HUD: dropped {dropped['unassigned']} unassigned (**) rows and {dropped['no-seat']} rows "
                  f"with no seat; added {len(added)} single-seat ZIPs from the county file: {sorted(added)}")
    no_zip = sorted(set(house_seats) - {s for v in seats.values() for s in v})
    if no_zip:
        issues.append(f"seats with no ZIP at all: {no_zip}")
    return {z: sorted(v) for z, v in sorted(seats.items())}


# ---------------------------------------------------------------- office selection
# See design_notes/vcard-office-selection.md. Each card carries the DC office and the
# local office nearest the user's ZIP; the choice is made here, per ZIP.

def address_key(a):
    m = re.match(r"\s*(\d+)\s+(?:[NSEW]\.?\s+)?([A-Za-z0-9]+)", a["lines"][-1]) if a["lines"] else None
    return (a["postalCode"][:5], m.group(1), m.group(2).lower()[:5]) if m else (a["postalCode"][:5], a["lines"][-1].lower())


def gazetteer(path):
    """{GEOID: (lat, lon)} from a Census Gazetteer national file (pipe- or tab-delimited)."""
    with zipfile.ZipFile(path) as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    rows = text.splitlines()
    sep = "|" if "|" in rows[0] else "\t"
    head = [h.strip() for h in rows[0].split(sep)]
    gi, la, lo = head.index("GEOID"), head.index("INTPTLAT"), head.index("INTPTLONG")
    out = {}
    for r in rows[1:]:
        f = r.split(sep)
        if len(f) > lo:
            out[f[gi].strip()] = (float(f[la]), float(f[lo]))
    if len(out) < 1000:
        raise DataError(f"{path.name}: only {len(out)} rows; refusing to use it")
    return out


def miles(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 7917.5 * math.asin(math.sqrt(h))


def eligible_offices(offices):
    """Indexes of the local offices a card may carry: those with a phone, else those with an address."""
    with_phone = [i for i, o in enumerate(offices) if o["kind"] == "local" and o["phones"]]
    return with_phone or [i for i, o in enumerate(offices) if o["kind"] == "local" and o["address"]]


def zip_candidates(seats, states, house_seats):
    """The fixed candidate order for one ZIP, shared with the page (src/congress.js):
    the House member of each seat in zipMatches order, then, for each distinct state in
    order of first appearance, its senator slots in order. Vacancies are None."""
    out, seen = [], []
    for s in seats:
        out.append(house_seats[s])
        st = s.split("-")[0]
        if st not in seen:
            seen.append(st)
    for st in seen:
        out.extend(states[st]["senators"])
    return out


def choose_offices(paths, zip_matches, house_seats, states, officials, office_points, config, issues):
    zcta = gazetteer(paths["census-zcta"])
    counties = gazetteer(paths["census-counties"])
    county = hud_payload(paths["hud-zip-county"], config, "zip-county")
    main_county = {}
    for r in county["results"]:
        z, g, w = str(r["zip"]), str(r["geoid"]), r.get("tot_ratio") or 0
        if z not in main_county or w > main_county[z][1]:
            main_county[z] = (g, w)

    def zip_point(z):
        if z in zcta:
            return zcta[z], "zcta"
        g = main_county.get(z, (None,))[0]
        if g in counties:
            return counties[g], "county"
        return None, "none"

    stats = {"officeRoster": 0, "officeZcta": 0, "officeCounty": 0, "officeNone": 0,
             "zipZcta": 0, "zipCounty": 0, "zipNone": 0, "zipsUsingFirstListed": 0}
    points, unplaced = {}, []
    for bid, o in officials.items():
        el = eligible_offices(o["offices"])
        pts = {}
        for i in el:
            p, src = office_points[bid][i], "Roster"
            if p is None and o["offices"][i]["address"]:
                p, src = zip_point(o["offices"][i]["address"]["postalCode"][:5])
                src = src.capitalize()
            stats["office" + (src if p else "None")] += 1
            if p is None and len(el) > 1:
                unplaced.append(f"{bid} {o['offices'][i]['label']}")
            pts[i] = p
        points[bid] = (el, pts)
    if unplaced:
        issues.append(f"offices with no location (treated as farthest): {unplaced}")

    # One string per ZIP, in sorted ZIP order (the order of zipMatches' keys), so the
    # ZIP keys are not repeated: that keeps the table about 22 KB gzipped, not 103 KB.
    out = []
    for z, seats in sorted(zip_matches.items()):
        zp, zsrc = zip_point(z)
        stats["zip" + zsrc.capitalize()] += 1
        chars, fell_back = [], False
        for bid in zip_candidates(seats, states, house_seats):
            if bid is None or not points[bid][0]:
                chars.append("-")
                continue
            el, pts = points[bid]
            if len(el) == 1:
                pick = el[0]
            elif zp is None:
                pick, fell_back = el[0], True
            else:
                pick = min(el, key=lambda i: (miles(zp, pts[i]) if pts[i] else math.inf, i))
            if pick > 9:
                raise DataError(f"{bid}: office index {pick} does not fit one digit")
            chars.append(str(pick))
        stats["zipsUsingFirstListed"] += fell_back
        out.append("".join(chars))
    return out, stats


# ---------------------------------------------------------------- validation

def validate(data, config):
    """Raise DataError unless data follows every hard rule in data-schema.md."""
    def walk(v, path):
        if isinstance(v, float):
            raise DataError(f"floating-point number at {path}")
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")
        elif not (v is None or isinstance(v, (str, int, bool))):
            raise DataError(f"unsupported value type at {path}")
    walk(data, "$")
    if data.get("schemaVersion") != SCHEMA_VERSION:
        raise DataError("wrong schemaVersion")
    for key in ("congress", "generatedAt", "sources", "states", "houseSeats", "zipMatches", "zipOffices", "officials"):
        if key not in data:
            raise DataError(f"missing top-level {key}")
    if "</" in serialize(data):
        raise DataError("'</' appears in the data")
    states, seats, officials = data["states"], data["houseSeats"], data["officials"]
    if set(states) != set(NAMES):
        raise DataError("states must cover the 50 states, DC, PR, GU, VI, AS and MP")
    refs = {}
    for st, s in states.items():
        want = 0 if st in NON_STATES else 2
        if len(s["senators"]) != want:
            raise DataError(f"{st} must have {want} senator slots")
        for b in s["senators"]:
            if b is not None:
                refs.setdefault(b, []).append(("senate", st, None))
    if len(seats) != config["houseSeatCount"] or data["congress"] != config["congress"]:
        raise DataError(f"expected {config['houseSeatCount']} House seats for the {config['congress']}th Congress")
    per_state = {}
    for seat in seats:
        per_state[seat.split("-")[0]] = per_state.get(seat.split("-")[0], 0) + 1
    if set(per_state) != set(NAMES) or any(per_state[s] != 1 for s in NON_STATES):
        raise DataError("every state needs at least one House seat, and DC and each territory exactly one")
    for seat, b in seats.items():
        if not SEAT_RE.match(seat) or seat.split("-")[0] not in NAMES:
            raise DataError(f"bad seat key {seat}")
        if b is not None:
            st, d = seat.split("-")
            refs.setdefault(b, []).append(("house", st, int(d)))
    for z, v in data["zipMatches"].items():
        if not ZIP_RE.match(z):
            raise DataError(f"bad ZIP key {z}")
        if not v or v != sorted(set(v)) or any(s not in seats for s in v):
            raise DataError(f"ZIP {z}: seat list must be non-empty, sorted, unique and known")
    if not isinstance(data["zipOffices"], list) or len(data["zipOffices"]) != len(data["zipMatches"]):
        raise DataError("zipOffices must be a list with one entry per ZIP in zipMatches")
    for z, code in zip(sorted(data["zipMatches"]), data["zipOffices"]):
        cands = zip_candidates(data["zipMatches"][z], states, seats)
        if not isinstance(code, str) or len(code) != len(cands):
            raise DataError(f"zipOffices[{z}] must have one character per candidate ({len(cands)})")
        for b, ch in zip(cands, code):
            el = eligible_offices(officials[b]["offices"]) if b in officials else []
            if (ch == "-") != (not el) or (ch != "-" and int(ch) not in el):
                raise DataError(f"zipOffices[{z}]: {ch!r} is not an eligible local office for {b}")
    if set(refs) != set(officials):
        raise DataError(f"officials and references differ: unreferenced {sorted(set(officials) - set(refs))}, "
                        f"missing {sorted(set(refs) - set(officials))}")
    for b, r in refs.items():
        if len(r) != 1:
            raise DataError(f"{b} is referenced {len(r)} times")
        chamber, st, d = r[0]
        o = officials[b]
        if o["state"] != st or o["district"] != d:
            raise DataError(f"{b}: state/district does not match the seat that references it")
        if (chamber == "senate") != (o["role"] == "senator"):
            raise DataError(f"{b}: role does not match chamber")
        if not o["name"]["full"] or not o["name"]["family"]:
            raise DataError(f"{b}: missing name")
        for off in o["offices"]:
            for ph in off["phones"]:
                if not re.match(r"^\+1\d{10}$", ph["number"]) or ph["type"] != "voice":
                    raise DataError(f"{b}: bad phone {ph}")
        for e in o["emails"]:
            if not EMAIL_RE.match(e["address"]):
                raise DataError(f"{b}: bad email {e}")
        for l in o["links"]:
            if l["purpose"] not in LINK_PURPOSES or not l["url"].startswith(("https://", "http://")):
                raise DataError(f"{b}: bad link {l}")


def serialize(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


# ---------------------------------------------------------------- summary

def summarize(old, new, issues, extra):
    print("\n=== Change summary ===")
    if old is None:
        print("No previous data/congress.json; this is the first build.")
    else:
        o_off, n_off = old.get("officials", {}), new["officials"]
        name = lambda d, b: d[b]["name"]["full"]
        added = sorted(set(n_off) - set(o_off)); removed = sorted(set(o_off) - set(n_off))
        changed = sorted(b for b in set(n_off) & set(o_off) if n_off[b] != o_off[b])
        print(f"Officials: {len(added)} added, {len(removed)} removed, {len(changed)} changed")
        for b in added:
            print(f"  + {b} {name(n_off, b)}")
        for b in removed:
            print(f"  - {b} {name(o_off, b)}")
        for b in changed:
            fields = [k for k in n_off[b] if n_off[b].get(k) != o_off[b].get(k)]
            print(f"  ~ {b} {name(n_off, b)}: {', '.join(fields)}")
        seat_changes = sorted(s for s in set(new["houseSeats"]) | set(old.get("houseSeats", {}))
                              if new["houseSeats"].get(s, "absent") != old.get("houseSeats", {}).get(s, "absent"))
        print(f"House seats changed: {seat_changes or 'none'}")
        sen_changes = [st for st in new["states"] if new["states"][st] != old.get("states", {}).get(st)]
        print(f"Senate delegations changed: {sen_changes or 'none'}")
        oz, nz = old.get("zipMatches", {}), new["zipMatches"]
        zc = [z for z in set(oz) | set(nz) if oz.get(z) != nz.get(z)]
        print(f"ZIPs: {len(nz)} now ({len(nz) - len(oz):+d}); {len(zc)} added, removed or changed")
        if "zipOffices" in old:
            o_codes = dict(zip(sorted(oz), old["zipOffices"]))
            n_codes = dict(zip(sorted(nz), new["zipOffices"]))
            print(f"  nearest-office choices changed for {sum(o_codes.get(z) != c for z, c in n_codes.items())} ZIPs")
        by_state = {}
        for z in zc:
            for st in {s.split('-')[0] for s in oz.get(z, []) + nz.get(z, [])}:
                by_state[st] = by_state.get(st, 0) + 1
        if by_state:
            print("  by state (hundreds in particular states suggests redistricting):",
                  ", ".join(f"{s} {n}" for s, n in sorted(by_state.items(), key=lambda x: -x[1])))
    off = new["officials"]
    vac_house = [s for s, b in new["houseSeats"].items() if b is None]
    vac_sen = [st for st, s in new["states"].items() if None in s["senators"]]
    print("\n=== Coverage and gaps ===")
    print(f"Officials: {len(off)} ({sum(o['role'] == 'senator' for o in off.values())} senators)")
    print(f"Vacant House seats: {vac_house or 'none'}; states with a vacant Senate seat: {vac_sen or 'none'}")
    print(f"ZIPs: {len(new['zipMatches'])}, with several seats: {sum(len(v) > 1 for v in new['zipMatches'].values())}")
    print(f"No local office: {sum(not any(x['kind'] == 'local' for x in o['offices']) for o in off.values())}")
    print(f"Verified policy-feedback link: {sum(any(l['purpose'] == 'policy-feedback' for l in o['links']) for o in off.values())} "
          f"of {len(off)} (upstream lists an unverified contact form for {extra['communityContactForms']}; "
          "the review skill verifies them)")
    st = extra["offices"]
    print(f"Card office locations: {st['officeRoster']} from the roster, {st['officeZcta']} from ZIP centres, "
          f"{st['officeCounty']} from county centres, {st['officeNone']} unknown. ZIP locations: {st['zipZcta']} ZIP "
          f"centres, {st['zipCounty']} county centres, {st['zipNone']} unknown; {st['zipsUsingFirstListed']} ZIPs fall "
          "back to the first listed office for at least one official")
    print(f"Published mailboxes: {sum(bool(o['emails']) for o in off.values())}; "
          f"reviewed records (verifiedAt set): {sum(o['verifiedAt'] is not None for o in off.values())}")
    print(f"\n=== Notes ({len(issues)}) ===")
    for i in issues:
        print("  " + i)


# ---------------------------------------------------------------- main

def main(argv):
    if argv[:1] == ["--check"]:
        validate(json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8")),
                 json.loads(CONFIG.read_text(encoding="utf-8")))
        print(f"{argv[1]}: valid")
        return
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if "--fetch" in argv:
        fetch_all(config, argv[argv.index("--fetch") + 1].split(","))
    elif "--offline" not in argv:
        fetch_all(config)
    data, issues, extra = build(config)
    validate(data, config)
    text = serialize(data)
    validate(json.loads(text), config)
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, OUT)
    summarize(old, data, issues, extra)
    print(f"\nWrote {OUT.relative_to(ROOT)} ({len(text.encode()):,} bytes)")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except DataError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("data/congress.json was not changed.", file=sys.stderr)
        sys.exit(1)
