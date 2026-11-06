---
name: "Phase 1: HUD data and final schema"
status: complete
---

# Phase 1: HUD data and final schema

Make the first authenticated HUD type-5 request and pick a quarter whose districts are the 119th Congress's. Inspect the real codes and coverage, then settle the final JSON schema: provenance, vacancies, delegates and the ZIP index.

Plan section: [the implementation plan, phase 1](../implementation-plan/plan.md).

## Completion (2026-11-05)

- **Findings:** [research/hud-crosswalk-findings.md](../../research/hud-crosswalk-findings.md), with counts in [hud-crosswalk-evidence.json](../../research/hud-crosswalk-evidence.json) and probe scripts in [research/hud-crosswalk-test/](../../research/hud-crosswalk-test/).
- **Final schema:** [design_notes/data-schema.md](../../design_notes/data-schema.md). It supersedes the proposal in `research/data-design.md`.
- **Result:**
  - Use HUD **2026 Q2**, pinned explicitly. It is 119th Congress geography.
  - Take the state from the district `geoid`, not HUD's `state` field.
  - Drop the `**` rows and Wake Island.
  - American Samoa and the Northern Mariana Islands need hand-maintained ZIPs.
  - Publish no ratios and no floating-point numbers.
  - Vacancies (FL-20 and TX-23) are `null` seats. Delegates are seat `-0`.
  - Appointed senators serve past their recorded term-end date.

**Verification:**
- The token works. National files for six quarters were downloaded and compared state by state.
- Sample ZIPs were checked against the official House lookup: 10003 and 97635 match; for 42223, HUD misses TN-7.
- The three rosters agree on 439 House members and 100 senators.
- The schema example was checked against the roster.
- A search of the repository and scratch files found the token nowhere outside `.env`.

**Limitations:**
- The quarter's Congress is inferred from change patterns, because HUD doesn't publish it.
- House lookup pages with a single result were not parsed.
- The American Samoa and Northern Mariana Islands ZIPs are not yet sourced (phase 2).

**Handed to phase 2:** the owner's decision on candidates with no residential addresses.
