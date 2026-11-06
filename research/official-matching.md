# Research findings: matching users to their officials

Researched November 4, 2026. Answers the [research intent](../.work-items/research-official-matching/intent.md). This records the original research recommendation; subsequent user direction is noted below. No matching implementation has been started.

**Follow-up:** the user subsequently approved a ZIP-first candidate flow, with official House lookup fallback and contact downloads for each selected representative plus the corresponding senators. The original recommendation below predates that direction. See [ZIP mapping research](zip-district-mapping.md) for inspected sources, state references per candidate, and a demonstrated limitation of the Census shortlist. No matching implementation has been started.

The user then selected HUD-USPS for local acquisition of the ZIP mapping and publication as static JSON. Credential setup is complete, but HUD access, quarter/Congress alignment and actual coverage have not yet been verified. The [data design handoff](data-design.md) records the approved direction and proposed format; the earlier no-account/no-key discussion below describes the initial research constraints, with the approved maintainer-side credential exception now explicit.

**Update 2026-11-05:** HUD access now works, and 2026 Q2 uses 119th Congress districts. See the [HUD crosswalk findings](hud-crosswalk-findings.md) and the final [data schema](../design_notes/data-schema.md).

## Answer and recommendation

The page can satisfy the primary user's needs entirely with bundled data: let the user select their state and recognize their House representative in a list, then obtain the state's senators automatically. Searching directly for a House member could also infer the state. Neither approach requires an address, API key, backend, or external request during matching.

**Recommendation:** use local state-and-name selection as the initial approach, with an optional link to the official House lookup for people who do not recognize their member. Consider integrated address lookup only if supporting that secondary audience justifies the additional complexity. This follows the project's stated priority for users who recognize their House member; its usability advantage is an inference, not a measured result.

The underlying relationships are simple: senators represent states, while House members represent districts. State alone therefore identifies the Senate pair, but generally cannot identify the House member. The official [House roster](https://www.house.gov/representatives) lists members by state and district; the [Capitol Visitor Center's Senate explanation](https://www.visitthecapitol.gov/education-resource/us-senate) confirms two senators per state.

## Practical options

| Option | Static page, no key or backend? | What it resolves | Main tradeoff |
|---|---|---|---|
| State, then recognized House member | Yes; bundle the roster | Senate pair plus the member the user selects | Fits the primary audience; relies on recognition and does not verify residence |
| Search House member by name | Yes; search bundled data | Selected member and that member's state's senators | Potentially fewer steps; needs state/district labels to distinguish similar names and mistakes |
| State only, or state plus district number | Yes | State only works for a single at-large House district; district number resolves other states | Many users recognize a name without knowing a district number |
| ZIP code | Yes with a bundled crosswalk | A shortlist of candidate districts | ZIPs can cross district lines; cannot promise one correct representative |
| Residential street address | Yes using an external service; Census supports keyless requests | Geographic state and district, then a local roster join | Network dependency, address disclosure to the provider, match failures, geography version management |
| Device location or a map pin | Yes with local district polygons, or a coordinate lookup service | District containing the chosen coordinates | Current device location may differ from home; accuracy and boundary uncertainty matter |
| Link to official House lookup | Yes; ordinary link | User identifies their member externally, then returns to select them | Low integration effort; interrupts the flow and requires returning to this page |

These are architectural feasibility judgments, not completed UI prototypes or timing comparisons. A static page can call an external API without hosting its own backend, but then matching is no longer self-contained. Bundling a roster also requires periodic publication of updated files; it does not make membership permanently current.

## Name selection needs no geographic service

A local roster can associate each current member with a stable ID, chamber, state, and House district. Search or selection identifies a record; its state identifies the Senate records. Names should be display/search values rather than database keys. Display state and district alongside names, and allow correction before downloading contacts.

The community-maintained [congress-legislators data documentation](https://github.com/unitedstates/congress-legislators#data-format-documentation) demonstrates that these fields and Bioguide IDs are available in downloadable structured data. It also documents at-large House districts as district `0`. This is evidence that local matching is practical, not a decision to adopt that project's contact data. Choosing the source and refresh process belongs to the separate contact-data research item.

Selecting a senator's name would establish a state but would still leave the House district unresolved in a state with multiple districts. Selecting a House member is sufficient to establish both, provided the user selects the member who represents their residence.

## ZIP codes are a filter, not proof of district

Do not select whichever district contains the largest share of a ZIP's population or addresses. That would assign the wrong member to people living in the other districts. Present candidates for recognition or ask for more information.

Census publishes [119th Congressional District relationship files](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.119th_Congress.html), including relationships to ZIP Code Tabulation Areas (ZCTAs). A preprocessed ZCTA-to-district shortlist could be bundled. However, [Census explains](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) that ZCTAs generalize postal ZIPs and do not represent every valid ZIP. Even a single candidate in such a file is not a universal guarantee for the entered postal ZIP.

[HUD's USPS crosswalk documentation](https://www.huduser.gov/portal/datasets/usps_crosswalk.html) describes quarterly address-based crosswalks and split geographies, but excludes PO-box-only ZIPs. Its current download flow requires login and its API requires an access token, so it does not meet a strict no-account/no-key sourcing requirement. Preprocessing data would remove a runtime credential dependency, but not the acquisition requirement. No HUD dataset was downloaded for this research.

For a concrete example, the [official House lookup for ZIP 10003 in Manhattan](https://www.house.gov/htbin/findrep?ZIP=10003) returned two possible representatives when checked during this research: Daniel Goldman (NY-10) and Jerrold Nadler (NY-12). It requested a street address to distinguish them. Each resident has one House representative; the ZIP spans multiple districts. We did not measure what share of ZIPs identifies a single district nationally.

ZIP entry is therefore feasible as an optional convenience, but adds another dataset and ambiguity handling to a product whose primary audience can already recognize a name.

## Address lookup is feasible, with specific constraints

The [Census Geocoder API documentation](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html) describes address-to-geography and coordinate-to-geography requests, JSONP callbacks, and benchmark/vintage parameters. It explicitly states that CORS is unsupported and directs browser clients to JSONP. No key is required by the documented request format or the live checks below. Ordinary cross-origin `fetch()` of JSON should therefore not be assumed to work.

An integrated version would send a residential address to Census, obtain a district, and resolve that district against the bundled roster. It would need a timeout, clear failure handling, and manual selection as a fallback. JSONP loads provider-supplied JavaScript, so hosting policy must permit that external script. A proxy would add a backend and conflict with the intended deployment model.

In plain terms, JSONP wraps the result in a call to a function on our page, such as `receiveResults({ /* results */ });`, and the browser loads it through a `<script>` element. This does not inherently require a different visible lookup flow. It should work through standard script loading in Safari and Chrome on phones, but this research did not verify either mobile browser. The tradeoffs beyond development effort are provider availability and latency, disclosure of the submitted address to Census, trust in executable provider responses, and extra address-entry effort for users who already recognize their representative.

The [Census Geocoder FAQ](https://www2.census.gov/geo/pdfs/maps-data/data/Census_Geocoder_FAQ.pdf) explains that coordinates are approximate and derived from street address ranges. New construction, missing ranges, and address changes can prevent matches. Consequently, a successful response is useful evidence, not a guarantee of rooftop precision near a district boundary. Show the matched address and resulting member so the user can correct a mismatch.

### Geography must match the chosen Congress

This is a material implementation requirement, not just a data-refresh detail. The [House lookup FAQ](https://www.house.gov/representatives/find-your-representative) distinguishes the district and member currently serving from redrawn districts used for the next election. It also explicitly permits linking to its lookup page. If the page is intended to identify currently serving officials, election winners should not replace them merely because election results are available.

In live checks on the research date, `Current_Current` already returned **120th Congressional Districts**, while `ACS2025_Current` returned **119th Congressional Districts**. The current serving roster is still for the 119th Congress. Thus, blindly combining the latest geographic layer with the current roster can produce incorrect assignments.

**Open policy question:** should the page identify officials currently serving the user, or officials for the upcoming Congress? The recommendation is currently serving officials because the project aims to help users influence votes now, but the user has not selected a policy. If upcoming representation is offered, it needs a distinct, clearly labeled meaning and a membership source that supports that period. In either case, geographic boundaries and the membership roster must describe the same Congress.

The observation above does **not** establish that Census changes its API immediately after elections. Geographic datasets follow their own publication schedule. This API identifies geography; it does not return election winners or the names of serving members. Those names come from a separate roster.

For a prospective implementation, explicitly validate the returned `CDSESSN` against the roster's chosen Congress and reject mismatches. Resolve state FIPS and district codes deliberately, including at-large and delegate codes; do not assume every response has a `CD119` property. The inspected `ACS2025_Current` responses lacked that property but did include `GEOID` and `CDSESSN`. Availability and schemas must be rechecked before implementation.

## Device location and local maps

The [W3C Geolocation specification](https://www.w3.org/TR/geolocation/) requires a secure context and user permission, and exposes a position with an accuracy estimate. The application needs no API key to request that position. However, a visitor could be at work, traveling, or close to a boundary. Asking whether the location is their residence and allowing correction would still be necessary.

Local point-in-polygon matching can avoid an external district lookup if district boundaries are bundled. A map pin could use the same mechanism without device permission, but asks users to locate their home on a map. A typed address would still need a geocoder or a substantial address database.

Census provides [TIGER/Line district boundaries for the 119th Congress](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.119th_Congress.html). Its [cartographic boundary files](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) are simplified for small-scale thematic maps. Prefer the detailed boundary source for residence matching; simplified outlines can introduce errors near borders. This option is possible, but adds geometry processing, payload, and maintenance costs. No national payload size or performance benchmark was measured.

## Verification performed

Read primary government documentation and the data maintainer's schema documentation. Also issued HTTPS requests from Python's standard library with no credentials, using public building addresses only:

| Check | Observed result on November 4, 2026 |
|---|---|
| Census `/benchmarks?format=json` and `/vintages?benchmark=4&format=json` | HTTP 200; available names included the benchmark/vintages used below |
| White House address, JSON request with an `Origin: https://example.org` header | HTTP 200, one match; no `Access-Control-Allow-Origin` response header |
| Same address with `format=jsonp&callback=researchCallback` | HTTP 200, JavaScript content type; response began `/**/researchCallback(` |
| White House address, `Current_Current` and `ACS2026_Current` | Returned congressional session `120` |
| White House address, `ACS2025_Current` and `ACS2024_Current` | Returned congressional session `119`, GEOID `1198` for DC's delegate district |
| 100 Larkin St, San Francisco, CA 94102, `Current_Current` | Returned session `120`, GEOID `0611` |
| Same San Francisco address, `ACS2025_Current` | Returned session `119`, GEOID `0611` |
| 600 4th Ave, Seattle, WA 98104, `ACS2025_Current` | Returned session `119`, GEOID `5307` |

Reproducible example: [San Francisco address, 119th Congress vintage](https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=100%20Larkin%20St%2C%20San%20Francisco%2C%20CA%2094102&benchmark=Public_AR_Current&vintage=ACS2025_Current&format=json). Responses are live and may change. The service documentation above explains the parameters; these observations are direct research checks.

These checks establish endpoint behavior for the sampled requests. They do not establish national address accuracy, show that differing vintages move these particular buildings between districts, execute JSONP in a browser, or demonstrate a complete mobile flow. No app code or unit tests were added.

## Remaining decisions and uncertainty

- Resolve the policy question above: currently serving officials versus upcoming representation. The research recommendation is current service; no policy decision has been made.
- Choose the actual primary interaction: state then name, or direct name search. No usability study has established which is faster or clearer on phones.
- Decide whether an external House lookup link is sufficient for users who cannot recognize their member, or whether integrated address lookup is worth supporting.
- Decide how to handle DC/territories and vacant seats. The literal promise of three contacts does not apply everywhere. The [House membership summary](https://radiotv.house.gov/house-data/party-breakdown) distinguishes delegates, a resident commissioner, and vacancies; missing seats must not be filled with stale or unrelated officials.
- Select and maintain the roster/contact source in the separate research item. Local selection and geographic lookup both depend on this being current.
- If address lookup is chosen, verify browser behavior and hosting policy, broader address coverage, boundary cases, Congress transitions, and failure recovery. This research does not establish a service uptime guarantee or complete provider comparison.

The requested research is complete: the options, constraints, sources, and limitations are recorded. Design selection and implementation remain separate work.
