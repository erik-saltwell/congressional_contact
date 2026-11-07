---
name: "Phase 6: Help overlay, walkthroughs and sharing"
status: implementing
---

# Phase 6: Help overlay, walkthroughs and sharing

Add the help overlay with iPhone and Android saving walkthroughs and a desktop note. Add a help link with no ZIP, and Copy link for the starting page or help.

Steps, dependencies and verification are in [the implementation plan, phase 6](../implementation-plan/plan.md). The plan's "Planning decisions" section records the owner decisions this phase must follow.

**Depends on:** phase 5 (live page and the recorded device steps).

## Progress (2026-11-06)

**Built** (in `src/`, not yet in the site checkout or committed):
- **Help link and Copy link:**
  - A "Need help? How to save a contact" line ends the results. It is the only help link on the page.
  - The line under the ZIP form ("How to save a contact" and "Copy link to this page") was removed after the owner saw it on a phone (owner, 2026-11-06). So the only Copy link is "Copy link to these instructions" inside the overlay, and there is no help link before a search.
- **Help overlay:**
  - It is a native modal `<dialog>`.
  - Focus starts on its title. Escape, Close, the Close button at the bottom, or a tap on the backdrop closes it, and focus then returns to the link that opened it.
  - Opening it never changes the URL. The page under it keeps its results and scroll position.
- **Shared help link:** `/congress/#help` opens the overlay on load, and so does a later change to `#help`.
- **Copy link:**
  - It copies the `#help` link, never results. The starting-page copy went with the removed line under the form.
  - On success it shows "Link copied." for 4 seconds.
  - If the copy fails, it shows the link in a selected read-only box.
- **Walkthroughs:**
  - **iPhone:** the New Contact sheet, then the check mark. This is the owner's path.
  - **Android:** the download, Open, choose Contacts, then the add button at the bottom. This is the owner's path.
  - **Troubleshooting:** a brief note for each phone. iPhone: "Create New Contact" on a contact card. Android: open the file from the Files or Downloads app. Neither troubleshooting path has been tried on a phone.
  - **Computer:** a short note linking to Google's import help page (answer 15147365, desktop).
- **Theme Escape handler:** the theme's handler only hides its search overlay and removes `body.overflow-hidden`, which the help overlay doesn't use, so there is no conflict.
- **Build guard:** it now allows reading `location` but still rejects any write: assigning `location` or any of its fields, and `assign`, `replace` and `reload`.

**Verification:**
- **Builds and site checks:** the pinned GitHub Pages build passes, with all 15 output checks.
- **`tools/help_check.js`** passes at 390x844:
  - the overlay is modal, takes focus, closes four ways and returns focus;
  - scroll and the URL are unchanged;
  - both copied links are correct and contain no ZIP;
  - the fallback box appears when a copy fails;
  - there is no sideways scrolling.
- **`/congress/#help` on load** opens the overlay.
- **`browser_check.js`** still passes: 10 ZIP codes, no console messages.
- **Not yet checked:**
  - the real Escape key, which was tested only through the dialog's own close path;
  - VoiceOver and TalkBack;
  - the walkthroughs followed on both phones;
  - the publish.

**Contrast gate** (`verify_states.mjs`, run on the page with its stylesheet and the site's colours):
- Run on `src/body.html` alone, the gate failed falsely: with no stylesheet it read the transparent background as black.
- With the real stylesheet:
  - every default and focus state passes, now that focus keeps the brown;
  - hover in the copper `#C57735` is 3.23:1, below AA's 4.5:1.
- The copper hover is the owner's choice (2026-11-06). It also applies to the existing house.gov links.
- **Decision (owner, 2026-11-06):** keep the copper hover as it is. No change to the page or the site.

## Resume note

**State (2026-11-06):**
- **Close control:** the top close control is a borderless × with a 48×48 tap target (owner request). `help_check.js` passed after this change. The pinned Jekyll build last ran before it.
- **Site checkout:** the Phase 6 build is copied into `../eriksaltwell.com` (`congress.html`, `assets/js/congress.js` and `assets/css/congress.css`; `_data/congress.json` is unchanged). It is not pushed yet, because the owner pushes the site repo. The owner's own `_config.yml` edit and new post in that checkout are not ours.
- **This repo:** the Phase 6 work is not committed until the owner asks.
- **Hover:** it stays copper (owner decision above).
- **Design plugin:** the ux-ui-agent-skills plugin is turned off for this project in `.claude/settings.local.json`. Its stop-hook contrast gate kept failing on `src/body.html` alone.

**Links under the form removed (2026-11-06):** the change is rebuilt and copied into `../eriksaltwell.com` (`congress.html` and `assets/css/congress.css` changed), but not pushed. `help_check.js` was updated and passes on a local test page at 390x844, with no console messages. The pinned Jekyll gems are no longer installed, so the Jekyll build and `check_site.py` were not rerun.

**Walkthrough screenshots (2026-11-07):** the owner's phone captures are in `design_notes/help_screenshots/` (Android 01-03, iPhone 01-04). Built into `src/`, not yet copied to the site checkout:
- **Rule (owner):** images are embedded in the page, with no linked image files. Shrinking, other formats, cropping and annotation are allowed where they help.
- `tools/help_shots.py` (needs Pillow) crops each capture, covers the owner's Google avatar in Android 03, rings the control to tap in orange, shrinks to 480 px wide (shown at 240 px) and writes WebP files to `src/help-shots/`. The 7 files total 47 KB.
- `build.py` replaces each `src="cc-shot:NAME"` in `body.html` with a data URI, and fails if an image is missing or unused. `congress.html` grows to about 67 KB.
- **Steps rewritten** around the captures:
  - **iPhone:** the contact card, then scroll to **Create New Contact**, then the check mark top right, then the check mark top left. The note says "If the New Contact screen opens straight away, start at step 3". The owner can't say which iPhone path is typical.
  - **Android:** Open, then Contacts with Just once or Always (the visitor's choice; Always skips the question next time), then **Save contact**. The button's real name is now known.
- `.cc-help` now sets `box-sizing: border-box` itself, so it fits a 390 px screen without Bootstrap.
- **Verification:** `help_check.js` passes on a local test page at 390x844, with no console messages. All 7 images load at 242 px wide.
- **Not checked:** the pinned Jekyll build (the gems are missing), and the look on real phones.

**Next:**
1. The owner pushes the site and tests on both phones and a computer:
   - open and close the overlay in each way (×, Close, backdrop, and Escape on the computer);
   - open help after a search and check the results and scroll position are kept;
   - save one official by following the walkthrough steps;
   - use both Copy link buttons and check the pasted links have no ZIP;
   - open a shared `/congress/#help` link;
   - if possible, try the troubleshooting paths.
2. Done (2026-11-07): the Android button is **Save contact**, now in the walkthrough. The screenshot build is copied into `../eriksaltwell.com` (`congress.html` and `assets/css/congress.css`), not pushed.
3. Fix whatever the owner reports, rebuild with `tools/build.py`, then copy with `tools/copy_to_site.py ../eriksaltwell.com`.
4. When the owner asks, commit. Then mark this item complete with the phone results.

**Still open from the Phase 5 notes:** whether the link labels ("Share your views") show on both phones.

