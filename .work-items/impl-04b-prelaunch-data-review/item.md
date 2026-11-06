---
name: "Phase 4b: Pre-launch review run"
status: implementing
---

# Phase 4b: Pre-launch review run

Run the review skill over every serving official before launch, with the owner approving corrections in batches, so that policy-feedback forms and contact details are verified.

Plan section: [the implementation plan, phase 4b](../implementation-plan/plan.md). Running record of every change: [data/reviews/SUMMARY.md](../../data/reviews/SUMMARY.md) (`python3 -I tools/review.py summary` regenerates it).

## Progress (2026-11-05)

**Done:**
- All 22 batches (539 officials) were reviewed.
  - Batches 1 to 3 were reviewed directly and approved one at a time.
  - Batches 4 to 22 were reviewed by subagents, at the owner's request, and approved together after reading `SUMMARY.md`.
- **727 proposals were applied, and none were rejected:** 537 feedback forms, 174 office corrections and 15 mailboxes, plus 1 website link change.

**Coverage, before and after:**

| | Before | After |
|---|---|---|
| Verified policy-feedback links | 0 of 539 | 537 |
| Officials with a verified date | 0 | 528 |
| Published mailboxes | 0 | 15, on 9 officials (Cruz has 7 regional ones) |
| Fax numbers | many | none (owner decision) |

The office corrections cover moved, closed and new offices, wrong phone numbers, and toll-free lines.

**Owner decisions during the run:**
- No faxes.
- A member's main contact form behind a ZIP or address check counts as the feedback form.
- When a site prints no street address, the address is removed and the phone kept.
- Forms drawn by script count when the page states their purpose.
- Districts with none of a ZIP's residential addresses are kept (this was decided in phase 2).

**Corrected before approval:** a subagent had inferred a ZIP (07071) for Pou's Lyndhurst office, which her site doesn't print. It was blanked.

**Tooling added during the run:**
- `tools/review_scan.py`: a site scanner. It defaults to 2 workers and has a `--show` option for context.
- A `partial` status in `tools/review.py`.
- `tools/review.py summary`.

## Blocker: 11 senators are only partly verified

Their sites are blocked by the Senate firewall from this machine, in both curl and a real browser. A re-probe at the end of the run still returned 403 for all of them.

- **Form topic lists unread:** Blumenthal, Murphy, Ernst and Crapo. Their forms are published, on the strength of each page's stated purpose.
- **Local offices unchecked:** Hickenlooper, Durbin, Tina Smith, Daines and Welch. Durbin's form page also rendered empty.
- **No feedback form found:**
  - Cramer: his contact-kevin page draws no form.
  - Darline Graham: every subpage of her site returns 404, so only her DC office is known.

**Resume:**
1. From a different network, or after the firewall relaxes, run `python3 -I tools/review.py prepare --ids B001277,M001169,E000295,C000880,H000273,D000563,S001203,D000618,C001096,G000608,W000800 --name senate-recheck`.
2. Review that batch and get the owner's approval.
3. Mark this item complete.

Since phase 4 (2026-11-06), `review.py apply` rebuilds with `--offline`, and that needs the two Census Gazetteer files in the cache. On a fresh checkout, run `python3 -I tools/build_data.py --fetch census-zcta,census-counties` once first.

Phase 4 is complete. Phase 5 rebuilds the data just before launch anyway.

**Verification so far:**
- Every batch's `report` validated before it was applied.
- `build_data.py --check data/congress.json` passes after all applies.
- A random sample of 12 applied forms was fetched from the live sites. All returned 200 and showed either the form or its ZIP or address check, with correctly titled pages.
