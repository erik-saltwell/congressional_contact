---
name: "Phase 2: Data script"
status: complete
---

# Phase 2: Data script

Build the local data script. It fetches the roster, offices, official rosters and the HUD crosswalk, joins them with the supplements, validates the result, keeps the last good data, and prints a change summary.

Plan section: [the implementation plan, phase 2](../implementation-plan/plan.md). Schema: [design_notes/data-schema.md](../../design_notes/data-schema.md).

## Owner decision (2026-11-05)

Keep ZIP candidates whose district holds none of the ZIP's residential addresses. This affects 238 ZIPs. Only `**` rows and seats with no representative are dropped.

## Completion (2026-11-05)

**What was built:**
- `tools/build_data.py`, which uses only the Python standard library:
  - `python3 -I tools/build_data.py` fetches every source and then builds;
  - `--offline` rebuilds from `data/cache/` only;
  - `--check FILE` validates an existing data file.
- `tools/data_config.json`: Congress 119, 441 House seats, HUD 2026 Q2.
- `data/supplements.json`: empty for now. The review skill fills it.
- `data/congress.json`: the first real dataset.
- `data/cache/` holds the raw downloads and is Git-ignored.

**How the script works:**
- Membership comes from the House Clerk and Senate feeds. A mismatch with the community roster stops the build.
- Vacancies come from Clerk seats with no member ID. The Clerk's `AQ` code is translated to American Samoa (`AS`).
- Term-end dates are never treated as departures.
- Guards on the district vintage:
  - the config declares which Congress the HUD quarter's districts belong to, and the build fails if that doesn't match the roster's Congress;
  - the build fails if HUD returns a different year or quarter than requested;
  - `validate()` checks the seat counts.
- The change summary breaks changed ZIPs down by state, to help spot redistricting in phase 9.
- The state comes from the HUD district code, never from HUD's `state` field.
- Every source is downloaded before the cache changes. The output goes to a temporary file and replaces `data/congress.json` only after it validates, both before and after it is written out as text.

**First build:**
- 539 officials: 100 senators, 433 representatives, 5 delegates and 1 resident commissioner.
- 441 seats, with FL-20 and TX-23 vacant.
- 39,355 ZIPs, 6,061 of them with several seats.
- 192 KB gzipped.

**Deviation from the plan:** American Samoa, the Northern Mariana Islands and 5 other single-seat ZIPs come from HUD's ZIP-to-county file instead of a hand-maintained `manual-zips.json`. This is the same pinned quarter and needs no hand upkeep. The schema doc is updated to match.

**Verification:**
- The full fetch and build succeeded. `--check` passes.
- Sample ZIPs match phase 1: 10003, 42223, 97635, 98103, 01731 (keeping MA-6), DC, PR, AS and MP.
- The appointed senators are still present.
- Failure cases were all rejected, each leaving `data/congress.json` byte-for-byte unchanged:
  - a form URL used as an email;
  - a link without a source or date;
  - an unknown link purpose;
  - an injected `</`;
  - broken supplements JSON;
  - a fetch failure, simulated with an unreachable proxy, which also left the cache unchanged.
- A valid supplement entry was applied end to end, shown in the change summary and then removed. An entry for an official who is not serving was ignored, with a note.
- Each new guard was tested and fails as intended: a mismatched HUD vintage, a mismatched quarter, and a missing seat in `--check`.
- The test mailbox is gone from the data, and the token appears nowhere in `tools/`, `data/` (including the cache), `research/` or the scratch files.
- Ruby's `YAML.safe_load` reads the file identically to `JSON.parse`. This approximates Jekyll's reader; the real Jekyll build check is in phase 4.

**Known gaps for later phases:**
- None of the 539 officials has a verified policy-feedback link or mailbox. Upstream has unverified forms for 88 of them. Phase 3 and phase 4b fill these.
- 4 officials have no local-office record upstream: Blair, Gallagher, Graham and Wahab.
