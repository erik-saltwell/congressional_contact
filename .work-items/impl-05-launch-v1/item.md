---
name: "Phase 5: Launch v1 on eriksaltwell.com"
status: implementing
---

# Phase 5: Launch v1 on eriksaltwell.com

Write the copy script, check saving on the iPhone and the Android phone (recording the exact taps and which labels survive), then publish the lookup-and-save page to eriksaltwell.com after the owner confirms. Target: before 2027-01-03.

Steps, dependencies and verification are in [the implementation plan, phase 5](../implementation-plan/plan.md). The plan's "Planning decisions" section records the owner decisions this phase must follow.

**Depends on:** phases 4 and 4b.

## Progress (2026-11-06)

- **Copy script written:** `tools/copy_to_site.py SITE_CHECKOUT`. It refuses to run unless the target is a Jekyll site (`_config.yml`). It refuses to replace a file that isn't ours, or to reuse a `/congress/` permalink another page already has. It never edits `_config.yml`, and it never commits.
- **Copied** into `../eriksaltwell.com`, at site commit `17536d1`. Only the four files were added, and nothing was committed in the site repository.
- **Unlinked publish:** the owner publishes the page with no menu entry, as a soft launch and for the phone tests.
- **Data:** the 2026-11-06 build, not refreshed, by owner choice. Refresh it before the linked launch.
- **Checks:**
  - A copy of the checkout with the page builds with the pinned GitHub Pages Jekyll.
  - `check_site.py` passes all 15 checks.
  - The browser check passes at 390 px: 10 sample ZIP codes, no console messages, no sideways scrolling, and the URL and title unchanged.
- **Not linked, but discoverable:** no page links to `/congress/`. The theme does list the page in `sitemap.xml` and in the site search index (`assets/data/searchcorpus.json`). To hide it from the sitemap, add `sitemap: false` to its front matter. Hiding it from search would need a change to the theme's search template.

## Label test (2026-11-06)

The first Android save (Google Contacts) of the live card kept every number, address and link, but showed every label as "Work" or "Website". The card wrote labels only as Apple's `itemN.X-ABLabel`.

`research/vcard-label-test/make.py` builds a test page of Murray cards that write the labels in different ways. The owner imported them on desktop Google Contacts and on the Android phone. A copy is in the site checkout at `/congress-label-test/`.

| Card | Labels written as | Desktop Google Contacts | Android phone | iPhone |
|---|---|---|---|---|
| A | `itemN.X-ABLabel`, `TYPE=WORK` | labels kept | "Work" | not tried |
| B | `TYPE=X-label` only | "Other" | not tried | not tried |
| C | `itemN.X-ABLabel` plus `TYPE=X-label` | labels kept | labels kept ("DC office", "Seattle office") | labels kept: the phones show "DC office" and "Seattle office" in the New Contact sheet |
| D | `TYPE=label` | "Other" | not tried | not tried |
| E | vCard 2.1 `TEL;X-label` | no phones or addresses | not tried | not tried |

**Changes to the real cards:**
- They now use form C.
- The note is only the card title (owner, 2026-11-06).

**Still open:**
- The link and email labels haven't been checked on either phone; the screenshots stop at the addresses or phones.
- The phones have only been tried with test card C, not with a card from `/congress/` itself.
- The owner deletes `/congress-label-test/` from the site after testing.

## Resume note

Next:
- the owner pushes the site;
- phone checks on the iPhone and the Android phone against the live unlinked URL: each card saves, which labels survive, the exact taps, and a single-card blob on Android;
- then a roster refresh, the `navbar-links` edit and the linked launch, which the owner confirms.
