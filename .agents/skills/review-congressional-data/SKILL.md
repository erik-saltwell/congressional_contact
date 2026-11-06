---
name: review-congressional-data
description: Verify Congressional Contact's officials against their official websites and apply owner-approved corrections. Use for a full review after a data refresh, a review of some states or officials, or a reported error in an official's phone, office, feedback form or mailbox.
---

# Review congressional data

Check each official's published record in `data/congress.json` against the official's own website. Propose corrections with sources, and apply only the corrections the owner approves. The owner decides; you investigate and propose.

The tooling is `tools/review.py`. The schema, including what the published data may contain, is in `design_notes/data-schema.md`.

## Steps

1. **Scope the batch.** Choose the scope from the request:
   - after a refresh, a full review: `python3 -I tools/review.py prepare --all` (batches of 25);
   - some states: `--states WA,OR`;
   - a reported error or particular people: `--ids J000298`.

   Each batch directory under `data/reviews/` gets a `packets.json` (what we publish now, plus upstream candidates) and a `proposals.json` skeleton. Done when the batch directories exist. For a full run, work one batch at a time through steps 2 to 4.
2. **Check every official in the batch** against the checklist below. Fill in that official's entry in `proposals.json`: `status`, `pagesChecked`, `notes` and `proposals`. Set `reviewedAt` to today's date. Done when no entry is still `pending`. Every entry is `verified` (every checklist item was checked, and the proposals fix everything that was wrong), `partial` (some items could not be checked; the notes say which, the proposals still apply, but no verified date is set) or `unverifiable` (nothing could be checked; notes say why, no proposals).
3. **Report:** `python3 -I tools/review.py report data/reviews/<batch>`. It validates the proposals and writes a numbered `report.md`. Give the owner the report's path and a short summary: counts, plus anything surprising. Done when the report is written and the owner has the summary.
4. **Apply exactly what the owner approves:** `python3 -I tools/review.py apply data/reviews/<batch> --approve all` or `--approve 1,4,7`. Wait for the owner's explicit numbers or "all"; silence or "looks good" for one item is not approval for the batch. The command writes `data/supplements.json`, rebuilds the data offline and prints the change summary. Done when the change summary shows each approved change. Relay any notes the rebuild prints.

When the owner rejects a proposal, the official stays unverified. Re-check that official in a new batch if the owner gives a reason.

## Checklist for each official

Start from the official's website (the `website` link in the packet), and the upstream `contactForm` candidate if there is one. Visit their contact, offices or locations page.

- **Website:** the homepage loads and belongs to this official. If it has moved, propose `set-link website`.
- **Policy-feedback form:** find the page where a constituent can send their opinion on legislation or policy. A general "contact" or "email" form with a topic list counts. A casework or agency-help form, newsletter signup, scheduling request, tour request or press inquiry does not. Read the page before proposing it; the upstream candidate is only a lead. Propose `set-link policy-feedback`. If the member's main Email or Contact form sits behind a ZIP or address check (`zip_authentication` or `address_authentication`), propose the form's own path (the `form=` target), and state the check in the evidence. The owner accepts these as feedback forms (2026-11-05). Forms drawn by script or in an iframe count when the page shows an issue list. `python3 -I tools/review_scan.py <batch>` finds forms, numbers and addresses to look at first, and `--show ID REGEX` prints the text around a match. If no such form exists, say so in the notes.
- **Mailboxes:** propose `add-email` only for an address printed on an official page, with its stated purpose (`general`, `casework` and so on). A form is never a mailbox.
- **Offices:** compare the DC office and every local office on the official's offices page with the packet. That means every phone number, every street address, and every office opened or closed. Fax numbers are not part of the data, so leave them out. If anything differs, propose `replace-offices` with the complete corrected list: the DC office first, then local offices, in the published shape. The list replaces the bulk roster's offices until the next review. Once you replace a list, copy every voice number the page shows, toll-free lines included.
- **Existing supplement:** if `currentSupplement` holds values, re-check them, and propose `remove-link` or `remove-email` for any that are gone.

Record every page you used in `pagesChecked`. A record whose checks all agree is `verified` with no proposals; that sets its `verifiedAt`.

## Proposal format

Each proposal has an `action`, a `source` (an https URL on the official's own site, or house.gov or senate.gov) and `evidence` (what that page shows, in a sentence, quoting the relevant text).

| action | extra fields |
|---|---|
| `set-link` | `purpose` (`website` or `policy-feedback`), `url` (https) |
| `remove-link` | `purpose`: `policy-feedback` |
| `add-email` | `address`, `purpose` |
| `remove-email` | `address` |
| `replace-offices` | `offices`: the full list. Each office is `{label, kind: dc or local, phones: [{number: +1XXXXXXXXXX, type: voice}], address: {lines, city, region, postalCode, country} or null}`. Labels follow the published style, such as `Washington, DC` and `Seattle, WA office` |

## Fetching pages

Go gently. The House and Senate sites sit behind one firewall (Akamai), and on 2026-11-05 seven reviewers running at once got this machine blocked from every house.gov page for over an hour. Run at most three reviewers at a time, and leave `review_scan.py` at its default of 2 workers. If https://www.house.gov/ returns 403, stop and wait 10 minutes before probing again.


Fetch with whatever web tool you have, or `curl -sL` with a browser user agent. When a page is blocked or drawn by JavaScript, use a browser tool if one is available. When nothing works, mark the record `unverifiable` and say what failed.

Look only: reading pages is the whole job. Leave every form unsubmitted, send no email, and dial nothing.

`data/supplements.json` changes only through `tools/review.py apply`. That keeps every value tied to its source, its date and the owner's approval.
