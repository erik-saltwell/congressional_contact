---
name: "Research Jekyll Integration"
status: complete
---

# Research Jekyll Integration

Work out how to publish Congressional Contact two ways from one shared source:
- a self-contained standalone HTML file that anyone can upload to their own site;
- a Jekyll-native version that the owner can quickly add to their Beautiful Jekyll homepage, eriksaltwell.com, served by GitHub Pages from https://github.com/erik-saltwell/eriksaltwell.com.

Both must keep the ZIP lookup and the vCard saving working.

See [design intent](intent.md) for the settled decisions, background findings and open research questions. The findings will go in the root-level [research directory](../../research/).

**Completed 2026-11-05.** The findings are in [research/jekyll-integration.md](../../research/jekyll-integration.md), and the reproducible test kit is in [research/jekyll-integration-test/](../../research/jekyll-integration-test/).

**Verification:** a local build with GitHub Pages' Jekyll 3.10.0 (`github-pages` gem, `--safe`, production).
- 22 checks comparing the output with the source passed.
- A phone-sized Chrome check of the ZIP lookup, the vCard blobs and the theme passed, with no console errors.
- The unprotected single file was shown to fail the site build.
- Not tested: real data (only synthetic data was used), a real phone, and editing the page's wording like a normal page.

**Owner decisions:**
- The Jekyll version has four files.
- A small script will copy them into place in the site checkout.
- The page is added to the menu with a one-line `_config.yml` edit, made once.

**Follow-ups for later items:**
- The copy script.
- The data script's rules: write only plain numbers, never in exponent form, and never let `</` appear in the data.
- The standalone file's styling and fonts, in Analyze Existing Site Design.
