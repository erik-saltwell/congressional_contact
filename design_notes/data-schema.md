# Published data schema (version 1)

Settled 2026-11-05 in [Phase 1: HUD data and final schema](../.work-items/impl-01-hud-data-and-schema/), based on real HUD and roster responses ([findings](../research/hud-crosswalk-findings.md)). It replaces the proposal in [research/data-design.md](../research/data-design.md).

The data script (phase 2) writes this file as `data/congress.json`. The build script inlines it into both outputs, and the page reads it from `#cc-data`.

## Shape

```json
{
  "schemaVersion": 1,
  "congress": 119,
  "generatedAt": "2026-11-05T20:00:00Z",
  "sources": [
    { "id": "hud-zip-cd", "url": "https://www.huduser.gov/hudapi/public/usps?type=5&query=All&year=2026&quarter=2", "version": "2026Q2", "fetchedAt": "2026-11-05T19:00:00Z" },
    { "id": "house-clerk", "url": "https://clerk.house.gov/xml/lists/MemberData.xml", "version": "publish-date 2026-11-03, congress 119", "fetchedAt": "2026-11-05T19:00:00Z" }
  ],
  "states": {
    "NY": { "name": "New York", "senators": ["S000148", "G000555"] },
    "OH": { "name": "Ohio", "senators": ["M001242", "H001104"] },
    "DC": { "name": "District of Columbia", "senators": [] }
  },
  "houseSeats": {
    "NY-10": "G000599",
    "NY-12": "N000002",
    "FL-20": null,
    "DC-0": "N000147"
  },
  "zipMatches": {
    "10003": ["NY-10", "NY-12"],
    "20001": ["DC-0"]
  },
  "zipOffices": ["1144", "-"],
  "officials": {
    "N000002": {
      "name": { "full": "Jerrold Nadler", "given": "Jerrold", "family": "Nadler", "suffix": null },
      "role": "representative",
      "party": "Democrat",
      "state": "NY",
      "district": 12,
      "offices": [
        {
          "label": "Washington, DC",
          "kind": "dc",
          "phones": [{ "number": "+12022255635", "type": "voice" }],
          "address": { "lines": ["2132 Rayburn House Office Building"], "city": "Washington", "region": "DC", "postalCode": "20515-3212", "country": "US" }
        }
      ],
      "emails": [],
      "links": [
        { "purpose": "website", "url": "https://nadler.house.gov/" },
        { "purpose": "policy-feedback", "url": "https://nadler.house.gov/contact/" }
      ],
      "verifiedAt": null
    }
  }
}
```

The example is abbreviated: only some sources and records are shown. Its member IDs, Nadler's phone and his DC address match the community roster fetched on 2026-11-05. His `policy-feedback` URL is a placeholder: the roster has no form for him, and it has not been checked. The data script fills the real values.

## Fields

| Field | Rule |
|---|---|
| `schemaVersion` | Integer. Raise it on any breaking change; the page checks it. |
| `congress` | The Congress that **both** the roster and the district geography describe. HUD does not say which Congress a quarter uses, so the script cannot detect this. Instead, `tools/data_config.json` declares the vintage of the pinned quarter (inferred as described in the phase 1 findings). The script fails if that declared vintage differs from the roster's Congress, if the House Clerk feed is for a different Congress, or if HUD returns a different year or quarter than the one requested. |
| `generatedAt` | When the build ran (ISO 8601, UTC). It is not a verification date. |
| `sources[]` | One entry for each input: `legislators-current`, `legislators-district-offices`, `house-clerk`, `senate`, `hud-zip-cd`, `hud-zip-county`, `census-zcta`, `census-counties` and `supplements`. The two Census Gazetteer files (year pinned in `tools/data_config.json`) give ZIP and county centres. The build uses them only to choose offices; no coordinates are published. Each has an `id`, a `url`, a `version` (the HUD year and quarter, a feed's publish date or Last-Modified value, or a file hash) and `fetchedAt`. The HUD URL always names its year and quarter. |
| `states` | Keyed by postal code. It covers all 50 states plus DC, PR, GU, VI, AS and MP. `name` is the display name. `senators` has exactly two entries for a state and none for DC or a territory. A vacant Senate seat is `null`. |
| `houseSeats` | Keyed by seat: `ST-N`, where N is the district number with no leading zero. At-large seats, delegates and the resident commissioner are `-0`. The value is a Bioguide ID, or `null` for a vacant seat. Every seat in the House (441 in the 119th Congress) has an entry. |
| `zipMatches` | Keyed by five-digit ZIP string (leading zeros kept). The value is a sorted list of seat keys. A ZIP that matches nothing is absent, which does not make it invalid. |
| `zipOffices` | Added 2026-11-06 (phase 4). It is additive, so `schemaVersion` is unchanged. It is a list with one string per ZIP, in the sorted order of `zipMatches`' keys. Each string has one character per candidate official, in a fixed order: the House member of each seat in that ZIP's `zipMatches` list, then, for each distinct state in order of first appearance, its senator slots. A digit is the position, in that official's `offices`, of the local office the vCard carries for this ZIP. `-` means a vacant seat or no eligible local office. The rules are in [vcard-office-selection.md](vcard-office-selection.md). |
| `officials` | Keyed by Bioguide ID. It contains every official named in `states` or `houseSeats`, and no one else. |
| `officials.*.role` | `senator`, `representative`, `delegate` or `resident-commissioner`. PR's member is the resident commissioner; DC, GU, VI, AS and MP have delegates. |
| `officials.*.district` | `null` for senators. `0` for at-large seats, delegates and the resident commissioner. |
| `officials.*.party` | The party name as the roster gives it. The page decides whether to show it. |
| `officials.*.offices[]` | The DC office first, then local offices. Each has a `label` people can read, a `kind` (`dc` or `local`), `phones[]` (each an E.164 `number` with `type` `voice`; fax numbers are not published, by owner decision 2026-11-05) and an `address` (or `null`). |
| `officials.*.emails[]` | Only mailboxes an official page publishes. Each has an `address` and a `purpose` (for example `general` or `casework`). A form URL never goes here. |
| `officials.*.links[]` | Each has a `purpose` (`website` or `policy-feedback`) and a `url`. `policy-feedback` is only a page that has been checked to accept comments on legislation or policy. |
| `officials.*.verifiedAt` | The date (`YYYY-MM-DD`) of the last online review of this record, or `null`. A rebuild never advances it. |

Source references for each contact value live in the input files (`data/supplements.json` and the review reports), not in the published data. That keeps the page small.

**The reporting address is not part of this file.** The build script adds it from per-host configuration, so a data refresh never overwrites a host's address. Phase 7 settles the mechanism.

## Hard rules (the data script fails on any of these)

1. **Only strings, integers, booleans, `null`, arrays and objects. No floating-point numbers anywhere.** This rules out exponent form, which Jekyll's YAML reader turns into strings. It is the reason HUD ratios are not published.
2. **No `</` anywhere in the serialized file.**
3. **ZIP keys match `^[0-9]{5}$`. Seat keys match `^[A-Z]{2}-[0-9]{1,2}$`.**
4. **Every reference resolves:**
   - each seat in `zipMatches` exists in `houseSeats`;
   - each ID that is not `null` exists in `officials`;
   - each official is referenced exactly once;
   - each official's `state` and `district` match the seat that references them.
5. **Seat counts match the apportionment for the chosen Congress**, and each state has two Senate entries.
6. **Membership matches the official feeds.** The House IDs and Senate IDs must match the Clerk and Senate feeds exactly. Vacancies come from Clerk seat records with an empty Bioguide ID. A past term-end date never removes anyone (for example, appointed senators serve until their successor is sworn in).

## How HUD rows become `zipMatches`

1. Fetch type 5 with `query=All` and an **explicit** `year` and `quarter`, which the data script's configuration sets. The API's "latest" default is never used.
2. Take the state from the `geoid`'s first two digits (state FIPS) and the district from the last two. HUD's `state` field is ignored.
3. Drop rows whose district is `**`, and rows whose state code has no seat (for example `68`, Wake Island).
4. Keep every other candidate, including those with no residential addresses (owner decision, 2026-11-05).
5. Fill gaps from HUD's ZIP-to-county file (type 2, same quarter). A ZIP missing from the district file is added only when all of its counties are in a state or territory with a single House seat. In 2026 Q2 this adds 9 ZIPs:
   - American Samoa: 96799.
   - Northern Mariana Islands: 96950, 96951, 96952.
   - DC: 20388, 56998.
   - Wyoming: 82002, 82010.
   - Alaska: 99811.

   This replaced the hand-maintained `manual-zips.json` that phase 1 proposed. HUD itself is now the source for these ZIPs.

## Input files (committed, not published)

- **`data/supplements.json`:** verified feedback forms and public mailboxes, keyed by Bioguide ID. Each entry records `source` and `verifiedAt`. Phase 3 decides whether this file also overrides wrong values from the bulk roster, or whether those go in a separate corrections file.
- **`tools/data_config.json`:** the Congress number, the expected House seat count, the pinned HUD year and quarter, and the pinned Census Gazetteer year.

## Size

Measured on 2026 Q2: `zipMatches` alone is 728 KB raw, or 105 KB gzipped (39,346 ZIPs). The first real build (phase 2, before any review) is 1.32 MB compact, or 192 KB gzipped. Adding `zipOffices` (phase 4) took it to 1.60 MB compact, or 217 KB gzipped. The committed `data/congress.json` is written indented for readable diffs (2.1 MB); the build script writes it compact.
