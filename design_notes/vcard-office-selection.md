# Office selection for vCards

Each official's vCard carries at most two offices: the Washington DC office and the local office nearest the user's ZIP. This note sets out how that office is chosen, where the choice is computed and what data it needs. The owner approved it on 2026-11-06.

The published data ([data-schema.md](data-schema.md)) lists every office an official has, from 1 to 10, with the DC office included. The rule here only trims what goes onto the card; it removes nothing from the data.

## Decisions

- **The card has one DC office and at most one local office.** All other offices are left off.
- **The card says nothing about what was left off** (owner, 2026-11-06). It has no "N more offices" note; the official's website link is already on the card.
- **The choice is computed at build time.** The page looks up the result and does no geography of its own.

## The rule for each official

1. **DC office:** the official's one office of kind `dc`. In the 2026-11-06 data, all 539 officials have exactly one DC office and every one has a phone. The build checks this and fails if it stops being true.
2. **Which local offices can be picked:** local offices with at least one phone. If an official has none, local offices with an address. If there are none of those either, the card has no local office.
3. **Choosing among them:** the office with the shortest straight-line distance from the user's ZIP. A tie goes to the office listed first.
4. **When either location is unknown:** if the user's ZIP has no location, pick the first eligible office in the list. In the roster that is usually the main district office. An office with no location counts as the farthest.

Each official is worked out separately for the same ZIP. A ZIP that spans two states therefore gives each state's senators their own nearest office.

In the 2026-11-06 data, 2 officials have no local office with a phone and 199 have exactly one, so for them there is nothing to choose. The other 338 have two or more. Across all officials, 40 local offices have no phone and 22 offices have no address.

## Locations

Straight-line distance needs a point for each office and for each ZIP. These come from free sources that need no key, and each one falls back to the next.

**Offices**

1. The latitude and longitude in the congress-legislators district-offices file, matched to our office. That file is already one of the data script's inputs.
2. The centre of the office's five-digit ZIP, from the Census ZCTA Gazetteer (public domain). Office lists that the review replaced (in `data/supplements.json`) have no coordinates, so they start at this step.
3. The centre of the office's county, found through the HUD ZIP-to-county file (type 2), which the data script already fetches.

**The user's ZIP**

1. Its Census ZCTA Gazetteer centre.
2. For a ZIP with no ZCTA, such as a PO-box-only ZIP, the centre of its main county from HUD type 2.
3. Otherwise there is no location, and rule 4 applies.

Coordinates are used only inside the build. HUD ratios and coordinates are floating-point numbers, which the published data may not contain, so they never appear in it.

## Build-time computation

The data script (`tools/build_data.py`, `choose_offices`) works out the chosen local office for each ZIP and each candidate official there. It publishes the result as `zipOffices` (see [data-schema.md](data-schema.md)):

- **One string per ZIP, in the sorted order of `zipMatches`' keys.** The ZIP keys are not repeated, which keeps the table small.
- **One character per candidate official:** the digit is the chosen office's position in that official's `offices` list, and `-` means a vacant seat or an official with no eligible local office.
- **Every candidate has a character,** including officials with only one eligible office, so the page has no fallback logic of its own.
- **The candidate order is fixed:** the House member of each seat in the ZIP's `zipMatches` list, in order; then, for each distinct state in order of first appearance, its senator slots in order. `zip_candidates()` in the data script and `candidates()` in `src/congress.js` implement the same rule.

Reasons for computing it at build time rather than in the page:

- The page stays simple and does no maths on the phone.
- Only integers are published, so the no-floats rule holds.
- Nearby ZIPs mostly get the same office, so the table should compress well.
- The build can check the result. `validate()` checks that every character points to an eligible office. The change summary counts where locations came from, how many ZIPs fell back to rule 4, and how many ZIPs' choices changed since the last build. It also names offices with no location.

**Rejected alternative:** publish whole-number coordinates for every ZIP and office and let the page compute distance. It makes the page more flexible but adds an estimated 100 KB gzipped to the data and puts more logic on the phone.

**Measured (2026-11-06, phase 4):** the table adds 22 KB gzipped (the data went from 195 KB to 217 KB gzipped). Keying it by ZIP, as first tried, cost 103 KB, the same as the rejected coordinates option, because the ZIP keys dominate. The field is additive, so `schemaVersion` stays 1.

**Results on the 2026-11-06 data:**
- Office locations: 1,146 from the roster, 133 from ZIP centres, 2 from county centres, and 21 unknown. The unknown ones are offices published with a phone but no street address.
- ZIP locations: 33,705 ZIP centres, 5,643 county centres, and 7 unknown.
- 4 ZIPs fall back to the first listed office for at least one official.
- An independent haversine check agreed on every sampled pair:
  - 6,119 ZIP and official pairs for roster office lists, using the roster's coordinates;
  - 9,406 pairs for the 128 reviewed office lists with two or more phone offices, using address-matched roster coordinates, then ZIP centres, then county centres. A browser check confirmed that the page decodes the table correctly for 187 cards in 60 random ZIPs.

## Known limits

- Straight-line distance ignores water, mountains and roads. It can pick a poorly placed office in Alaska, Hawaii, around the Chesapeake Bay or Puget Sound, and in other places where travel is not direct.
- ZIP and county centres are coarse for large rural ZIPs and counties.
- Because of the fallback order and rule 4, a card always has a local office whenever the official has an eligible one.
