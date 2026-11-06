# Research: congressional contact data and freshness

Researched November 4, 2026. Answers the [work-item intent](../.work-items/research-contact-data-source/intent.md). Assumes the user's House representative and senators have already been identified. The source comparisons and detailed refresh process below record the initial research recommendations.

## Approved follow-up decisions

**Update 2026-11-05:** HUD access now works, and 2026 Q2 uses 119th Congress districts. See the [HUD crosswalk findings](hud-crosswalk-findings.md) and the final [data schema](../design_notes/data-schema.md).

The user approved the maintained static-data approach and JSON storage, followed by the ZIP-first workflow and HUD-USPS as the ZIP-mapping source. HUD access is for local data generation; the published website and JSON remain credential-free. The token is configured locally, but no authenticated HUD request or production generator has been run. See [approved data approach and proposed JSON format](data-design.md) for the decisions, schema proposal and outstanding validation. Rebuilding when Congress changes is the user's stated baseline; additional mid-Congress refreshes were recommended, and the exact cadence remains open.

## Answer

The requested VCF is feasible without a runtime backend, API key, or account. A maintained static dataset can supply each official's DC phone/address, available local office phones/addresses, public email addresses where published, and a legislative feedback-form URL. Generate the selected contacts in browser JavaScript, or pre-generate individual VCFs when publishing the site.

The qualification is **where published and verified**. There is no complete central directory of public constituent email addresses. The [House's own FAQ](https://www.house.gov/representatives/find-your-representative) says offices choose whether to publish an email address or use a web form. A page described as “Email” may contain a form rather than a mailbox. Do not manufacture email addresses or substitute a form URL into a VCF `EMAIL` property.

**Recommendation:** publish a compact, versioned dataset assembled from the community bulk roster and district-office files, cross-check membership/DC contact details against official House and Senate feeds, and maintain a small supplemental registry for verified legislative feedback URLs and published mailboxes. Rebuild periodically. The deployed product remains static; maintenance happens before deployment.

## Sources and field coverage

| Source | Useful fields | Limits and role |
|---|---|---|
| [congress-legislators current JSON](https://unitedstates.github.io/congress-legislators/legislators-current.json) | Bioguide ID, name, chamber, state/district, official website, DC phone and address, some contact URLs | Practical bulk starting point; includes historical terms, so select the appropriate serving term |
| [District-office JSON](https://unitedstates.github.io/congress-legislators/legislators-district-offices.json) | Multiple local offices with phones, street addresses, cities, states, ZIPs, sometimes fax/hours | Join by Bioguide ID; incomplete fields and missing members exist; does not replace the DC record |
| [House Clerk MemberData XML](https://clerk.house.gov/xml/lists/MemberData.xml) | Official House roster, Bioguide IDs, DC room/building, phone, Congress and publication date | Official cross-check; inspected member records do not provide local offices, mailboxes, or feedback-form URLs |
| [Senate contact XML](https://www.senate.gov/general/contact_information/senators_cfm.xml) | Official Senate roster, Bioguide IDs, DC phone/address, website and a contact-related field | The field named `email` held URLs for all 100 inspected senators; inspect values rather than trusting the field name |
| [contact-congress registry](https://github.com/unitedstates/contact-congress) | Per-member contact-form automation metadata, including initial page URLs | Candidate link source only. Its README says House forms have not been actively maintained since January 2017, though contributions are accepted. A recent repository commit does not verify every member's entry |
| Each official's own website | Authoritative office details, actual feedback page, any published public mailboxes and their purpose | Required to validate/fill gaps; layouts differ, so this is a maintenance task rather than a uniform public API |

The [congress-legislators documentation](https://github.com/unitedstates/congress-legislators) describes the bulk files, office records, and ID relationships. Both it and [contact-congress](https://github.com/unitedstates/contact-congress/blob/master/LICENSE) publish their datasets under CC0. Their presence in this report does not imply an accuracy guarantee. The [House XML guide](https://xml.house.gov/MemberData/MemberData_UserGuide.pdf) documents the official member feed and its changing publication date.

### Measured coverage

These are direct counts of the downloaded data, not advertised guarantees. See [the evidence summary](contact-data-source-evidence.json) for source URLs, response metadata and checks.

| Download/check | Observed result |
|---|---|
| Community current roster | 539 records: 100 senators and 439 House members, including delegates/resident commissioner |
| Current-term DC fields | All 539 contained phone, address, office and website fields |
| Current-term `contact_form` | Present for 86 senators and only 2 House members |
| Current-term `email` | Present for none |
| Local-office dataset | 535 members, all of them in the downloaded current roster; 1,306 office records |
| Local-office fields | 1,274 offices had phones; 1,301 had street addresses; 1,302 had ZIPs; all had city/state; none had `email` |
| Members missing a local-office entry | Four roster members; do not infer that they have no local offices |
| Official membership cross-check | The named House ID set matched the community House set (439); the Senate ID sets also matched (100) |
| Contact-form registry | 792 member YAML files, of which 525 matched the downloaded roster: 100 senators and 425 House members. All 525 parsed and had an initial `visit` URL; 14 current members had no matching file |

The House XML also contained two vacant-seat records without member IDs: its 441 seat records are not 441 serving people. Join actual members by ID and handle vacancies explicitly.

Coverage means a value exists. It does not establish that every number works, every address is current, or every candidate URL opens a legislative feedback form. Filtering the form registry against the serving roster is essential because it contains former members too.

## Legislative feedback forms and real email addresses

For this project, save the page where a constituent can comment on legislation or policy. Do not substitute a newsletter subscription, press inquiry, scheduling request or casework form. A general legislative feedback form with an issue dropdown meets this need; there need not be a separate permanent URL for each issue.

Three public examples were inspected without submitting messages:

- [Pramila Jayapal's contact page](https://jayapal.house.gov/contact/) provides DC and Seattle phone/address details and a form with issue category, subject and message. Its published casework mailbox is specifically for federal-agency help; it should not be relabeled as a general policy inbox.
- [Patty Murray's feedback page](https://www.murray.senate.gov/write-to-patty/) asks for a topic, subject and message and links separately to federal-agency assistance.
- [Maria Cantwell's feedback page](https://www.cantwell.senate.gov/contact/email/form) is presented as “E-Mail Maria” within “Share Your Thoughts.” Her [office-locations page](https://www.cantwell.senate.gov/contact/locations) lists DC and six local offices; their published phone numbers agreed with the inspected bulk records.

HTTP GET checks of the three registry candidate URLs and Cantwell's older roster contact URL returned 200, with redirects where applicable. This is evidence that these sample links resolve, not proof that submission succeeds or all nationwide links are valid. No form was submitted and no message was sent.

Maintain supplemental entries keyed by Bioguide ID, with the verified URL, purpose, source page, and verification date. Include a real mailbox only when an official page publishes it, retaining any restriction such as “casework.” Generic legislative feedback should point to the appropriate form. If a form has not been verified, retain the official homepage as a clearly labeled fallback rather than inventing a `/contact/email` URL.

## What goes into the VCF

One contact per official can contain multiple office numbers and addresses. The [vCard 4.0 standard](https://www.rfc-editor.org/info/rfc6350/) supports repeated `TEL`, `ADR`, `EMAIL`, and `URL` properties. The [vCard 3.0 specification](https://www.rfc-editor.org/info/rfc2426/) also describes phone, address, email, website, notes, unique identifiers, and revision fields. Final version selection and phone-import behavior belong to the separate import research.

| Information | VCF representation |
|---|---|
| Official's name and office | Name/organization/title fields; associate with a stable member ID |
| DC and local office phones | Separate telephone properties; distinguish voice from fax |
| DC and local postal addresses | Separate address properties |
| Public mailboxes, if verified | Email properties; retain purpose restrictions |
| Legislative feedback page and homepage | URL properties; make their purposes clear |
| Office labels and provenance | Labels where supported, plus readable notes as a fallback |

The user should be able to distinguish “Washington, DC” from “Seattle office,” and “Send policy feedback” from “Official website.” Exact preservation of custom phone/URL labels, multiple URLs and notes needs verification in the target contacts apps; standards support does not establish their presentation. Do not use a URL as an email address. Include available local offices rather than claiming a nearest office without doing that separate geographic calculation.

Downloading a VCF creates a contact snapshot. Updating the site's data later does not, by itself, update contacts already imported into a phone. A stable `UID` and revision timestamp can identify records but do not guarantee that a later import merges them correctly.

## Static and dynamic construction are separate from data refresh

| Approach | Behavior | Tradeoffs |
|---|---|---|
| Bundled data, browser-generated VCF | JavaScript selects the matched officials and serializes their records | Supports a single-file page and avoids runtime data dependencies; copying the page copies a snapshot |
| Pre-generated VCF files | Publishing produces one VCF per official; selected cards can be combined in browser code if needed | Simple static delivery; extra files unless embedded; file generation and data refresh are still required |
| Fetch a project-maintained JSON file | Static page fetches a normalized dataset, then builds the VCF | Can update data independently of page markup; needs network access and an explicitly chosen host; external self-hosters depend on that host unless they copy the data |
| Fetch upstream sources directly in the browser | Visitor downloads upstream data and generates contacts | Keyless community JSON is fetchable, but gaps remain, upstream availability/schema changes affect users, and multiple files can be inconsistent |

For live community-JSON checks, requests with an `Origin` header received `Access-Control-Allow-Origin: *`. The two uncompressed bodies totaled 1,942,902 bytes and included considerable information this page does not need. This establishes a plausible cross-origin JSON path without Census-style JSONP, but not a completed Safari/Chrome integration.

The official House/Senate XML responses had no `Access-Control-Allow-Origin` header in the inspected responses. Do not assume our static browser page can fetch them directly. They can instead be downloaded by a local or build-time maintenance process, which is not subject to browser CORS. No credentials were needed for the research downloads.

## Freshness recommendation

A static site cannot keep its embedded data current without someone or something publishing updates. Fetching a public upstream file on every visit only makes the page as fresh as that file; it does not validate the underlying information.

The community JSON responses had `Last-Modified: Thu, 24 Sep 2026 10:21:30 GMT`. The latest queried main-branch change to the current-roster YAML was October 5, and the latest queried district-office YAML change was July 12. These are file/repository signals, not per-field verification dates. The House feed declared publication on November 3; the Senate response had an October 8 Last-Modified date. The membership sets agreed despite these differing dates, but a download timestamp alone should never be called a verification timestamp.

Proposed maintenance process:

1. Check sources daily as a starting policy, with particular attention around swearing-ins, vacancies, replacements and office moves. Frequency remains a project choice; there is no demonstrated daily freshness guarantee from the upstream datasets.
2. Resolve the currently intended membership period, cross-check official IDs, and join contact data by Bioguide ID. Reconcile discrepancies rather than assigning the previous member's details to a successor.
3. Merge verified supplements for policy forms and published mailboxes. Validate field types, phone/address presence, URL destinations, duplicates and unexpected removals. A successful HTTP status alone is insufficient to validate a feedback page's purpose.
4. Publish one coherent, compact dataset with source references, source revisions, fetched dates, per-field verification dates where actually known, and a dataset build timestamp. Generate any static VCFs from that same snapshot.
5. Keep the last usable published version if an upstream download fails, record the failure, and flag stale fields for review. Do not silently replace a valid phone with an empty value because a fetch failed.

This can run manually on a maintainer's machine or as a scheduled build. It does not require visitors or self-hosters to run a server. An abandoned self-hosted copy will still age; it needs either a documented refresh command or an intentional dependency on a maintained remote dataset.

## Open decisions and limits

- Implement the approved maintained JSON approach; finalize contact-field source precedence and whether page markup embeds the JSON or reads a separate static file. HUD is selected for ZIP mapping, with authenticated acquisition and coverage validation still pending.
- Choose the refresh cadence, acceptable age, handling of stale optional fields, and ownership of the supplemental form/email registry.
- Resolve current versus upcoming representation consistently with the [matching research](official-matching.md). Research here checked current-membership IDs; it did not implement a future-membership feed.
- Accept that some officials offer a feedback form without a public general-purpose mailbox. Whether to include purpose-limited mailboxes as extra contact fields is a product choice; their purpose must remain visible.
- Verify multi-phone/address/URL labels and email-purpose notes in target contacts apps. This research made no phone imports and did not check every official's site, dial numbers, validate mailbox delivery, or submit forms.

The research establishes feasible sources, measured coverage, important gaps and maintenance options. It does not deliver a complete nationwide curated contact dataset or implement the site. Those are separate work after the source and maintenance choices are made.
