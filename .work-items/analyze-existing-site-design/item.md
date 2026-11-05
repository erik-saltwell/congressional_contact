---
name: "Analyze Existing Site Design"
status: complete
---

# Analyze Existing Site Design

Analyze the design system used by the owner's existing Jekyll site (eriksaltwell.com, Beautiful Jekyll theme) and document enough of it to make Congressional Contact cohesive and consistent with that site, both when integrated into Jekyll and when delivered as a standalone page.

See [design intent](intent.md). Analysis results will go in the root-level [design_notes directory](../../design_notes/).

The intent was updated on 2026-11-05 to build on the completed [Jekyll integration research](../../research/jekyll-integration.md): one shared source, the same markup with theme classes in both outputs, CSS variables in the standalone file, and the open question of fonts.

**Completed 2026-11-05.** The analysis is in [design_notes/existing-site-design.md](../../design_notes/existing-site-design.md).

**Verification:**
- The site's theme files were compared with upstream Beautiful Jekyll.
- The live site's computed styles were measured at phone width.
- Contrast was computed for every colour pair.
- The reduced CSS and fonts were measured.
- A styled sample of the recommended options passed the design gate; the stock-colour version failed it, as a negative control.

**Owner decisions:**
- The standalone file loads Lora and Open Sans from Google Fonts. This is an exception to the no-external-dependencies rule, for fonts only.
- The page keeps the stock theme and Bootstrap colours, accepting their AA contrast failures.

- **Guiding preference:** match the existing site's design wherever possible. Under it, buttons use the theme's sizes (`btn-lg` for the form's submit button, standard size for Save), official names use the theme's heading style, and there are no icons unless they use the theme's Font Awesome.

The sample page shows the recommended options that were not chosen.
