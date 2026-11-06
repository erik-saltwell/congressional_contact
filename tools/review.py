#!/usr/bin/env python3
"""Batch tooling for the review-congressional-data skill.

    python3 -I tools/review.py prepare --all [--batch-size 25]
    python3 -I tools/review.py prepare --states WA,OR | --ids J000298,M001111 [--name NAME]
    python3 -I tools/review.py report  data/reviews/<batch>
    python3 -I tools/review.py apply   data/reviews/<batch> --approve all|1,2,5
    python3 -I tools/review.py summary   # writes data/reviews/SUMMARY.md across all batches

prepare  writes packets.json (what we publish now, plus upstream candidates)
         and a proposals.json skeleton for the agent to fill in.
report   validates proposals.json, numbers every proposal and writes report.md.
apply    applies only the approved proposal numbers to data/supplements.json,
         records the decision in decisions.json and rebuilds the data offline.
         If the rebuild fails, supplements.json is restored.

Proposal and status formats are documented in
.agents/skills/review-congressional-data/SKILL.md.
"""
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_data as bd  # noqa: E402

REVIEWS = bd.DATA / "reviews"
STATUSES = {"verified", "partial", "unverifiable"}
ACTIONS = {"set-link", "remove-link", "add-email", "remove-email", "replace-offices"}


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def dump(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def today():
    return dt.date.today().isoformat()


def published():
    if not bd.OUT.exists():
        fail("data/congress.json does not exist; run tools/build_data.py first")
    return load(bd.OUT)


def seat_label(o):
    if o["role"] == "senator":
        return f"Senator, {o['state']}"
    return f"{o['role'].replace('-', ' ').title()}, {o['state']}-{o['district']}"


def upstream_roster():
    path, _ = bd.cached("legislators-current")
    return {p["id"]["bioguide"]: p for p in load(path)}


def upstream_local():
    path, _ = bd.cached("legislators-district-offices")
    return {p["id"]["bioguide"]: p.get("offices", []) for p in load(path)}


def supplements():
    return load(bd.SUPPLEMENTS) if bd.SUPPLEMENTS.exists() else {"officials": {}}


# ---------------------------------------------------------------- prepare

def prepare(args):
    data = published()
    officials = data["officials"]
    size, name, ids = 25, None, None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--all":
            ids = sorted(officials, key=lambda b: (officials[b]["state"], officials[b]["role"] != "senator",
                                                   officials[b]["district"] or 0, b))
        elif a == "--states":
            i += 1
            want = set(args[i].upper().split(","))
            ids = sorted((b for b, o in officials.items() if o["state"] in want),
                         key=lambda b: (officials[b]["state"], officials[b]["role"] != "senator",
                                        officials[b]["district"] or 0, b))
        elif a == "--ids":
            i += 1
            ids = args[i].split(",")
        elif a == "--batch-size":
            i += 1
            size = int(args[i])
        elif a == "--name":
            i += 1
            name = args[i]
        else:
            fail(f"unknown option {a}")
        i += 1
    if not ids:
        fail("choose --all, --states or --ids")
    unknown = [b for b in ids if b not in officials]
    if unknown:
        fail(f"not serving officials in data/congress.json: {unknown}")
    roster, sup = upstream_roster(), supplements()["officials"]
    chunks = [ids[k:k + size] for k in range(0, len(ids), size)]
    made = []
    for n, chunk in enumerate(chunks, 1):
        label = name or ("full" if len(ids) == len(officials) else "batch")
        bname = f"{today()}-{label}" + (f"-{n:02d}" if len(chunks) > 1 else "")
        d = REVIEWS / bname
        if d.exists():
            fail(f"{d.relative_to(bd.ROOT)} already exists; pass --name to choose another")
        d.mkdir(parents=True)
        packets = {"batch": bname, "createdAt": today(), "dataGeneratedAt": data["generatedAt"], "officials": {}}
        skeleton = {"batch": bname, "reviewedAt": None, "officials": {}}
        for b in chunk:
            o = officials[b]
            term = roster[b]["terms"][-1]
            packets["officials"][b] = {
                "seat": seat_label(o),
                "published": o,
                "upstreamCandidates": {"contactForm": term.get("contact_form"), "website": term.get("url")},
                "currentSupplement": sup.get(b),
            }
            skeleton["officials"][b] = {"name": o["name"]["full"], "seat": seat_label(o), "status": "pending",
                                        "pagesChecked": [], "notes": "", "proposals": []}
        dump(d / "packets.json", packets)
        dump(d / "proposals.json", skeleton)
        made.append((d, len(chunk)))
    for d, n in made:
        print(f"{d.relative_to(bd.ROOT)}: {n} officials")


# ---------------------------------------------------------------- validate + report

def check_proposals(d):
    props = load(d / "proposals.json")
    packets = load(d / "packets.json")
    if set(props["officials"]) != set(packets["officials"]):
        fail("proposals.json must cover exactly the officials in packets.json")
    if not bd.DATE_RE.match(str(props.get("reviewedAt"))):
        fail("set reviewedAt (YYYY-MM-DD) in proposals.json")
    numbered = []
    for b, r in props["officials"].items():
        w = f"{b} {r.get('name', '')}"
        if r.get("status") not in STATUSES:
            fail(f"{w}: status must be verified, partial or unverifiable, not {r.get('status')!r}")
        pages = r.get("pagesChecked") or []
        if r["status"] == "partial" and not r.get("notes"):
            fail(f"{w}: a partial review needs notes saying what could not be checked")
        if r["status"] in ("verified", "partial") and not pages:
            fail(f"{w}: list the official pages checked")
        if any(not str(u).startswith("https://") for u in pages):
            fail(f"{w}: pagesChecked must be https URLs")
        if r["status"] == "unverifiable" and (not r.get("notes") or r.get("proposals")):
            fail(f"{w}: an unverifiable record needs notes explaining why, and no proposals")
        for p in r.get("proposals", []):
            check_one(p, w)
            numbered.append((b, p))
    return props, packets, numbered


def check_one(p, w):
    act = p.get("action")
    if act not in ACTIONS:
        fail(f"{w}: unknown action {act!r}")
    if not str(p.get("source", "")).startswith("https://"):
        fail(f"{w}: {act} needs an https source URL on an official page")
    if not str(p.get("evidence", "")).strip():
        fail(f"{w}: {act} needs evidence: what the source page shows")
    try:
        if act == "set-link":
            if p.get("purpose") not in bd.LINK_PURPOSES or not str(p.get("url", "")).startswith("https://"):
                raise bd.DataError("set-link needs purpose website|policy-feedback and an https url")
        elif act == "remove-link":
            if p.get("purpose") != "policy-feedback":
                raise bd.DataError("remove-link applies to the policy-feedback link only")
        elif act == "add-email":
            if not bd.EMAIL_RE.match(str(p.get("address", ""))) or not p.get("purpose"):
                raise bd.DataError("add-email needs a real address and a purpose (form URLs go in set-link)")
        elif act == "remove-email":
            if not bd.EMAIL_RE.match(str(p.get("address", ""))):
                raise bd.DataError("remove-email needs the address")
        elif act == "replace-offices":
            bd.check_offices(p.get("offices"), "offices")
    except bd.DataError as e:
        fail(f"{w}: {e}")


def describe(p, current):
    act = p["action"]
    if act == "set-link":
        old = next((l["url"] for l in current["links"] if l["purpose"] == p["purpose"]), "none")
        return f"Set {p['purpose']} link: {old} -> {p['url']}"
    if act == "remove-link":
        return "Remove the policy-feedback link"
    if act == "add-email":
        return f"Add mailbox {p['address']} ({p['purpose']})"
    if act == "remove-email":
        return f"Remove mailbox {p['address']}"
    lines = ["Replace the office list with:"]
    for o in p["offices"]:
        phones = ", ".join(f"{ph['number']} ({ph['type']})" for ph in o["phones"]) or "no phone"
        addr = o["address"]
        where = (", ".join(addr["lines"]) + f", {addr['city']}, {addr['region']} {addr['postalCode']}") if addr else "no address"
        lines.append(f"  - {o['label']}: {phones}; {where}")
    return "\n".join(lines)


def report(args):
    d = batch_dir(args)
    props, packets, numbered = check_proposals(d)
    out = [f"# Review {props['batch']}", "",
           f"Reviewed {props['reviewedAt']} against data generated {packets['dataGeneratedAt']}.", ""]
    counts = {s: sum(r["status"] == s for r in props["officials"].values()) for s in STATUSES}
    out += [f"{len(props['officials'])} officials: {counts['verified']} verified, {counts['partial']} partly checked, "
            f"{counts['unverifiable']} could not be checked. {len(numbered)} proposed changes.", "",
            "Approve with `python3 -I tools/review.py apply " + str(d.relative_to(bd.ROOT)) +
            " --approve all` or a list of numbers such as `--approve 1,3`.", ""]
    n = 0
    for b, r in props["officials"].items():
        cur = packets["officials"][b]["published"]
        out += [f"## {r['name']} ({r['seat']}, {b})", "", f"**Status:** {r['status']}"]
        if r.get("notes"):
            out += ["", r["notes"]]
        if r.get("pagesChecked"):
            out += ["", "Pages checked: " + ", ".join(r["pagesChecked"])]
        if not r.get("proposals"):
            out += ["", "No changes proposed." if r["status"] == "verified" else ""]
        for p in r.get("proposals", []):
            n += 1
            out += ["", f"**#{n}.** {describe(p, cur)}", f"  Source: {p['source']}", f"  Evidence: {p['evidence']}"]
        out.append("")
    (d / "report.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {(d / 'report.md').relative_to(bd.ROOT)} ({len(numbered)} proposals)")


# ---------------------------------------------------------------- apply

def apply(args):
    d = batch_dir(args)
    if "--approve" not in args:
        fail("pass --approve all or --approve 1,2,...")
    choice = args[args.index("--approve") + 1]
    props, packets, numbered = check_proposals(d)
    if (d / "decisions.json").exists():
        fail(f"{d.relative_to(bd.ROOT)} was already applied")
    if choice == "all":
        approved = set(range(1, len(numbered) + 1))
    else:
        approved = {int(x) for x in choice.split(",") if x}
        bad = [x for x in approved if not 1 <= x <= len(numbered)]
        if bad:
            fail(f"no such proposal numbers: {bad}")
    when = props["reviewedAt"]
    roster, local = upstream_roster(), upstream_local()
    doc = supplements()
    entries = doc.setdefault("officials", {})
    backup = bd.SUPPLEMENTS.read_bytes() if bd.SUPPLEMENTS.exists() else None
    rejected_for = set()
    for num, (b, p) in enumerate(numbered, 1):
        if num not in approved:
            rejected_for.add(b)
            continue
        e = entries.setdefault(b, {"links": [], "emails": []})
        e.setdefault("links", []); e.setdefault("emails", [])
        src = {"source": p["source"], "verifiedAt": when}
        act = p["action"]
        if act == "set-link":
            e["links"] = [l for l in e["links"] if l["purpose"] != p["purpose"]] + \
                         [{"purpose": p["purpose"], "url": p["url"], **src}]
        elif act == "remove-link":
            e["links"] = [l for l in e["links"] if l["purpose"] != p["purpose"]]
        elif act == "add-email":
            e["emails"] = [m for m in e["emails"] if m["address"].lower() != p["address"].lower()] + \
                          [{"address": p["address"], "purpose": p["purpose"], **src}]
        elif act == "remove-email":
            e["emails"] = [m for m in e["emails"] if m["address"].lower() != p["address"].lower()]
        elif act == "replace-offices":
            term = roster[b]["terms"][-1]
            up = bd.upstream_offices(term, local.get(b, []), b, [])
            e["offices"] = {"list": p["offices"], "upstreamHash": bd.offices_hash(up), **src}
    for b, r in props["officials"].items():
        if r["status"] == "verified" and b not in rejected_for:
            entries.setdefault(b, {"links": [], "emails": []})["verifiedAt"] = when
    doc["officials"] = dict(sorted(entries.items()))
    dump(bd.SUPPLEMENTS, doc)
    result = subprocess.run([sys.executable, "-I", str(bd.ROOT / "tools" / "build_data.py"), "--offline"])
    if result.returncode != 0:
        if backup is None:
            bd.SUPPLEMENTS.unlink()
        else:
            bd.SUPPLEMENTS.write_bytes(backup)
        fail("rebuild failed; data/supplements.json restored and nothing applied")
    dump(d / "decisions.json", {"appliedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                                "approved": sorted(approved),
                                "rejected": [n for n in range(1, len(numbered) + 1) if n not in approved]})
    print(f"applied {len(approved)} of {len(numbered)} proposals from {d.relative_to(bd.ROOT)}")


def summary(args):
    """Write data/reviews/SUMMARY.md: every batch, its state, and every proposed change."""
    rows, detail = [], []
    totals = {"applied": 0, "pending": 0, "rejected": 0}
    for d in sorted(p for p in REVIEWS.iterdir() if (p / "packets.json").exists()):
        props = load(d / "proposals.json")
        offs = props["officials"]
        done = sum(r["status"] != "pending" for r in offs.values())
        dec = load(d / "decisions.json") if (d / "decisions.json").exists() else None
        nums, n = [], 0
        for b, r in offs.items():
            for p in r.get("proposals", []):
                n += 1
                nums.append((n, b, r, p))
        state = ("applied" if dec else "awaiting approval" if (d / "report.md").exists() and done == len(offs)
                 else f"in review ({done}/{len(offs)})")
        statuses = {s: sum(r["status"] == s for r in offs.values()) for s in ("verified", "partial", "unverifiable")}
        forms = sum(p["action"] == "set-link" and p["purpose"] == "policy-feedback" for _, _, _, p in nums)
        rows.append(f"| {d.name} | {len(offs)} | {state} | {statuses['verified']} / {statuses['partial']} / "
                    f"{statuses['unverifiable']} | {forms} | {len(nums) - forms} |")
        notable = [(k, b, r, p) for k, b, r, p in nums if not (p["action"] == "set-link" and p["purpose"] == "policy-feedback")]
        flagged = [(b, r) for b, r in offs.items() if r["status"] in ("partial", "unverifiable")]
        if notable or flagged:
            detail += [f"### {d.name} ({state})", ""]
            for k, b, r, p in notable:
                mark = "" if not dec else (" (applied)" if k in dec["approved"] else " (rejected)")
                first = describe(p, {"links": []}).splitlines()[0]
                detail.append(f"- **#{k}** {r['name']} ({r['seat']}): {first}{mark}. {p['evidence']}")
            for b, r in flagged:
                detail.append(f"- {r['name']} ({r['seat']}) is **{r['status']}**: {r.get('notes', '')}")
            detail.append("")
        for k, *_ in nums:
            key = "pending" if not dec else ("applied" if k in dec["approved"] else "rejected")
            totals[key] += 1
    out = ["# Pre-launch review summary", "",
           f"Proposals: {totals['applied']} applied, {totals['pending']} awaiting approval, {totals['rejected']} rejected. "
           "Each batch's full evidence is in its report.md.", "",
           "| Batch | Officials | State | Verified / partial / unverifiable | Forms | Other changes |",
           "|---|---|---|---|---|---|", *rows, "",
           "## Changes other than feedback forms, and records not fully checked", "", *detail]
    (REVIEWS / "SUMMARY.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {(REVIEWS / 'SUMMARY.md').relative_to(bd.ROOT)}")


def batch_dir(args):
    if not args:
        fail("give the batch directory")
    d = pathlib.Path(args[0]).resolve()
    if not (d / "packets.json").exists():
        fail(f"{args[0]} is not a review batch (no packets.json)")
    return d


if __name__ == "__main__":
    cmds = {"prepare": prepare, "report": report, "apply": apply, "summary": summary}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(2)
    cmds[sys.argv[1]](sys.argv[2:])
