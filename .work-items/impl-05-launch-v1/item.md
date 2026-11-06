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

## Resume note

Next:
- the owner pushes the site;
- phone checks on the iPhone and the Android phone against the live unlinked URL: each card saves, which labels survive, the exact taps, and a single-card blob on Android;
- then a roster refresh, the `navbar-links` edit and the linked launch, which the owner confirms.
