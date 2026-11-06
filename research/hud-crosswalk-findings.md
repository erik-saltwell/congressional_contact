# HUD ZIP-to-district crosswalk: findings

Researched 2026-11-05 for [Phase 1: HUD data and final schema](../.work-items/impl-01-hud-data-and-schema/). The schema these findings led to is in [design_notes/data-schema.md](../design_notes/data-schema.md). Counts are in [hud-crosswalk-evidence.json](hud-crosswalk-evidence.json), and the probe scripts are in [hud-crosswalk-test/](hud-crosswalk-test/).

## Summary

- **Access works.** An authenticated request to the HUD USPS crosswalk API (type 5, ZIP to congressional district) using the local token returned data. `query=All` returns the whole country in one response of about 6 MB. No paging is needed.
- **Use 2026 Q2, pinned explicitly.** It is the newest quarter, and its districts are the **119th Congress's**. HUD does not say which Congress each quarter uses, so this is inferred from the change patterns below. The data script must always ask for an explicit year and quarter. If the API picks its default "latest" quarter, the districts could switch to the 120th Congress's without warning.
- **Never take the state from HUD's `state` field.** That field is the ZIP's postal state, not the district's state. In 131 rows they differ; for example, ZIP 42223's TN-1 row says `KY`. Take the state from the first two digits of the district `geoid` (its state FIPS code) instead.
- **Coverage (2026 Q2):**
  - 39,347 ZIPs. 6,061 have more than one district, 123 span two states, and the most districts for one ZIP is 4.
  - DC, Puerto Rico, Guam and the U.S. Virgin Islands are present, each as district `00`.
  - **American Samoa and the Northern Mariana Islands are missing entirely**, although both have delegates. They need a small hand-maintained ZIP list.
- **Rows to drop:**
  - 5 rows whose district is `**` (unassigned). Each is a tiny sliver of a ZIP that has a real district too.
  - One `6800` row for Wake Island, which has no representative.
- **Ratios are not needed.** The page never chooses by share, and 71 ratio values come out in exponent form, which Jekyll's YAML reader turns into strings. Leave ratios out of the published data entirely.
- **The published ZIP index is small:** 728 KB raw, 105 KB gzipped, as a map from each ZIP to sorted seat keys such as `"NY-12"`.

## How the vintage was worked out

The national file was downloaded for six quarters. For each pair of quarters, the ZIPs whose set of districts changed were counted by state.

| Change | ZIPs changed | Pattern | Reading |
|---|---|---|---|
| 2024 Q1 → 2025 Q1 | 1,703 | NC 400, AL 278, NY 275, LA 274, GA 179 | The states redrawn for the 119th Congress. **2025 Q1 onward is 119th geography** |
| 2025 Q1 → 2025 Q3 | 11 | none | Routine |
| 2025 Q3 → 2025 Q4 | 0 | none | Routine |
| 2025 Q4 → 2026 Q1 | 624 | at most 46 per state, spread across many states | 625 candidates removed and 43 added. The removed ones have a median residential share of 0.04%. This is sliver cleanup, not redistricting: the 2025–26 mid-decade maps (TX, CA, MO, NC, OH, UT) would move hundreds of ZIPs in those states |
| 2026 Q1 → 2026 Q2 | 7 | none | Routine |

The same method will detect the switch to 120th geography (phase 9): a real switch moves hundreds of ZIPs in the redrawn states.

## Comparison with the official House lookup

HUD 2026 Q2 against `house.gov/htbin/findrep`, checked 2026-11-05:

| ZIP | HUD | House lookup |
|---|---|---|
| 10003 | NY-10, NY-12 | NY-10, NY-12 |
| 42223 | KY-1, TN-1 | KY-1, TN-1, **TN-7** |
| 97635 | CA-1, OR-2 | CA-1, OR-2 |
| 01731 | MA-5, plus MA-6 with no residential addresses | MA-5, MA-6 |
| 50321 | IA-3, plus IA-1 with no residential addresses | IA-1, IA-3 |
| 20164, 78557, 90631 | one district, plus one with no residential addresses | a single result |

- **No source is complete.** For 42223, HUD misses TN-7, and the Census 2020 ZCTA file misses TN-1. The link to the official House lookup stays essential.
- **Candidates with no residential addresses.** In 238 ZIPs with several districts, at least one district holds none of the ZIP's residential addresses. Dropping those candidates would make 202 of the ZIPs single-district. The House lookup is inconsistent: it lists such a candidate for 01731 and 50321 but returns a single result for the three other ZIPs.
  - **Recommendation:** keep these candidates. The approved flows forbid choosing by share. An extra candidate costs little for a user who recognizes their representative's name, while a dropped one could hide the right person.
  - This choice belongs to the owner and is recorded in [phase 2](../.work-items/impl-02-data-script/). Keep the ratios in the local cache so the choice can be revisited without fetching again.

## Roster findings that affect the data script

Checked 2026-11-05 against the community `legislators-current.json` (Last-Modified 2026-09-24), the House Clerk `MemberData.xml` (published 2026-11-03, 119th Congress) and the Senate contact XML.

- **The three sources agree on membership:** 439 House members and 100 senators, with identical Bioguide ID sets.
- **Two House seats are vacant: FL-20 and TX-23.** The Clerk feed lists them as seat records with an empty Bioguide ID; this is how vacancies can be detected.
- **Delegates and the resident commissioner use district `0`** in the community data, matching HUD's `00`. The community data does not separate delegates from the resident commissioner. Puerto Rico's member is the resident commissioner; DC, GU, VI, AS and MP have delegates.
- **Appointed senators: Jon Husted (OH, H001104) and Ashley Moody (FL, M001244).** Both have a term end of 2026-11-03, the special election date. They keep serving until the winners are sworn in. **A term-end date in the past does not mean the person has left office.** Take membership from the official feeds, and rebuild just before launch.

## Limitations

- The Congress each quarter uses is inferred from change patterns. HUD does not publish it.
- House lookup pages with one result are drawn by JavaScript in the browser. So the single results for 98103, 20164, 78557 and 90631 were not confirmed against named districts.
- `hud-crosswalk-test/house_lookup.py` handles only pages with several results, and it splits names oddly. It is a probe, not a validated tool.
- The American Samoa and Northern Mariana Islands ZIP codes have not been checked against a primary source yet. This is a phase 2 step.
- No address-level ground truth was checked. HUD's own documentation says that ZIPs used only for PO boxes are not included.

## Reproducing

Raw responses were kept out of the repository; phase 2 caches them under the Git-ignored `data/cache/`.

- **Fetch one quarter.** The script reads `HUD_API_TOKEN` from `.env` and never prints it:
  ```
  python3 -I research/hud-crosswalk-test/hud_probe.py .env OUT.json type=5 query=All year=2026 quarter=2
  ```
- **Compare quarters:**
  ```
  python3 -I research/hud-crosswalk-test/hud_compare.py Q1.json Q2.json ...
  ```
- **Query the House lookup** (pages with several results only):
  ```
  python3 -I research/hud-crosswalk-test/house_lookup.py 10003 42223
  ```
