"""Generate a synthetic dataset shaped like research/data-design.md.

Throwaway research fixture: sized like the real data (about 40k ZIPs and
540 officials) and seeded with strings that stress Liquid, YAML and HTML.
Usage: python3 -I gen_sample.py OUT.json
"""
import json
import random
import sys

random.seed(119)
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
          "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
          "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
          "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
TRICKY = [
    "José Álvarez-Núñez", "Patrick O'Brien", "Smith & Jones",
    "Braces {{ not.liquid }}", "Tags {% not_a_tag %}", 'Quote "Q" Name', "Back\\slash",
    "Emoji-free — dash", "Tab\tinside",
]


def office(i, dc):
    return {
        "label": "Washington, DC" if dc else f"District Office {i}",
        "kind": "dc" if dc else "district",
        "phones": [{"number": f"+1202225{i:04d}", "type": "voice"},
                   {"number": f"+1202226{i:04d}", "type": "fax"}],
        "address": {"lines": [f"{100 + i} Rayburn House Office Building"], "city": "Washington",
                    "region": "DC", "postalCode": "20515", "country": "US"},
    }


def official(i, role, state, district):
    given = TRICKY[i % len(TRICKY)] if i < len(TRICKY) else f"Given{i}"
    return {
        "name": {"full": f"{given} Family{i}", "given": given, "family": f"Family{i}"},
        "role": role, "state": state, "district": district,
        "offices": [office(i, True), office(i, False)],
        "emails": [],
        "links": [{"purpose": "website", "url": f"https://member{i}.house.gov/"},
                  {"purpose": "policy-feedback", "url": f"https://member{i}.house.gov/contact/?a=1&b=2"}],
        "sourceUrls": [f"https://member{i}.house.gov/contact/"],
        "verifiedAt": None,
    }


def main(out):
    officials, states, reps = {}, {}, []
    n = 0
    for st in STATES:
        ids = []
        for _ in range(2):
            oid = f"S{n:06d}"
            officials[oid] = official(n, "senator", st, None)
            ids.append(oid)
            n += 1
        states[st] = {"senatorIds": ids}
    for k in range(435):
        st = STATES[k % len(STATES)]
        oid = f"R{n:06d}"
        officials[oid] = official(n, "representative", st, k // len(STATES) + 1)
        reps.append(oid)
        n += 1
    zips = {}
    for z in range(40000):
        key = f"{random.randint(501, 99950):05d}"
        cands = random.sample(reps, 2 if random.random() < 0.1 else 1)
        zips[key] = [{"state": officials[r]["state"], "district": officials[r]["district"],
                      "representativeId": r} for r in cands]
    zips["01001"] = [{"state": "MA", "district": 1, "representativeId": reps[0]}]
    data = {"schemaVersion": 1, "congress": 119, "generatedAt": "2026-11-05T00:00:00Z",
            "officials": officials, "states": states, "zipMatches": zips}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main(sys.argv[1])
