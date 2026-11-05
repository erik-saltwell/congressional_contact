# Research Jekyll Integration: design intent

## Intended outcome

Find out how Congressional Contact can be published in two forms built from one shared source:

1. **Standalone file.** A single self-contained HTML file that anyone can upload to their own website.
2. **Jekyll version.** A Jekyll-native version that the owner can add quickly and easily to their Beautiful Jekyll homepage, eriksaltwell.com.

Both forms must keep the page's JavaScript working. That JavaScript does two jobs:
- the **ZIP lookup**: the user enters a ZIP code and the page shows the matching officials;
- **building and saving the vCards**: each contact card is built in the browser and saved from a link next to each official.

"Search" in the earlier intent meant the ZIP lookup. It did not mean the theme's own site search.

## Background findings (verified 2026-11-05)

- **eriksaltwell.com runs on Jekyll.** The live site reports `Jekyll v3.10.0` and the Beautiful Jekyll 6.0.1 theme, and GitHub Pages serves it.
- **Source repo:** https://github.com/erik-saltwell/eriksaltwell.com. It is public, is not a fork, and has a single branch, `main`. The Pages settings show it built from `main` at the root, with the custom domain `www.eriksaltwell.com`.
- **Pages build mode:** "legacy" (deploy from a branch), with no Actions workflow in the repo. The owner pushes source files and GitHub builds and publishes the site, so no local build is needed. Because GitHub's built-in Pages build is used, only GitHub Pages' fixed set of Jekyll plugins is available.
- **Theme files:** the Beautiful Jekyll files (`_layouts/`, `_includes/`, `assets/css/`) are copied into the repo. They are not loaded as a remote theme.
- **DNS:** the domain uses Namecheap as both registrar and DNS host. `www` is a CNAME to `erik-saltwell.github.io`, and the bare domain points at GitHub Pages' A records.
- **`erik-saltwell/saltwell_com` is not the live site.** It is an older, unused site repo. Its `baseURL` is `saltwell.com`, which now redirects to an unrelated company. It does not serve the owner's homepage and is out of scope.

## Settled decisions

- **Build pipeline (owner's goal).** Two short Python scripts live in this repo:
  1. A **data script** rebuilds the officials and ZIP data. The owner runs it directly or through a Claude skill.
  2. A **build script** assembles both published outputs from that data plus source parts (markup, CSS and JS fragments).

  The source parts are build inputs stored in this repo and are never published themselves.
- **One shared source** for both outputs. The outputs are not maintained by hand as separate copies.
- **Priorities.**
  1. Highest: the Jekyll version is simple and quick to add to the owner's site.
  2. Lower: other owners of Jekyll sites can adopt it, and they may need to adjust the styling for their own themes.
  3. Separately, self-hosters get the standalone file.
- **Owner's site update step.** Copy the Jekyll output into the site's repo, commit and push.
- **Jekyll version has four files (owner decision, 2026-11-05, after the research):**
  - `congress.html` at the site root;
  - `_data/congress.json`;
  - `assets/js/congress.js`;
  - `assets/css/congress.css`.

  The owner chose this over a single file that relies on `{% raw %}`.
- **A small copy script is required (owner decision, 2026-11-05).** It copies the four files from the build output into place in a local checkout of the owner's site. It is to be built in a later implementation item.
- **Menu listing (owner decision, 2026-11-05).** Adding the page to the site's top menu is a documented one-line `navbar-links` edit to `_config.yml`, made once by hand. Nothing else about the page needs a site config change.
- **Data delivery.** The data is inlined in both outputs, so the page's JavaScript works the same way in both and never fetches data at runtime.
- **What "Jekyll-native" means:**
  - **The site's look by default.** The page uses the site's layout plus Beautiful Jekyll and Bootstrap classes, with as little CSS of its own as possible.
  - **Jekyll conventions.** The data lives in `_data/`, and Liquid inserts it into the page at build time, for example with `jsonify`. Any CSS or JS goes under `assets/`, loaded through Beautiful Jekyll's `css:` and `js:` front matter. Updating the data should then mean replacing one JSON file.
  - **Nice to have:** the page's wording can be edited like any other page.
- **Standalone styling.** The standalone file uses the same markup and theme classes as the Jekyll version. It inlines only the theme and Bootstrap styles the page uses, and collects colors and fonts into CSS variables at the top so self-hosters can restyle it.
- **Research method.** Read the documentation, then build a throwaway test page in a local clone of the site with `jekyll serve`, using the same Jekyll and plugin versions as GitHub Pages. Do not push it to the live site.

## Questions for the research

- ~~Number of files in the Jekyll version.~~ Resolved: four files (see "Settled decisions").
- Does inserting `_data` with `jsonify` work under GitHub Pages' Jekyll 3.10 with no custom plugins? How large can the inlined data be before builds or page loads suffer?
- Does any inline JS or data contain `{{` or `{%`, which Liquid would try to process? Is `{% raw %}` needed, and where?
- Do the `js:` and `css:` front matter work as expected in Beautiful Jekyll 6.0.1? Does the page's JavaScript run alongside the theme's scripts (jQuery, Bootstrap and the search overlay) without clashing?
- In the local test, inside the theme, do the ZIP lookup and the vCard downloads both work?
- How can the build script produce both outputs from the same markup, adding only the styling layer, the front matter and the data insertion?
- Which theme and Bootstrap styles must the standalone file inline, and roughly how big are they?
- What would another owner of a Jekyll site, using a different theme, need to change?

## Out of scope

- The theme's own site search (`post_search`). The page only needs to avoid breaking it.
- The `saltwell_com` repo.
- Pushing anything to the live site during the research.
- Phone import behavior, which was already tested on the `vcard-test` branch.

## Deliverable

Save the findings in the root-level [research directory](../../research/). Explain:
- the feasible approaches for the Jekyll version and how many files it needs;
- what the local test showed;
- how the shared build would produce both outputs;
- the limitations that remain.

No implementation decisions beyond those above are established by this document.
