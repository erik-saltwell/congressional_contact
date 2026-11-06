# Approved data approach and proposed JSON format

> **Superseded in part (2026-11-05).** The final schema is now [design_notes/data-schema.md](../design_notes/data-schema.md). HUD access has been verified; see the [HUD crosswalk findings](hud-crosswalk-findings.md). The JSON below is the original proposal and is kept for history. The approved direction above still stands.

Recorded November 4, 2026, following the [contact-data research](contact-data-source.md) and [ZIP-mapping research](zip-district-mapping.md).

## Approved direction

- Publish maintained static JSON containing the contact information and lookup indexes. Generate VCFs from that data in the browser; visitors do not need a backend, account or API key.
- Use the bulk contact-data approach described in the contact-data research, supplemented by verified legislative feedback-form links and published public mailboxes. HUD supplies the ZIP mapping, not officials' contact details.
- Use the **HUD-USPS ZIP-to-congressional-district crosswalk** as the chosen mapping source. Its [API documentation](https://www.huduser.gov/portal/dataset/uspszip-api.html) identifies ZIP-to-CD as crosswalk type `5`.
- Acquire HUD data during local data generation, then publish the resulting mapping as JSON. The maintainer credential is not part of the website or generated dataset.
- Offer a ZIP-first workflow: enter a ZIP, show candidate House members and the corresponding senators, and provide a download/open action for the selected representative plus their two senators. Offer the official House lookup for ambiguity and retain an escape route for missing or unexpected matches.
- Keep one collection of officials with state and ZIP indexes. Each ZIP candidate references its state so the appropriate senators can be resolved, including when candidates span state lines.

These decisions supersede the earlier preference for state/name selection as the initial interaction and the later conditional recommendation to use Census ZCTAs as the default mapping. The underlying Census research and its observed limitations remain useful comparison evidence.

## Proposed JSON structure

The following captures the discussed structure. It is a format proposal, not a generated dataset or implemented schema. The ZIP example reflects earlier inspected Census/House results; it has not yet been checked against an authenticated HUD response.

```json
{
  "schemaVersion": 1,
  "congress": 119,
  "generatedAt": "2026-11-04T20:00:00Z",
  "officials": {
    "J000298": {
      "name": {
        "full": "Pramila Jayapal",
        "given": "Pramila",
        "family": "Jayapal"
      },
      "role": "representative",
      "state": "WA",
      "district": 7,
      "offices": [
        {
          "label": "Washington, DC",
          "kind": "dc",
          "phones": [
            { "number": "+12022253106", "type": "voice" }
          ],
          "address": {
            "lines": ["2346 Rayburn House Office Building"],
            "city": "Washington",
            "region": "DC",
            "postalCode": "20515",
            "country": "US"
          }
        }
      ],
      "emails": [],
      "links": [
        {
          "purpose": "website",
          "url": "https://jayapal.house.gov/"
        },
        {
          "purpose": "policy-feedback",
          "url": "https://jayapal.house.gov/contact/"
        }
      ],
      "sourceUrls": ["https://jayapal.house.gov/contact/"],
      "verifiedAt": null
    }
  },
  "states": {
    "WA": {
      "senatorIds": ["C000127", "M001111"]
    }
  },
  "zipMatches": {
    "98103": [
      { "state": "WA", "district": 7, "representativeId": "J000298" }
    ]
  }
}
```

The timestamp is illustrative. The example abbreviates the officials collection and local offices: a complete dataset must include every referenced official and all available verified office details. The sample contact fields were drawn from the [previously inspected official contact page](https://jayapal.house.gov/contact/).

Conventions discussed:

- Key officials by Bioguide ID and postal ZIPs by five-character strings, preserving leading zeros. Store state once per candidate rather than once per ZIP; a ZIP can have candidates in different states.
- Resolve senators through `states[candidate.state].senatorIds`; do not repeat the Senate pair on every representative. Display senators once for a shared state; associate the correct pair with each candidate when states differ.
- Include multiple DC/local office records with labeled voice/fax numbers and structured addresses. A senator's `district` is `null`; normalize at-large representatives to `0`. Delegate/resident-commissioner codes need deliberate translation from the source.
- Store genuine mailboxes separately from links. An email entry has `address` and `purpose`; a casework mailbox must remain labeled as casework. Use empty arrays for unavailable collections and `null` for an unavailable address.
- Distinguish website and policy-feedback URLs. Store source references and actual verification dates; rebuilding advances `generatedAt`, not an unverified field's `verifiedAt`.
- Record the HUD quarter, source revision or downloaded-file identity, geographic Congress and acquisition date in dataset provenance. The exact provenance layout, vacancy representation and final field requirements remain to be specified after inspecting HUD's response.

## Credential setup completed

The user registered for HUD's **USPS ZIP CODE CROSSWALK** dataset and supplied a token through private secret entry. It is stored locally as `HUD_API_TOKEN` in the repository's `.env` file. That file is Git-ignored and has owner-only permissions (`0600`). The checked-in template is [.env.example](../.env.example), and [.gitignore](../.gitignore) excludes local environment files while allowing that template.

Only local data-generation tools should load this variable and use it in HUD's documented `Authorization: Bearer` header. No token value belongs in research documents, URLs, logs, browser bundles or published JSON. The generator has not been written; a `.env` file by itself does not load the token into a process.

Credential storage and file permissions were verified. **Update 2026-11-05:** the token works against the API. National files for six quarters were downloaded and compared with the research examples, and 2026 Q2 was identified as 119th Congress geography; see the [HUD crosswalk findings](hud-crosswalk-findings.md).

## Refresh policy and remaining work

The user's stated baseline is to rebuild when Congress changes. Membership changes, office moves, contact-link changes and postal updates can occur within a Congress, so additional refreshes were recommended. A fixed schedule, maximum acceptable age and automation have not been approved or implemented.

Next, when data acquisition or implementation is requested. Steps 1–3 are done in phase 1: see the [findings](hud-crosswalk-findings.md) and the [schema](../design_notes/data-schema.md). Step 4 is phases 2 and 4 of the [implementation plan](../.work-items/implementation-plan/plan.md).

1. Make an authenticated HUD type-5 request using the local token, choosing an explicit quarter. Verify the serving Congress represented by that quarter rather than assuming the newest geography is appropriate.
2. Inspect the returned state/district codes and coverage. Compare at least `10003`, `98103` and the cross-state `42223` with the earlier evidence and official House lookup. Preserve all candidates rather than selecting a dominant district by address share.
3. Acquire the complete chosen crosswalk, join it to the same Congress's roster, and settle the final JSON schema, provenance and vacancy handling.
4. Implement reproducible JSON generation, VCF serialization and the approved lookup flow. Verify the resulting phone import behavior through the separate import work.

HUD's documented PO-box-only ZIP omission still applies; selecting it does not establish universal postal coverage. Current versus upcoming representation remains an open policy choice. Choosing the source and saving this design do not by themselves resolve those questions or start implementation.
