---
name: "Phase 4: Page core and Jekyll build"
status: complete
---

# Phase 4: Page core and Jekyll build

Build the lookup-and-save page from the shared source, and a build script that writes the four Jekyll files. The page covers multi-district and multi-state ZIPs, DC and territories, vacancies, no-match recovery and Start over, and keeps the ZIP out of the URL.

Steps, dependencies and verification are in [the implementation plan, phase 4](../implementation-plan/plan.md). The plan's "Planning decisions" section records the owner decisions this phase must follow.

**Depends on:** phase 2 (real data). It can run alongside phase 3.

**Also follow:**
- [vcard-office-selection.md](../../design_notes/vcard-office-selection.md) (approved 2026-11-06): each card carries the DC office and the nearest local office. The data script precomputes the choice for each ZIP.
- The site's 2026-11-05 recolour, in the update section of [existing-site-design.md](../../design_notes/existing-site-design.md).

## Completion (2026-11-06)

**What was built:**
- **`src/body.html`, `src/congress.js`, `src/congress.css`:** the shared page source.
- **`tools/build.py`:** asserts the build rules, then writes the four Jekyll files to `dist/jekyll/`, which is Git-ignored. The page's permalink is `/congress/`.
- **`tools/check_site.py BUILT_SITE`:** output checks on a Jekyll build.
- **`tools/browser_check.js`:** run it with Chrome DevTools `evaluate_script` at 390×844.
- **`tools/build_data.py`:**
  - now publishes `zipOffices`, the nearest-office table;
  - fetches two pinned Census Gazetteer files;
  - has a new `--fetch ID,ID` option that fetches only those sources and leaves the roster and HUD cache as they are.
- **`wwwroot/`:** the empty placeholder was deleted.

**Choices made during implementation.** These are not owner decisions, and each is easy to change.
- **Page title:** "Your Congress" (owner, 2026-11-06). The title shrinks on phones. "Congressional Contact" had broken mid-word in the theme's 50 px title.
- **Party is not shown.** The page shows each official's name, role and district.
- **Results are grouped by state,** with senators first and then the House candidates. A small state label appears only when a ZIP spans two or more states (owner, 2026-11-06).
- **Notes:**
  - A ZIP in several districts gets a note pointing to the house.gov lookup.
  - A ZIP in several states gets a note saying the right senators are the ones for the state you live in.
  - DC and the territories say "<place> has no U.S. senators".
  - A vacant seat is an entry with no save button.
- **Design review (owner, 2026-11-06):** the colours now follow the recoloured site, there is one button style, the copy is shorter, and the invalid-ZIP state uses `is-invalid`. Details are in the new section of [existing-site-design.md](../../design_notes/existing-site-design.md). Start over is a text link. A second review the same day:
  - removed the intro and "to your phone";
  - combined the notes;
  - fixed the scroll position under the navbar;
  - strengthened the state boundaries;
  - added "Representatives (choose yours)";
  - made the error text brown;
  - marked opened cards.

  A third round restructured the results into state, then Senators and Representatives cards, then people, with burgundy messages. It removed Start over and the summary line. See "Hierarchy and messages" in [existing-site-design.md](../../design_notes/existing-site-design.md).
- **vCard labels:** phones, addresses and URLs use `itemN.` groups with `X-ABLabel`:
  - phones and addresses: "DC office", "<City> office" or "District office" (the label for a delegate's local office in Washington);
  - URLs: "Website" and "Share your views".

  Labels have no commas, and folding never splits an escape. Phase 5 tests which labels phones keep.

**Verification:**
- **Pinned GitHub Pages build:** `github-pages` 233 and Jekyll 3.10.0, on a scratch clone of the site at its current HEAD, so it includes the 2026-11-05 recolour. It passes, and `check_site.py` passes all 15 checks, including the data round trip through Jekyll's YAML reader.
- **Browser at 390×844:** checked with these ZIPs:

  | ZIP | Case |
  |---|---|
  | 98101 | single district |
  | 10003 | split district |
  | 42223 | two states |
  | 82001 | at large |
  | 20001 | DC |
  | 00901 | Puerto Rico |
  | 96799 | American Samoa |
  | 33068 | vacant FL-20 |
  | 99999 | no match |
  | 12 | invalid entry |

  - There was no horizontal overflow and no console messages.
  - The URL and title never changed, and Start over resets the page.
  - The only network requests were the theme's own.
  - Fonts and colours are the theme's: Lora body text on `#F8F7F5`, and names in Open Sans 800. The submit button is 48 px tall and Save buttons are 38 px.
- **vCards** were read for a senator, a representative, an at-large member, a delegate and the resident commissioner. All are CRLF only, with lines of at most 75 octets, and each phone number appears once.
- **Office choice:**
  - an independent haversine calculation agreed on every sampled pair: 6,119 for roster office lists and 9,406 for the 128 reviewed office lists with two or more phone offices;
  - the page's cards matched the table for 187 cards in 60 random ZIPs.
- **Build guards:** source deliberately broken six ways (URL change, title change, non-`cc-` class, non-`cc-` id, Liquid in the markup, a theme variable) was rejected each time.

**Limits and follow-ups:**
- **Not tested on real phones yet.** That is phase 5.
- **Office numbers are limited to one digit.** Kennedy and Rick Scott already have 10 offices, so their highest local office number is 9. If a review or refresh gives anyone an 11th office, `build_data.py` stops with an error. That also blocks `review.py apply`. The fix would be a wider encoding in `zipOffices`.
- **`--offline` needs the two Census files in the Git-ignored cache.** On a fresh checkout, run `python3 -I tools/build_data.py --fetch census-zcta,census-counties` once.
- **[user-experience-flows.md](../../design_notes/user-experience-flows.md) still says each card has "the available full contact details".** The approved office selection supersedes that for offices. The flows document was left unchanged.
- **21 local offices have a phone but no street address,** so they count as farthest. An example is Blunt Rochester's Wilmington and Georgetown offices. A city-name lookup could place them; it is not part of the approved design.
- **To repeat the site build:** clone the site into a scratch directory, copy `dist/jekyll/` and `research/jekyll-integration-test/Gemfile.pages*` into it, and follow "Reproduce" in [research/jekyll-integration.md](../../research/jekyll-integration.md), building with `--safe --baseurl ""`.
