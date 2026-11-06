# Implementation plan

Drafted 2026-11-05. This plan covers everything from the first real data download to the 120th Congress refresh. Each phase has its own work item (listed in [item.md](item.md)), and each phase item links back to its section here.

## Intent in brief

Congressional Contact is a phone-first page. A visitor enters a ZIP, sees their senators and every candidate House representative, and saves each official as a vCard with one tap per person. The page is static. It has no backend, accounts or visitor-side keys, and its data is maintained JSON inlined into the page. One shared source builds two outputs: a four-file Jekyll version for eriksaltwell.com and a standalone single HTML file for self-hosters.

Background documents. They are not repeated here.
- [Project context](../../.agent_context.md)
- [User experience flows](../../design_notes/user-experience-flows.md): approved behaviour.
- [Existing site design](../../design_notes/existing-site-design.md): styling decisions under "Owner decisions".
- [Jekyll integration](../../research/jekyll-integration.md): four-file layout, build rules and hazards.
- [Data design](../../research/data-design.md): proposed JSON schema and HUD next steps.
- [Contact data source](../../research/contact-data-source.md) and [ZIP mapping](../../research/zip-district-mapping.md): sources and coverage.
- [Multi-contact import](../../research/multi-contact-import-findings.md): why there is one card per official.

## Planning decisions (owner, 2026-11-05)

These answers were given while the plan was drafted. They shape the phases.

1. **No ZIP in the URL.** The research rule wins: the ZIP never goes in the query string, the hash or the page title, because the Jekyll page inherits the site's Google Analytics. Shareable ZIP-results links are dropped from the flows. The help link (one with no ZIP), "Start over" and copying the starting-page link remain. See the note added to the [flows document](../../design_notes/user-experience-flows.md).
2. **Launch before January on the 119th Congress, then rebuild.** The first release uses the 119th roster and 119th district geography. A full new-Congress refresh follows once the 120th Congress is seated on 2027-01-03. Mid-decade redistricting means that refresh changes boundaries as well as members.
3. **The review skill gates launch.** The "review congressional data" skill is built before launch and used for the pre-launch verification of every official. That verification includes finding policy-feedback forms; the bulk roster has them for only 2 House members.
4. **Lookup and save first.** The first public release is the minimal lookup-and-save page on eriksaltwell.com. Help and walkthroughs, sharing, bad-data reporting, the standalone file and self-hosting releases come in later phases.

## Code and assets inspected

Opened during planning:
- `research/jekyll-integration-test/build_variants.py`: the proven shape for the build script. It reads `src/` parts, inlines JSON with `</` escaped, writes the Jekyll variant B files and a standalone file. It is a throwaway fixture, so the real script is rewritten from it, not copied.
- `research/jekyll-integration-test/src/congress.js` and `src/body.html`: a prototype ZIP form, lookup and vCard blob links. Its vCard has no labels, emails or notes and handles no vacancies. It uses `btn-sm`, which the design decisions reject.
- `.env.example`: `HUD_API_TOKEN`. `.env` exists locally and is Git-ignored.
- `wwwroot/congressional_contact-html`: an empty placeholder file. Remove it or replace it during phase 4.
- Local tools: `python3`, `uv`, `node` 24 and `ruby` are present. `bundle` is not installed, so the pinned Jekyll build needs Bundler first.

Known only from the research notes, not opened during planning:
- `src/congress.css`, `check_output.py`, `browser_check.js`, `gen_sample.py` and `Gemfile.pages(.lock)` in `research/jekyll-integration-test/`: the verification approach and the pinned GitHub Pages environment (`github-pages` 233, Jekyll 3.10.0).
- `design_notes/site-design-sample.html`: the styled standalone sample (recommended options, not the chosen colours).

## Proposed repository layout

This is a proposal; phase 2 and phase 4 confirm it.

| Path | Contents | Committed |
|---|---|---|
| `tools/` | Data script, build script, copy script, shared check scripts | Yes |
| `data/congress.json` | The last good published dataset | Yes |
| `data/supplements.json` | Verified feedback forms and mailboxes, keyed by Bioguide ID, with source and verification date | Yes |
| `data/cache/` | Raw upstream downloads, including HUD responses | No (Git-ignored) |
| `src/` | Shared page parts: `body.html`, `congress.js`, `congress.css`, plus `theme.css` for the standalone file | Yes |
| `dist/jekyll/`, `dist/standalone/` | Build outputs | No; attached to releases |

## Verification approach (all phases)

The workflow forbids unit tests. Verification uses:
- assertions inside the data and build scripts: schema and reference checks, no `</` in data, no exponent-form numbers, no front matter in asset files, `cc-` prefixes;
- the pinned GitHub Pages Jekyll build (`--safe`, `JEKYLL_ENV=production`, `--baseurl ""`) on a local site clone, plus a `check_output.py`-style comparison;
- a browser check at 390×844 with Chrome DevTools: lookup, blob links, vCard text, no overflow, no console errors and no network requests beyond the theme's own;
- hands-on checks on the iPhone and the Android phone for any change to saving or navigation;
- the self-hosting checklist from the flows document, once it exists (phase 9).

The live-site push and GitHub releases are outward-facing. They happen only after the owner confirms at that step.

## Phases and dependencies

```
1 HUD data + schema ──► 2 Data script ──┬─► 3 Review skill ──► 4b Pre-launch review run ─┐
                                        └─► 4 Page core + Jekyll build ──────────────────┴─► 5 Launch v1
5 ──► 6 Help + sharing ──► 7 Reporting ──► 8 Standalone + self-hosting
2, 3 ──► 9 120th Congress refresh (starts on or after 2027-01-03; preempts 6–8 when due)
```

Phases 3 and 4 can run in parallel once phase 2 is done. Phases 1 to 5 must all finish before 2027-01-03, about eight weeks away. The pre-launch review run is the largest and least predictable piece, so start it as soon as the skill works.

---

### Phase 1: HUD data and final schema

Work item: [impl-01-hud-data-and-schema](../impl-01-hud-data-and-schema/)

**Goal:** confirm HUD access and choose a quarter whose districts are the 119th Congress's. Then settle the JSON schema against real responses. Every later phase depends on the schema.

- [x] Make one authenticated HUD type-5 request with the local token. Never log or print the token.
- [x] Find which quarters exist and which Congress's districts each quarter uses. Pick the newest quarter that is still 119th geography. Recent quarters may already use 120th districts in redistricted states; check, don't assume.
- [x] Inspect the codes: state and district format, at-large districts, DC, the territories, and delegate or resident-commissioner codes (possibly `98`). Inspect what is in each row besides the district.
- [x] Compare `10003`, `98103`, `42223` and `97635` with the official House lookup and the Census evidence. Keep every candidate.
- [x] Measure coverage: how many ZIPs, how many have several candidates, how many span several states, and the full size of the download.
- [x] Finalize the schema in `research/data-design.md`, or in a new design note that it links to. Cover:
  - provenance: HUD quarter, source revisions, Congress, fetch dates and build time;
  - how a vacancy is represented;
  - delegates and the resident commissioner, and states or territories with no senators;
  - the compact ZIP index format, if size calls for it;
  - which fields are required;
  - where the reporting address goes in page data. It stays empty until phase 7.
- [x] Record the findings and remove the "unverified" warnings that the results answer.

**Done 2026-11-05.** See the [HUD findings](../../research/hud-crosswalk-findings.md) and the [schema](../../design_notes/data-schema.md). Result: use **2026 Q2**, which is 119th geography.

**Verification:** the request and comparison results recorded with dates; the schema checked against real sample rows; a token search of the repo and logs finds nothing.

### Phase 2: Data script

Work item: [impl-02-data-script](../impl-02-data-script/)

**Goal:** one reproducible local command (for example `uv run tools/build_data.py`) that builds `data/congress.json` from the upstream sources and summarizes what changed.

- [x] Fetch, then cache under `data/cache/`:
  - the congress-legislators current roster and district offices;
  - the House Clerk and Senate XML;
  - the HUD crosswalk for the chosen quarter. Load the token from `.env` inside the script only.
- [x] Select current terms, cross-check membership by Bioguide ID against the official rosters, and join offices.
  - Membership comes from the House Clerk and Senate feeds. If the IDs don't match the community roster, the run fails instead of just warning.
  - Never treat a term-end date in the past as a departure. Appointed senators such as Husted (OH) and Moody (FL) serve until their successors are sworn in.
  - Vacancies are Clerk seat records with an empty Bioguide ID (currently FL-20 and TX-23).
  - Take each HUD row's state from the `geoid` FIPS code, never from HUD's `state` field.
  - Pin the HUD year and quarter in the script's configuration (2026 Q2); never use the API's default.
  - Follow the inclusion rules in [data-schema.md](../../design_notes/data-schema.md).
- [x] Turn delegate codes into the schema's form; at-large is `0`.
- [x] Represent vacancies explicitly. Never give a seat a previous member's details.
- [x] Merge `data/supplements.json` for feedback forms and published mailboxes. Keep each mailbox's purpose, such as casework. Never put a form URL in an email field.
- [x] Validate, and fail loudly on any of these:
  - a missing reference;
  - a state without its senators;
  - a seat with no member and no vacancy record;
  - `</` anywhere in the data;
  - a number in exponent form;
  - a malformed ZIP key.
- [x] Keep the last good data. Write to a temporary file and replace `data/congress.json` only after validation passes. A failed fetch leaves the last good file untouched.
- [x] Print a change summary against the last good data: officials, contact details and ZIP mappings, with missing data and validation failures called out.
- [x] Add `data/cache/` to `.gitignore`.
- [x] Cover American Samoa and the Northern Mariana Islands. Done instead from HUD's ZIP-to-county file; see the [schema](../../design_notes/data-schema.md). No hand-maintained ZIP file is needed.
- [x] **Owner decision (2026-11-05):** keep ZIP candidates whose district holds none of the ZIP's residential addresses (238 ZIPs).

**Done 2026-11-05.** Usage: `python3 -I tools/build_data.py` (fetch and build), `--offline` (build from the cache only), `--check FILE` (validate). Results are recorded in the [phase 2 item](../impl-02-data-script/item.md).

**Verification:**
- A full run on real data succeeds.
- Broken inputs are rejected: a bad supplement entry, an injected `</`, a simulated fetch failure. In each case the last good file is unchanged.
- The sample ZIPs from phase 1 resolve correctly.
- The output loads in Jekyll's YAML reader, using the phase 4 build.

### Phase 3: Review congressional data skill

Work item: [impl-03-review-data-skill](../impl-03-review-data-skill/)

**Goal:** an agent skill, usable from Claude and Codex, that checks each official's record online and proposes corrections with sources. The owner approves the corrections and the agent applies them.

- [x] Write the skill (`writing-for-agents` / `skill-creator` guidance). Decide where it lives so that both Claude and Codex find it; Codex's discovery path still needs confirming.
- [x] It checks each official's record against their official website: the DC office, the local offices, the policy-feedback form (not casework, newsletter or scheduling), any published mailboxes and their purpose, and the homepage.
- [x] It writes a reviewable report: each discrepancy, its source link and the proposed change. The report is batched so a full review of about 540 officials is workable.
- [x] After approval, it applies only the approved changes to `data/supplements.json`, or a corrections layer if bulk-roster values must be overridden, with the date verified. It then reruns the data script.
- [x] It supports a full run (every official, as the flows require on a full refresh) and a targeted run (one official, for reported errors).
- [x] Decide how bulk-roster errors are overridden. Supplements now cover forms and mailboxes only; phone or office corrections may need the same override layer.

**Done 2026-11-05.** See the [phase 3 item](../impl-03-review-data-skill/item.md).

**Verification:** dry runs on a handful of officials of different kinds (senator, representative, delegate), checked by hand against their websites; one approved change applied end to end and visible in rebuilt data.

### Phase 4: Page core and Jekyll build

Work item: [impl-04-page-core-and-build](../impl-04-page-core-and-build/)

**Goal:** the lookup-and-save page, built by `tools/build.py` into the four Jekyll files, using real data.

- [x] Write the shared source in `src/`, starting from the prototype. Markup uses theme and Bootstrap classes, and every id and class is prefixed `cc-`. It follows the design decisions: `btn btn-primary btn-lg` submit; a standard `btn btn-primary` for each Save; names as theme headings; `#eee` dividers; no icons; stock colours.
- [x] Lookup behaviour (flows document):
  - a brief explanation, then the ZIP field;
  - lookup only on explicit submit;
  - every candidate representative, with senators grouped by state;
  - a vacancy shown as vacant;
  - DC and territories show their delegate or resident commissioner;
  - no match: say the ZIP has no matches (not that it is invalid), with a House lookup link that opens a new tab;
  - a "results may be incomplete" note with the same link;
  - "Start over" resets to the initial state.
- [x] Generate vCard 3.0 in UTF-8 with CRLF line endings, as a blob link per official. Include:
  - a name and organization or title;
  - labeled DC and local phones;
  - structured addresses;
  - verified emails, with their purpose;
  - the website and policy-feedback URLs, labeled;
  - a `NOTE` as a readable fallback for labels;
  - a stable `UID` and `REV`.
  - each phone number once per card. Reviewed office lists can repeat a number under two offices, such as Murray's toll-free line.
  - no fax numbers. The data no longer contains any (owner decision, 2026-11-05).

  Phase 5 tests which labelling form the phones keep.
- [x] Privacy rules: the ZIP never goes in the URL or the title; the page fires no events of its own; no network requests.
- [x] Build script: Jekyll output in `dist/jekyll/`. Front matter: `layout: page`, title, `subtitle`, `share-description`, `description`, `permalink`, `css:` and `js:`. Plus `_data/congress.json`, `assets/js/congress.js` and `assets/css/congress.css`. Include the assertions listed under "Verification approach". The script is structured so that phase 8 can add the standalone output.
- [x] Handle the empty `wwwroot/` placeholder.

- [x] Office selection (added 2026-11-06): each card carries the DC office and the nearest local office, precomputed per ZIP by the data script ([vcard-office-selection.md](../../design_notes/vcard-office-selection.md)).

**Status 2026-11-06:** complete. Results and the choices made during implementation are in the [phase 4 item](../impl-04-page-core-and-build/item.md).

**Verification:**
- The pinned GitHub Pages build of a local site clone passes, with output checks.
- A browser check at 390×844 on real data covers: single-district, multi-district (`10003`), multi-state (`42223`), at-large, DC, a territory, a vacancy if one exists, and no match.
- vCard text is inspected for one official of each kind.
- No console errors and no horizontal overflow.

### Phase 4b: Pre-launch review run

Work item: [impl-04b-prelaunch-data-review](../impl-04b-prelaunch-data-review/)

**Goal:** every serving official's record is verified online, and policy-feedback forms are filled in, before launch.

- [x] Run the phase 3 skill over every official, in batches.
- [x] The owner reviews each batch report. The agent applies approved corrections.
- [ ] Rebuild the data. Record coverage after the review: forms, mailboxes, offices, and anything left unverified with the reason.

**Status 2026-11-05:** all 22 batches have been reviewed and applied (727 proposals). 528 of 539 officials are verified. 11 senators are partial because the Senate firewall blocks their sites from this machine. See the [phase 4b item](../impl-04b-prelaunch-data-review/item.md).

**Verification:** a coverage summary before and after; spot checks of some applied forms against official sites; the data script validates cleanly.

### Phase 5: Launch v1 on eriksaltwell.com

Work item: [impl-05-launch-v1](../impl-05-launch-v1/)

**Goal:** the lookup-and-save page is live on the owner's site, and saving works on both phones.

Depends on phases 4 and 4b.

- [ ] Copy script (`tools/copy_to_site.py SITE_CHECKOUT`). It places the four files in a local checkout of the site and refuses to overwrite anything unexpected.
- [ ] Document the one-time `navbar-links` edit to `_config.yml` and how the owner publishes (copy, commit, push).
- [ ] Device checks on the iPhone (Safari) and the Android phone (Chrome), before the live push. The phones reach the build either over the local network (a Jekyll or static server on the LAN; blob downloads may need HTTPS, so check this) or through a temporary preview deploy, which counts as publishing and needs the owner's confirmation. Check:
  - each official saves;
  - which phone, URL, email and note labels survive;
  - the exact taps from the save link to a saved contact, written down for the phase 6 walkthroughs;
  - what happens to a single-contact blob on Android (not tested yet).
- [ ] If labels are lost, adjust the vCard form and recheck.
- [ ] **Owner-confirmed:** commit and push to the site repo, and make the menu edit.
- [ ] Immediately before the push, fetch the roster again and rebuild. The Ohio and Florida special-election winners, and possibly FL-20 and TX-23, may be sworn in during the launch window.
- [ ] Smoke-check the public URL: lookup, a save on each phone, Start over, no ZIP in the URL.

**Verification:** device results recorded with OS and browser versions; live smoke check recorded.

### Phase 6: Help overlay, walkthroughs and sharing

Work item: [impl-06-help-and-sharing](../impl-06-help-and-sharing/)

**Goal:** the saving help described in the flows, plus a way to share the page and its help.

- [ ] A help overlay with a close button. Separate iPhone and Android walkthroughs, from tapping save to finishing in the contacts app. The normal steps come first, then brief troubleshooting for a card that arrives as a downloaded file. Use the steps recorded in phase 5.
- [ ] A short desktop note that links to Google Contacts' import instructions.
- [ ] A help link with no ZIP that opens the overlay (for example a `#help` fragment). Closing the overlay returns to the same results and scroll position.
- [ ] "Copy link" copies the starting-page link or the help link, never results. Handle a failed copy (implementation choice).
- [ ] Keyboard and screen-reader basics for the overlay: focus moves into the overlay and returns, and Escape closes it. Check that the theme's Escape handler for its search overlay does not conflict.
- [ ] Owner-confirmed publish, as in phase 5.

**Verification:** browser checks of the overlay states and focus; the walkthrough followed on both phones; live smoke check.

### Phase 7: Bad-data reporting

Work item: [impl-07-bad-data-reporting](../impl-07-bad-data-reporting/)

**Goal:** a visitor can report a missing or unexpected match, or wrong contact details, by email to the configured recipient.

- [ ] Store the reporting address in page data. Reporting stays inactive (hidden) when the address is empty or the placeholder.
- [ ] Add report actions for: no match, an unexpected or missing representative, and wrong details for a particular official.
- [ ] Each action opens a `mailto:` draft with the ZIP and the official's name in the body, asking the visitor to describe the error. The ZIP goes only in the email, never in the page URL.
- [ ] The owner provides their address for the Jekyll build. The standalone build uses a fake placeholder.
- [ ] Owner-confirmed publish.

**Verification:** the drafts open in a phone mail app and a desktop mail app with correct prefills; reporting is hidden in a placeholder build.

### Phase 8: Standalone file and self-hosting releases

Work item: [impl-08-standalone-and-self-hosting](../impl-08-standalone-and-self-hosting/)

**Goal:** self-hosters can download one HTML file, configure reporting, upload it and check it. They can also find updates.

- [ ] Theme layer in `src/theme.css`:
  - `:root` variables using the theme's names and **stock Beautiful Jekyll values**, not eriksaltwell.com's, plus `--heading-col: #404040` and the darkened teal `#006B80` for buttons and links (owner, 2026-11-06);
  - no owner branding: an empty header bar, and a footer bar with only a "Host your own copy" link (see "Standalone file styling" in [existing-site-design.md](../../design_notes/existing-site-design.md));
  - the reduced Bootstrap 4.4.1 and Beautiful Jekyll rules (`purgecss`, as reproduced in the design notes);
  - the Google Fonts link for Lora 400 and Open Sans 300, 400 and 800.
  - the page header markup (title and subtitle) below the empty header bar.
- [ ] The standalone output from `tools/build.py`, with data inlined and `</` escaped, and the placeholder reporting address.
- [ ] A "Host your own" link from the page to the repository docs.
- [ ] README self-hosting docs. Cover:
  - downloads;
  - configuring the reporting address;
  - uploading;
  - the verification checklist (from the flows, without shared ZIP links);
  - which files and sections handle styling;
  - what an update replaces and how to keep custom CSS;
  - GitHub release notifications;
  - notes for other Jekyll themes.
- [ ] A release process: build both outputs and attach them to a GitHub release. **Owner-confirmed.** The live page is checked before the release is announced.

**Verification:**
- The standalone file is served by a plain static server and checked in a phone-sized browser.
- It is checked once with Google Fonts blocked, falling back to the theme's font stacks.
- The self-host checklist is run against it.
- One phone save from the standalone file.

### Phase 9: 120th Congress refresh

Work item: [impl-09-120th-congress-refresh](../impl-09-120th-congress-refresh/)

**Goal:** switch to the 120th Congress's members and districts once they are seated. The target is shortly after 2027-01-03.

Depends on phases 2, 3 and 5. When this phase is due, it preempts phases 6 to 8.

- [ ] Before January: check whether HUD has a quarter with 120th geography, and how the roster sources mark new terms. To detect 120th geography, count the ZIPs that change between quarters, by state. A real switch moves hundreds of ZIPs in the redrawn states, such as TX, CA, MO, NC, OH and UT (see the [HUD findings](../../research/hud-crosswalk-findings.md)). If HUD has no 120th quarter by early January, Census's 120th relationship files are a possible fallback (the geocoder already returns 120th districts). That choice is the owner's. If no 120th quarter exists by early January, decide with the owner what to do. The roster and the geography must describe the same Congress.
- [ ] After swearing-in: rerun the data script for the 120th. Review the change summary, in which almost every House record may change.
- [ ] Run the review skill over every official, then the owner approves corrections. New members' websites and forms may still be thin in early January; record what is not yet verifiable.
- [ ] Rebuild, run the browser checks on the sample ZIPs, then publish (owner-confirmed). Include a GitHub release if phase 8 has shipped.

**Verification:** the change summary is reviewed; sample ZIPs in redistricted states are checked against the House lookup; live smoke check.

## Material unknowns and risks

- **HUD quarter and Congress alignment:** settled for the 119th Congress (2026 Q2). The open risk is HUD falling behind the 120th Congress (phase 9).
- **Schedule:** phases 1 to 5 must finish in about eight weeks, and phase 4b (owner review of about 540 officials) is the bottleneck.
- **vCard labels:** how phone contacts apps keep custom phone and URL labels, multiple URLs and notes is unknown until phase 5.
- **Data size:** the real dataset may be larger than the 0.3 MB gzipped synthetic estimate. Phase 1 decides whether a compact ZIP index is worth it.
- **Stale project context:** `.agent_context.md` (user-maintained) still lists questions that the flows and these decisions have since settled.
