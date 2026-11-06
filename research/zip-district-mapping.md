# Research: ZIP-to-district mappings for the static lookup

Researched November 4, 2026, as follow-up to [official matching](official-matching.md). The user approved a ZIP-first flow: show candidate representatives and the associated senators, offer the official House lookup for uncertainty, and let a user save the three contacts associated with their selected representative. Contact information will be stored in JSON. This document preserves the source evaluation; no production lookup was implemented.

## Approved source decision

**Update 2026-11-05:** HUD access now works, and 2026 Q2 uses 119th Congress districts. See the [HUD crosswalk findings](hud-crosswalk-findings.md) and the final [data schema](../design_notes/data-schema.md).

The user selected **HUD-USPS ZIP-to-congressional-district data**, to be acquired during local data generation and published as static JSON. The HUD token is configured locally in a Git-ignored `.env` file; the deployed page needs no credential. No authenticated request or HUD data validation has been performed yet. See [approved data approach and proposed JSON format](data-design.md) for the workflow, credential setup, state references per candidate, refresh discussion and remaining checks.

This decision supersedes the conditional Census-first recommendation at the end of this initial research. Census remains comparison evidence rather than the selected primary mapping source.

## Finding

**A free, directly downloadable Census mapping is available and small enough for a static site. It provides a geographic shortlist, not a complete mapping of current postal ZIPs.** A spot-check found a real difference from the official House lookup, so the fallback needs to remain available for single and missing matches as well as multiple matches.

The most straightforward source is the Census Bureau's [119th Congressional District to 2020 ZCTA relationship file](https://www2.census.gov/geo/docs/maps-data/data/rel2020/cd-sld/tab20_cd11920_zcta520_natl.txt), documented among its [119th Congress relationship products](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.119th_Congress.html). It downloaded without an account or API key. State is encoded in each congressional district GEOID, and [Census state codes](https://www2.census.gov/geo/docs/reference/state.txt) translate it to the state's postal abbreviation.

## Direct inspection and trial conversion

Downloaded the pipe-delimited Census file and retained rows with both geography identifiers, a real district rather than `ZZ`, and positive land overlap. Deduplicated by the complete pair of ZCTA and district GEOID, preserving state. This produced:

| Measurement | Observed result |
|---|---:|
| Source file size | 6,195,997 bytes |
| Source rows | 40,397 |
| Retained district/ZCTA pairs | 40,079 |
| Distinct ZCTA keys | 33,791 |
| Keys with one district candidate | 27,962 |
| Keys with multiple candidates | 5,829 |
| Keys with candidates in more than one state | 137 |
| Largest candidate count | 4 |
| Trial compact JSON size | 618,464 bytes |
| Trial gzip size | 89,315 bytes |

The size measurement uses a minimal JSON object mapping five-character ZCTA strings to arrays of four-character district GEOIDs. It excludes the metadata, state names, official IDs, and contact records required for the final dataset. These counts describe the trial geography index, not the share of people or actual postal ZIPs covered correctly. Positive land overlap can still be an uninhabited sliver; it does not prove that constituents live in every candidate district.

Examples from the downloaded file:

| ZCTA key | Candidate districts |
|---|---|
| `10003` | NY-10, NY-12 |
| `98103` | WA-7 |
| `42223` | KY-1, TN-7 |
| `97635` | CA-1, OR-2 |

Keys must remain strings to preserve leading zeros. District/state identifiers must be interpreted within the dataset's Congress. Standard at-large districts use `00`; delegate/resident-commissioner records can use `98`, which needs an explicit translation when joining a roster that uses district `0`.

## Postal ZIP accuracy: a concrete limitation

[Census explains](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) that ZCTAs are generalized areal representations of postal ZIPs, and not every valid ZIP has a ZCTA. The file combines 2020 ZCTAs with 119th Congress district geography; it is not a current USPS delivery-address crosswalk. A postal ZIP may therefore have no key, or a candidate set that differs from a postal lookup.

Direct HTTP requests to the official House lookup confirmed:

- [ZIP 10003](https://www.house.gov/htbin/findrep?ZIP=10003): NY-10 and NY-12, agreeing with the trial index.
- [ZIP 42223](https://www.house.gov/htbin/findrep?ZIP=42223): KY-1, TN-1 and TN-7. The trial Census index did not include TN-1 for this key.

This is a comparison of the two services, not address-level ground truth for all residents. Nevertheless, it establishes that the Census shortlist is not equivalent to the official House postal lookup. No nationwide error rate was measured. No address was submitted to the House form and no CAPTCHA was bypassed.

## Alternatives researched

| Source | Assessment for this project |
|---|---|
| Census relationship file above | Best verified account-free input for a reproducible geographic shortlist. Preserve its limitations in the UI and metadata |
| [HUD-USPS ZIP crosswalk](https://www.huduser.gov/portal/datasets/usps_crosswalk.html) | A postal-address-based source, updated quarterly. Its [API documents ZIP-to-CD as type 5](https://www.huduser.gov/portal/dataset/uspszip-api.html), including state+district identifiers. The download workflow requires login and the API requires a token. A maintainer could acquire data at build time while the deployed page stays credential-free. Current ZIP-CD district vintage and actual mapping quality still require inspection |
| [OpenSourceActivismTech CSV and generator](https://github.com/OpenSourceActivismTech/us-zipcodes-congress) | Downloadable 119th Congress Census-derived mapping, but adds an unnecessary intermediate dependency. Code inspection found a tract-based join that can broaden candidates, and final deduplication uses ZCTA+district number without state. The inspected CSV had 33,774 keys; 1,927 Census-index keys had a different candidate set. Prefer the direct relationship table |
| [What District Am I In? downloads](https://whatdistrictamiin.com/zip-code-to-congressional-district/) | Provides free CSV/JSON, but describes Census-derived geography and missing PO-box/single-delivery ZIPs. It does not remove the postal-versus-ZCTA limitation. Downloads were not independently audited |
| [ZIPInfo congressional ZIP database](https://www.zipinfo.com/products/cdz/) | Vendor offers a 119th Congress downloadable postal-ZIP dataset, including ZIP types and multiple-district flags. It requires purchase, and its product page distinguishes external redistribution through a separate addendum. Accuracy and suitability for an openly copied/self-hosted dataset were not validated; no purchase or license agreement was made |

HUD's documentation also excludes PO-box-only ZIPs. An attempted direct download of the historical `ZIP_CD_062024.xlsx` URL returned HTTP 202 with an empty HTML body rather than a spreadsheet; it was not usable evidence of current data access. During that initial research pass, no HUD account was created or token requested; the subsequent credential setup is recorded above. Its current API page says no special content restrictions have been provided; do not infer that a third-party README's description of the separate USPS vacancy-data sublicense necessarily governs this crosswalk.

The CRS district workbook was also identified, but its [official accompanying report](https://www.congress.gov/crs_external_products/IN/PDF/IN12489/IN12489.5.pdf) describes a workbook for congressional users to download from CRS.gov. No publicly downloadable, independently inspectable workbook was obtained in this research.

## JSON and workflow implications

The state reference belongs to **each candidate**, because a ZIP-shaped key may produce candidates in different states. An illustrative fragment using the verified Census index is:

```json
{
  "zipMatches": {
    "10003": [
      { "state": "NY", "district": 10 },
      { "state": "NY", "district": 12 }
    ],
    "42223": [
      { "state": "KY", "district": 1 },
      { "state": "TN", "district": 7 }
    ]
  }
}
```

This intentionally shows the Census candidate set, including its known difference for `42223`; it is not a corrected postal mapping. A production build could add each district's current `representativeId` after joining the chosen roster. Use the candidate's state to access `states[state].senatorIds`. Do not attach one universal state or Senate pair to a ZIP key. If candidates span states, group results by state or show the senators associated with the selected representative. Vacancies and territories require their existing special handling.

The dataset should state its Congress, source URL/version, mapping basis (`zcta`, not `postal-zip`), ZCTA vintage and generation date. An ambiguous result offers the recognition-based choice discussed with the user. Single and missing matches also retain the official lookup/name-search fallback. Do not classify an unmatched key as an invalid ZIP. Revisit the source when district boundaries change; rebuilding the same old source will not produce new geography.

## Original recommendation and subsequent decision

For an initial, openly self-hostable implementation, use the direct Census relationship file **if the product accepts a best-effort shortlist with a reliable escape route**. The proposed workflow is feasible on that basis. It cannot promise that every postal ZIP will return all relevant representatives.

If complete postal coverage is required before launch, the next task identified by the initial research was to acquire and inspect a current postal-based crosswalk. This research did not verify a complete, current postal-ZIP mapping available without an account or purchase. The user subsequently selected HUD and supplied credentials for local acquisition. The source choice is now settled; successful authenticated access, Congress/quarter alignment and coverage validation are still pending.

Detailed counts and comparison results are recorded in [zip-district-mapping-evidence.json](zip-district-mapping-evidence.json). Research checks used temporary downloads and direct parsing only; no production dataset or app code was added.
