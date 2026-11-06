---
name: "Phase 3: Review congressional data skill"
status: complete
---

# Phase 3: Review congressional data skill

Build the agent skill that checks each official's record online, proposes corrections with sources, and applies only the corrections the owner approves. It supports full and targeted runs.

Plan section: [the implementation plan, phase 3](../implementation-plan/plan.md).

## Completion (2026-11-05)

**What was built:**
- **The skill:** [.agents/skills/review-congressional-data/SKILL.md](../../.agents/skills/review-congressional-data/SKILL.md).
  - Codex reads repo skills from `.agents/skills/`. `.claude/skills/review-congressional-data` is a relative symlink to the same folder, matching how the owner's user-level skills are shared.
  - It runs in four steps: prepare a batch, check each official against the checklist, report, then apply only what the owner approves.
- **`tools/review.py`**, which the skill runs:
  - `prepare` makes one batch for given officials (`--ids`), states (`--states`), or batches of 25 for a full run (`--all`);
  - `report` validates the proposals and writes a numbered `report.md`;
  - `apply --approve all|1,2` writes `data/supplements.json` with each value's source and date, then rebuilds. If the rebuild fails, it restores the supplements. It refuses to apply the same batch twice.
- **Batches live in `data/reviews/<date>-<name>/`:** `packets.json`, `proposals.json`, `report.md` and `decisions.json`. They are meant to be committed as the audit trail.

**Decision: how bulk-roster errors are corrected.** A supplement entry can carry a reviewed `offices` list. It replaces the bulk roster's offices for that official, and it records a hash of the upstream offices at approval time. When the upstream data changes later, `build_data.py` prints a note to review that official again.

**Owner decisions (2026-11-05):**
- **No fax numbers anywhere in the contact data.** The data script drops them, validation rejects them, and the skill and the schema note say so. This removed faxes from 235 officials.
- The dry-run batch was approved in full.

**Verification:**
- A dry run checked 4 officials against their websites by hand: Murray (senator, WA), Jayapal (representative, WA-7), Norton (delegate, DC) and Radewagen (delegate, American Samoa). It found:
  - feedback forms for all four;
  - Murray's Olympia office wrongly given upstream as "771 Capitol Way Sound" (her site says 711 Capitol Way South);
  - Murray's toll-free number, missing from the data.
- All 5 approved changes were applied end to end and show in the rebuilt data and the change summary.
- `report` rejects a pending entry, a non-https source and a form URL given as an email. `apply` refuses to run without an approval list, or a second time.
- Changing upstream offices under a reviewed list triggers the "review again" note; restoring the cache clears it.
- Claude listed the skill in this session. One `codex exec` prompt confirmed that Codex sees `review-congressional-data` as a repo skill.

**Findings for later phases:**
- **Senate firewall:** it blocks some homepages (Murray's returned 403) while her contact pages load. Python's HTTP client was blocked where `curl` worked. The skill tells agents to fall back to `curl` or a browser, or to mark the record `unverifiable`.
- **Forms behind an address check:** Norton's form asks for an address before showing anything, so its contents can't be read. Such forms are proposed with that limitation stated in the evidence.

**Not tested:** the restore after a failed rebuild in `apply`. The code path exists but was not exercised.
